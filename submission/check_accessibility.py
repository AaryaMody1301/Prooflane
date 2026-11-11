"""Optional fresh axe/layout audit against isolated sample/simulation UI."""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from browser_check import local_app


def main():
    from playwright.sync_api import expect, sync_playwright
    results = []
    with tempfile.TemporaryDirectory(prefix="prooflane-axe-") as temp, sync_playwright() as pw, local_app(Path(temp) / "qa.sqlite3") as base:
        browser = pw.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.goto(base)

        def scan(stage):
            for width in (1280, 320):
                page.set_viewport_size({"width": width, "height": 900})
                if not page.evaluate("Boolean(window.axe)"):
                    page.add_script_tag(path=ROOT / ".venv/axe.min.js")
                audit = page.evaluate("async () => {const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','best-practice']}}); const compact=x=>({id:x.id,impact:x.impact,nodes:x.nodes.map(n=>({target:n.target,summary:n.failureSummary}))});return {version:r.testEngine.version,violations:r.violations.map(compact),incomplete:r.incomplete.map(compact),passes:r.passes.length};}")
                audit.update(stage=stage, width=width, no_horizontal_overflow=page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth"))
                results.append(audit)
            page.set_viewport_size({"width": 1280, "height": 900})

        scan("library")
        page.locator("#library-compare").click()
        page.locator("#draft").click()
        expect(page.locator("#status")).to_have_text("Review scope")
        page.locator("#source-upload").set_input_files(ROOT / "examples/source.csv")
        scan("source-scope")
        page.locator("#agree").click()
        page.locator("#substituted").click()
        page.locator("#verify").click()
        expect(page.locator("#status")).to_have_text("Changes needed")
        scan("source-blocked")
        page.locator("#repair").click()
        expect(page.locator("#apply-repair")).to_be_visible()
        scan("correction-preview")
        page.locator("#apply-repair").click()
        page.locator("#verify").click()
        expect(page.locator("#status")).to_have_text("Ready for approval")
        scan("seven-passes")
        page.locator("#approve").click()
        page.locator("#order").click()
        page.locator("#capture").click()
        expect(page.locator("#status")).to_have_text("Simulation complete")
        scan("receipt")
        page.locator("#open-verifier").click()
        page.locator("#verify-export").click()
        expect(page.locator("#error")).to_be_focused()
        scan("verifier-error")
        version = browser.version
        browser.close()
    report = {"browser": "Chrome " + version, "modes": "sample/simulation", "scans": results, "violation_count": sum(len(x["violations"]) for x in results), "all_layouts_pass": all(x["no_horizontal_overflow"] for x in results), "limitations": "Automated axe and viewport emulation only. Incomplete rules require manual review; no screen-reader speech or physical-device certification."}
    (ROOT / "submission/ACCESSIBILITY_2026-11-11.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"scans": len(results), "violations": report["violation_count"], "layouts_pass": report["all_layouts_pass"], "incomplete_rule_ids": sorted({r["id"] for x in results for r in x["incomplete"]})}))
    return int(report["violation_count"] > 0 or not report["all_layouts_pass"])


if __name__ == "__main__":
    raise SystemExit(main())
