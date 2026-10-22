# Submission readiness — 22 October 2026

**Verdict: a working prototype, with submission work still open.** Merged `main` passes its checks and the clean sample walkthrough. A local starter-brief correction also passes offline tests and a reviewed real-service preflight. This report does not establish a submitted Devpost entry or a published video.

## Candidate and evidence

- Audited merged commit: `92685dd1fd6ac44ba93da74af660fd5bdcc97b30`, from [PR #5](https://github.com/AaryaMody1301/Prooflane/pull/5). Its source tree matched the working checkout before the correction below.
- The repository is public, defaults to `main`, and GitHub detects the MIT license. The archive contains the application, HTML client, examples, documentation and tests; no `.env` or SQLite database is included. A limited scan found no Google-key or private-key-header patterns; this is not a full history/secret audit.
- [Main CI run 39739898719](https://github.com/AaryaMody1301/Prooflane/actions/runs/39739898719) passes on Ubuntu/Python 3.11 and Windows/Python 3.14. Both jobs run the Python tests, client checks and compilation. That run predates this report and the local brief correction.
- A Git archive of the exact merge was extracted into a separate directory, with no `.env`, saved projects or provider credentials. Python 3.14.8 alone starts the default application; no pip/npm installation is needed. The walkthrough used `PORT=63777` for isolation and the default sample AI/simulated payments.
- Chrome completes draft → review five checks → agreement → faulty sample with three failures → corrected sample with five passes → approval → simulated checkout → USD 120.00 receipt. The evidence button downloads an actual 3,885-byte JSON file. Verification, approval and receipt hashes equal the browser-normalized corrected CSV hash, and raw CSV rows/customer emails are absent.
- Stopping and restarting that server, then reloading the saved project, restores the receipt and matching-hash display. Console warning/error capture is empty. The checked 929×917 viewport has no horizontal document overflow. This is an automated walkthrough on the same computer, not an independent person or fresh-machine trial.
- Receipt project: `4fcbc008182e4fe59c131422dcf81066`. Checked CSV SHA-256: `63b500480384b3cc711da1596f901eda79ffa3599ceefa5c9d01f706f2e6cd0c`. This receipt is simulated; no PayPal transaction occurred.

The existing [component review](UI_COMPONENT_REVIEW_2026-10-22.md) supplies the broader layout, keyboard, native evidence-download and 30 zero-violation axe-scan evidence. This audit did not repeat that full matrix.

## Starter-brief correction and live preflight

An initial credential-backed preflight returned Gemini HTTP 503 after the adapter's bounded retry; PayPal sandbox OAuth succeeded. After the interruption, Gemini responded with five checks and one blocking clarification. A focused plan review reproduced the reason: the word **cleaned** did not specify cleaning transformations or validation criteria. Blocking agreement was correct behavior.

The local correction removes that word from the starter brief and updates the client restore assertion. The fixed sample plan derives its first quotation from the same brief. Existing projects retain their saved terms. Validation, clarification blocking, model selection, retries and payment logic are unchanged.

At **16:41 IST on 22 October**, the corrected brief passed a fresh real-service preflight with `gemini-3.6-flash` and PayPal sandbox OAuth. The returned plan was reviewed against the fixture, including exact source quotations and parameters:

| Obligation | Actual returned check |
| --- | --- |
| `order_id`, `customer_email`, `revenue` columns | Required columns, exactly these three names |
| Every `order_id` unique | Unique `order_id` |
| Every `customer_email` present | Nonempty `customer_email` |
| Numeric revenue ≥ 0 | Numeric range on `revenue`, minimum 0, no added maximum |
| At least 3 rows | Row count, minimum 3, no added maximum |

All five checks match the intended obligations without extra restrictions; clarifications are empty. The diagnostic creates no project, order or capture. Authentication does not constitute a new checkout test. A passing response does not guarantee future provider availability; the earlier 503 remains relevant to demo preparation.

After the correction, all 22 Python tests, the expanded Node controller checks and Python compilation pass locally. The full clean browser walkthrough above used merged `main` before this one-word correction; the changed default is covered by the controller/configuration checks and the reviewed live plan. No layout code changed.

Raw synthetic provider plans, downloaded evidence, the receipt screenshot and the clean archive are retained locally under ignored `.venv/submission-readiness-2026-10-22/`. No credentials or normal application database were copied into that directory.

## Submission requirements

The [official rules](https://paypalaihackathon.devpost.com/rules), checked on 22 October, allow a runnable repository with complete setup instructions instead of public hosting. They require meaningful AI and PayPal sandbox integration, an English description, a public open-source repository, and a working-project video publicly visible on YouTube. Keep the video under three minutes. Complete and confirm the Devpost submission. The deadline is **13 November 2026 at 01:30 IST** (12 November at noon PST); our working target remains 11 November. Judge access must remain available through **15 December at 21:30 IST**.

| Item | Readiness | Remaining evidence/action |
| --- | --- | --- |
| AI + PayPal sandbox integration | Demonstrated | [Reviewed real AI](PHASE2_AI_COMPLETION_2026-10-20.json) and [actual USD 1.00 capture, cancellation and reconciliation](PHASE3_SANDBOX_COMPLETION_2026-10-20.json) are dated 20 October. No new capture was made in this audit. |
| Functional build and judge setup | Automated clean run passes | A second person should follow the README without coaching. Explain how judges obtain their own local provider credentials or any supported private test access; keep merchant secrets out of the public repo and video. |
| Public code and open-source license | Verified | Preserve the MIT license and verify final submission links signed out. |
| English project description and tool usage | Repository overview exists | Finish the Devpost narrative, platform/testing instructions and accurate AI/tool disclosure. No Devpost draft link was supplied or inspected. |
| Public YouTube demo under three minutes | Unverified/open | Record and check a real end-to-end demo; clearly label fresh AI, sample fixtures and sandbox/simulated payment footage. No video link was supplied or found in the repository. |
| Devpost entry and submission confirmation | Unverified/open | Confirm enrollment, entrant/team eligibility, required fields, URLs and submitted status in the user's account. |
| Final code candidate | Local correction prepared | Review and merge the two-line brief/test correction and accompanying documentation; check CI on that candidate before freezing the submission. |

## Quality gates from our build plan

These are our remaining acceptance goals, not additional eligibility requirements quoted from the hackathon:

1. Complete a second synthetic delivery example through real AI and actual sandbox checkout. The new sales-plan preflight is not a second completed payment flow.
2. Have another person complete fresh setup and the judge path. An automated archive run on this computer does not close this gate.
3. Gather target freelancer/client feedback and record real observations. Do not invent interviews, demand or time-saving metrics.
4. Complete spoken screen-reader and physical-device acceptance. Native 200% zoom, forced colors and OS file dragging were not retested for the current interface. Earlier native file selection and accessibility evidence remains dated in the linked reviews.

The intended submission is a localhost prototype operated by one person, using synthetic briefs/CSV and sandbox funds. It does not supply separate buyer/seller accounts, escrow or guaranteed payment. Public hosting would require separate security work and is unnecessary for the repository-based judge path.

## Recommended order

Merge and check the brief correction; finish the independent walkthrough and second real-service example; record a 2:45 demo; finish the Devpost copy/access instructions; verify the public links and submitted status. Further visual redesign is lower priority than these missing acceptance and presentation artifacts.
