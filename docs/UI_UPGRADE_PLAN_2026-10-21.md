# Prooflane UI upgrade: research and implementation plan

21 October 2026. Research baseline: `3588e5f1156a4fb95137ad465e889969a87a1d42`, including the pending-input and error-focus fixes in PR #2. The user subsequently approved implementation. The working upgrade and its remaining acceptance limits are recorded in [workspace QA results](UI_WORKSPACE_RESULTS_2026-10-21.json) and [PR #3](https://github.com/AaryaMody1301/Prooflane/pull/3).

## Recommendation

Turn the long form into a compact project workspace with three stages: **Scope → Delivery → Payment**. Make the current task, agreed amount, delivery result and next action immediately clear. Use a calm, distinctive visual system and make the connection between the agreed checks, human approval and payment receipt the central story.

The current UI is functional and reasonably consistent, but its hierarchy makes the product feel like a development walkthrough. A successful upgrade should make a data freelancer or client understand the delivery's status without reading the whole page.

## What the current UI shows

These are fresh DOM measurements of the paid sample project, reloaded with an empty CSV preview. Positions are document coordinates in CSS pixels, not universal measurements for every state.

| Observation | Desktop, 1280 × 844 | Mobile, 390 × 844 | Implication |
| --- | ---: | ---: | --- |
| First brief field starts | 674px | 788px | The introduction and resume box consume most of the first screen. |
| Scope review starts | 1105px | 1296px | The project's requirements are separated from its current outcome. |
| Verification results start | 2343px | 2703px | The product's distinctive proof is buried. |
| Payment summary starts | 532px | 3388px | On mobile, price and payment context arrive after the entire workflow. |
| Total page height | 3070px | 4883px | A completed project still leads with the intake form. |

Additional review findings:

- Brief creation, completed scope, delivery results and payment compete on one growing page. There is no compact overview of the current stage and required next action.
- Acceptance cards and results repeat long lists; failed checks do not receive a sufficiently strong visual priority.
- The CSV textarea is prominent while evidence of what passed or failed is farther down. File handling needs a clearer hierarchy, without inventing a spreadsheet editor.
- Many supporting labels and evidence strings are 10–12px. This is a readability concern; this review did not establish a WCAG failure.
- Receipt IDs and hashes are shown as small technical strings. The receipt needs a clear outcome, amount, environment and delivery-match explanation before those details.
- “Working starter” and the project start date occupy product chrome. Move build-history information into About/help while keeping sample/sandbox and single-operator limitations clear.

The previous QA results establish functionality for the reviewed flows. They do not establish independent-user usability or visual competitiveness.

Local baseline captures and measurements: `.venv/ui-review-2026-10-21/current-desktop.jpg`, `current-mobile.jpg`, and `current-layout.json`.

## Research and its application

Sources checked on 21 October 2026. Product examples inform individual patterns; they do not establish that this design will improve judging scores.

| Primary source | Relevant finding | Application to Prooflane |
| --- | --- | --- |
| [Official hackathon rules](https://paypalaihackathon.devpost.com/rules), Judges & Criteria and submission requirements | Design and presentation are two of five equally weighted criteria. Judges assess a coherent product experience and an understandable working demonstration; a static design alone is insufficient. | Prioritize the complete scope-to-receipt journey and readable demonstration states. Keep the working integration at the center of the redesign. |
| [Linear's UI redesign](https://linear.app/now/how-we-redesigned-the-linear-ui), March 2024 | Linear describes improving alignment, hierarchy and density while reducing visual noise, and testing layouts across states. | Use compact project chrome, consistent spacing and a restrained visual hierarchy. Borrow those principles rather than reproducing Linear's navigation or theme system. |
| [Bonsai client portal](https://help.hellobonsai.com/en/articles/4409019-how-to-use-the-client-portal) and [project overview](https://help.hellobonsai.com/en/articles/12783206-all-about-projects) | Project information, files, billing and activity are organized around the client project. | Organize Prooflane around one named delivery. Keep amount, status and evidence within that project's context. |
| [NN/g: Progressive Disclosure](https://www.nngroup.com/articles/progressive-disclosure/) | Secondary detail can be deferred; interdependent tasks still need an easy way to move between related information. | Keep agreed scope accessible from delivery review. Collapse raw CSV, full IDs and historical events; keep failed requirements, source quotations during agreement, price and consequential actions visible. |
| [PayPal checkout flow](https://developer.paypal.com/platforms/checkout/standard/upgrade-integration/) and [SDK lifecycle reference](https://developer.paypal.com/sdk/js/reference/) | Approval, server capture, cancellation, errors and confirmation are separate parts of checkout. | Give each existing payment state explicit copy and recovery actions. This is UX guidance; changing the working REST/redirect integration is not required for the redesign. |
| [WCAG contrast](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html), [target size](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html), [focus not obscured](https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html) | Normal text generally needs 4.5:1 contrast, large text 3:1; target minimum is 24 × 24px with exceptions; focused controls must not be entirely obscured. | Measure contrast, use a larger 44px touch target as our design target, retain visible focus, and test any mobile action bar against keyboard focus and zoom. These checks alone do not certify conformance. |

## Proposed product structure

The empty state explains the value in one short sentence and offers **New project** plus the existing saved-project picker. After a project is selected, the workspace leads with its name, persisted status, agreed amount and modes. The large marketing introduction no longer precedes every active task.

Desktop layout:

```text
Prooflane                 Project picker          New project
Sales data handover       Sample AI · Simulated payment
Scope reviewed      →     Delivery needs changes      → Payment
┌───────────────────────────────────────┬───────────────────┐
│ Active task + one primary next action │ Agreed USD amount │
│ Rule / result / actionable evidence   │ Payment status    │
│ Scope remains directly accessible     │ Proof trail       │
│ CSV preview and detail disclosures    │ Evidence details  │
└───────────────────────────────────────┴───────────────────┘
```

On mobile, show project, amount, mode and current stage above the active task. Use a single column and a compact action area. Detailed history follows the task. A sticky action bar is conditional on passing focus/zoom checks; otherwise keep the action in normal flow.

### Scope

- Keep brief and USD input together for a new project, with one **Draft checks** action.
- Show each proposed rule alongside its complete source quotation before agreement. Make all clarifications prominent and block agreement as today.
- Summarize the agreed price beside **Agree to scope**. Use existing approval wording accurately; this app remains a single-operator demonstration.
- Once scope is agreed, present it as a read-only review. **New project** clearly creates a separate project instead of suggesting that saved terms can be edited.

### Delivery

- Lead with an outcome: **3 checks need attention** or **All 5 checks passed**, plus checked row count and a concise next step.
- Render a semantic verification table: agreed rule, text status and actual evidence. Rank failures first while preserving each result's association with its agreed rule.
- Show existing failure-line information clearly. Do not invent cell values, AI confidence, semantic guarantees or a data grid unsupported by the API.
- Keep native file selection accessible. Put sample faulty/corrected examples under an explicitly labeled example control. Keep the raw CSV preview available in a disclosure with a readable monospace style.
- Use existing result fields to display reviewable evidence. A parsed spreadsheet preview is deferred because it needs correct handling of quoted CSV and a separate data contract decision.
- Keep the human approval action separate from verification. A changed preview still requires rechecking; a pending request locks inputs; checkout freezes the approved snapshot.

### Payment and receipt

- Before checkout: show the exact USD amount, verified/approved delivery and **Continue to PayPal sandbox** when permitted. Explain the remaining prerequisite when blocked.
- On return: show reconciliation progress, pending, cancellation or error explicitly. A return URL or buyer approval alone never creates a paid display.
- After a completed capture: show **Sandbox payment reconciled**, amount, the matching approved-delivery proof and an evidence export action. Simulated receipts use **Simulation complete** and explicitly say no PayPal transaction occurred.
- Put the full hash, order/capture IDs and activity history in clearly labeled expandable details; keep the delivery-match explanation and modes visible.
- Keep the receipt's persisted modes distinct from the app's current configuration. Reopening an older simulated project must not relabel it as a real provider transaction.

## Visual direction

A precise workspace for reviewing data and payments: warm near-white canvas, white working surfaces, dark ink typography, one indigo action color and restrained green/red status accents. Use a stronger wordmark, aligned rows and clear separators. Use text labels and icons together for outcomes.

| Element | Proposed target |
| --- | --- |
| Canvas / panel / ink | `#f6f7f9` / `#ffffff` / `#162338` |
| Primary action / success / error | `#3657df` / `#08715b` / `#b4323b` |
| Supporting text | Start with `#526278`; measure against each actual surface. |
| Typography | Local system sans; 28px project title, 20–24px task headings, 15–16px body, 13–14px supporting text. Monospace only for data and IDs. |
| Spacing | 4/8/12/16/24/32px scale, compact rows, 8–12px corners, subtle borders. |
| Interaction | One filled primary action per task; clear loading text, visible keyboard focus, reduced-motion support. |

Local concept: `.venv/ui-review-2026-10-21/workspace-concept.html`. It contains synthetic Scope, Needs fixes and Receipt examples, with no API or payment connection. It is a planning artifact, not a working replacement or submission evidence.

## Implementation sequence

Use a separate focused UI branch after incorporating PR #2. Keep this research separate from that completed QA PR.

| Order | Work | Completion check |
| --- | --- | --- |
| 1 | Confirm the workspace composition with the local desktop/mobile concept; settle Scope, Needs fixes, Verified and Receipt hierarchy. | The working implementation now includes all four views; independent reviewer identification remains a user-testing goal. |
| 2 | Update the app shell, shared CSS tokens, compact project header and three stage views in `static/index.html`. Derive the default view from existing backend status; retain access to completed stages. | Creation, resume and all existing states render; no saved-project mutation or extra provider request from navigation. |
| 3 | Implement scope review, failure-first verification results, upload/preview hierarchy and payment/receipt presentation. | Existing checks, quotations, human approval, input locks, frozen delivery and payment gates retain their behavior. |
| 4 | Update controller/browser checks and document the new judge path. Capture real screenshots at all reviewed widths and states. | CI passes; keyboard/recovery checks pass; independent user feedback is recorded before claiming usability success. |

Frontend view defaults must follow the actual lifecycle:

| Existing state | Default view | Primary action |
| --- | --- | --- |
| No project | Scope | Draft checks |
| DRAFT with clarifications | Scope | Resolve brief and draft a new project; agreement blocked |
| Reviewable DRAFT | Scope | Agree to scope |
| AGREED or changed preview | Delivery | Run checks |
| BLOCKED | Delivery | Replace/correct the CSV and rerun checks |
| VERIFIED, unchanged preview | Delivery | Approve this delivery |
| APPROVED | Payment | Continue to checkout |
| CHECKOUT_PENDING | Payment | Retry the same checkout within the existing allowed window; show uncertainty |
| ORDER_CREATED | Payment | Open existing PayPal approval or reconcile stored order; simulated mode offers its labeled test action |
| PAYMENT_PENDING | Payment | Reconcile again; retain pending status |
| PAID | Payment / receipt | Export evidence |
| Cancellation, provider error or foreign token | Relevant stage with focused error | State-specific recovery; never infer payment success |

The implementation touches `static/index.html`, its handlers and stable element IDs, `test_client.cjs`, `browser_check.py`, README instructions and the Phase 4 QA record. Review all selectors, hidden/disabled assumptions and focus behavior together. Existing backend APIs, validation and persisted project data already support the proposed first upgrade.

## Acceptance targets

These are proposed pass criteria, not results of tests already performed:

- At 1280 × 800, the active task heading begins within the first 240px of the product UI. Project, amount, mode and next action are visible without traversing completed forms.
- At 390px, amount and current state appear before task content; the payment context is no longer below the full delivery history. No page overflow at 320/390/768/1280/1440px.
- Source quotations and clarifications remain easy to review before agreement. Failed checks include meaningful text and line information, without relying on color alone.
- Test no project, clarification, draft, agreed, dirty, blocked, verified, approved, checkout uncertainty, order-created, payment-pending, paid, cancellation and provider-error states. Include long project names/IDs, repeat callbacks, mode mismatch and reload/resume.
- Recheck keyboard-only use, visible focus, busy-state restoration, 200% zoom, 320px reflow, contrast, touch targets and reduced motion. Verify a mobile action bar never covers the active input, error or export control.
- Keep all 22 Python tests and the client controller passing. Add focused assertions for view defaults and failure ordering; use real-browser checks for visibility/focus and layout instead of mirroring CSS in unit tests.
- Ask three independent testers to identify what is blocked and why, correct a sample CSV, approve deliberately and distinguish simulation from sandbox. Record confusion and observed task completion; invent no time-saved or conversion claims.
- Rehearse a working demo under three minutes: audience/problem → reviewed AI scope → visible failed delivery → correction and human approval → actual PayPal sandbox → matching receipt/evidence. Label edited wait time and provider modes honestly.

Deferred scope: public hosting, independent accounts, refunds, milestones, revenue dashboards, additional sponsor integrations, a frontend framework migration and a spreadsheet editor. Revisit only if a tested completion gate requires them.

This research used the isolated sample/simulation UI and public sources. It made no new Gemini or PayPal requests. Independent users, physical mobile devices and assistive technologies have not yet validated the proposed design.
