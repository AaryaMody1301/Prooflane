# Prooflane build and submission plan

Updated 17 October 2026. [PayPal AI Hackathon](https://paypalaihackathon.devpost.com/) submission target: **11 November**; official deadline: **13 November 2026, 1:30 AM IST**. Recheck the [rules](https://paypalaihackathon.devpost.com/rules) before submission.

## Product

An independent data freelancer and client agree to a measurable CSV delivery and a USD price. Gemini drafts reviewable checks from the brief. Ordinary code evaluates the CSV. A human approves the checked file's SHA-256. PayPal sandbox checkout connects that approved snapshot to a reconciled capture receipt.

Keep one delivery, one agreed amount and one capture per project. Do not expand into escrow, arbitrary generated code, automatic payouts or a general freelance marketplace.

## Verified locally

- Thirteen passing standard-library tests, including a real localhost HTTP flow.
- Faulty sample fails three checks; corrected sample passes all five.
- Replacing a delivery clears its approval. Checkout freezes the evidence before a provider request, including an uncertain timeout.
- Stable request IDs and provider readback support payment retries; pending or mismatched captures do not produce paid receipts.
- Evidence JSON includes the brief, checks, results, approval, modes and payment IDs, without raw CSV contents or credentials.
- Offline setup diagnostics never contact providers. Explicit provider diagnostics send a synthetic brief and perform sandbox OAuth only.
- Python compilation and client JavaScript syntax checks pass.

Real Gemini and PayPal sandbox calls have **not** been verified with credentials. Browser/mobile interaction and visual QA are outstanding because Chromium was unavailable in the development environment. Simulation and provider test doubles are not proof of a PayPal transaction.

## Next integration gate

1. Clone the repo, run `python3 app.py`, and finish the sample workflow.
2. Create a PayPal sandbox REST app with a business test account and a separate personal buyer test account. Put sandbox app credentials in local `.env` only.
3. Add a Gemini API key from a free-tier project without billing. Set `AI_MODE=gemini` and `PAYMENT_MODE=sandbox`.
4. Run `python3 app.py doctor`, then `python3 app.py doctor --providers`. Resolve configuration or provider errors before proceeding.
5. Restart the app and create a new project. Try a custom measurable brief and review every check for omissions. Try an ambiguous requirement and confirm it cannot silently become an accepted obligation.
6. Submit the faulty CSV, correct it, approve the exact delivery, approve checkout as the sandbox buyer, and reconcile. Check capture ID, USD amount, approved hash and provider modes in the downloaded evidence.
7. Run a separate cancellation and retry scenario. Confirm cancellation stays unpaid and repeated reconciliation does not create another recorded capture.
8. Complete desktop/mobile browser QA and test a fresh setup from the public repository.

## Submission gate

- Actual Devpost enrollment and eligibility confirmed.
- Meaningful credential-backed AI and PayPal sandbox flow demonstrated.
- Public repository, MIT license, accurate setup and judge instructions.
- English project description and an under-three-minute public YouTube demonstration.
- Honest AI-use disclosure and evidence for impact claims; no invented user interviews or metrics.
- Judge access maintained through the judging period.

The starter is localhost-only and demonstrates both roles with one operator. Public hosting requires independent accounts, project authorization, HTTPS/session protection, durable storage and verified webhooks. Keep the first integration working before adding hosted features.
