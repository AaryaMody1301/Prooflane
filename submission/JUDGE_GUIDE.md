# Judge setup and expected results

Repository: https://github.com/AaryaMody1301/Prooflane

Use Python 3.11+. Clone the repository, enter it, run `python app.py`, and open http://127.0.0.1:8787. A fresh clone has no `.env` and needs no installation or credentials. If your command is `python3`, substitute it. The localhost server is intentionally not a hosted multi-user service.

## Five-minute offline demonstration

1. In All projects, choose **Compare a delivery with its source**. Set USD 1.00 if desired and draft the supplied brief. Expect seven proposed checks, **Sample AI fixture** and **Simulated payments**.
2. Review the quotations and attach `examples/source.csv`. Agree. The source hash is now frozen.
3. Load `examples/substituted.csv` and run checks. Expect five passes and two source failures: one missing original key, one unexpected replacement, and an unmatched value. The total is still 285. Approval and checkout are blocked.
4. Load `examples/changed-value.csv` and check again. Expect six passes and one failure. The source total is 285; delivery total is 284.99; the difference is -0.01.
5. Choose **Preview source corrections**. Expect one proposed value restoration, grounded in a source record. Apply it. The UI requires fresh checks. Undo restores the previous preview; after Undo run checks again before requesting another correction.
6. Apply the correction again, expand **View or edit CSV preview**, and **Download this CSV preview**. Keep this exact download. Run checks; expect seven passes. Explicitly approve the delivery.
7. Create and complete the simulated checkout. Expect **Simulation complete**, USD 1.00 (or your chosen price), matching hashes and a version 2 evidence reference. This is not an actual PayPal transaction.
8. Download the evidence JSON and open **Verify files and receipt separately**. Select that export, the downloaded corrected delivery and `examples/source.csv`. Leave PayPal lookup unchecked. Expect local checks passed and **Simulated payment — no PayPal transaction**.
9. Change the verifier delivery to `examples/changed-value.csv`. The old success disappears; running verification rejects the changed snapshot.
10. Restart the server and reopen the saved project. Its receipt persists; unsaved CSV previews do not.

## Terminal verification without the original database

Run from the repository using the downloaded evidence and delivery paths:

```bash
python verify_receipt.py evidence.json reviewed-delivery.csv --source examples/source.csv
```

It needs the source files and export, not the original SQLite database. Exit 0 means valid local consistency. A changed file or tampered amount/manifest fails with exit 1. Offline JSON alone cannot authenticate a payment.

## Optional real integrations

Follow the README's local `.env` setup with your own free-tier Gemini key and PayPal sandbox Business app keys. Restart, create a new project, and review the **Gemini AI / PayPal sandbox** labels. Use a distinct Personal sandbox buyer, finish Pay Now, then reconcile the stored order. Never use live credentials or enable paid resources.

The checkbox in the separate verifier, or the CLI's `--paypal`, makes an authenticated read-only sandbox order lookup using this machine's merchant keys. It requires a single completed capture, exact amount/currency and matching manifest. Missing credentials fail honestly. An unchecked real sandbox receipt remains provider-unverified.

Fresh 11 November provider evidence is in `PROVIDER_WORKFLOW_2026-11-11.json`. The historical 20 October inventory payment is a different transaction. Provider authentication/order creation alone is not a completed payment.

## Recovery and limitations

- Custom briefs in sample mode are intentionally rejected. Use the supplied examples or configure Gemini.
- For vague scope, use **Try a clarification example** and draft revised measurable wording; the original draft/price remain saved.
- Reattach the exact source after reload. A new source requires a new agreement.
- An uncertain order freezes the delivery. Retry that same checkout within 15 minutes; afterward inspect the sandbox dashboard first.
- A cancelled or unapproved order stays unpaid. Restarting or revisiting a return link does not create a second capture.
- No network is needed for the default walkthrough. Gemini or PayPal outages do not change the selected modes.
- Physical devices, spoken screen readers and independent-person acceptance have not been freshly validated. No customer outcome claims are made.

Keep the public repository, instructions and public demo accessible through the end of judging, 15 December 2026.
