"""Money/state/CSV checks plus a real localhost HTTP flow; no external credentials."""
import copy
import json
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from http.server import ThreadingHTTPServer

from app import Handler, PayPal, Problem, ROOT, SAMPLE_BRIEF, Store, doctor, draft_plan, money, sample_plan, validate_plan, verify_csv

FAILED = (ROOT / "examples/failed.csv").read_text()
PASSED = (ROOT / "examples/passed.csv").read_text()


def new(store):
    return store.create({"brief": SAMPLE_BRIEF, "price": "120.00"})


def ready(store):
    p = new(store)
    for action, body in [("agree", {}), ("verify", {"csv": PASSED}), ("approve", {})]:
        p = store.act(p["id"], action, body, "http://127.0.0.1:8787")
    return p


def order_result(p, state="COMPLETED", currency="USD", value="120.00"):
    capture = {"id": "SANDBOX-CAPTURE", "status": state, "amount": {"currency_code": currency, "value": value}}
    return {"id": p["order"]["id"], "status": "COMPLETED", "purchase_units": [{"custom_id": p["id"], "amount": {"currency_code": "USD", "value": "120.00"}, "payments": {"captures": [capture]}}]}


class FakePayPal:
    def __init__(self):
        self.state, self.currency = "COMPLETED", "USD"
        self.creates, self.captures = 0, 0

    def create(self, p, origin):
        self.creates += 1
        return {"id": "SANDBOX-ORDER", "status": "CREATED", "purchase_units": [{"custom_id": p["id"], "amount": {"currency_code": "USD", "value": "120.00"}}], "links": [{"rel": "payer-action", "href": "https://www.sandbox.paypal.com/checkoutnow?token=SANDBOX-ORDER"}]}

    def capture(self, p):
        self.captures += 1
        return order_result(p, self.state, self.currency)


class Checks(unittest.TestCase):
    def setUp(self):
        self.store = Store(":memory:")

    def tearDown(self):
        self.store.db.close()

    def test_money_boundaries(self):
        self.assertEqual(money("120.01"), 12001)
        for value in ["-1", "0", "0.99", "10000.01", "NaN", "1.234", "1e2", 120, None, "1;DROP"]:
            with self.subTest(value=value), self.assertRaises(Problem):
                money(value)

    def test_ai_schema_fails_closed(self):
        self.assertEqual(validate_plan(sample_plan(), SAMPLE_BRIEF), sample_plan())
        for replacement in [[], [{"kind": "python", "source": SAMPLE_BRIEF}], [{"kind": "unique", "column": "order_id", "source": "invented"}], [{"kind": "row_count", "min": float("nan"), "source": "Include at least 3 rows."}], [{"kind": "row_count", "min": 2.5, "source": "Include at least 3 rows."}]]:
            plan = sample_plan()
            plan["checks"] = replacement
            with self.subTest(replacement=replacement), self.assertRaises(Problem):
                validate_plan(plan, SAMPLE_BRIEF)
        plan = sample_plan()
        plan["checks"][0]["send_payment"] = True
        with self.assertRaises(Problem):
            validate_plan(plan, SAMPLE_BRIEF)

    def test_gemini_adapter_and_no_silent_fallback(self):
        result = {"candidates": [{"content": {"parts": [{"text": json.dumps(sample_plan())}]}}]}
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-placeholder"}), patch("app.json_request", return_value=result) as call:
            self.assertEqual(draft_plan(SAMPLE_BRIEF, "gemini", "gemini-2.5-flash"), sample_plan())
            self.assertEqual(call.call_args.args[1]["generationConfig"]["responseMimeType"], "application/json")
            self.assertNotIn("key=", call.call_args.args[0])
            self.assertEqual(call.call_args.kwargs["timeout"], 60)
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-placeholder"}), patch("app.json_request", side_effect=Problem("Provider unavailable", 502)), self.assertRaises(Problem):
            draft_plan(SAMPLE_BRIEF, "gemini", "gemini-2.5-flash")
        with self.assertRaises(Problem):
            draft_plan("A new custom brief", "sample", "gemini-2.5-flash")
        for response in [{}, {"candidates": []}, {"candidates": [{"content": {"parts": [{"text": "not JSON"}]}}]}]:
            with self.subTest(response=response), patch.dict("os.environ", {"GEMINI_API_KEY": "test-placeholder"}), patch("app.json_request", return_value=response), self.assertRaises(Problem):
                draft_plan(SAMPLE_BRIEF, "gemini", "gemini-2.5-flash")

    def test_gemini_custom_scope_and_clarifications(self):
        # Provider responses below are test doubles, not evidence of real Gemini interpretation.
        requirements = ["Deliver an inventory CSV with sku and quantity columns.", "Every sku must be unique.", "Quantity must be a number between 0 and 100.", "Include exactly 2 rows."]
        brief = " ".join(requirements)
        plan = {"title": "Inventory handover", "clarifications": [], "checks": [
            {"kind": "required_columns", "columns": ["sku", "quantity"], "source": requirements[0]},
            {"kind": "unique", "column": "sku", "source": requirements[1]},
            {"kind": "number_range", "column": "quantity", "min": 0, "max": 100, "source": requirements[2]},
            {"kind": "row_count", "min": 2, "max": 2, "source": requirements[3]},
        ]}
        self.store.ai_mode = "gemini"
        for ambiguous in (False, True):
            current_brief = brief + (" Make the data insightful." if ambiguous else "")
            plan["clarifications"] = ["What measurable CSV checks define insightful?"] if ambiguous else []
            response = {"candidates": [{"content": {"parts": [{"text": json.dumps(plan)}]}}]}
            with patch.dict("os.environ", {"GEMINI_API_KEY": "test-placeholder"}), patch("app.json_request", return_value=response):
                project = self.store.create({"brief": current_brief, "price": "42.50"})
            self.assertEqual(project["plan"], plan)
            self.assertEqual(project["payment_mode"], "simulation")
            if ambiguous:
                with self.assertRaises(Problem):
                    self.store.act(project["id"], "agree", {}, "")
                self.assertEqual(self.store.get(project["id"])["status"], "DRAFT")
                self.assertIsNone(self.store.get(project["id"])["order"])
            else:
                self.store.act(project["id"], "agree", {}, "")
                passed = self.store.act(project["id"], "verify", {"csv": "sku,quantity\nA,0\nB,100\n"}, "")
                self.assertEqual(passed["status"], "VERIFIED")
                failed = self.store.act(project["id"], "verify", {"csv": "sku,quantity\nA,101\nB,100\n"}, "")
                self.assertEqual(failed["status"], "BLOCKED")
        plan["checks"][0]["source"] = "Invented requirement."
        response = {"candidates": [{"content": {"parts": [{"text": json.dumps(plan)}]}}]}
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-placeholder"}), patch("app.json_request", return_value=response), self.assertRaises(Problem):
            self.store.create({"brief": brief, "price": "42.50"})
        self.assertEqual(self.store.db.execute("SELECT COUNT(*) FROM projects").fetchone()[0], 2)

    def test_real_csv_checks_and_parser_limits(self):
        failed = verify_csv(FAILED, sample_plan()["checks"])
        self.assertFalse(failed["passed"])
        self.assertEqual([r["passed"] for r in failed["checks"]], [True, False, False, False, True])
        self.assertEqual(failed["checks"][1]["failed_rows"], [3])
        self.assertTrue(verify_csv(PASSED, sample_plan()["checks"])["passed"])
        for raw in ["", "a,a\n1,2", "a,b\n1", "a,b\n1,2,3", "a\n", "a\n" + "1\n" * 5001, "a\n" + "x" * 300_000]:
            with self.subTest(raw=raw[:20]), self.assertRaises(Problem):
                verify_csv(raw, sample_plan()["checks"])
        for value in ["NaN", "Infinity", "-1", "abc"]:
            self.assertFalse(verify_csv(PASSED.replace(",125", "," + value), sample_plan()["checks"])["passed"])

    def test_failed_delivery_and_stale_approval_block_payment(self):
        p = new(self.store)
        with self.assertRaises(Problem):
            self.store.act(p["id"], "order", {}, "")
        self.store.act(p["id"], "agree", {}, "")
        p = self.store.act(p["id"], "verify", {"csv": FAILED}, "")
        self.assertEqual(p["status"], "BLOCKED")
        with self.assertRaises(Problem):
            self.store.act(p["id"], "approve", {}, "")
        self.store.act(p["id"], "verify", {"csv": PASSED}, "")
        self.store.act(p["id"], "approve", {}, "")
        p = self.store.act(p["id"], "verify", {"csv": FAILED}, "")
        self.assertIsNone(p["approval"])
        with self.assertRaises(Problem):
            self.store.act(p["id"], "order", {}, "")

    def test_exactly_one_simulated_capture_and_frozen_delivery(self):
        p = ready(self.store)
        p = self.store.act(p["id"], "order", {}, "")
        oid = p["order"]["id"]
        with self.assertRaises(Problem):
            self.store.act(p["id"], "verify", {"csv": PASSED}, "")
        with self.assertRaises(Problem):
            self.store.act(p["id"], "capture", {"order_id": "foreign-order"}, "")
        p = self.store.act(p["id"], "capture", {"order_id": oid, "price": "1.00"}, "")
        replay = self.store.act(p["id"], "capture", {"order_id": oid}, "")
        self.assertEqual(p, replay)
        self.assertEqual(p["receipt"]["amount"], "120.00")
        self.assertEqual(p["receipt"]["delivery_sha256"], p["verification"]["sha256"])

    def test_sandbox_pending_mismatch_and_mode_switch(self):
        fake = FakePayPal()
        self.store.payment_mode, self.store.paypal = "sandbox", fake
        p = ready(self.store)
        p = self.store.act(p["id"], "order", {}, "http://127.0.0.1:8787")
        self.store.act(p["id"], "order", {}, "")
        self.assertEqual(fake.creates, 1)
        body = {"order_id": p["order"]["id"]}
        fake.currency = "EUR"
        with self.assertRaises(Problem):
            self.store.act(p["id"], "capture", body, "")
        self.assertIsNone(self.store.get(p["id"])["receipt"])
        fake.currency, fake.state = "USD", "PENDING"
        p = self.store.act(p["id"], "capture", body, "")
        self.assertEqual(p["status"], "PAYMENT_PENDING")
        self.assertIsNone(p["receipt"])
        self.store.payment_mode = "simulation"
        with self.assertRaises(Problem):
            self.store.act(p["id"], "capture", body, "")
        self.store.payment_mode, fake.state = "sandbox", "COMPLETED"
        p = self.store.act(p["id"], "capture", body, "")
        self.assertEqual(p["status"], "PAID")
        self.assertEqual(p["receipt"]["mode"], "sandbox")

    def test_capture_adapter_reconciles_before_retry(self):
        p = ready(self.store)
        p = self.store.act(p["id"], "order", {}, "")
        adapter = PayPal("test", "test")
        completed = order_result(p)
        with patch.object(adapter, "call", return_value=completed) as call:
            self.assertEqual(adapter.capture(p), completed)
            self.assertEqual(call.call_count, 1)
        approved = copy.deepcopy(completed)
        approved["status"] = "APPROVED"
        with patch.object(adapter, "call", side_effect=[approved, completed]) as call:
            adapter.capture(p)
            self.assertEqual(call.call_args.args[2], "px-" + p["id"])
        mismatch = copy.deepcopy(approved)
        mismatch["purchase_units"][0]["custom_id"] = "foreign-project"
        with patch.object(adapter, "call", return_value=mismatch) as call, self.assertRaises(Problem):
            adapter.capture(p)
        self.assertEqual(call.call_count, 1)

    def test_uncertain_checkout_freezes_delivery_before_retry(self):
        fake = FakePayPal()
        self.store.payment_mode, self.store.paypal = "sandbox", fake
        p = ready(self.store)
        with patch.object(fake, "create", side_effect=Problem("Provider timed out", 502)):
            with self.assertRaises(Problem):
                self.store.act(p["id"], "order", {}, "http://127.0.0.1:8787")
        pending = self.store.get(p["id"])
        self.assertEqual(pending["status"], "CHECKOUT_PENDING")
        self.assertIsNone(pending["order"])
        for action, body in [("verify", {"csv": FAILED}), ("approve", {})]:
            with self.assertRaises(Problem):
                self.store.act(p["id"], action, body, "")
        # Projects saved by the older starter also stay frozen after an attempted checkout.
        pending["status"] = "APPROVED"
        self.store.save(pending)
        with self.assertRaises(Problem):
            self.store.act(p["id"], "verify", {"csv": FAILED}, "")
        p = self.store.act(p["id"], "order", {}, "http://127.0.0.1:8787")
        self.assertEqual(p["status"], "ORDER_CREATED")
        self.assertEqual(p["approval"], pending["approval"])
        self.assertEqual(p["checkout_attempted_at"], pending["checkout_attempted_at"])
        self.assertEqual(fake.creates, 1)
        self.assertEqual(sum(e["action"] == "CHECKOUT_STARTED" for e in p["events"]), 1)

    def test_uncertain_checkout_stops_after_retry_window(self):
        fake = FakePayPal()
        self.store.payment_mode, self.store.paypal = "sandbox", fake
        p = ready(self.store)
        p["status"], p["checkout_attempted_at"] = "CHECKOUT_PENDING", 1
        self.store.save(p)
        with self.assertRaises(Problem) as error:
            self.store.act(p["id"], "order", {}, "http://127.0.0.1:8787")
        self.assertEqual(error.exception.status, 409)
        self.assertEqual(fake.creates, 0)

    def test_doctor_is_offline_by_default_and_never_creates_orders(self):
        keys = {"GEMINI_API_KEY": "private-gemini-placeholder", "PAYPAL_CLIENT_ID": "private-id-placeholder", "PAYPAL_CLIENT_SECRET": "private-secret-placeholder"}
        with patch.dict("os.environ", keys, clear=True), patch("app.draft_plan", return_value=sample_plan()) as ai, patch.object(PayPal, "authenticate") as auth, patch.object(PayPal, "create") as create:
            report = doctor("gemini", "sandbox", "gemini-2.5-flash")
            self.assertTrue(report["configured_for_real_services"])
            self.assertFalse(report["provider_checks_passed"])
            ai.assert_not_called()
            auth.assert_not_called()
            report = doctor("gemini", "sandbox", "gemini-2.5-flash", providers=True)
            self.assertTrue(report["provider_checks_passed"])
            ai.assert_called_once()
            auth.assert_called_once()
            create.assert_not_called()
            for secret in keys.values():
                self.assertNotIn(secret, json.dumps(report))
        with patch.dict("os.environ", {}, clear=True), patch("app.draft_plan") as ai, patch.object(PayPal, "authenticate") as auth:
            self.assertFalse(doctor("sample", "simulation", "gemini-2.5-flash", providers=True)["configured_for_real_services"])
            ai.assert_not_called()
            auth.assert_not_called()

    def test_ai_only_doctor_probes_both_briefs_without_paypal(self):
        measurable = {"title": "Inventory handover", "clarifications": [], "checks": [
            {"kind": "required_columns", "columns": ["quantity", "sku"], "source": "sku and quantity columns"},
            {"kind": "unique", "column": "sku", "source": "Every sku must be unique."},
            {"kind": "number_range", "column": "quantity", "min": 0, "max": 100, "source": "Quantity must be a number between 0 and 100."},
            {"kind": "row_count", "min": 2, "max": 2, "source": "Include exactly 2 rows."},
        ]}
        ambiguous = copy.deepcopy(measurable)
        ambiguous["clarifications"] = ["What measurable CSV checks define insightful?"]
        incomplete = copy.deepcopy(measurable)
        incomplete["checks"][2].pop("max")
        incomplete["checks"].pop()
        with patch.dict("os.environ", {"GEMINI_API_KEY": "private-gemini-placeholder"}, clear=True), patch.object(PayPal, "authenticate") as auth, patch.object(PayPal, "create") as create, patch.object(PayPal, "capture") as capture:
            for responses, expected in [([measurable, ambiguous], True), ([measurable, measurable], False), ([ambiguous, ambiguous], False), ([incomplete, ambiguous], False), ([Problem("Provider returned HTTP 429.", 502), ambiguous], False)]:
                with self.subTest(expected=expected), patch("app.draft_plan", side_effect=responses) as ai:
                    report = doctor("gemini", "simulation", "gemini-3.8-flash", ai_only=True)
                self.assertEqual(report["provider_checks_passed"], expected)
                self.assertFalse(report["configured_for_real_services"])
                self.assertIn("review_required", report)
                self.assertEqual(ai.call_count, 2)
                first, second = [call.args[0] for call in ai.call_args_list]
                self.assertIn("sku and quantity", first)
                self.assertIn("between 0 and 100", first)
                self.assertEqual(second, first + " Make the data insightful.")
                self.assertEqual(report["provider_checks"]["gemini"]["ambiguous"]["plan"], responses[1])
                self.assertNotIn("private-gemini-placeholder", json.dumps(report))
                if responses[0] is incomplete:
                    coverage = report["provider_checks"]["gemini"]["measurable"]["coverage"]
                    self.assertFalse(coverage["quantity_0_100"])
                    self.assertFalse(coverage["exactly_2_rows"])
            auth.assert_not_called()
            create.assert_not_called()
            capture.assert_not_called()

    def test_ai_only_doctor_blocks_missing_key_and_wrong_modes(self):
        for ai_mode, payment_mode, keys in [("gemini", "simulation", {}), ("sample", "simulation", {"GEMINI_API_KEY": "test-placeholder"}), ("gemini", "sandbox", {"GEMINI_API_KEY": "test-placeholder"})]:
            with self.subTest(ai_mode=ai_mode, payment_mode=payment_mode), patch.dict("os.environ", keys, clear=True), patch("app.draft_plan") as ai, patch.object(PayPal, "authenticate") as auth:
                report = doctor(ai_mode, payment_mode, "gemini-2.5-flash", ai_only=True)
                self.assertFalse(report["provider_checks_passed"])
                self.assertIn("blocked:", report["provider_checks"])
                ai.assert_not_called()
                auth.assert_not_called()

    def test_persistence(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test.sqlite3"
            first = Store(path)
            p = ready(first)
            first.db.close()
            second = Store(path)
            self.assertEqual(second.get(p["id"]), p)
            second.db.close()

    def test_localhost_http_flow_and_concurrent_replays(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        server.store = self.store
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        base = "http://127.0.0.1:" + str(server.server_port)
        def post(path, body, extra=None):
            req = Request(base + path, data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "X-Prooflane-Request": "1", **(extra or {})})
            with urlopen(req, timeout=5) as response:
                return json.load(response)
        try:
            with urlopen(base) as response:
                self.assertIn(b"See the proof. Then pay.", response.read())
            with self.assertRaises(HTTPError) as error:
                post("/api/projects", {"brief": SAMPLE_BRIEF, "price": "120.00"}, {"Origin": "https://evil.example"})
            self.assertEqual(error.exception.code, 403)
            error.exception.close()
            p = post("/api/projects", {"brief": SAMPLE_BRIEF, "price": "120.00"})
            path = "/api/projects/" + p["id"]
            for action, body in [("agree", {}), ("verify", {"csv": FAILED}), ("verify", {"csv": PASSED}), ("approve", {}), ("order", {})]:
                p = post(path + "/" + action, body)
            with ThreadPoolExecutor(max_workers=4) as pool:
                results = list(pool.map(lambda _: post(path + "/capture", {"order_id": p["order"]["id"]}), range(8)))
            self.assertTrue(all(result == results[0] for result in results))
            self.assertEqual(sum(e["action"] == "PAYMENT_RECONCILED" for e in results[0]["events"]), 1)
            with urlopen(base + path + "/evidence") as response:
                evidence = json.load(response)
                self.assertIn("attachment;", response.headers["Content-Disposition"])
            self.assertEqual(evidence["format"], "prooflane-evidence-v1")
            self.assertEqual(evidence["project"], results[0])
            self.assertEqual(evidence["project"]["receipt"]["ai_mode"], "sample")
            self.assertEqual(evidence["project"]["receipt"]["mode"], "simulation")
            self.assertNotIn(json.dumps(PASSED), json.dumps(evidence))
            # The saved-project picker lists recent projects and restores an older receipt.
            other = post("/api/projects", {"brief": SAMPLE_BRIEF, "price": "75.50"})
            with urlopen(base + "/api/projects") as response:
                saved = json.load(response)
            self.assertEqual([item["id"] for item in saved], [other["id"], p["id"]])
            with urlopen(base + path) as response:
                resumed = json.load(response)
            self.assertEqual(resumed, results[0])
            self.assertEqual(resumed["receipt"]["amount"], "120.00")
            self.assertEqual(saved[0]["cents"], 7550)
        finally:
            server.shutdown()
            server.server_close()
            worker.join()


if __name__ == "__main__":
    unittest.main(verbosity=2)
