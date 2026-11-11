"""Optional real-browser check. Uses synthetic data, sample AI and simulated payments."""
import argparse
import hashlib
import json
import tempfile
import threading
from contextlib import contextmanager
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from app import Handler, ROOT, SAMPLE_BRIEF, Store, verify_evidence


@contextmanager
def local_app(db_path):
    store = Store(db_path)  # Explicit defaults; never loads .env or real providers.
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.store = store
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        worker.join()
        store.db.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--channel", choices=["chrome", "msedge", "chromium"], default="chrome")
    parser.add_argument("--headed", action="store_true", help="Show the dedicated test browser")
    parser.add_argument("--screenshots", type=Path, help="Save synthetic desktop/390px pages here for visual review")
    args = parser.parse_args()
    try:
        from playwright.sync_api import expect, sync_playwright
    except ImportError:
        parser.exit(2, "Optional dependency missing. Run: python -m pip install playwright\n")

    with tempfile.TemporaryDirectory(prefix="prooflane-browser-") as directory, sync_playwright() as playwright:
        launch = {"headless": not args.headed}
        if args.channel != "chromium":
            launch["channel"] = args.channel
        browser = playwright.chromium.launch(**launch)
        try:
            context = browser.new_context(viewport={"width": 1280, "height": 960}, accept_downloads=True)
            allowed_ports, external, errors = set(), [], []

            def guard(route):
                target = urlparse(route.request.url)
                if target.scheme == "http" and target.hostname == "127.0.0.1" and target.port in allowed_ports:
                    route.continue_()
                else:
                    external.append(route.request.url)
                    route.abort()

            context.route("**/*", guard)
            page = context.new_page()
            page.on("pageerror", lambda error: errors.append(str(error)))

            def layout(stage):
                for width in (1280, 768, 390, 320):
                    page.set_viewport_size({"width": width, "height": 844})
                    assert page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth"), f"Horizontal overflow: {stage} at {width}px"
                    assert page.evaluate("() => {const right=document.querySelector('.grid').getBoundingClientRect().right; return [...document.querySelectorAll('.main,.side,.main>.card,.side>.card')].every(el=>el.getBoundingClientRect().right<=right+1);}"), f"Cards exceed their grid: {stage} at {width}px"
                    expect(page.get_by_label("Resume a saved project")).to_be_visible()
                    if args.screenshots:
                        args.screenshots.mkdir(parents=True, exist_ok=True)
                        page.screenshot(path=args.screenshots / f"{stage}-{width}.png", full_page=True)
                page.set_viewport_size({"width": 1280, "height": 960})

            db_path = Path(directory) / "check.sqlite3"
            def example(name):
                if page.locator("#delivery-inputs").get_attribute("open") is None:
                    page.locator("#delivery-inputs > summary").click()
                page.locator("#" + name).click()

            def open_preview():
                if page.locator("#preview").get_attribute("open") is None:
                    page.locator("#preview > summary").click()

            with local_app(db_path) as base:
                allowed_ports.add(urlparse(base).port)
                page.goto(base)
                expect(page.locator("#mode-title")).to_contain_text("Sample AI fixture")
                page.keyboard.press("Tab")
                expect(page.get_by_role("link", name="Skip to workspace")).to_be_focused()
                page.keyboard.press("Enter")
                expect(page.locator("#workspace")).to_be_focused()
                assert page.get_by_role("main").count() == 1
                layout("initial")
                expect(page.locator("#library")).to_be_visible()
                page.locator("#studio-payment").click()
                expect(page.locator("#studio-caption")).to_contain_text("No verification or payment recorded")
                page.locator("#studio-open").click()
                page.locator("#draft").click()
                expect(page.locator("#status")).to_have_text("Review scope")
                project_id = parse_qs(urlparse(page.url).query)["project"][0]
                layout("scope")
                page.locator("#agree").click()
                example("failed")
                page.locator("#verify").click()
                expect(page.locator("#status")).to_have_text("Changes needed")
                expect(page.locator("#results .pill.fail")).to_have_count(3)
                expect(page.locator("#order")).to_be_disabled()
                expect(page.locator("#approve")).to_be_hidden()
                page.locator("#results .rule-detail > summary").first.click()
                expect(page.locator("#results .rule-detail[open] q")).to_have_text("Every order_id must be unique.")
                page.locator("#filter-failed").click()
                expect(page.locator("#results .pill.fail")).to_have_count(3)
                expect(page.locator("#results .pill.pass")).to_have_count(0)
                page.locator("#filter-all").click()
                layout("blocked")

                passed = (ROOT / "examples/passed.csv").read_text()
                if page.locator("#delivery-inputs").get_attribute("open") is None:
                    page.locator("#delivery-inputs > summary").click()
                page.locator("#upload").set_input_files(ROOT / "examples/passed.csv")
                expect(page.locator("#csv")).to_have_value(passed)
                page.locator("#verify").click()
                expect(page.locator("#status")).to_have_text("Ready for approval")
                open_preview()
                page.locator("#csv").fill(passed + "\n")
                expect(page.locator("#approve")).to_be_disabled()
                expect(page.locator("#dirty-note")).to_be_visible()
                page.locator("#nav-projects").click()
                expect(page.locator("#library")).to_be_visible()
                page.locator("#nav-delivery").click()
                expect(page.locator("#csv")).to_have_value(passed + "\n")
                expect(page.locator("#approve")).to_be_disabled()
                layout("changed-preview")
                page.locator("#verify").click()
                page.locator("#approve").click()
                expect(page.locator("#status")).to_have_text("Delivery approved")
                page.locator("#nav-delivery").click()
                open_preview()
                page.locator("#csv").fill(passed)
                expect(page.locator("#order")).to_be_disabled()
                page.locator("#verify").click()
                page.locator("#approve").click()
                layout("approved")
                page.locator("#order").click()
                expect(page.locator("#status")).to_have_text("Awaiting payment")
                expect(page.locator("#csv")).to_have_js_property("readOnly", True)
                page.locator("#capture").click()
                expect(page.locator("#status")).to_have_text("Simulation complete")
                expect(page.locator("#receipt")).to_contain_text("sample AI · simulation payment")

                with page.expect_download() as download_event:
                    page.locator("#evidence").click()
                download = download_event.value
                evidence = json.loads(Path(download.path()).read_text())
                receipt = evidence["project"]["receipt"]
                saved_project = evidence["project"]
                assert receipt["amount"] == "120.00" and receipt["mode"] == "simulation"
                assert receipt["delivery_sha256"] == saved_project["verification"]["sha256"] == saved_project["approval"]["sha256"] == hashlib.sha256(passed.encode()).hexdigest()
                assert receipt["order_id"] == saved_project["order"]["id"] == "SIM-ORDER-" + project_id
                assert receipt["capture_id"] == "SIM-CAPTURE-" + project_id
                assert receipt["currency"] == "USD" and receipt["ai_mode"] == "sample"
                assert json.dumps(passed) not in json.dumps(evidence)
                assert all(email not in json.dumps(evidence) for email in ("mila@example.com", "arun@example.com", "lee@example.com"))
                layout("paid")

                page.locator("#new-project").click()
                page.locator("#price").fill("75.50")
                page.locator("#draft").click()
                expect(page.locator("#status")).to_have_text("Review scope")
                draft_id = parse_qs(urlparse(page.url).query)["project"][0]
                assert draft_id != project_id
                page.locator("#projects").select_option(project_id)
                expect(page.locator("#status")).to_have_text("Simulation complete")
                page.locator("#projects").select_option(draft_id)
                expect(page.locator("#status")).to_have_text("Review scope")
                expect(page.locator("#price")).to_have_value("75.50")
                expect(page.locator("#receipt")).to_be_empty()
                page.locator("#agree").click()
                example("passed")
                expect(page.locator("#csv")).to_have_value(passed)
                page.locator("#projects").select_option(project_id)
                expect(page.locator("#status")).to_have_text("Simulation complete")
                expect(page.locator("#brief")).to_have_value(SAMPLE_BRIEF)
                expect(page.locator("#price")).to_have_value("120.00")
                expect(page.locator("#csv")).to_have_value("")
                page.reload()
                expect(page.locator("#status")).to_have_text("Simulation complete")
                page.set_viewport_size({"width": 390, "height": 844})
                page.locator("#new-project").click()
                page.locator("#brief").focus()
                page.locator("#brief").press("Tab")
                expect(page.locator("#price")).to_be_focused()
                page.locator("#price").press("Tab")
                expect(page.locator("#draft")).to_be_focused()
                assert page.locator("#draft").evaluate("el => el.matches(':focus-visible') && getComputedStyle(el).outlineStyle !== 'none'")
                if args.screenshots:
                    page.screenshot(path=args.screenshots / "keyboard-focus-390.png")

                # Leave a second, differently priced order unpaid for a genuine return reconciliation after restart.
                page.locator("#projects").select_option(draft_id)
                expect(page.locator("#status")).to_have_text("Awaiting delivery")
                example("passed")
                page.locator("#verify").click()
                page.locator("#approve").click()
                page.locator("#order").click()
                expect(page.locator("#status")).to_have_text("Awaiting payment")

            # Reopen the same SQLite file in a new server to check actual restart recovery.
            with local_app(db_path) as base:
                allowed_ports.add(urlparse(base).port)
                page.goto(base + "/?project=" + project_id)
                expect(page.locator("#status")).to_have_text("Simulation complete")
                expect(page.locator("#receipt")).to_contain_text(receipt["capture_id"])
                captures = []
                page.on("request", lambda request: captures.append(request.url) if request.method == "POST" and request.url.endswith("/capture") else None)
                with page.expect_response(lambda response: response.request.method == "POST" and response.url.endswith("/capture")) as capture_response:
                    page.goto(base + "/return?project=" + project_id + "&token=SIM-ORDER-" + project_id)
                assert capture_response.value.status == 200
                expect(page.locator("#status")).to_have_text("Simulation complete")
                expect(page.locator("#error")).to_be_hidden()
                expect(page.locator("#capture")).to_be_hidden()
                assert len(captures) == 1
                page.goto(base + "/return?project=" + draft_id + "&token=SIM-ORDER-" + draft_id)
                expect(page.locator("#status")).to_have_text("Simulation complete")
                expect(page.locator("#price")).to_have_value("75.50")
                expect(page.locator("#receipt")).to_contain_text("75.50 USD")
                assert len(captures) == 2
                page.goto(base + "/return?project=" + project_id + "&token=foreign-order")
                expect(page.locator("#error")).to_contain_text("does not match")
                expect(page.locator("#error")).not_to_contain_text("Start the local app")
                assert len(captures) == 2
                layout("foreign-token")
                page.goto(base + "/?project=" + "0" * 32)
                expect(page.locator("#error")).to_contain_text("Project not found")
                expect(page.locator("#draft")).to_be_enabled()
                layout("missing-project")

                # Exercise the current seven-check judging story with real native files.
                page.goto(base)
                page.locator("#library-compare").click()
                page.locator("#price").fill("1.00")
                page.locator("#draft").click()
                expect(page.locator("#plan-checks .check")).to_have_count(7)
                page.locator("#source-upload").set_input_files(ROOT / "examples/source.csv")
                expect(page.locator("#agree")).to_be_enabled()
                page.locator("#agree").click()
                example("substituted")
                page.locator("#verify").click()
                expect(page.locator("#status")).to_have_text("Changes needed")
                expect(page.locator("#results .pill.fail")).to_have_count(2)
                expect(page.locator("#results .pill.pass")).to_have_count(5)
                expect(page.locator("#order")).to_be_disabled()
                layout("source-substitution")
                example("changed-value")
                page.locator("#verify").click()
                expect(page.locator("#results .pill.fail")).to_have_count(1)
                expect(page.locator("#results")).to_contain_text("difference -0.01")
                original = page.locator("#csv").input_value()
                page.locator("#repair").click()
                expect(page.locator("#repair-preview")).to_contain_text("Restore source value")
                layout("source-correction-review")
                page.locator("#apply-repair").click()
                corrected = page.locator("#csv").input_value()
                assert corrected != original
                expect(page.locator("#approve")).to_be_disabled()
                page.locator("#undo-repair").click()
                expect(page.locator("#csv")).to_have_value(original)
                # Undo deliberately invalidates the checked preview, too.
                page.locator("#verify").click()
                page.locator("#repair").click()
                page.locator("#apply-repair").click()
                expect(page.locator("#csv")).to_have_value(corrected)
                with page.expect_download() as delivery_download:
                    page.locator("#download-csv").click()
                delivery_file = Path(directory) / "reviewed-delivery.csv"
                delivery_download.value.save_as(delivery_file)
                assert delivery_file.read_text() == corrected
                page.locator("#verify").click()
                expect(page.locator("#results .pill.pass")).to_have_count(7)
                page.locator("#approve").click()
                page.locator("#order").click()
                page.locator("#capture").click()
                expect(page.locator("#status")).to_have_text("Simulation complete")
                layout("source-receipt")
                with page.expect_download() as evidence_download:
                    page.locator("#evidence").click()
                evidence_file = Path(directory) / "source-evidence.json"
                evidence_download.value.save_as(evidence_file)
                source_evidence = json.loads(evidence_file.read_text())
                result = verify_evidence(source_evidence, corrected, (ROOT / "examples/source.csv").read_text())
                assert result["checks"] == 7 and result["payment_status"] == "simulated"
                assert result["amount"] == "1.00" and not result["payment_verified"]
                source_id = result["project_id"]
                page.locator("#open-verifier").click()
                page.locator("#verifier-evidence").set_input_files(evidence_file)
                page.locator("#verifier-delivery").set_input_files(delivery_file)
                page.locator("#verifier-source").set_input_files(ROOT / "examples/source.csv")
                page.locator("#verify-export").click()
                expect(page.locator("#verifier-result")).to_contain_text("Local file and agreement checks passed")
                expect(page.locator("#verifier-result")).to_contain_text("no PayPal transaction")
                layout("independent-verifier")
                page.locator("#verifier-delivery").set_input_files(ROOT / "examples/changed-value.csv")
                expect(page.locator("#verifier-result")).to_be_empty()
                page.locator("#verify-export").click()
                expect(page.locator("#error")).to_contain_text("does not match")
                expect(page.locator("#error")).to_be_focused()
                expect(page.locator("#verifier-result")).to_be_empty()

            with local_app(db_path) as base:
                allowed_ports.add(urlparse(base).port)
                page.goto(base + "/?project=" + source_id)
                expect(page.locator("#status")).to_have_text("Simulation complete")
                expect(page.locator("#receipt-binding")).to_contain_text(result["manifest_sha256"])
            assert not errors, errors
            assert not external, external
            print("PASS: five- and seven-check browser workflows, native files/downloads, both source attacks, correction Apply/Undo, manifest receipt, independent verifier/tamper rejection, 320/390/768/1280px layouts, keyboard focus, restart and return recovery.")
            print("Browser: " + args.channel + " " + browser.version)
            print("Mode: sample AI + simulation only. No real AI or PayPal transaction was tested.")
        finally:
            browser.close()


if __name__ == "__main__":
    main()
