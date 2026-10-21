# Native files and accessibility review — 21 October 2026

Chrome native CSV upload, evidence download and 200% browser zoom now pass. The repaired UI has zero violations across 34 standard axe-core 4.14.0 scans. Keyboard, error recovery, table semantics, reflow, text spacing and preference checks pass within the tested local workflow. This does not establish full accessibility conformance: spoken screen-reader behavior and physical assistive devices remain open.

The [machine-readable results](UI_ACCESSIBILITY_RESULTS_2026-10-21.json) record the exact tested UI content hash, scan states, measured widths and limitations. This follow-up supersedes the native-file limitations in the earlier [workspace checkpoint](UI_WORKSPACE_RESULTS_2026-10-21.json); that historical record is unchanged.

## Native file checks

- Selected `examples/passed.csv` through Chrome's file chooser in the working app. The filename appeared, the preview became dirty, and all five acceptance checks passed. No extension permission was changed during this run.
- Selected a synthetic 300,001-byte file through the same chooser path. The size error received focus, the previous preview stayed unchanged, and the file control was restored.
- Activated **Download evidence record** with Enter. Chrome produced a native download event and saved a 4,040-byte JSON attachment. The downloaded file has the expected USD 120.00 simulated receipt, one capture event, matching verification/approval/receipt hashes, and no CSV rows or sample customer emails.
- Hash comparison uses the checked textarea text, whose line endings are normalized by the browser. It does not claim byte identity with the original CRLF file.

These are synthetic local sample/simulation checks in separate ignored databases. They did not contact Gemini or PayPal, alter the configured `.env`, or touch the normal application database.

## Findings fixed

| Finding | Change |
| --- | --- |
| Project context and errors fell outside the main landmark | Include the project header, errors, navigation and stages in one main landmark |
| The mode container used a label without a supported role | Use a named group |
| Repeated header controls lacked a keyboard bypass | Add a visible-on-focus skip link; first Tab and Enter reach the workspace |
| Input borders were only 1.69:1 against white | Use a control border reaching 3.70:1 on white and 3.45:1 on the page |
| Switching button appearance briefly paired dark text with blue | Remove the background transition; the immediate state now passes contrast |
| Saved-project selection changes the displayed stage | Explain that behavior in the select's accessible description |

## Checks and practical limits

| Area | Evidence |
| --- | --- |
| Automated rules | WCAG 2 A/AA, 2.1 A/AA, 2.2 AA and best-practice tags; 34 standard scans, zero violations |
| States | Initial form, draft, agreed delivery, blocked checks, changed preview, verified, approved, order created, receipt, errors, expanded disclosures; separate offline clarification/pending/mode/hash warning fixtures |
| Keyboard | First-tab skip link, saved-project selection, stage navigation, disclosures, file selection, Enter verification/export, Space approval, Enter simulated checkout/capture; no trap observed |
| Focus | Twelve production tab stops remain visible with a 3px outline; errors receive focus; approval/order/capture each focus the payment heading |
| Names and structure | One main, named modes/navigation, associated labels, valid ARIA references, descriptive title/headings; mobile Chrome AX tree retains the table, five row headers and three column headers |
| Reflow and targets | 25 valid measurements at 320, 390, 844, 929 and 1280 CSS pixels; no horizontal overflow; visible tested controls at least 24×24px; 844×390 landscape checked |
| Native 200% zoom | User set Chrome's native menu to 200%; observed DPR 1→2 and viewport 929×861→464×430. Receipt, expanded receipt, Scope, Delivery, new-project form and price error have no horizontal overflow or undersized controls. Error and export focus stay fully visible. User restored 100%, observed DPR 1 and 929×861 again |
| Text spacing | At 320px, Scope, verified Delivery and Receipt retain controls and content with 1.5 line height, 2em paragraph spacing, .12em letter spacing and .16em word spacing |
| Reduced motion | Emulated preference matches and no production animation/transition remains |
| Forced colors | Manual rendered-color review passes all 23 flagged nodes, minimum 19.56:1; native Windows contrast themes were not exercised |
| Status and speech | Error/status roles and focus changes inspected; actual NVDA/JAWS/Narrator speech, live-region announcements and braille remain unverified |

Axe leaves the decorative receipt checkmark for manual color review. It is noninteractive, `aria-hidden`, accompanied by the matching-hash text, and its normal rendered contrast is 5.19:1. Forced-colors scans reproduce the vendor's [mixed foreground/background color defect](https://github.com/dequelabs/axe-core/issues/3978); the raw flags were retained, then checked against the rendered colors and a screenshot. They are not presented as an unqualified automated pass.

The scanner was served only in an ignored QA copy of the production HTML, with its test controls excluded. Its pinned npm version/origin, raw scans, measurements, fixtures and screenshots remain under `.venv/ui-accessibility-2026-10-21/`. Production gains no dependency or audit controls. Temporary viewport and preference emulation was reset.

All 22 Python tests, the Node controller suite and compilation pass locally and in [Windows/Ubuntu CI on the code commit](https://github.com/AaryaMody1301/Prooflane/actions/runs/39577407446). The optional browser runner now protects first-tab skip-link activation and the single main landmark; it was compiled, not executed in this run. The corresponding actions were verified through connected Chrome.

## Open acceptance checks

- Actual screen-reader announcements and assistive-device operation. The connected tools expose DOM/AX information, with native application control disabled.
- Firefox, Safari, physical touch devices and independent disabled-user completion.
- PayPal's external authentication, timing and checkout screens are outside this local sample audit. The remaining Phase 4 real-service and independent-user gates are unchanged.

The test scope follows the [WCAG 2.2 quick reference](https://www.w3.org/WAI/WCAG22/quickref/), especially [non-text contrast](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html), [reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html) and [text spacing](https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html). [Axe's own documentation](https://github.com/dequelabs/axe-core) distinguishes automated findings from the manual checks still needed.
