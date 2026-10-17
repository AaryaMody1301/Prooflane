# Prooflane

**Agree on the work. See the proof. Then pay.**

Prooflane is an outcome checkout for independent data freelancers and small analytics agencies. An AI model drafts reviewable acceptance checks from a client brief. A deterministic CSV evaluator checks the delivery. A human approves the exact delivery snapshot, then a PayPal sandbox order connects that snapshot to a reconciled payment receipt.

New project started on 11 October 2026 for the [PayPal AI Hackathon](https://paypalaihackathon.devpost.com/). Built with the Ponytail approach: Python's standard library, SQLite, and a buildless HTML client.

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

If order creation times out, the delivery freezes immediately in `CHECKOUT_PENDING`. Retry the same checkout within 15 minutes; its request ID and approved hash remain unchanged. After that window, inspect orders in the sandbox dashboard before starting another project. Editing or replacing a CSV preview requires fresh checks before the UI permits approval or checkout.

## Verify

```bash
python3 -m unittest -v test_app.py
```

Thirteen tests cover malformed plans and CSVs, exact money values, failed deliveries, stale approvals, frozen checkout evidence after a provider timeout, the retry window, pending and mismatched captures, repeated requests, persistence, offline/provider setup diagnostics, and a localhost HTTP flow with concurrent capture replays and an evidence download. Tests do not require network access or credentials.

## Implementation

- `app.py`: HTTP routes, SQLite state, acceptance-plan validation, CSV checks, Gemini REST and PayPal Orders v2 adapters.
- `static/index.html`: responsive client with scope review, CSV loading, delivery evidence, checkout, receipt, and activity.
- `examples/`: synthetic faulty and corrected CSVs.
- `test_app.py`: runnable checks.
- `docs/BUILD_PLAN.md`: immediate integration gates, project scope and submission checklist.

Supported checks: required columns, unique nonempty values, nonempty values, numeric ranges and row counts. Up to 300 KB, 5,000 data rows, 30 columns and 20 checks. AI output is data only; no generated code is executed. Prices use integer cents, never floats. Deliveries cannot change after an order starts. A stable `PayPal-Request-Id` is reused for each create and capture action. Capture retries first retrieve the existing order. An uncertain create result older than 15 minutes requires manual inspection rather than blindly creating another order.

## Current boundary and next work

The server intentionally binds to localhost and uses one operator to demonstrate the buyer and seller workflow. It has no independent user authentication, public deployment, background webhook processing, legal contracts, escrow, tax invoicing, guaranteed freelancer payment, or dispute automation. The SHA-256 records a delivery snapshot; it is not proof of ownership, correctness beyond the displayed tests, or a tamper-proof database.

Before public hosting, add authenticated buyer/seller roles, authorization on every project route, HTTPS, CSRF/session controls, durable storage and verified webhook reconciliation. Do not expose this starter through a tunnel or change its host guards. The hosted implementation and integration checks are mapped in the accompanying research report.

Visual browser QA has not been performed in this environment. The client JavaScript passes syntax validation, and the server/client HTML route is covered by the HTTP test.

## License

MIT. Keep third-party licensing and AI-use disclosure accurate in the final submission. Research sources are attributed in the accompanying report.
