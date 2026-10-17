# Prooflane: phased build plan

Updated 17 October 2026. Work through one phase at a time. A phase advances only when its completion gate has evidence; a fixture or test double does not complete a real-service gate.

**Product:** a client agrees to measurable CSV work and a USD price. AI proposes reviewable acceptance checks; code tests the delivery; a human approves the exact checked file; PayPal sandbox checkout connects that snapshot to a reconciled capture receipt.

**Submission target:** 11 November. **Official deadline:** 13 November 2026, 1:30 AM IST. The official rules permit complete repository setup/run instructions instead of public hosting, and require a public open-source repository plus a public YouTube demo under three minutes. Sources are linked below.

## Schedule and completion gates

Dates are working targets in IST, not automatic phase transitions. Keep 12 November as a submission buffer.

| Phase | Target | Build | Completion gate | Current state |
| --- | --- | --- | --- | --- |
| 1. Local MVP | 17–18 October | Sample brief, review, CSV checks, approval, simulated receipt, saved-project resume, evidence export | Reproducible local flow; faulty file blocked; corrected file paid in simulation; restart/resume preserves evidence | Complete 17 October; headed Edge and desktop/390px visual gates passed |
| 2. Real AI | 19–21 October | Gemini configuration and custom measurable briefs with human review | Actual provider responses for measurable and ambiguous briefs; errors never silently use the sample fixture | Active after Phase 1 gate; offline checks pass, local Gemini key missing |
| 3. PayPal sandbox | 22–25 October | Actual create, buyer approval, capture/readback, cancellation and retry | One real sandbox capture linked to the approved hash; cancellation unpaid; retry and amount mismatch handled | Adapter implemented; credentials and real checkout pending |
| 4. Usability and reliability | 26 October–4 November | Desktop/mobile QA, a second use case, fresh setup, user feedback, final recovery checks | Another person completes the judge path; evidence agrees with the provider; issues fixed | Planned |
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

Gate: credential-backed results for a measurable and an ambiguous brief; reviewed checks and honest limitations. The existing `doctor --providers` checks both Gemini and PayPal, so reserve that combined check for Phase 3 when both are configured. CSV contents stay local.

17 October progress, started only after Phase 1's gate passed:

- Offline `python app.py doctor` reports `AI_MODE=sample`, `PAYMENT_MODE=simulation`, model `gemini-2.5-flash`, and `GEMINI_API_KEY` absent (values never printed). Its exit status 1 is expected until both real-service modes are configured, not a failure of sample mode. No local `.env` exists and no provider call was attempted.
- Added offline Gemini contract coverage for this synthetic measurable brief: “Deliver an inventory CSV with sku and quantity columns. Every sku must be unique. Quantity must be a number between 0 and 100. Include exactly 2 rows.” Test-double checks cover all four requirements with exact quotations, accept quantity bounds 0 and 100, and block 101. Appending “Make the data insightful.” produces a test-double clarification that blocks agreement. Invented quotes create no project; empty/malformed responses and provider errors have no sample fallback. These results verify adapter/state handling, not Gemini's ability to interpret briefs; actual coverage must still be reviewed by a human.
- **Blocked input:** a local free-tier Gemini API key. Follow the README's Phase 2 setup: create `.env` from `.env.example` only if absent, set `AI_MODE=gemini`, `GEMINI_API_KEY` locally and keep `PAYMENT_MODE=simulation`; restart with `python app.py`. Try the two briefs above and record model, actual checks/quotes, missing obligations, clarifications, provider errors and outcome here. No genuine provider results or current model/quota availability are claimed. Phase 2 remains incomplete; PayPal sandbox testing has not begun.

## Phase 3 — PayPal sandbox

Prerequisite: reviewed real-AI plan. Use a sandbox business merchant and a separate sandbox personal buyer. No live-payment endpoint is supported.

1. Put sandbox app client ID and secret in local `.env`. Select `PAYMENT_MODE=sandbox` and keep real AI enabled. Run `python3 app.py doctor`, then `python3 app.py doctor --providers`.
2. Create a new project. Fail a CSV, correct it, approve the hash, create the order, approve as the sandbox buyer and reconcile the capture.
3. Compare the sandbox order/capture IDs, USD amount and project mapping with the downloaded evidence. A return URL or browser message never establishes payment completion.
4. Run a separate cancellation. It must remain unpaid.
5. Exercise repeat reconciliation, pending capture, timeout/readback and wrong amount/project cases. Test doubles cover exceptional states but must be labeled as such.
6. Keep stable create/capture request IDs. An unresolved create freezes delivery; retry the same request within the starter's 15-minute window. After that, inspect sandbox orders before starting another project.

Gate: actual completed sandbox capture, separate cancellation, matching evidence and retry results. OAuth authentication alone does not complete this phase.

## Phase 4 — usability, reliability and judge access

- Test desktop and narrow mobile layouts, keyboard navigation, readable failure details, loading/error states and the PayPal return path.
- Test a second synthetic data-delivery example through real AI and sandbox checkout.
- Ask target data freelancers/clients to try scope review. Aim for three conversations; document real observations, without inventing interview results or savings metrics.
- Have someone run a fresh checkout from the public repo, add their local credentials and follow the README without coaching.
- Recheck persistence, frozen deliveries, stale approvals, mismatched amounts, pending captures, duplicate callbacks and recovery after restart.
- Prepare clear judge setup and access instructions. Keep the functioning build available through judging. Supply any special testing access privately through the submission's supported mechanism; never publish merchant secrets.

Public hosting is a separate decision after Phase 3. Choose it only if it materially improves judge access and there is time to finish independent buyer/seller authentication, per-project authorization, HTTPS/session protection, durable storage and verified webhooks. Do not expose the current localhost starter through a tunnel. Complete local judge instructions are the fallback, so hosting cannot consume the integration buffer.

Gate: working fresh setup, independent walkthrough, browser findings resolved and payment evidence verified. Feature freeze begins 5 November.

## Phase 5 — submit

- Confirm Devpost enrollment and eligibility.
- Finish the English description: problem, target user, AI's role, PayPal's role, architecture, completed work and limitations.
- Record a 2:45 demo: brief → real AI/review → failed CSV → correction/approval → actual sandbox checkout → reconciled evidence.
- Show provider modes clearly. Disclose AI assistance and third-party dependencies accurately; retain the MIT license.
- Check the public repository and YouTube links from a signed-out view. Verify setup instructions and required judge access.
- Submit by 11 November and verify the submitted status. Recheck the official deadline before the final handoff.

Gate: submitted project with functioning access, working links and evidence supporting the demonstration. Keep access available through the judging period, which ends 15 December 2026 at 9:30 PM IST.

## Scope rules and blockers

Phase 1 is complete. The next active work is Phase 2's actual Gemini interpretation and clarification review, waiting for a local key. Keep payments simulated; sandbox credentials and transaction testing belong to Phase 3. Configure credentials locally; do not paste them into chat or commit `.env`.

Keep one delivery, one agreed amount and one capture. Defer escrow, automatic payouts, refunds, multi-milestone work, arbitrary generated code, additional file formats, marketplace features and sponsor integrations. Add an item only if observed user feedback or a broken completion gate requires it.

## Sources checked 17 October

- [Official rules: required AI + PayPal sandbox, judge access, public open-source repo, video and dates](https://paypalaihackathon.devpost.com/rules).
- [PayPal Orders v2](https://developer.paypal.com/api/orders/v2/).
- [PayPal request idempotency](https://developer.paypal.com/api/rest/reference/idempotency/): endpoint support and retention vary; the local retry window is an application guard.
- [Gemini structured output](https://ai.google.dev/gemini-api/docs/structured-output): use supported schema constraints and validate the returned data on the server.
- [Gemini pricing and free-tier conditions](https://ai.google.dev/gemini-api/docs/pricing): recheck availability before enabling a provider.
