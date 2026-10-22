# Prooflane: phased build plan

Updated 22 October 2026. Work through one phase at a time. A phase advances only when its completion gate has evidence; a fixture or test double does not complete a real-service gate.

**Product:** a client agrees to measurable CSV work and a USD price. AI proposes reviewable acceptance checks; code tests the delivery; a human approves the exact checked file; PayPal sandbox checkout connects that snapshot to a reconciled capture receipt.

**Submission target:** 11 November. **Official deadline:** 13 November 2026, 1:30 AM IST. The official rules permit complete repository setup/run instructions instead of public hosting, and require a public open-source repository plus a public YouTube demo under three minutes. Sources are linked below.

## Schedule and completion gates

Dates are working targets in IST, not automatic phase transitions. Keep 12 November as a submission buffer.

| Phase | Target | Build | Completion gate | Current state |
| --- | --- | --- | --- | --- |
| 1. Local MVP | 17–18 October | Sample brief, review, CSV checks, approval, simulated receipt, saved-project resume, evidence export | Reproducible local flow; faulty file blocked; corrected file paid in simulation; restart/resume preserves evidence | Complete 17 October; headed Edge and desktop/390px visual gates passed |
| 2. Real AI | 19–21 October | Gemini configuration and custom measurable briefs with human review | Actual provider responses for measurable and ambiguous briefs; errors never silently use the sample fixture | Complete 20 October for the reviewed Gemini 3.6 inventory flow; source/coverage review, real browser and ambiguity blocking verified |
| 3. PayPal sandbox | 22–25 October | Actual create, buyer approval, capture/readback, cancellation and retry | One real sandbox capture linked to the approved hash; cancellation unpaid; retry and amount mismatch handled | Complete 20 October for the reviewed inventory flow; actual USD 1.00 capture/readback, repeated reconciliation and separate normal cancellation pass; wrong-amount/pending/timeout cases remain offline contracts |
| 4. Usability and reliability | 26 October–4 November | Desktop/mobile QA, a second use case, fresh setup, user feedback, final recovery checks | Another person completes the judge path; evidence agrees with the provider; issues fixed | In progress; CI, recovery, native files and standard accessibility scans pass; screen readers/physical devices, second real-service case, independent setup and feedback remain open |
| 5. Submission | 5–11 November | Feature freeze, demonstration, project description, judge instructions and submission | Public links work; video under 3 minutes; Devpost submission confirmed | Planned |

## Phase 1 — local MVP

Scope: Python 3.11+ standard library, SQLite, one HTML client, one local operator, USD, one delivery and one payment per project. No framework installation or hosted database.

- [x] Fixed sample acceptance plan, with the sample mode labeled.
- [x] Five restricted checks: required columns, unique nonempty values, no missing values, numeric bounds and row count.
- [x] Synthetic faulty/corrected CSV examples, file/row limits and SHA-256.
- [x] Human scope agreement and approval of the checked snapshot.
- [x] Replacement invalidates approval; a changed preview requires fresh checks.
- [x] Checkout freezes evidence before the provider request, including a timeout.
- [x] Mode-labeled simulated receipt and downloadable evidence JSON without raw CSV contents or credentials.
- [x] Saved-project picker restores the brief, amount, review state, receipt and activity. Switching clears unsaved CSV previews.
- [x] Persistence, HTTP, money, payment-state and provider contract tests.
- [x] Client handler check against the real HTTP API: project switching, restored fields/receipt, cleared previews and valid/invalid PayPal returns. Uses DOM stubs; no visual verification claim.
- [x] Run the optional `browser_check.py` real-browser sample workflow, file upload, evidence download, restart recovery and desktop/390px checks in installed Edge.
- [x] Inspect rendered desktop/390px pages: usable native controls, readable failures/errors, receipt modes, wrapped hashes and visible keyboard focus. No document overflow or cards outside the grid in tested states.

Completion evidence, 17 October 2026: clean initial checkout `051065a` on `main`; no AGENTS.md found in the repository or its parent directories. Windows 10.0.26300, PowerShell 7.6.7, Python 3.14.7 (`python`; the `py` launcher found no interpreter), Node 24.20.0, installed Edge 155.0.4283.45. Optional Playwright 1.64.0 is confined to ignored `.venv`; application runtime remains standard-library-only.

Actual checks:

- `python -m unittest -v test_app.py`: 14 tests pass, including real HTTP/SQLite persistence and concurrent simulated capture replays.
- `$env:PYTHON = (Get-Command python).Source; node test_client.cjs`: passes against the actual localhost API.
- `.\.venv\Scripts\python.exe browser_check.py --channel msedge --headed --screenshots .venv/visual-qa`: passes. The faulty file has exactly three failures and checkout is blocked. Corrected upload passes; edits before approval and checkout require new checks. The exported approval, verification and receipt hashes equal the actual CSV SHA-256; simulated order/capture IDs and USD amount match, without raw CSV/customer emails. Two projects restore different prices and states; switching clears previews. Reopening SQLite in a new server preserves records. A valid return captures an unpaid second order; paid-order replay is safe; foreign tokens make no capture request.
- Desktop (1280px) and narrow (390px) pages checked at initial, scope, blocked, changed-preview, approved, paid and error states. Screenshots inspected for controls, readable failure details, simulation labels, hash wrapping and focus. Keyboard traversal reaches brief, price and draft with a visible outline. The misleading restart advice on project/return errors was removed and regression checked.

**Phase 1 gate passed.** Synthetic screenshots remain under ignored `.venv/visual-qa`; test databases/downloads are temporary. No actual AI or PayPal request was made by these checks. Chrome, Safari, Firefox, physical mobile devices and screen readers remain untested; Phase 4 retains the broader usability gate.

## Phase 2 — real AI

Start with the existing adapter and validation. Recheck model availability and structured-output support before choosing a different model; a new framework or model migration is not required just to begin.

1. Add a Gemini key in local `.env`, select `AI_MODE=gemini`, and keep `PAYMENT_MODE=simulation` while testing interpretation. Use a free-tier project without billing.
2. Send a new measurable brief. Review that all obligations appear, bounds are correct and every check quotes the original text. A source quote alone is not proof of correct interpretation.
3. Try ambiguous and unsupported obligations. They must produce a clarification or a rejected plan that cannot proceed to agreement.
4. Check provider errors, malformed JSON, invented source text, unsupported checks and empty output. No silent sample fallback.
5. Record the model, synthetic brief, reviewed output, correction needed and final outcome. Keep credentials out of evidence and videos.

Gate: credential-backed results for a measurable and an ambiguous brief; reviewed checks and honest limitations. Use `doctor --ai` with simulated payments for this phase. Reserve the combined `doctor --providers` check for Phase 3. CSV contents stay local.

17 October progress, started only after Phase 1's gate passed:

- Offline `python app.py doctor` reports `AI_MODE=sample`, `PAYMENT_MODE=simulation`, model `gemini-2.5-flash`, and `GEMINI_API_KEY` absent (values never printed). Its exit status 1 is expected until both real-service modes are configured, not a failure of sample mode. No local `.env` exists and no provider call was attempted.
- Added offline Gemini contract coverage for this synthetic measurable brief: “Deliver an inventory CSV with sku and quantity columns. Every sku must be unique. Quantity must be a number between 0 and 100. Include exactly 2 rows.” Test-double checks cover all four requirements with exact quotations, accept quantity bounds 0 and 100, and block 101. Appending “Make the data insightful.” produces a test-double clarification that blocks agreement. Invented quotes create no project; empty/malformed responses and provider errors have no sample fallback. These results verify adapter/state handling, not Gemini's ability to interpret briefs; actual coverage must still be reviewed by a human.
- **Blocked input:** a local free-tier Gemini API key. Follow the README's Phase 2 setup: create `.env` from `.env.example` only if absent, set `AI_MODE=gemini`, `GEMINI_API_KEY` locally and keep `PAYMENT_MODE=simulation`; restart with `python app.py`. Try the two briefs above and record model, actual checks/quotes, missing obligations, clarifications, provider errors and outcome here. No genuine provider results or current model/quota availability are claimed. Phase 2 remains incomplete; PayPal sandbox testing has not begun.

18 October progress — the missing key above is now configured locally:

- Added `python app.py doctor --ai`. It sends only the two synthetic briefs to Gemini, reports full plans and checks required columns, unique sku, quantity min=0/max=100 and row-count min=max=2. It fails on missing coverage, wrong clarification state, provider errors or wrong modes. Human review remains required. PayPal authentication/order/capture are never called, and no projects or database are created.
- Genuine provider responses and reviews are saved in [PHASE2_AI_RESULTS.json](PHASE2_AI_RESULTS.json). `gemini-2.5-flash` returned HTTP 404 for both briefs. Google's model documentation limits 2.5 access for new users; model listing succeeded, so the key could authenticate. Tested documented free-tier replacements `gemini-3.5-flash-lite` and `gemini-3.8-flash`.
- Flash-Lite's ambiguous response quoted sources exactly and requested clarification, but omitted the quantity maximum and the exact row-count maximum. A measurable request timed out after 60 seconds. Captured numeric text showed thousands of trailing zeros. Flash 3.8's measurable response omitted the maximum and row count and invented a small positive lower bound instead of zero; its ambiguous response was rejected as unusable. Schema validity did not establish correct coverage. A decimal-text experiment also failed validation and was discarded; the public numeric plan contract is retained.
- Tightened prompt guidance for bounds and supported row counts, removed the low-temperature override per Google's Gemini 3 guidance, capped output at 8,192 tokens and extended only the AI response timeout to 60 seconds. Configuration/template defaults now select `gemini-3.8-flash`; no silent model or sample fallback was added. Final focused diagnostic and one retry both returned HTTP 503. No accepted real-AI browser walkthrough was possible, and no completion claim is made for these adapter changes.
- Verification: 16 Python tests, Node controller check, compilation and the headed Edge sample workflow pass. The browser runner still ignores the real key and uses sample AI/simulation; desktop/390px evidence, persistence, hash guards and return recovery remain passing. Local `.env` is ignored and keeps `PAYMENT_MODE=simulation`. No PayPal provider request was made.

19 October progress — adapter hardening, not a new provider result:

- Identified two acceptance gaps: optional wire bounds let a model omit endpoints; schema/source validation did not check explicit quoted limits or flag a wholly unrepresented sentence.
- The Gemini schema now requires explicit nullable fields. The public stored plan format is preserved after normalization. The adapter rejects unfinished responses, malformed output and decimal precision loss.
- Server validation rejects mismatched/missing limits for recognized inclusive English range and row-count forms. Both captured incomplete plans now fail before project persistence in offline replay. A sentence with no quoted check adds a server review clarification when the model supplied none; agreement stays blocked.
- These guards do not reconstruct missing checks or bounds and do not prove semantics inside compound sentences or unrecognized wording. Human review remains required.
- Added one Gemini-only retry, after one second, for HTTP 500/502/503/504. No retry for authentication, missing models, quota errors, timeout or invalid plans; no alternate model, sample fallback or PayPal request. At most two attempts per brief.
- Verification: 21 Python tests, Node controller check and compilation pass. New regressions replay the genuine captured plans in test envelopes and cover exact bounds, omitted sentences, null normalization, truncation, decimal underflow and exhausted retries. The historical headed Edge browser result is not claimed as rerun here.
- This workspace has neither a configured Gemini environment key nor local `.env`; the key recorded on the VS Code machine is not available here. The AI-only doctor correctly reports a configuration block without making a provider request. No secrets were requested or moved, and `PHASE2_AI_RESULTS.json` remains the unchanged historical record.

20 October progress — fresh credential-backed recheck:

- Checked clean `main` at `c3fd7b3`; no applicable AGENTS.md was found. The Windows aliases did not launch Python. Installed the [official Python NuGet runtime](https://docs.python.org/3/using/windows.html#the-nuget-org-packages) under ignored `.venv/runtime`, then created `.venv` with Python 3.14.8 and optional Playwright 1.64.0. No system installation or PATH change was made.
- Prepared ignored `.env` for Gemini and simulated payments; the key was configured locally without appearing in chat or evidence. PayPal credentials remain absent. Rechecked the selected model's official structured-output support and listed free tier; kept the same model and request settings.
- All 21 Python tests, the Node controller check (Node 24.18.0), compilation and the headless Edge 155.0.4283.62 **sample** browser runner pass. The runner covers upload, faulty/corrected CSVs, approval guards, simulated receipt/hash evidence, resume, restart, return tokens, keyboard focus and desktop/390px overflow. Inspected desktop scope and narrow paid screenshots. This is a new sample-mode pass, not a real-service completion claim.
- Ran the actual two-brief `doctor --ai`. The ambiguous response passes all four coverage flags. Reviewed its complete source sentences, quantity min=0/max=100, exactly-two-row min=max=2 and clarification for “insightful”; no extra check or restriction was returned. The measurable response failed with HTTP 503 after the adapter's single retry. The combined diagnostic exits 1.
- Tried the measurable brief through the actual Edge UI and localhost API with Gemini enabled. The provider-unavailable error was displayed, checkout stayed disabled and no project or order was saved. The browser returned local HTTP 502; the sanitized message does not distinguish timeout from other unavailable/invalid provider responses. No successful measurable CSV/approval/receipt flow was reached.
- A separate small control, “Return the word OK.”, made one request to the same model with a 256-token output cap and the existing 60-second timeout. It returned provider-unavailable after 60.26 seconds. There was no further retry, alternate model, sample fallback or PayPal request. Intermittent provider availability/latency remains a blocker; these failures alone do not justify an application-source change.
- Fresh sanitized reports and the reviewed ambiguous plan are in [PHASE2_AI_RECHECK_2026-10-20.json](PHASE2_AI_RECHECK_2026-10-20.json). The 18 October evidence remains unchanged. Screenshots and one-off browser/control tooling stay under ignored `.venv`.

Later 20 October — Phase 2 completion:

- A fresh Gemini 3.8 diagnostic still failed (HTTP 500/unavailable). A same-model `LOW` thinking comparison also failed after roughly 60 seconds per brief; that setting was not deployed.
- Explicitly tested documented free-tier `gemini-3.6-flash` with the existing prompt/schema/validators. Both four-obligation probes pass in 8.53 and 6.80 seconds. Reviewed complete exact quotations, columns, uniqueness, quantity min=0/max=100, row-count min=max=2 and the subjective-obligation clarification. No extra check or restriction appeared. Selected 3.6 in local configuration and the application/template defaults; no automatic fallback was added.
- Actual Chrome UI: created a real-AI inventory project, agreed its reviewed scope, blocked two faulty checks, corrected quantities to 0 and 100, approved the hash and completed a USD 42.50 simulated receipt. Evidence attachment API and verification/approval/receipt hashes match; reload and backend restart preserve the saved real-AI projects. This was an automated synthetic walkthrough, not an independent human trial or PayPal transaction.
- The full ambiguous UI request and one manual retry returned HTTP 503 without creating projects. A fresh minimal ambiguous brief returned the required-column check and an explicit “insightful” clarification. Agreement and checkout were disabled; a direct agreement request returned HTTP 409 and left the draft unchanged with no order.
- Chrome extension file access blocked the file chooser; corrected CSV was entered in the preview. Download-event automation timed out, so the actual evidence attachment endpoint was fetched and verified directly. No extension permission was changed. Earlier Edge sample upload/download QA remains separate passing evidence.
- [PHASE2_AI_COMPLETION_2026-10-20.json](PHASE2_AI_COMPLETION_2026-10-20.json) records the actual provider plans, failed comparisons, browser states and limitations. The model can still return transient 503s, and these cases do not establish general semantic completeness.

**Phase 2 gate passed for the reviewed inventory flow.** Phase 3 started afterward. Keep `doctor --ai` restricted to simulated payments for any repeat AI-only probe; current sandbox setup uses `doctor --providers`.

## Phase 3 — PayPal sandbox

Prerequisite: reviewed real-AI plan. Use a sandbox business merchant and a separate sandbox personal buyer. No live-payment endpoint is supported.

1. Put sandbox app client ID and secret in local `.env`. Select `PAYMENT_MODE=sandbox` and keep real AI enabled. Run `python3 app.py doctor`, then `python3 app.py doctor --providers`.
2. Create a new project. Fail a CSV, correct it, approve the hash, create the order, approve as the sandbox buyer and reconcile the capture.
3. Compare the sandbox order/capture IDs, USD amount and project mapping with the downloaded evidence. A return URL or browser message never establishes payment completion.
4. Run a separate cancellation. It must remain unpaid.
5. Exercise repeat reconciliation, pending capture, timeout/readback and wrong amount/project cases. Test doubles cover exceptional states but must be labeled as such.
6. Keep stable create/capture request IDs. An unresolved create freezes delivery; retry the same request within the starter's 15-minute window. After that, inspect sandbox orders before starting another project.

Gate: actual completed sandbox capture, separate cancellation, matching evidence and retry results. OAuth authentication alone does not complete this phase.

20 October credential preflight: both sandbox app credentials are configured locally. One call through the existing `PayPal.authenticate()` adapter to `https://api-m.sandbox.paypal.com/v1/oauth2/token` returned HTTP 200 in 1.12 seconds. Credentials and the access token were not printed or saved in evidence. The [sanitized preflight record](PAYPAL_SANDBOX_PREFLIGHT_2026-10-20.json) records one OAuth request and zero orders/captures at that point. Payments stayed simulated until Phase 2 passed.

20 October sandbox execution — after Phase 2's gate:

- Selected `PAYMENT_MODE=sandbox` with `gemini-3.6-flash`; offline configuration and combined `doctor --providers` pass. The combined probe returned five Gemini checks with no clarification and successful PayPal OAuth; it created no payments.
- Created a new USD 1.00 real-AI inventory project, reviewed all four checks, blocked the duplicate/out-of-range CSV, corrected both boundary values and approved SHA-256 `9392061e121e8e6a8b40b552f3c2390c010de46236406d6db1580d757cf2b555`.
- The original sandbox buyer and merchant were both India-registered. Buyer login succeeded, but PayPal blocked approval with `UNSUPPORTED_PAYEE_CURRENCY`. An approved US Personal sandbox buyer then completed the same order. Order `62Y81094JH0739710` has one `COMPLETED` USD 1.00 capture, `6C523873TS2828007`; its custom/invoice IDs match the project. No application currency validation or live-account settings changed.
- Actual readback includes `amount.breakdown={}`. The old whole-dictionary comparison wrongly rejected it. Fixed the shared order validator to compare currency/value and retain exact order/project identity. Updated create/capture fixtures to include the observed metadata; a new regression reproduces the failure before the fix and rejects missing/malformed amounts and actual currency/value mismatches. All 22 Python tests, Node controller and compilation pass; a fresh actual readback now validates.
- The provider amount, completed capture, local receipt and evidence export match USD 1.00 and the approved hash. Three local reconciliation replays and another browser return preserve the same receipt. Provider readbacks before and after those replays contain the same single completed capture.
- The separate real-AI USD 1.00 order was cancelled from PayPal's normal approval review with the US buyer. Prooflane shows cancellation and remains `ORDER_CREATED` with no receipt; reconciliation refuses it because approval is missing. Provider readback remains `PAYER_ACTION_REQUIRED` with zero captures. Cancellation leaves an unapproved order available; it does not mark it paid.
- The [completion record](PHASE3_SANDBOX_COMPLETION_2026-10-20.json) contains matching payment evidence, cancellation and restart results. The [earlier progress record](PHASE3_SANDBOX_PROGRESS_2026-10-20.json) is historical and preserves the currency blocker and readback bug. Credentials, access tokens and account logins are excluded.

**Phase 3 gate passed for the reviewed inventory flow.** Actual capture, matching evidence, repeated reconciliation and normal cancellation are verified. Exceptional pending/timeout/wrong-amount cases remain labeled offline contract tests; they were not induced against the provider.

## Phase 4 — usability, reliability and judge access

Started 20 October after Phase 3 passed. The first recovery check passes: restarting the backend and reloading the paid project preserves the receipt, order, approval, verification and event history; the separately cancelled project remains unpaid. No new order or capture was requested by that recovery check. See the `phase4_start` fields in the [completion evidence](PHASE3_SANDBOX_COMPLETION_2026-10-20.json).

21 October [CI and UI checkpoint](PHASE4_PROGRESS_2026-10-21.json):

- Added credential-free CI for Ubuntu/Python 3.11 and Windows/Python 3.14 with Node 24. Both jobs pass the 22 Python tests, controller regression and compilation.
- Chrome sample/simulation review passes scope, blocked and paid layouts at 320/390/768/1280px, desktop/mobile keyboard focus, readable CSV-line failures, project switching, receipt/hash agreement, reload and valid/foreign return-token recovery. These checks use separate ignored test databases; they make no Gemini or PayPal requests.
- Fixed two observed issues: verification no longer permits preview edits while a response is pending, and mobile errors receive focus instead of appearing above the viewport. The controller regression failed before the shared UI fix and passes afterward; the delayed browser retest rejects edits and restores controls after completion.
- At this checkpoint native file-chooser upload was blocked and browser download-event automation was not repeated. The later [native-file/accessibility review](UI_ACCESSIBILITY_REVIEW_2026-10-21.md) supersedes those two limitations with passing native checks; the original checkpoint remains historical evidence.

The following gates remain open:

- Complete actual screen-reader announcements and physical-device acceptance; native 200% zoom now passes, while AX semantics do not substitute for spoken-screen-reader checks.
- Test a second synthetic data-delivery example through real AI and sandbox checkout.
- Ask target data freelancers/clients to try scope review. Aim for three conversations; document real observations, without inventing interview results or savings metrics.
- Have someone run a fresh checkout from the public repo, add their local credentials and follow the README without coaching.
- Recheck persistence, frozen deliveries, stale approvals, mismatched amounts, pending captures, duplicate callbacks and recovery after restart.
- Prepare clear judge setup and access instructions. Keep the functioning build available through judging. Supply any special testing access privately through the submission's supported mechanism; never publish merchant secrets.

Public hosting is a separate decision after Phase 3. Choose it only if it materially improves judge access and there is time to finish independent buyer/seller authentication, per-project authorization, HTTPS/session protection, durable storage and verified webhooks. Do not expose the current localhost starter through a tunnel. Complete local judge instructions are the fallback, so hosting cannot consume the integration buffer.

Gate: working fresh setup, independent walkthrough, browser findings resolved and payment evidence verified. Feature freeze begins 5 November.

21 October workspace upgrade: the [research plan](UI_UPGRADE_PLAN_2026-10-21.md) is implemented as Scope, Delivery and Payment views using the existing APIs and saved-project format. The [QA record](UI_WORKSPACE_RESULTS_2026-10-21.json) covers the sample checkout, failure-first results, stale-preview approval guards, persisted modes, receipts and return recovery. All 22 Python tests, the extended controller and Linux/Windows CI pass for the code commit. Twenty DOM layout checks span 320–1440px; selected receipt text/control contrast is at least 5.19:1. These results do not certify accessibility or close the independent-user and real-service gates above.

22 October [interface redesign](UI_REDESIGN_2026-10-22.md): modern project library, search/filter controls, sidebar navigation, recorded progress, CSV drop zone, result filters and redesigned project/receipt surfaces are implemented. Backend and expanded controller checks pass locally. Fresh Chrome sample checkout, native upload/download, 20 layout checks at 320–1440px and 21 axe scans pass after repairing narrow text-spacing navigation. The downloaded receipt matches the checked/approved CSV. Screen-reader speech, physical devices and native 200% zoom remain unverified for this revision; the earlier evidence stays historical.

The later [component-focused judging review](UI_COMPONENT_REVIEW_2026-10-22.md) adds the current ink-and-mint presentation, live saved-evidence preview, quoted source disclosures, workflow cards and safer reopening of changed previews. A fresh sample checkout, actual evidence download, 30 axe scans and 20 layout measurements pass. This improves the Design and Presentation evidence; target-user feedback, independent setup and the second real-service case remain required.

The [source-to-payment upgrade](VERIFIED_OUTCOMES_2026-10-22.md) implements the approved [product strategy](PRODUCT_STRATEGY_2026-10-22.md): source-key/value comparisons, frozen source agreement, clarification revisions, reviewed corrections with Undo, a versioned PayPal reference and standalone receipt verification. All 32 backend tests and the expanded controller pass locally. The new source flow has native file and Chrome checks. Fresh Gemini responses verify the seven-rule plan and clarification revision after an initial HTTP 503; its USD 1.00 sandbox order is waiting for buyer approval. These additions do not close Phase 4 until the expanded live case, independent setup and feedback have evidence.

## Phase 5 — submit

- Confirm Devpost enrollment and eligibility.
- Finish the English description: problem, target user, AI's role, PayPal's role, architecture, completed work and limitations.
- Record a 2:45 demo: brief → real AI/review → failed CSV → correction/approval → actual sandbox checkout → reconciled evidence.
- Show provider modes clearly. Disclose AI assistance and third-party dependencies accurately; retain the MIT license.
- Check the public repository and YouTube links from a signed-out view. Verify setup instructions and required judge access.
- Submit by 11 November and verify the submitted status. Recheck the official deadline before the final handoff.

Gate: submitted project with functioning access, working links and evidence supporting the demonstration. Keep access available through the judging period, which ends 15 December 2026 at 9:30 PM IST.

## Scope rules and blockers

Phases 1–3 are complete for the reviewed inventory case. This checkout runs Gemini 3.6 Flash with sandbox payments; Gemini 3.8 failures and the explicit model comparison remain in the evidence. The India buyer/merchant currency blocker was resolved for testing by using the approved US sandbox buyer on the original order. One completed USD 1.00 capture matches the evidence; repeated reconciliation, normal cancellation and restart recovery pass. Phase 4 now has passing CI, native file checks and repaired browser accessibility checks; screen readers/physical devices, a second real-service case, independent setup and user-feedback gates remain open. Configure credentials locally; do not paste them into chat or commit `.env`.

Keep one delivery, one agreed amount and one capture. Defer escrow, automatic payouts, refunds, multi-milestone work, arbitrary generated code, additional file formats, marketplace features and sponsor integrations. Add an item only if observed user feedback or a broken completion gate requires it.

## Sources

Checked 17 October:

- [Official rules: required AI + PayPal sandbox, judge access, public open-source repo, video and dates](https://paypalaihackathon.devpost.com/rules).
- [PayPal Orders v2](https://developer.paypal.com/api/orders/v2/).
- [PayPal request idempotency](https://developer.paypal.com/api/rest/reference/idempotency/): endpoint support and retention vary; the local retry window is an application guard.
- [Gemini structured output](https://ai.google.dev/gemini-api/docs/structured-output): use supported schema constraints and validate the returned data on the server.
- [Gemini pricing and free-tier conditions](https://ai.google.dev/gemini-api/docs/pricing): recheck availability before enabling a provider.

Checked 18 October:

- [Gemini 2.5 Flash access restrictions for new users](https://ai.google.dev/gemini-api/docs/models/gemini-2.5-flash).
- [Gemini 3.8 Flash structured-output support](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash) and [current free-tier listing](https://ai.google.dev/gemini-api/docs/pricing).
- [Gemini 3 temperature guidance](https://ai.google.dev/gemini-api/docs/gemini-3): keep the default temperature.

Checked 19 October:

- [GenerateContent schema reference](https://ai.google.dev/api/generate-content): required/nullable fields and candidate finish reasons. The existing GenerateContent integration is retained; the wire format still needs a fresh credential-backed check.
- [Gemini troubleshooting and transient retry guidance](https://ai.google.dev/gemini-api/docs/troubleshooting).

Checked 20 October:

- [Gemini 3.8 Flash model capabilities](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash), [listed free tier](https://ai.google.dev/gemini-api/docs/pricing) and [structured-output contract](https://ai.google.dev/gemini-api/docs/structured-output). These document support; they do not prove this account's quota or availability.
- [Python's project-local NuGet runtime guidance](https://docs.python.org/3/using/windows.html#the-nuget-org-packages) and [Python 3.14.8 package](https://www.nuget.org/packages/python/3.14.8).
- [Gemini 3.6 Flash capabilities](https://ai.google.dev/gemini-api/docs/models/gemini-3.6-flash), [GenerateContent structured output support](https://ai.google.dev/gemini-api/docs/generate-content/structured-output) and [thinking configuration contract](https://ai.google.dev/api/generate-content#ThinkingConfig).
- [PayPal Orders v2](https://developer.paypal.com/api/orders/v2/): actual create/readback exercised; optional order amount breakdown is metadata alongside the currency/value total.
