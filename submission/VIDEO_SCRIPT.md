# Finished demo and recording plan

File: `media/prooflane-demo.mp4`. Measured runtime: **164.8 seconds (2:44.8)**, H.264, 1440×810, 30 fps, burned English captions, no voice/music. Real Chrome interaction with the running app; no screen or payment confirmation was fabricated. `media/VIDEO_VALIDATION.json` contains measured metadata; `media/ASSET_MANIFEST.json` records steps, projects and file digest.

The principal recording uses a fresh live Gemini plan and real deterministic checks, then stops at approved/eligible checkout **without creating an order**. At 2:02 it explicitly switches to a **separate** seven-check project whose USD 1.00 sandbox capture completed earlier during this run. It shows that actual receipt and performs a fresh authenticated PayPal lookup in the separate verifier. This distinction is captioned before and during the switch. The video does not show the external PayPal login/approval page: browser account automation was unavailable, and the buyer approved manually outside this recording.

## Narration / captions and shot list

| Time | Actual clicks / shot | Caption or optional narration |
| --- | --- | --- |
| 0:00–0:12 | Current All projects overview | Prooflane — Proof Before Payment. A CSV can look valid and still contain the wrong records. |
| 0:12–0:24 | Compare a delivery with its source → USD 1.00 → Draft acceptance plan; wait for real Gemini | Live Gemini drafts measurable checks from the brief. The client sets the price. AI cannot approve work or payment. |
| 0:24–0:35 | Review seven quotations → upload `examples/source.csv` → Agree | Review all seven requirements and attach the original source. Agree explicitly. CSV rows stay local. |
| 0:35–0:48 | Upload `examples/substituted.csv` → Run checks | This delivery substitutes an order. The five structural checks pass; source reconciliation fails. |
| 0:48–1:00 | Needs attention; inspect missing/unexpected keys and unchanged total | The total still matches: 285. Missing and unexpected source keys block approval and checkout. |
| 1:00–1:14 | Replace with `examples/changed-value.csv` → Run checks | Now change revenue by just one cent. Decimal comparison detects the exact -0.01 difference. |
| 1:14–1:27 | Preview source corrections; inspect before/after | Review the proposed correction against the agreed source. No invented data, generated code or silent file changes. |
| 1:27–1:39 | Apply → Undo → recheck → Preview → Apply | Apply is explicit. Undo restores the previous preview. Both require fresh verification before approval. |
| 1:39–1:52 | Run all seven checks; show passes → Approve | All seven checks pass on the corrected version. Explicit approval freezes the agreement, source, price and delivery hash. |
| 1:52–2:02 | Approved checkout eligibility, no new order | Checkout is now eligible for this approved delivery. The following receipt is from a SEPARATE verified sandbox run. |
| 2:02–2:16 | Open previously completed seven-check project; display actual USD 1.00 receipt and modes | Separate run: actual USD 1.00 PayPal sandbox capture. The same seven-check workflow; a distinct project and transaction. |
| 2:16–2:28 | Download that evidence; open separate verifier; choose export, exact delivery and source | Export its evidence and verify the original files separately. The verifier does not need the original project database. |
| 2:28–2:37 | Check authenticated PayPal lookup → Verify; show actual confirmation | Authenticated, read-only PayPal lookup confirms this capture, exact USD amount and version 2 manifest reference. |
| 2:37–2:44.8 | Replace delivery with changed-value example → Verify → show rejection | A changed delivery fails verification. Prooflane connects reviewed work, approval and checkout. github.com/AaryaMody1301/Prooflane |

## Reproduce or replace the footage

The optional `record_demo.py` uses Playwright and imageio-ffmpeg in `.venv`, never runtime packages. Start the configured real-provider app and complete a separate seven-check sandbox transaction first. Keep its exact corrected delivery in `.venv/sandbox-reviewed-delivery.csv`.

```powershell
.\.venv\Scripts\python.exe submission/record_demo.py --receipt YOUR_COMPLETED_PROJECT_ID
```

The recorder makes a **new live Gemini request** and new review project. It never creates another PayPal order or supplies buyer credentials. A provider failure aborts rather than becoming fixture footage. Raw WebM stays ignored under `.venv/demo-recording`; final MP4, SRT and real screenshots go to `media`. If provider latency exceeds planned holds, the script records it and may uniformly compress playback; the actual delivered asset records **1.0×** speed.

For a manual replacement, use the same clicks and supplied files with a free screen recorder, keep mode labels legible, add the provided captions, and export below three minutes. Only claim a continuous checkout if the footage really depicts that same transaction. Do not substitute historical inventory footage for this project without labeling the different scenario.

## Publication handoff

Review the actual MP4, then upload it to YouTube as **Public** using `VIDEO_DESCRIPTION.txt` and `media/thumbnail.png`. Confirm signed-out playback, duration and legibility. No upload has been performed or public YouTube URL verified. Then use the real URL in the Devpost entry and README; final Devpost submission requires explicit confirmation.
