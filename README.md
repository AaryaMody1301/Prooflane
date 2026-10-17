# Prooflane

**Agree on the work. See the proof. Then pay.**

Prooflane is an outcome checkout for independent data freelancers and small analytics agencies. An AI model drafts reviewable acceptance checks from a client brief. A deterministic CSV evaluator checks the delivery. A human approves the exact delivery snapshot, then a PayPal sandbox order connects that snapshot to a reconciled payment receipt.

New project started on 11 October 2026 for the [PayPal AI Hackathon](https://paypalaihackathon.devpost.com/). Built with the Ponytail approach: Python's standard library, SQLite, and a buildless HTML client.

Follow the [five-phase build plan](docs/BUILD_PLAN.md): local MVP → real AI → PayPal sandbox → usability/reliability → submission. **Phase 1 is complete:** its real-browser workflow and desktop/390px visual gates passed on 17 October. **Phase 2 is active**, with offline adapter checks passing and actual Gemini validation waiting for a local API key. PayPal sandbox validation remains Phase 3.

## Run

Requires Python 3.11 or newer. No pip install, Node, database account, or paid service is needed for sample mode.

```bash
python3 app.py
```

Open **http://127.0.0.1:8787**. On Windows, use `py app.py` if `python3` is unavailable. Stop with Ctrl+C. Restarting keeps locally saved projects in `prooflane.sqlite3`.

1. Draft the sample brief at USD 120.00.
2. Review the five proposed checks and agree on them.
3. Load the faulty example, run checks, and inspect the three failures.
4. Load the corrected example and run checks again.
5. Approve that delivery, create checkout, and complete the simulated payment.
6. Inspect the receipt and activity ledger, then download the evidence JSON. Its delivery hash matches the approved CSV; the export contains the plan and results, without CSV contents.
7. Restart the app, then use **Resume a saved project** to reopen the receipt. Its brief, price, checks and payment state are restored. CSV previews are not saved; upload again if you need to replace a delivery before checkout starts. Switching projects clears unsaved CSV previews. Drafting a new plan creates a separate project.

**Default mode is a fixed acceptance-plan fixture plus a payment simulator. It does not call an AI model or PayPal.** The UI and receipts label both modes. The CSV evaluation, state transitions, hashes, persistence, and HTTP requests work in either mode.

## Connect real services

Copy `.env.example` to `.env` locally. This file is ignored by Git. Keep credentials out of chat, videos, screenshots, and public repositories.

For real AI, set:

```dotenv
AI_MODE=gemini
GEMINI_API_KEY=your_local_key
GEMINI_MODEL=gemini-2.5-flash
```

Use [Google AI Studio](https://aistudio.google.com/apikey) and confirm your project's current [free-tier availability](https://ai.google.dev/gemini-api/docs/pricing) without enabling billing. The model name is configurable. Only the brief goes to Gemini; CSV contents are evaluated locally. Use synthetic briefs because free-tier inputs may be used for product improvement. Unsupported or ambiguous obligations produce clarifications or a rejected plan; revise the brief and draft a new project. Review every proposed check for missing or misunderstood requirements.

For actual PayPal sandbox payments, set:

```dotenv
PAYMENT_MODE=sandbox
PAYPAL_CLIENT_ID=your_sandbox_app_client_id
PAYPAL_CLIENT_SECRET=your_sandbox_app_secret
```

Use the [PayPal Developer Dashboard](https://developer.paypal.com/dashboard/). Create a sandbox REST app tied to a business test account, and use a different personal test account to approve checkout. Keep your real account details accurate. Test accounts and balances are fictitious. Set the sandbox merchant to receive USD. No live-payment base URL exists in this code.

Check configuration before starting a new project:

```bash
python3 app.py doctor
python3 app.py doctor --providers
```

The first command runs offline and reports modes and whether each credential is present, without printing values. It exits with status 1 until both real-service modes and all credentials are configured; sample mode still runs normally. The second command explicitly sends a synthetic brief to Gemini and authenticates with PayPal's sandbox. It never creates an order or captures a payment. Successful provider checks still require the full checkout test below. Keep billing disabled for a zero-cost setup; a free-tier quota failure is an explicit error.

Restart after configuration changes and create a **new project**. During checkout, the browser opens PayPal's sandbox approval page and returns to this localhost app. The callback's token must match the stored order. The backend checks the order's project ID and USD amount before capture, then checks the capture amount and completion status before recording payment. A cancelled or pending transaction is not marked paid. Reconcile again to inspect a pending capture.

Both adapters have local contract tests. Neither provider has been called with actual credentials in the 17 October update. This is a working starter, not a hackathon-ready submission until the real AI and PayPal sandbox flow has been demonstrated.

### Next local step: Phase 2 only

The offline `python app.py doctor` check on 17 October found no `GEMINI_API_KEY` in the process environment or local `.env`; no provider request was made. From PowerShell, create the ignored configuration only if it does not already exist:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Edit `.env` locally to set these values, replacing the key placeholder with your free-tier AI Studio key:

```dotenv
AI_MODE=gemini
PAYMENT_MODE=simulation
GEMINI_API_KEY=your_local_key
GEMINI_MODEL=gemini-2.5-flash
```

Restart with `python app.py` and draft a new project. Review a synthetic inventory brief: “Deliver an inventory CSV with sku and quantity columns. Every sku must be unique. Quantity must be a number between 0 and 100. Include exactly 2 rows.” Expect required columns, unique sku, quantity bounds 0–100 and exactly two rows, each quoting its requirement. Then append “Make the data insightful.” and check for clarification or rejection, with agreement blocked. Record actual returned checks, omissions, model, provider errors and outcome in the build plan. Schema validation checks quotations and supported types; human review must still catch omitted or misinterpreted obligations. Real model availability, quota and interpretation remain unverified without the key. Keep billing disabled and payments simulated. Reserve `doctor --providers`, which also contacts PayPal, for Phase 3.

If order creation times out, the delivery freezes immediately in `CHECKOUT_PENDING`. Retry the same checkout within 15 minutes; its request ID and approved hash remain unchanged. After that window, inspect orders in the sandbox dashboard before starting another project. Editing or replacing a CSV preview requires fresh checks before the UI permits approval or checkout.

## Verify

```bash
python3 -m unittest -v test_app.py
```

Fourteen tests cover malformed plans and CSVs, exact money values, failed deliveries, stale approvals, frozen checkout evidence after a provider timeout, the retry window, pending and mismatched captures, repeated requests, persistence, offline/provider setup diagnostics, and a localhost HTTP flow with concurrent capture replays and an evidence download. Gemini test doubles also cover a custom inventory plan, exact source quotations, bounds, clarification-blocked agreement, empty/malformed provider output and no silent fallback. These are offline contract checks, not actual provider results. Tests do not require network access or credentials.

Optional client controller check with Node 20 or newer (no npm packages):

```bash
node test_client.cjs
```

On Windows, select the interpreter explicitly if `python3` is unavailable: `$env:PYTHON = (Get-Command python).Source; node test_client.cjs`.

This starts a temporary Python HTTP server and runs the actual client handlers against it using DOM stubs. It checks simulated checkout, saved-project selection, restored brief/price/receipt, cleared previews, fresh-page resume, return reconciliation and invalid-return recovery. It does not validate browser layout, native controls or accessibility. The Python app and core test suite do not require Node.

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

Supported checks: required columns, unique nonempty values, nonempty values, numeric ranges and row counts. Up to 300 KB, 5,000 data rows, 30 columns and 20 checks. AI output is data only; no generated code is executed. Prices use integer cents, never floats. Deliveries cannot change after an order starts. A stable `PayPal-Request-Id` is reused for each create and capture action. Capture retries first retrieve the existing order. An uncertain create result older than 15 minutes requires manual inspection rather than blindly creating another order.

## Current boundary and next work

The server intentionally binds to localhost and uses one operator to demonstrate the buyer and seller workflow. It has no independent user authentication, public deployment, background webhook processing, legal contracts, escrow, tax invoicing, guaranteed freelancer payment, or dispute automation. The SHA-256 records a delivery snapshot; it is not proof of ownership, correctness beyond the displayed tests, or a tamper-proof database.

Before public hosting, add authenticated buyer/seller roles, authorization on every project route, HTTPS, CSRF/session controls, durable storage and verified webhook reconciliation. Do not expose this starter through a tunnel or change its host guards. The hosted implementation and integration checks are mapped in the accompanying research report.

The local browser/visual gate is verified above. Real Gemini responses and PayPal sandbox transactions are still pending their separate phase gates.

## License

MIT. Keep third-party licensing and AI-use disclosure accurate in the final submission. Research sources are attributed in the accompanying report.
