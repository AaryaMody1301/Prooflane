# Product strategy for a stronger hackathon entry

Researched 22 October 2026. This is a proposed build direction, not implemented functionality or a prediction of winning. The existing readiness report and its unmerged starter-brief correction remain separate work.

**Recommendation: make Prooflane demonstrate an agreement that the work can actually be checked against, followed by a payment whose connection to that work can be verified.** Concentrate on freelance data handoffs. The signature demonstration should catch a plausible but incorrect delivery before checkout, then verify the accepted result after a real sandbox payment.

Suggested pitch: **“A missing order can hide inside a valid spreadsheet. Prooflane catches it before checkout and lets you verify exactly what was paid for.”**

## Research and assessment

The [official rubric](https://paypalaihackathon.devpost.com/rules) weights technology, design, impact, innovation and presentation equally. This argues for a coherent demonstration with credible user evidence. More integrations alone do not establish strength across those criteria.

Adjacent products already establish important parts of the experience:

- [Upwork](https://support.upwork.com/hc/en-us/articles/44564821903763-Understanding-milestones-on-fixed-price-contracts) documents funded milestones, scope alignment and client approval.
- [Contra](https://help.contra.com/en/articles/9322763-paid-projects) documents paid projects and milestone approval/payment structures.
- [Soda AI CLI](https://soda.io/blog/introducing-soda-ai-cli) generates data contracts/checks and can act on local files. [GX Core](https://docs.greatexpectations.io/docs/core/introduction/) supplies data-validation workflows.

My inference: a project tracker, natural-language checks and checkout are useful foundations, but a stronger entry needs to demonstrate the commercial value of connecting them. These public pages do not establish that the proposed combination is globally unique.

The current [entry gallery](https://paypalaihackathon.devpost.com/project-gallery) is unpublished. There is no basis for ranking Prooflane against the actual submitted field yet.

## The most important gap

The current acceptance contract checks required columns, unique IDs, present emails, nonnegative revenue and a minimum row count. An offline probe confirmed that a completely different three-row dataset passes all five checks. This is correct under that limited agreement: preserving the client's original records was never a requirement.

For a data-cleanup job, however, the client's intended outcome may also require every original order and its revenue to survive the handoff. Capturing and enforcing those obligations would demonstrate a more valuable product.

## Proposed scope, in priority order

| Priority | Capability | Demonstrated value | Completion gate |
| --- | --- | --- | --- |
| 1 | Source-to-delivery comparison | Detect missing/invented orders and altered business values even when a file passes format checks | Agreed source hash is frozen; explicit cross-file requirements reject the altered examples and allow the correct delivery |
| 2 | Payment-bound manifest and verifier | Connect the source, agreed terms, delivery, amount and provider payment record | New manifest reference round-trips through an actual sandbox order/capture; verification works without the original SQLite database |
| 3 | Interactive scope clarification | Turn vague expectations into reviewed, executable obligations | Unsupported requirements remain blocked; answered questions produce a new reviewable draft and preserve the original text |
| 4, if the first three are stable | Reviewable repair proposals | Help the freelancer correct evidence-backed problems without inventing business data | Only supported local operations; explicit before/after review; edits invalidate prior verification/approval |

### 1. Prove the agreed relationship to the source

Let the client attach an original CSV and explicitly agree to the relationships the delivery must preserve. Start with a one-to-one sales handoff and two restricted comparison kinds:

- The delivery contains exactly the agreed source key set, with no missing or invented `order_id` values.
- For each key, a named numeric value such as `revenue` matches the source, using decimal arithmetic.

Present counts and revenue reconciliation as evidence derived from those rules. Retain the existing shape/uniqueness checks. Do not silently add obligations that the parties did not agree to.

Keep both raw CSVs local. The server computes the source hash before agreement. A resumed comparison requires reattaching a source with that exact hash. Model inputs can remain limited to the brief and explicitly allowed structural information; raw rows and identifiers do not need to go to the AI.

Acceptance examples:

1. Correct formatting cleanup preserves all IDs and amounts: pass.
2. A delivery replaces an order with a new ID but keeps the same number of valid-looking rows: block checkout.
3. A delivery changes one positive revenue value by 0.01: block checkout.
4. A different source is attached after agreement: require a new agreement, without modifying the old one.
5. Conflicting duplicate source records cannot be resolved by guessing which business value is true: request human clarification.

The claim is limited to the stated comparisons. It does not prove that the original source itself is true or that every possible business requirement has been satisfied.

### 2. Verify the relationship to the PayPal payment

Create a versioned, canonical manifest containing project identity, agreed terms, source hash, delivery hash, exact USD cents/currency and provider modes. Freeze it at approval and reuse it for retries.

PayPal's [purchase-unit reference](https://developer.paypal.com/sdk/orders/v2/definitions/purchase_unit_request) documents `custom_id` as a caller-supplied reconciliation identifier, up to 255 characters, returned in transaction/settlement contexts. A short version/project/manifest-digest reference fits this field. It is not visible to the payer, so display the agreement in Prooflane and demonstrate the reference through authenticated provider readback.

This is a proposed use of documented metadata, requiring an actual sandbox round-trip before claiming it works. PayPal records the reference; Prooflane performs the delivery checks. The reference is not a PayPal certification of work quality or an independent digital signature.

Build a small verifier that takes the exported manifest plus the source and delivered files. It should recompute hashes and supported checks without relying on the original project database. With merchant-authorized sandbox access, it also retrieves the provider record and compares manifest reference, amount, currency and capture status. Without provider access, show payment as unverified rather than inferring it from an editable JSON file. Never distribute merchant secrets with the receipt.

Acceptance examples:

- The correct files, contract and provider record agree.
- A changed delivered value, altered amount, changed rule, swapped source or foreign order produces a specific failure.
- Missing provider access is clearly distinguished from confirmed payment.
- Retry still yields one capture and the same manifest reference.
- Existing receipts remain readable and are explicitly identified as the earlier format; no new binding claim is added to them.

### 3. Help the parties make an executable agreement

When the AI asks what “cleaned” or “accurate” means, let the user answer in the same workspace. Show the resulting requirements and source text together before agreement. Suggest supported options; keep unsupported obligations visible and blocked.

Record the original brief and clarification history. Changing agreed terms starts a new draft/version and requires renewed approval. The AI must not set the price, remove an inconvenient requirement, or decide that a failed requirement can be ignored.

This turns the ambiguity caught in the readiness audit into a useful product interaction. It also deepens AI's role without making the model responsible for determining payment eligibility.

### 4. Offer bounded, reviewable corrections

Only after the core proof workflow is stable, let AI propose a short plan composed of supported operations. Useful first operations are restoring a missing record/value from the agreed source, trimming agreed fields, and removing exact duplicate rows when authorized by the scope. Keep conflicting records and unknown values for human resolution.

Display a row/cell diff and the effect on every rule before applying a proposal. Retain the original file for recovery. Re-run the deterministic checks after applying it and require fresh human approval. The AI receives sanitized rule failures and operation capabilities; the local executor applies permitted operations. No generated Python/SQL or arbitrary shell execution is needed.

Call this an agent only if it actually chooses and invokes the restricted workflow tools. An animated sequence or several scripted personas would not establish autonomous behavior.

PayPal publishes [MCP/agent tooling](https://developer.paypal.com/ai-tools/mcp-server), and the hackathon's [resources](https://paypalaihackathon.devpost.com/resources) encourage workflows that take commerce actions. Use those tools only if they improve this exact journey. The existing Orders adapter already supplies a working integration; replacing it is unnecessary for the proposal.

## Implementation boundaries

Reuse the buildless client, Python evaluator, SQLite project JSON and Orders adapter. The implementation would reach:

- `app.py`: comparison kinds/schema, exact requirement validation, two-file limits, source hashing, draft/agree/verify transitions, canonical manifest and order/readback validation.
- `static/index.html`: source attachment, clarification answers, comparison evidence, optional repair diff and explicit verification states.
- `test_app.py`: cross-file attacks, decimal values, old receipt compatibility, manifest changes, wrong reference/amount and capture replay.
- `test_client.cjs`: two-file preview invalidation, request locks, changed terms, restored projects and unchanged checkout guards.
- A small verifier entry point reusing the validated comparison/manifest code; the exported JSON is untrusted input and cannot contain executable instructions or arbitrary provider URLs.
- `README.md`, examples and browser verification: the actual source/delivery pair, setup and accurate claims about fixtures, provider responses and completed payments.

Do not expose the current localhost app as a multi-user service. Independent hosted buyer/seller access would require authentication, authorization, session protection, storage and webhook work. A public hosted platform is a separate project decision; complete repository setup remains an allowed judging route.

## The 2:45 demonstration to build toward

| Time | What the judge sees |
| --- | --- |
| 0:00–0:15 | A realistic sales handoff: a valid-looking delivery is missing a real order. State the client and payment decision. |
| 0:15–0:40 | AI resolves a vague requirement; the client reviews measurable terms and the source snapshot. |
| 0:40–1:10 | The flawed delivery passes formatting but fails source comparison. The missing order and revenue difference are visible; checkout remains blocked. |
| 1:10–1:40 | A reviewed correction restores the agreed source values. All checks pass and the human approves the exact file. If repairs were cut, upload a corrected file normally. |
| 1:40–2:15 | Complete an actual USD 1.00 PayPal sandbox checkout and reconcile the capture with its manifest reference. |
| 2:15–2:45 | Verify the exported receipt/files outside the project database; change one value and show the mismatch. Close with real pilot observations. |

Use synthetic data. Label fresh/cached/sample AI and sandbox/simulated payments accurately. No simulated receipt should be presented as an actual sandbox transaction.

## Protect the schedule and demonstrate impact

Planning targets, subject to the first implementation spike:

- **22–24 October:** validate the handoff problem with a freelancer/client, define the source/expected delivery pair and spike the two comparison rules.
- **25–28 October:** finish source agreement, comparison evidence and regression tests.
- **29–31 October:** finish the manifest/verifier and a real sandbox round-trip.
- **1–4 November:** finish clarification UX, independent setup and user trials. Add repair proposals only if the core flow is stable. Cut them if they threaten the complete demo.
- **5 November:** feature freeze, consistent with the existing build plan.
- **5–8 November:** recovery/accessibility checks, final real-service evidence, demo recording and English submission materials.
- **9–11 November:** signed-out link checks, judge-access instructions and submission confirmation. Keep the official deadline buffer.

Ask three relevant people to complete a realistic review task. Record time, missed discrepancies, unclear terms and whether they can identify the exact approved file. Compare with their ordinary spreadsheet review on the same task when practical. Report the actual sample size and observations; these would be pilot results, not broad proof of demand or invented savings.

The existing readiness gates still apply. The strongest proposal does not replace the video, independent setup, user feedback or confirmed Devpost submission. Its value must be demonstrated in a reliable build.
