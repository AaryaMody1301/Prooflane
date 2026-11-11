# Prooflane — Proof Before Payment

## Inspiration

A freelance data delivery can look correct while containing the wrong records. Column names, unique IDs and a matching total are not enough: one order can replace another, or revenue can change by a cent. The client then has to decide whether to approve a payment without a clear connection between the agreed work, the checked file and the transaction.

We built Prooflane around that decision: agree on what success means, check the delivery against its source, approve the exact passing version, and connect that approval to PayPal checkout.

## What it does

Prooflane helps independent data freelancers, small analytics agencies and their clients review CSV handoffs before payment.

The client supplies a brief and an exact USD price. Gemini proposes constrained acceptance checks, each quoting its requirement. A person reviews the proposed scope and attaches the original source before agreeing. Python then checks the delivered file deterministically.

Our supplied attack examples are deliberately plausible. A substituted order passes the five structural checks and preserves the total, but fails source reconciliation. A one-cent revenue change passes the key check and fails the per-order decimal comparison. Both block approval and checkout.

Prooflane previews corrections based on the agreed source, showing the before/after values and source records. The operator explicitly applies them; Undo restores the preview. Both require fresh verification. Corrections do not invent values, run generated code or overwrite original files.

After every check passes, a person approves the exact delivery snapshot. A versioned SHA-256 manifest covers the brief, checks, USD amount, modes, source and delivery. PayPal Orders v2 stores its reference in `custom_id`. Prooflane checks the reference and amount, reconciles the completed capture, and exports the evidence.

The separate verifier works without the original application database. It recomputes supported checks and hashes; optional authenticated, read-only PayPal lookup confirms the sandbox transaction. Offline consistency alone is never presented as payment authentication.

## How we built it

The runtime uses Python 3.11+ standard-library HTTP and CSV modules, SQLite, `Decimal`, SHA-256, and a buildless HTML/CSS/JavaScript client. There are no runtime packages or paid hosting requirements.

Gemini's REST API returns a constrained structured plan from the brief. The server validates the schema, exact quotations, supported operations and recognized explicit limits. Ambiguous or unsupported obligations require clarification and a reviewed new draft. The AI cannot set prices, approve work, execute code or authorize payment. CSV rows are not sent to Gemini.

PayPal is part of the approval boundary and evidence trail. The sandbox adapter creates an order only for approved work, freezes the delivery before the request, uses stable idempotency keys, reads back before capture, and rejects foreign orders or mismatched amounts/references. Completed payment requires a completed order and capture. Uncertain, cancelled and pending states remain unpaid.

## Challenges we ran into

Structured output is not proof of correct interpretation. Historical Gemini responses omitted numeric bounds despite returning JSON. We added conservative validation and preserved human review; we do not claim a general natural-language correctness guarantee. Provider failures stay visible rather than becoming sample responses.

A total can hide incorrect data. Source-key and per-order decimal checks catch the supplied substitution and one-cent attacks that simpler validation misses.

A payment response can be uncertain or malformed. Freezing evidence before order creation, stable request IDs, provider readback and strict completion checks let us retry without assuming success. Separate local and provider verification labels prevent an editable evidence export from masquerading as authenticated payment proof.

## Accomplishments

On 11 November 2026, a fresh Gemini 3.8 plan contained all seven intended checks with exact quotations and no additional restrictions. The source workflow blocked both attack files, applied a reviewed correction, passed verification and recorded explicit operator approval. After manual Personal sandbox buyer approval, PayPal completed a USD 1.00 sandbox capture. The standalone verifier confirmed the order, capture, amount and version 2 manifest through authenticated readback.

The 34 backend tests and Node controller suite pass. Real Chrome and Edge walkthroughs cover native files/downloads, both source attacks, Apply/Undo, approval, simulated checkout, independent verifier rejection, restart/return recovery and layouts at 320, 390, 768 and 1280 pixels. Those browser regression runs use explicitly labeled fixtures and simulation; they are distinct from the real-provider run.

The project is public under MIT and can run with Python alone. A no-key fixture/simulation path lets judges reproduce the complete local experience before optionally connecting their own providers.

## What we learned

The useful connection is human-reviewed requirements → source-based checks → frozen approval evidence → reconciled checkout. A hash is meaningful only when the viewer understands what it binds and which outside system actually confirms the payment.

## What is not implemented

Prooflane is a localhost, single-operator prototype. It does not provide escrow, live payments, independent buyer/seller accounts, public hosting, webhooks, automatic dispute resolution or guarantees about the real-world truth of source data. Evidence exports are not digitally signed. We have not conducted user interviews or measured customer impact, and we claim no adoption or accuracy metric.

## What's next

Run observed trials with freelance data clients and providers to learn where requirements and failure explanations remain unclear. Before offering a hosted service, add authenticated roles, per-project authorization, HTTPS/session protections and verified webhook reconciliation. Preserve the separation between AI interpretation, deterministic evidence, human approval and payment.

## Development during the hackathon

Repository commits begin on 17 October 2026, within the 1 October–12 November submission period. Development added the initial local checkout, real Gemini integration, actual sandbox checkout, recovery and accessibility work, source reconciliation, reviewable corrections, version 2 manifests, independent verification, and final submission verification. Dated reports and commits distinguish historical results from fresh tests.

## Tools used

Python, SQLite, HTML, CSS, JavaScript, Google Gemini API, PayPal Orders v2 sandbox and GitHub Actions. Playwright, Node.js, axe-core and FFmpeg are optional development/QA/media tools where recorded. OpenAI Codex assisted engineering, testing, documentation and submission preparation. The application does not depend on Codex or an OpenAI API at runtime. No optional sponsor-prize integration or agentic-commerce capability is claimed.
