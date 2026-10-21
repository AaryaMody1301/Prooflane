# Prooflane

**Agree on the work. See the proof. Then pay.**

Prooflane is an outcome checkout for independent data freelancers and small analytics agencies. An AI model drafts reviewable acceptance checks from a client brief. A deterministic CSV evaluator checks the delivery. A human approves the exact delivery snapshot, then a PayPal sandbox order connects that snapshot to a reconciled payment receipt.

New project started on 11 October 2026 for the [PayPal AI Hackathon](https://paypalaihackathon.devpost.com/). Built with the Ponytail approach: Python's standard library, SQLite, and a buildless HTML client.

Follow the [five-phase build plan](docs/BUILD_PLAN.md): local MVP → real AI → PayPal sandbox → usability/reliability → submission. **Phases 1–3 are complete for the reviewed inventory flow. Phase 4 has started:** Gemini 3.6 Flash drafts the reviewed checks, an actual USD 1.00 sandbox capture matches the approved delivery, repeated reconciliation keeps one capture, and a separate cancelled checkout stays unpaid. The paid receipt and frozen evidence survive restart. See the [AI completion evidence](docs/PHASE2_AI_COMPLETION_2026-10-20.json) and [sandbox completion evidence](docs/PHASE3_SANDBOX_COMPLETION_2026-10-20.json). Independent setup, user feedback and the remaining usability checks are still open.

## Run

Requires Python 3.11 or newer. No pip install, Node, database account, or paid service is needed for sample mode.

```bash
python3 app.py
```

Open **http://127.0.0.1:8787**. On Windows, use `python app.py` if `python3` is unavailable; `py app.py` also works when the launcher has an interpreter configured. Stop with Ctrl+C. Restarting keeps locally saved projects in `prooflane.sqlite3`.

1. Choose **New project**, then draft the sample brief at USD 120.00.
2. In **Scope**, review the five proposed checks and their source quotations, then agree on them.
3. In **Delivery**, open **Choose or replace CSV**, load the faulty example, run checks, and inspect the three failures listed first.
4. Open the same control, load the corrected example and run checks again. **View or edit CSV preview** reveals the raw preview; edits require fresh checks.
5. Approve that delivery. The workspace moves to **Payment**, where you create checkout and complete the simulated payment.
6. Inspect the receipt and activity ledger, then download the evidence JSON. Its delivery hash matches the approved CSV; the export contains the plan and results, without CSV contents.
7. Restart the app, then use **Resume a saved project** to reopen the receipt directly. Its brief, price, checks and payment state are restored. Use the stage buttons to revisit the agreed scope or delivery evidence. CSV previews are not saved; upload again if you need to replace a delivery before checkout starts. Switching projects clears unsaved CSV previews. **New project** opens a separate brief; saved terms stay read-only.

**Default mode is a fixed acceptance-plan fixture plus a payment simulator. It does not call an AI model or PayPal.** The UI and receipts label both modes. The CSV evaluation, state transitions, hashes, persistence, and HTTP requests work in either mode.

## Connect real services

Copy `.env.example` to `.env` locally. This file is ignored by Git. Keep credentials out of chat, videos, screenshots, and public repositories.

For real AI, set:

```dotenv
AI_MODE=gemini
GEMINI_API_KEY=your_local_key
GEMINI_MODEL=gemini-3.6-flash
```

Use [Google AI Studio](https://aistudio.google.com/apikey) and confirm your project's current [free-tier availability](https://ai.google.dev/gemini-api/docs/pricing) without enabling billing. The model name is configurable. Only the brief goes to Gemini; CSV contents are evaluated locally. Use synthetic briefs because free-tier inputs may be used for product improvement. Unsupported or ambiguous obligations produce clarifications or a rejected plan; revise the brief and draft a new project. Review every proposed check for missing or misunderstood requirements.

For actual PayPal sandbox payments, set:

```dotenv
PAYMENT_MODE=sandbox
PAYPAL_CLIENT_ID=your_sandbox_app_client_id
PAYPAL_CLIENT_SECRET=your_sandbox_app_secret
```

Use the [PayPal Developer Dashboard](https://developer.paypal.com/dashboard/). Create a sandbox REST app tied to a business test account, and use a different personal test account to approve checkout. Keep your real account details accurate. Test accounts and balances are fictitious. Set the sandbox merchant to receive USD. For an India-registered sandbox merchant, use an international sandbox buyer, such as a US Personal test account: [PayPal India supports international payments only](https://www.paypal.com/in/cshelp/article/can-i-use-paypal-to-receive-payments-from-indian-customers-help1049). The original India buyer/India merchant pair failed; the same order completed with the US sandbox buyer. No live-payment base URL exists in this code.

Check configuration before starting a new project:

```bash
python3 app.py doctor
python3 app.py doctor --ai
python3 app.py doctor --providers
```

The first command runs offline and reports modes and whether credentials are present, without printing values. Its status 1 is expected during Phase 2 because `configured_for_real_services` requires PayPal as well. Sample mode still runs normally.

`doctor --ai` is the Phase 2 check: it requires Gemini mode, a local key and simulated payments. It sends a measurable inventory brief and an ambiguous variant, prints the returned plans and checks all four known requirements: columns, unique sku, quantity 0–100 and exactly two rows. It also checks the expected clarification state. Errors or missing coverage exit with status 1; passing probes still require human review for exact quotations, extra restrictions and interpretation. This command never contacts PayPal or creates a database, project, order or payment.

Reserve `doctor --providers` for Phase 3. It sends a synthetic brief to Gemini and authenticates with PayPal's sandbox, without creating orders or capturing payments. Authentication alone does not complete the checkout gate. Keep billing disabled; provider and quota failures have no simulated fallback.

Restart after configuration changes and create a **new project**. During checkout, the browser opens PayPal's sandbox approval page and returns to this localhost app. The callback's token must match the stored order. The backend checks the order's project ID and USD amount before capture, then checks the capture amount and completion status before recording payment. A cancelled or pending transaction is not marked paid. Reconcile again to inspect a pending capture.

Both adapters have local contract tests. The [18 October provider review](docs/PHASE2_AI_RESULTS.json) and [early 20 October recheck](docs/PHASE2_AI_RECHECK_2026-10-20.json) retain the original failures. The [later Gemini 3.6 completion](docs/PHASE2_AI_COMPLETION_2026-10-20.json) records reviewed real plans and browser evidence. The [sandbox completion record](docs/PHASE3_SANDBOX_COMPLETION_2026-10-20.json) verifies actual buyer approval/capture, matching evidence, repeated reconciliation, cancellation and restart recovery. The [earlier progress record](docs/PHASE3_SANDBOX_PROGRESS_2026-10-20.json) preserves the original currency blocker. This is a working starter, not a hackathon-ready submission.

### Real AI setup and repeat checks

This checkout uses the verified Gemini 3.6 Flash and sandbox payment configuration. For a fresh setup or a repeat of Phase 2, keep payments simulated during AI interpretation checks. Create the ignored configuration only if it does not already exist:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Edit `.env` locally to set these values, replacing the key placeholder with your free-tier AI Studio key:

```dotenv
AI_MODE=gemini
PAYMENT_MODE=simulation
GEMINI_API_KEY=your_local_key
GEMINI_MODEL=gemini-3.6-flash
```

Run `python app.py doctor --ai` when provider availability recovers. Then restart with `python app.py` and draft a new project. The probe uses: “Deliver an inventory CSV with sku and quantity columns. Every sku must be unique. Quantity must be a number between 0 and 100. Include exactly 2 rows.” Expect all four obligations with exact source quotations. Appending “Make the data insightful.” must ask for clarification or reject the plan, with agreement blocked. Inspect actual returned checks, missing obligations, extra restrictions and provider errors; schema validation alone does not prove correct interpretation. Complete the real browser/API walkthrough before closing Phase 2.

The default model is now `gemini-3.6-flash`, explicitly selected after both synthetic probes passed review. Gemini 3.8 Flash repeatedly returned HTTP 500/503 or unavailable; a low-thinking experiment did not resolve that. The [selected model supports structured output](https://ai.google.dev/gemini-api/docs/models/gemini-3.6-flash), with a [listed free tier](https://ai.google.dev/gemini-api/docs/pricing), checked 20 October. It can still return transient 503s. No automatic model or sample fallback exists. The adapter retains default temperature, an 8,192-token output limit and a 60-second AI timeout; the low-thinking experiment was not deployed. Keep billing disabled.

### Phase 2 hardening — 19 October

Gemini now receives a schema requiring explicit `column`, `columns`, `min` and `max` fields. Inapplicable values use `null`; the adapter removes those placeholders before storing the existing public plan format. Descriptions ask for full requirement quotations and both stated endpoints. Responses must finish with `STOP`; truncated, blocked or malformed responses create no project. Decimal parsing rejects precision loss such as a tiny positive bound silently rounding to zero.

The server independently checks a small set of explicit inclusive English forms: `between X and Y`, `greater than or equal to X`, `less than or equal to X`, `at least`, `at most`, and `exactly N [data] rows`. A missing, altered or additional bound for a recognized form rejects the plan. If a brief sentence has no quoted check and the model supplied no clarifications, the server adds a clearly labeled `Server review` clarification, which blocks agreement.

These are conservative guards, not a general language parser or proof of semantic completeness. Context sentences can need review; multiple obligations within one sentence and unrecognized wording still need human inspection. The guards never fill missing limits, create replacement checks or substitute a sample plan.

Gemini HTTP 500/502/503/504 responses get at most one retry after one second, using the same model, brief and schema. Authentication/not-found/quota errors, timeouts and invalid plans are not automatically retried. The two-brief diagnostic can therefore make up to four Gemini requests; each attempt retains the 60-second timeout. PayPal retry behavior is unchanged. This follows the [official transient-error guidance](https://ai.google.dev/gemini-api/docs/troubleshooting) with a deliberately small request budget.

Validation on 19 October: 21 offline Python tests, the Node controller check and compilation passed, including replay of both captured incomplete plans, omitted-sentence blocking, finished-response checks, bounded retry exhaustion and no PayPal calls. That workspace had no Gemini key, so no new provider or real-AI browser request was made that day. Historical provider evidence stays in `docs/PHASE2_AI_RESULTS.json`.

### Phase 2 recheck — 20 October

Earlier on 20 October, the configured `gemini-3.8-flash` returned a correct ambiguous plan: all four expected checks, exact full quotations, quantity bounds 0–100, exactly two rows and a clarification for “Make the data insightful.” No extra check or restriction appeared. The measurable diagnostic exhausted its bounded retry with HTTP 503. A real Edge browser draft then returned a provider-unavailable error; the UI displayed the error, kept checkout disabled and saved no project. A separate one-attempt “Return the word OK.” control also failed after 60.26 seconds. That recheck did not pass Phase 2; the later completion below uses an explicitly reviewed different model.

All 21 Python tests, the Node controller check, compilation and the Edge **sample** browser runner pass again. Desktop scope, narrow paid-state and real-AI error screenshots were inspected. The sample runner still uses fixtures and simulated payments. The [dated evidence](docs/PHASE2_AI_RECHECK_2026-10-20.json) contains the returned plan, diagnostic failure, browser result and small control; it contains no credentials. No application-source or model-setting change was made.

This checkout now has Python 3.14.8 and optional Playwright inside ignored `.venv`; its Windows `python`/`py` aliases did not run. Use the project interpreter here:

```powershell
.\.venv\Scripts\python.exe app.py doctor --ai
.\.venv\Scripts\python.exe app.py
```

Use `PAYMENT_MODE=simulation` for a repeat `doctor --ai`. This checkout has since advanced to `PAYMENT_MODE=sandbox`; its current preflight command is `.\.venv\Scripts\python.exe app.py doctor --providers`.

### Phase 2 and Phase 3 completion — 20 October

Gemini 3.6 Flash passed the full measurable and ambiguous diagnostic in 8.53 and 6.80 seconds respectively. Reviewed plans include the four exact source sentences, both quantity bounds and both exact-row limits, with no extra restrictions. A Chrome walkthrough blocked the duplicate/out-of-range CSV, accepted quantities 0 and 100, approved the exact hash and produced a clearly labeled USD 42.50 **simulated** receipt. The evidence attachment API, receipt hashes, reload and backend restart preserve that state.

Two full ambiguous browser requests returned 503 without creating projects. A fresh minimal ambiguous brief returned the required columns plus a clarification for “insightful”; agreement and checkout were disabled, and a direct agreement request returned HTTP 409 without changing the draft. This completes the reviewed Phase 2 case; other briefs still require review. Chrome extension upload permission and download-event automation blocked those two browser-tool checks. The corrected CSV was entered in the preview and its evidence attachment verified through the API; the earlier Edge sample upload/download regression passed.

Both providers pass `doctor --providers` in sandbox mode. A new USD 1.00 project passed failure/correction and approval before creating an actual PayPal sandbox order. Its readback has the matching project ID, currency, amount and delivery hash. An empty PayPal `amount.breakdown` field exposed an overly strict dictionary comparison; the validator now checks currency/value while retaining order/project identity. The regression fails before the fix and passes afterward, alongside all 22 tests and the client controller check.

The initial buyer and merchant were both India-registered; checkout failed with `UNSUPPORTED_PAYEE_CURRENCY`. With the approved US Personal sandbox buyer, the same order `62Y81094JH0739710` completed as capture `6C523873TS2828007` for USD 1.00. Provider readback, the local receipt and the evidence export agree on order, amount, project and approved SHA-256. Three reconciliation replays and another browser return preserve that receipt and one completed capture. The separate order was cancelled from PayPal's normal review page; it remains unpaid with zero captures, and reconciliation refuses it. [Phase 3 completion evidence](docs/PHASE3_SANDBOX_COMPLETION_2026-10-20.json) records these results without account logins or secrets.

**Current step: Phase 4.** Post-capture restart/resume passes. The [21 October CI and UI checkpoint](docs/PHASE4_PROGRESS_2026-10-21.json) adds passing Linux/Windows checks and Chrome sample-mode review at 320, 390, 768 and 1280px. Pending requests now lock editable inputs, and errors receive focus so they are visible on mobile. Keyboard focus, failure details, simulated receipts, project switching and return-token recovery pass. The later [native-file and accessibility review](docs/UI_ACCESSIBILITY_REVIEW_2026-10-21.md) verifies Chrome file-chooser upload and actual evidence download, with matching downloaded receipt hashes. A second real-AI/sandbox delivery example, independent fresh setup and target-user feedback remain open; Phase 4 is not complete.

The [workspace upgrade](docs/UI_WORKSPACE_RESULTS_2026-10-21.json) implements the [researched UI plan](docs/UI_UPGRADE_PLAN_2026-10-21.md): compact Scope, Delivery and Payment views; failure-first results; visible price/mode context; read-only saved terms; and a receipt showing whether its hash matches the checked and approved version. Twenty layout checks cover four views at 320/390/768/1280/1440px, with an additional 640px reflow check. The [accessibility follow-up](docs/UI_ACCESSIBILITY_RESULTS_2026-10-21.json) adds a keyboard skip link, complete main landmark, named modes, stronger control borders and removal of a transient button-contrast failure. Thirty-four standard axe scans have zero violations; keyboard, error focus, mobile table semantics, text spacing and reflow pass. Native 200% zoom, actual screen-reader speech and physical-device acceptance remain open; this is not a full conformance claim.

If order creation times out, the delivery freezes immediately in `CHECKOUT_PENDING`. Retry the same checkout within 15 minutes; its request ID and approved hash remain unchanged. After that window, inspect orders in the sandbox dashboard before starting another project. Editing or replacing a CSV preview requires fresh checks before the UI permits approval or checkout.

## Verify

```bash
python3 -m unittest -v test_app.py
```

Twenty-two tests cover malformed plans and CSVs, exact money values, failed deliveries, stale approvals, frozen checkout evidence after a provider timeout, the retry window, pending and mismatched captures, repeated requests, persistence, offline/provider setup diagnostics, and a localhost HTTP flow with concurrent capture replays and an evidence download. Order readback accepts PayPal's optional amount breakdown while rejecting missing/malformed totals and actual currency/value mismatches. Gemini checks include replay of the captured bad plans, exact quoted bounds, missing-sentence review, nullable wire fields, unfinished responses, decimal underflow, bounded HTTP retries and clarification-blocked agreement. The AI-only diagnostic tests cover missing keys, wrong modes, provider errors, incomplete coverage and no PayPal calls. These are offline contract checks, separate from the linked provider results. Tests do not require network access or credentials.

Optional client controller check with Node 20 or newer (no npm packages):

```bash
node test_client.cjs
```

On Windows, select the interpreter explicitly if `python3` is unavailable: `$env:PYTHON = (Get-Command python).Source; node test_client.cjs`.

This starts a temporary Python HTTP server and runs the actual client handlers against it using DOM stubs. It checks simulated checkout, saved-project selection, restored brief/price/receipt, cleared previews, fresh-page resume, return reconciliation, invalid-return recovery, input locks during verification, changed-preview approval guards and error focus. It also checks nine lifecycle view defaults, failure ordering, navigation without requests or lost previews, saved receipt modes, hash-mismatch display, file-handler behavior and oversized-file recovery. Lifecycle fixtures are frontend checks, not new provider acceptance. It does not validate browser layout, native controls or accessibility. The Python app and core test suite do not require Node.

[GitHub Actions checks](.github/workflows/checks.yml) run the 22 Python tests, Node controller check and Python compilation on Ubuntu with Python 3.11 and Windows with Python 3.14, using Node 24. They run for pull requests and pushes to `main`, without provider credentials, npm packages or external-service calls. Both jobs [passed for the Phase 4 code changes](https://github.com/AaryaMody1301/Prooflane/actions/runs/39547552760). Browser review and real-service acceptance remain separate checks.

### Real-browser Phase 1 check

On Windows, use an ignored virtual environment for the optional browser tools. The verified machine has Python 3.14.7, PowerShell 7.6.7, Node 24.20.0 and Edge 155.0.4283.45; `py` reports no installed interpreter and Chrome was unavailable. Run from the repo in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install playwright
.\.venv\Scripts\python.exe browser_check.py --channel msedge --headed --screenshots .venv/visual-qa
```

This is an optional development dependency; running Prooflane still needs only Python's standard library. The check opens a dedicated browser session, starts its own temporary localhost server and database, and uses sample AI plus simulated payments regardless of `.env`. It checks CSV upload, failure/correction, stale-preview guards, simulated capture, evidence download, project resume, restart recovery, valid/foreign return tokens, keyboard focus and horizontal overflow at desktop and 390px widths. External page requests are blocked. It does not use your regular browser profile, credentials or saved projects.

Reuse `.venv` if it already exists. With Chrome installed, use `--channel chrome`. For bundled Chromium, run `.\.venv\Scripts\python.exe -m playwright install chromium`, then use `--channel chromium`. On macOS/Linux, create the environment with `python3 -m venv .venv` and use `.venv/bin/python`. Installation and browser-channel behavior follow the [official Playwright library](https://playwright.dev/python/docs/library) and [browser documentation](https://playwright.dev/python/docs/browsers).

The runner prints `PASS` only after its assertions finish; failures exit with an error. Test databases and downloads are temporary. The optional `--screenshots` directory keeps synthetic desktop/390px pages for visual inspection; `.venv/visual-qa` is ignored. Without that option, no screenshots are retained. Review the rendered pages and failure messages as well; a 390px viewport is not a real-device or full accessibility audit.

**Verified 17 October 2026:** all 14 Python tests, the Node controller check and the headed Edge runner pass (Playwright 1.64.0). Rendered desktop/390px screenshots were inspected for scope, failure details, changed-preview guidance, receipt labels, errors, hash wrapping and keyboard focus. Assertions check overflow/card boundaries throughout the workflow, exact CSV/approval/receipt hashes and payment IDs, absence of CSV contents/customer emails in evidence, two-price project restore, server restart, a new capture through a valid return and foreign-token rejection. The return error no longer suggests restarting an already running app. Phase 1's completion gate passes. Chrome, Safari, Firefox, physical-device and screen-reader checks were not performed; broader usability work remains in Phase 4.

## Implementation

- `app.py`: HTTP routes, SQLite state, acceptance-plan validation, CSV checks, Gemini REST and PayPal Orders v2 adapters.
- `static/index.html`: responsive client with scope review, CSV loading, delivery evidence, checkout, receipt, and activity.
- `examples/`: synthetic faulty and corrected CSVs.
- `test_app.py`: runnable checks.
- `test_client.cjs`: optional controller regression check against the real localhost API.
- `browser_check.py`: optional real-browser Phase 1 workflow, layout and restart check.
- `docs/BUILD_PLAN.md`: immediate integration gates, project scope and submission checklist.
- `docs/PHASE2_AI_RESULTS.json`: historical 18 October Gemini responses, reviewed gaps and provider errors before Phase 2 passed.
- `docs/PHASE2_AI_COMPLETION_2026-10-20.json`: later reviewed Gemini 3.6 probes and real-AI browser completion evidence.
- `docs/PHASE3_SANDBOX_PROGRESS_2026-10-20.json`: historical checkpoint before capture, preserving the initial orders/readback, metadata fix, currency blocker and unpaid error/cancel return.
- `docs/PHASE3_SANDBOX_COMPLETION_2026-10-20.json`: completed USD 1.00 sandbox capture, matching evidence, repeated reconciliation, normal cancellation and post-capture restart recovery. The progress record above is historical.

Supported checks: required columns, unique nonempty values, nonempty values, numeric ranges and row counts. Up to 300 KB, 5,000 data rows, 30 columns and 20 checks. AI output is data only; no generated code is executed. Prices use integer cents, never floats. Deliveries cannot change after an order starts. A stable `PayPal-Request-Id` is reused for each create and capture action. Capture retries first retrieve the existing order. An uncertain create result older than 15 minutes requires manual inspection rather than blindly creating another order.

## Current boundary and next work

The server intentionally binds to localhost and uses one operator to demonstrate the buyer and seller workflow. It has no independent user authentication, public deployment, background webhook processing, legal contracts, escrow, tax invoicing, guaranteed freelancer payment, or dispute automation. The SHA-256 records a delivery snapshot; it is not proof of ownership, correctness beyond the displayed tests, or a tamper-proof database.

Before public hosting, add authenticated buyer/seller roles, authorization on every project route, HTTPS, CSRF/session controls, durable storage and verified webhook reconciliation. Do not expose this starter through a tunnel or change its host guards. The hosted implementation and integration checks are mapped in the accompanying research report.

The local sample browser/visual, reviewed real-AI inventory and actual PayPal sandbox gates are verified above. Phase 4 is underway; independent setup, user feedback, a second delivery example and remaining usability checks are incomplete. No public deployment or submission is claimed.

## License

MIT. Keep third-party licensing and AI-use disclosure accurate in the final submission. Research sources are attributed in the accompanying report.
