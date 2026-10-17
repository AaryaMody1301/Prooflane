"""Optional real-browser check. Uses synthetic data, sample AI and simulated payments."""
import argparse
import json
import tempfile
import threading
from contextlib import contextmanager
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from app import Handler, ROOT, SAMPLE_BRIEF, Store


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
            db_path = Path(directory) / "check.sqlite3"
            with local_app(db_path) as base:
                allowed_ports.add(urlparse(base).port)
                page.goto(base)
                expect(page.locator("#mode-title")).to_contain_text("Sample AI fixture")
                page.locator("#draft").click()
                expect(page.locator("#status")).to_have_text("DRAFT")
                project_id = parse_qs(urlparse(page.url).query)["project"][0]
                page.locator("#agree").click()
                page.locator("#failed").click()
                page.locator("#verify").click()
                expect(page.locator("#status")).to_have_text("BLOCKED")
                expect(page.locator("#results .pill.fail")).to_have_count(3)
                expect(page.locator("#order")).to_be_disabled()
                expect(page.locator("#approve")).to_be_hidden()

                passed = (ROOT / "examples/passed.csv").read_text()
                page.locator("#upload").set_input_files(ROOT / "examples/passed.csv")
                expect(page.locator("#csv")).to_have_value(passed)
                page.locator("#verify").click()
                expect(page.locator("#status")).to_have_text("VERIFIED")
                page.locator("#csv").fill(passed + "\n")
                expect(page.locator("#approve")).to_be_disabled()
                expect(page.locator("#dirty-note")).to_be_visible()
                page.locator("#verify").click()
                page.locator("#approve").click()
                expect(page.locator("#status")).to_have_text("APPROVED")
                page.locator("#csv").fill(passed)
                expect(page.locator("#order")).to_be_disabled()
                page.locator("#verify").click()
                page.locator("#approve").click()
                page.locator("#order").click()
                expect(page.locator("#status")).to_have_text("ORDER CREATED")
                expect(page.locator("#csv")).not_to_be_editable()
                page.locator("#capture").click()
                expect(page.locator("#status")).to_have_text("PAID")
                expect(page.locator("#receipt")).to_contain_text("sample AI · simulation payment")

                with page.expect_download() as download_event:
                    page.locator("#evidence").click()
                download = download_event.value
                evidence = json.loads(Path(download.path()).read_text())
                receipt = evidence["project"]["receipt"]
                assert receipt["amount"] == "120.00" and receipt["mode"] == "simulation"
                assert receipt["delivery_sha256"] == evidence["project"]["verification"]["sha256"]
                assert json.dumps(passed) not in json.dumps(evidence)

                page.locator("#price").fill("75.50")
                page.locator("#draft").click()
                expect(page.locator("#status")).to_have_text("DRAFT")
                assert parse_qs(urlparse(page.url).query)["project"][0] != project_id
                page.locator("#projects").select_option(project_id)
                expect(page.locator("#status")).to_have_text("PAID")
                expect(page.locator("#brief")).to_have_value(SAMPLE_BRIEF)
                expect(page.locator("#price")).to_have_value("120.00")
                expect(page.locator("#csv")).to_have_value("")
                page.reload()
                expect(page.locator("#status")).to_have_text("PAID")
                for width in (1280, 390):
                    page.set_viewport_size({"width": width, "height": 844})
                    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), f"Horizontal overflow at {width}px"
                    expect(page.get_by_label("Resume a saved project")).to_be_visible()
                page.locator("#projects").focus()
                page.locator("#projects").press("Tab")
                expect(page.locator("#brief")).to_be_focused()

            # Reopen the same SQLite file in a new server to check actual restart recovery.
            with local_app(db_path) as base:
                allowed_ports.add(urlparse(base).port)
                page.goto(base + "/?project=" + project_id)
                expect(page.locator("#status")).to_have_text("PAID")
                expect(page.locator("#receipt")).to_contain_text(receipt["capture_id"])
                captures = []
                page.on("request", lambda request: captures.append(request.url) if request.method == "POST" and request.url.endswith("/capture") else None)
                with page.expect_response(lambda response: response.request.method == "POST" and response.url.endswith("/capture")) as capture_response:
                    page.goto(base + "/return?project=" + project_id + "&token=SIM-ORDER-" + project_id)
                assert capture_response.value.status == 200
                expect(page.locator("#status")).to_have_text("PAID")
                expect(page.locator("#error")).to_be_hidden()
                expect(page.locator("#capture")).to_be_hidden()
                assert len(captures) == 1
                page.goto(base + "/return?project=" + project_id + "&token=foreign-order")
                expect(page.locator("#error")).to_contain_text("does not match")
                assert len(captures) == 1
                page.goto(base + "/?project=" + "0" * 32)
                expect(page.locator("#error")).to_contain_text("Project not found")
                expect(page.locator("#draft")).to_be_enabled()
            assert not errors, errors
            assert not external, external
            print("PASS: real-browser sample flow, upload, approval guards, simulated checkout, evidence download, saved-project resume, desktop/390px layout, keyboard focus, restart and return recovery.")
            print("Mode: sample AI + simulation only. No real AI or PayPal transaction was tested.")
        finally:
            browser.close()


if __name__ == "__main__":
    main()
