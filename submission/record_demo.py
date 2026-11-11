"""Record genuine app interaction; optional Playwright + imageio-ffmpeg dev tools only.

Run against the already-running real-provider app. A separate completed seven-check
sandbox receipt must be supplied; the video explicitly identifies that separate run.
Never loads credentials into the browser, creates another order or approves PayPal.
"""
import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

CAPTIONS = [
    (0, 12, "Prooflane — Proof Before Payment.\nA CSV can look valid and still contain the wrong records."),
    (12, 24, "Live Gemini drafts measurable checks from the brief.\nThe client sets the price. AI cannot approve work or payment."),
    (24, 35, "Review all seven requirements and attach the original source.\nAgree explicitly. CSV rows stay local."),
    (35, 48, "This delivery substitutes an order.\nThe five structural checks pass; source reconciliation fails."),
    (48, 60, "The total still matches: 285.\nMissing and unexpected source keys block approval and checkout."),
    (60, 74, "Now change revenue by just one cent.\nDecimal comparison detects the exact -0.01 difference."),
    (74, 87, "Review the proposed correction against the agreed source.\nNo invented data, generated code or silent file changes."),
    (87, 99, "Apply is explicit. Undo restores the previous preview.\nBoth require fresh verification before approval."),
    (99, 112, "All seven checks pass on the corrected version.\nExplicit approval freezes the agreement, source, price and delivery hash."),
    (112, 122, "Checkout is now eligible for this approved delivery.\nThe following receipt is from a SEPARATE verified sandbox run."),
    (122, 136, "Separate run: actual USD 1.00 PayPal sandbox capture.\nThe same seven-check workflow; a distinct project and transaction."),
    (136, 148, "Export its evidence and verify the original files separately.\nThe verifier does not need the original project database."),
    (148, 157, "Authenticated, read-only PayPal lookup confirms this capture,\nexact USD amount and version 2 manifest reference."),
    (157, 165, "A changed delivery fails verification.\nProoflane connects reviewed work, approval and checkout. github.com/AaryaMody1301/Prooflane"),
]


def stamp(seconds):
    milliseconds = round(seconds * 1000)
    return f"{milliseconds // 3600000:02}:{milliseconds // 60000 % 60:02}:{milliseconds // 1000 % 60:02},{milliseconds % 1000:03}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="http://127.0.0.1:8787")
    parser.add_argument("--receipt", required=True, help="Completed sandbox project ID")
    parser.add_argument("--channel", default="chrome", choices=["chrome", "msedge", "chromium"])
    args = parser.parse_args()
    parsed = urlparse(args.base)
    if parsed.scheme != "http" or parsed.hostname != "127.0.0.1" or not args.receipt.isalnum():
        parser.error("Use the local app and its exact project ID.")
    from playwright.sync_api import expect, sync_playwright
    import imageio_ffmpeg

    media = ROOT / "submission/media"
    scratch = ROOT / ".venv/demo-recording"
    media.mkdir(parents=True, exist_ok=True)
    scratch.mkdir(parents=True, exist_ok=True)
    subtitle = media / "prooflane-demo.srt"
    report = {"format": "prooflane-media-v1", "main_workflow": "live Gemini + sandbox configuration, no order created", "separate_receipt_project": args.receipt, "captioned": True, "music": False, "duration_target_seconds": 165, "screenshots": [], "steps": []}
    shifts, shift = [], 0
    with sync_playwright() as pw:
        launch = {"headless": True, "slow_mo": 250}
        if args.channel != "chromium":
            launch["channel"] = args.channel
        browser = pw.chromium.launch(**launch)
        context = browser.new_context(viewport={"width": 1440, "height": 720}, record_video_dir=scratch, record_video_size={"width": 1440, "height": 720}, accept_downloads=True)
        external, errors = [], []

        def guard(route):
            target = urlparse(route.request.url)
            if (target.scheme, target.hostname, target.port) == (parsed.scheme, parsed.hostname, parsed.port):
                route.continue_()
            else:
                external.append(target.hostname)
                route.abort()

        context.route("**/*", guard)
        page = context.new_page()
        video = page.video
        page.set_default_timeout(15000)
        page.on("pageerror", lambda e: errors.append(str(e)))
        start = time.monotonic()

        def hold(end, name, focus=None, screenshot=None):
            nonlocal shift
            if focus:
                page.locator(focus).scroll_into_view_if_needed()
            if screenshot:
                page.screenshot(path=media / screenshot, full_page=False)
                report["screenshots"].append(screenshot)
            elapsed = time.monotonic() - start
            if elapsed > end + shift:
                delta = elapsed - (end + shift) + 1
                shifts.append((end, delta))
                shift += delta
            report["steps"].append({"stage": name, "actions_finished_seconds": round(elapsed, 2), "hold_until": round(end + shift, 2)})
            if elapsed < end + shift:
                page.wait_for_timeout((end + shift - elapsed) * 1000)
            print(name, flush=True)

        try:
            page.goto(args.base)
            expect(page.locator("#mode-title")).to_have_text("Gemini AI")
            hold(12, "opening", "#library-title", "01-overview.png")
            page.locator("#library-compare").click()
            page.locator("#price").fill("1.00")
            page.locator("#draft").click()
            expect(page.locator("#status")).to_have_text("Review scope", timeout=125000)
            expect(page.locator("#plan-checks .check")).to_have_count(7)
            report["main_project_id"] = page.url.split("project=")[1]
            hold(24, "live-gemini-plan", "#plan-checks", "02-gemini-checks.png")
            page.locator("#source-upload").set_input_files(ROOT / "examples/source.csv")
            page.locator("#agree").click()
            hold(35, "source-agreement", "#delivery-heading")

            def upload(path):
                if page.locator("#delivery-inputs").get_attribute("open") is None:
                    page.locator("#delivery-inputs > summary").click()
                page.locator("#upload").set_input_files(path)

            upload(ROOT / "examples/substituted.csv")
            page.locator("#verify").click()
            expect(page.locator("#results .pill.fail")).to_have_count(2)
            hold(48, "substituted-order-blocked", "#results", "03-source-failure.png")
            page.locator("#filter-failed").click()
            hold(60, "source-failure-explanation", "#results")
            upload(ROOT / "examples/changed-value.csv")
            page.locator("#verify").click()
            expect(page.locator("#results")).to_contain_text("difference -0.01")
            page.locator("#filter-failed").click()
            hold(74, "one-cent-rejected", "#results", "04-one-cent.png")
            page.locator("#repair").click()
            hold(87, "correction-preview", "#repair-preview", "05-correction.png")
            page.locator("#apply-repair").click()
            page.locator("#undo-repair").click()
            page.locator("#verify").click()
            page.locator("#repair").click()
            page.locator("#apply-repair").click()
            hold(99, "apply-and-undo", "#dirty-note")
            page.locator("#verify").click()
            expect(page.locator("#results .pill.pass")).to_have_count(7)
            hold(107, "seven-passes", "#results", "06-seven-passes.png")
            page.locator("#approve").click()
            expect(page.locator("#status")).to_have_text("Delivery approved")
            hold(122, "approved-checkout-eligible", "#payment-heading", "07-approval.png")
            # A distinct real transaction is deliberately and visibly disclosed in captions.
            page.goto(args.base + "/?project=" + args.receipt)
            expect(page.locator("#status")).to_have_text("Sandbox payment reconciled")
            expect(page.locator("#receipt")).to_contain_text("1.00 USD")
            hold(136, "separate-real-sandbox-receipt", "#receipt", "08-sandbox-receipt.png")
            with page.expect_download() as event:
                page.locator("#evidence").click()
            evidence_path = scratch / "sandbox-evidence.json"
            event.value.save_as(evidence_path)
            page.locator("#open-verifier").click()
            page.locator("#verifier-evidence").set_input_files(evidence_path)
            page.locator("#verifier-delivery").set_input_files(ROOT / ".venv/sandbox-reviewed-delivery.csv")
            page.locator("#verifier-source").set_input_files(ROOT / "examples/source.csv")
            hold(148, "export-and-independent-files", "#verify-export")
            page.locator("#verifier-paypal").check()
            page.locator("#verify-export").click()
            expect(page.locator("#verifier-result")).to_contain_text("Confirmed by PayPal sandbox", timeout=30000)
            hold(157, "authenticated-provider-verifier", "#verifier-result", "09-independent-confirmation.png")
            page.locator("#verifier-delivery").set_input_files(ROOT / "examples/changed-value.csv")
            page.locator("#verify-export").click()
            expect(page.locator("#error")).to_contain_text("does not match")
            hold(165, "changed-delivery-rejected", "#error", "10-tamper-rejected.png")
            assert not errors, errors
            assert not external, external
        finally:
            context.close()
            browser.close()

        raw_video = Path(video.path())
    # Caption band is an editorial overlay below the genuine, unmodified app footage.
    output = media / "prooflane-demo.mp4"
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    factor = 165 / (165 + shift)
    def mapped(seconds):
        return (seconds + sum(delta for anchor, delta in shifts if anchor <= seconds)) * factor
    subtitle.write_text("\n".join(f"{i}\n{stamp(mapped(a))} --> {stamp(mapped(b))}\n{text}\n" for i, (a, b, text) in enumerate(CAPTIONS, 1)), encoding="utf-8")
    subtitle_filter = f"setpts=PTS*{factor:.9f},pad=iw:ih+90:0:0:color=0x10221c,subtitles=prooflane-demo.srt:force_style='FontName=Segoe UI,FontSize=10,PrimaryColour=&H00FFFFFF,Outline=0,Shadow=0,Alignment=2,MarginV=5'"
    subprocess.run([ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-i", str(raw_video), "-t", "165", "-vf", subtitle_filter, "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-pix_fmt", "yuv420p", "-r", "30", "-movflags", "+faststart", str(output)], cwd=media, check=True)
    report.update(video=output.name, bytes=output.stat().st_size, sha256=hashlib.sha256(output.read_bytes()).hexdigest(), browser=args.channel, playback_speed=round(1 / factor, 4), render="H.264, 1440x810, 30fps; burned English captions; no soundtrack; uniformly time-compressed if provider latency exceeds the target")
    (media / "ASSET_MANIFEST.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
