# Scrypt × Vesuvius Challenge: status (updated Mon Oct 5, 2026, ~10:05 AM ET)

Target: the October Progress Prize, deadline **Oct 31, 2026, 11:59pm PT** (Nov 1, 2:59am ET).
Ledger of Scrypt Vesuvius work (CPU box). This file is optional context for the Progress Prize package.
Code: `scrypt_vc/` (`run_all.sh` reproduces everything; `requirements.txt`). Outputs: `out/`. villa reference clone: `villa/` at commit `5a4388f`.

## Round update (Oct 5 ~10:05 AM ET) — opportunity rescan + zero-cost strengthen

**Deadline live:** Oct 31, 2026, 11:59pm Pacific (`scrollprize.org/prizes`). Sep winners still not posted; latest listed Jul/Aug 2026.

### A) Fresh opportunity ranking (~3.5 weeks)

| Rank | Opportunity | Impact | Effort | Discord? | Notes |
|---|---|---|---|---|---|
| **1** | **Ship the package** (note+PDF, 15 confirmed, audit CLI, GIF, licenses, checklist) | High ($1–5k band plausible; $20k unlikely alone) | Low: public repo + form | **Yes** — early release favored; ask Annotation if seed-audit useful | **Primary path.** Submit only when Salvador says |
| **2** | **Upstream / Discord soft-landing** of checker after interest | Med if adopted | Low–med | **Required** | Niche still open vs spiralcheck (fit meshes) / windcheck (tifxyz self-cross) |
| **3** | **Fiber B as secondary appendix** (Aug-01 held-out aggregate now solid) | Low–med for Oct | Done for metrics | Optional | Not the lead; scale resolved |
| **4** | Tiny villa docs/PR linking seed-audit after Discord | Med if merged | Med | **Yes first** | Don’t cold-PR |
| **5** | More scrolls’ `winding_inference` if published | Med | Needs data | Optional | Paris4 only for now |

**Avoid / dead ends:** ScrollFiesta & patch-connectivity ($20k Jul–Aug); consumer-GPU spiral ports (awarded); pitching auto chains; villa #203 volume warp; >50GB downloads; First Letters/Title/GP track; ink training without niche; Sep-15 fiber preds as default (worse on 1 crop).

**Judge pattern reminder:** early OSS, used-by-others signals, failure-case analytics (TAUIL / windcheck / audits paid $1k), docs. Our fit is failure-case analytics on `winding_inference` seeds.

### B) Zero-cost executed this turn (no publish / Discord / Atrium / >50MB)
- **Aug-01 multi-crop aggregate** (already-local 3 held-out crops, 143 GT runs): conservative **29.1%** deviation, **61.1%** auto-clean, **37.1%** GT recall → `out/fiber/paris4_aug01_heldout_aggregate.json`
- **Audit demos:** `out/demos/audit_no_human.json` (population-only path), `out/demos/audit_report_demo.md`
- **Packaging:** root `README.md`, `SUBMISSION_CHECKLIST.md`
- Fetched tiny upstream metadata: `mask_report.json` (2.3 KB), `verification.json` (921 B) — no note regen (no new scientific claim)
- **Downloads this turn:** ~3 KB

## Round update (Oct 5 ~9:50 AM ET) — audit suite CLI + fiber salvage (approved)

Salvador approved: (1) winding_inference seed-audit eval suite CLI; (2) fiber salvage on small crops + scale clarification.
**No** publish / Discord / form / Atrium GPU. Downloads this turn: **38.05 MB** (one Sep-15 L3 crop × 3 channels).

### (1) Seed-audit evaluation suite — DONE
- Library: `scrypt_vc/checker/audit.py`
- CLI: `python -m checker audit|self-check` (docs: `scrypt_vc/checker/README.md`)
- Schema updated: `winding_inference_audit.v1.schema.json` (candidates triage; confirmed optional/attached)
- **Self-check PASSED** on Paris4: 94/1 single-ray, DR6 238/30/10 strong, 50% multi-ray disagree (triage), 15 confirmed attached
- Outputs: `out/winding_inference_audit.v1.json`, `.selfcheck.json`, population stats
- Explicit: **does not claim confirmation without human labels + 3D same-sheet**

### (2) Fiber salvage — DONE (1 crop; under 50 MB)
- Sep-15 run exists: `.../fibers/20260411134726-fibers-20260915212757-L1/`
- Fetched held-out `L3_24_7_5` only → `data/paris4_fiber_crops_sep15/` (38.2 MB on disk; 38.05 MB download)
- Same tracer configs vs Aug-01 crop (GT was annotated on Aug-01 preds):

| pred run | cfg | seeded deviation ↓ | mean correct steps | auto clean | auto GT recall |
|---|---|---:|---:|---:|---:|
| Aug-01 | conservative | **32.1%** | 21.6 | **54.4%** | **31.7%** |
| Sep-15 | conservative | 41.1% | 24.2 | 48.1% | 27.2% |
| Aug-01 | default | 35.7% | 23.3 | 52.9% | 31.2% |
| Sep-15 | default | 43.8% | 25.3 | 48.4% | 26.7% |

- **Sep-15 is worse on this crop** for deviation / clean / recall (one crop only; not a full re-benchmark). Prefer Aug-01 preds for tracer work until broader evidence.
- JSON: `out/fiber/paris4_aug01_vs_sep15_L3_24_7_5.json`

### Fibers vs PCL scale — RESOLVED
- Fit/PCL space = level-2 9.6 µm. Eval `vc3d_fiber` line_points = **base 2.4 µm (L0)**.
- Fitter: `load_fiber_point_collection(..., coordinate_scale=0.25)` (or dyadic auto from shapes).
- **Implication:** export auto fibers in base voxels (as `export_vc3d.py` already does); do **not** pre-divide by 4. Details: `out/fiber/fibers_vs_pcl_scale.json`.
- Note/PDF **not** regenerated (winding diagnosis unchanged; fiber evidence lives in STATUS + fiber JSON).

## Round update (Oct 5 ~9:30 AM ET) — opportunity rescan + zero-cost strengthen

**Deadline confirmed live:** Progress Prize **Oct 31, 2026, 11:59pm Pacific** (`scrollprize.org/prizes`). Sep winners still not posted; latest listed months Jul/Aug 2026.

### Fresh opportunity scan (sources)
- Live prizes page (favors early release, real-data gains, **failure-case analytics**, docs).
- July/Aug winners: ScrollFiesta / patch-connectivity dominate $20k; $1k band = windcheck, TIFXYZ Doctor, scroll-data-audit, TAUIL negative ink analysis, consumer-GPU spiral ports.
- Open Problems (Jul 10): spiral eval suites + automate relative windings; conservative fiber tracing; label quality. **spiralcheck** (Nicodol) already covers held-out *fit mesh* eval; **windcheck** covers tifxyz self-intersection — our niche remains **`winding_inference` seed audit** (upstream of the fit), not mesh QA.
- GitHub MCP still needsAuth; public issues only (#203 whole-volume warp = large/data-heavy). Discord not scraped.
- **Avoid:** ScrollFiesta/patch connectivity; consumer-GPU spiral ports; ink training without niche; >50 GB downloads; pitching auto chains as improvement (Keeper).

### Ranked opportunities (~3.5 weeks to Oct 31)

| Rank | Opportunity | Impact | Effort | Discord? | Status |
|---|---|---|---|---|---|
| **1** | **Ship diagnosis note** (15 confirmed seed errors + negative fit + docs/GIF/CLI) as Progress submission | High ($1–5k plausible) | Low left: public repo + form | **Yes** — early use signal; ask if Annotation wants upstream | Package ready; **submit only when Salvador says** |
| **2** | **`winding_inference` eval suite** | Med–high | ✅ CLI+self-check | **Yes** — would Annotation run on new exports? | `python -m checker self-check` passes |
| **3** | **Fiber B salvage** — re-score conservative tracer on **2026-09-15** fiber preds (GT was 2026-08-01); clarify fibers↔PCL scale | Med–low for Oct | Med; small crops only | **Yes** — coordinate scale + whether bulk same-winding is wanted | Not started this turn |
| **4** | **More geometric confirms / second scroll** if another `winding_inference` publishes | Med | Needs data | Optional | Paris4 only for now |
| **5** | **Upstream villa PR** (export checker hooks / docs link) after Discord interest | Med if adopted | Med | **Required first** | Blocked on Discord approval |

**Not ranked / avoid:** auto-chain GPU ablations; villa #203 volume warp; First Letters / Title / Grand Prize track.

### Zero-cost executed this turn (no publish / Discord / Atrium / >50MB downloads)
- Population stats: 50% multi-ray disagreement at human points (triage-only); seeds all integers; confirmed taxonomy **10×(−1), 4×(+1), 1× reversed level**.
- `checker_cases/case_catalog.json` + `.csv`
- `out/winding_inference_population_stats.json`
- `scrypt_vc/checker/winding_inference_audit.v1.schema.json` + `out/winding_inference_audit.v1.json`
- Note addendum + PDF regenerated (13 pages)
- **GIF path:** `/workspace/vesuvius/checker_cases/case02_wrong_direction.gif`

## Round update (Oct 5 ~8:55 AM ET) — more cases + polish (approved; no publish)

Salvador approved (2) more confirmed cases from already-downloaded data + (3) reproducibility polish.
**No** Discord / form submit / publish / Atrium GPU / large downloads.

### (2) More confirmed cases
- Widened `chain_offsets` to **DR=8** → `out/checker_chain_offsets_dr8.json` (37 strong candidates vs 10 at DR=6).
- 3D same-sheet verify on **tiny** m7 crops (17×96×96; URL restored / same as `verify_cc.py`). 21 new candidates after excluding DR=6 ten.
- **New:** 10 CONFIRMED, 6 probable, 5 ambiguous (`checker_cases/geometric_check_dr8_new.json` + figures for confirmed).
- **Totals:** **15 CONFIRMED**, 8 probable, 8 ambiguous (probable/ambiguous kept separate).
- Note + PDF regenerated with the expansion tables and sample figures.

### (3) Reproducibility polish
- `scrypt_vc/README.md` (how to run checker / reproduce note figures)
- `LICENSE` (MIT) + `DATA_LICENSE.md` (CC-BY-NC for scan-derived artifacts)
- `python -m checker` / `scrypt_vc/run_checker.sh`; wired into `run_all.sh` when `winding_inference` is present
- `checker_cases/case02_wrong_direction.gif` (~30 s, wrong-direction ray)
- `checker_cases/README.md` updated

**Still not done / not started this turn:** Discord, form submit, Atrium GPU, shipping a public repo.

## Headline milestones
| | Result | Status |
|---|---|---|
| A. Auto winding constraints | Works end to end on 8 PHercParis4 z-slices. Agreement with human relative-winding chains on adjacent pairs: **91.7%** on 7 held-out slices (482 pairs), **95.3%** when skipping uncertain chunks at a threshold fixed on the dev slice only (0.98): 424/509 human pairs scored = **83.3% coverage** (the earlier 97.7% figure was withdrawn: its threshold was picked on held-out data). Long-range pairs: **65.9%**, which is **worse than a straight-line crossing-count baseline (86.5%, |Δ| only)**. Round 2: on the same 424 accepted adjacent pairs, ours is 95.3% vs 90.1% for the baseline; LOSO hybrid 77.0% vs 77.2% baseline. **Keeper (Oct 5): do not pitch auto chains as an improvement; lead with the diagnosis note and the negative fit.** | Prototype. The weakness is known (see below). |
| A. Output | `out/winding/auto_relative_windings.json`: 8,973 auto chains / ~66k points in the VC3D point-collection schema (`relative_windings.json`). Not yet run through `fit_spiral.py` (needs a GPU). | Unverified in the fitter |
| B. Conservative fiber tracer (on the published fiber predictions) | 3 held-out Paris4 crops / **143** GT runs (Aug-01 preds): deviation **53.0% → 29.1%** (permissive→conservative); correct steps 36.4→19.8 L3 voxels; auto clean **32.5% → 61.1%**; GT recall **21.9% → 37.1%**. Aggregate: `out/fiber/paris4_aug01_heldout_aggregate.json`. Sep-15 worse on 1 crop. | Prototype; secondary to diagnosis |
| B. Output | 2,788 auto traces from one crop written as `vc3d_fiber` v1 JSON. **All of them pass villa's own `parse_vc3d_fiber_format`.** | Parser-valid; not loaded in VC3D yet |
| B0. Classical tracer on raw CT vs the fiber-skeletons cubes | **Negative result.** In-region point precision is 29% (structure tensor) and 19% (H/V Hessian), against a 25–28% chance level for bright voxels. | Dropped as the main path |

## Key findings that change the plan
1. **The VC team already has a neural automatic winding generator.** `vesuvius/neural_tracing/winding_models` contains a phase model whose ray crossings are exported by `export_spiral_supervision.py`. Its output is published as `spiral_datasets/PHercParis4/winding_inference/` (1.15M rays, 22.7M crossings) and consumed by the fitter (`dense_spacing_mode=winding_model`). Project A therefore has to be pitched as **a cheap, CPU-only, interpretable, cycle-checked generator that writes ordinary relative-winding PCLs and reports contradictions**, and/or as a **checker for the neural crossings**. It cannot be pitched as "the first automatic winding constraints". **Decision needed** (see the end).
2. **Fiber prediction volumes are published:** `s3://vesuvius-challenge-open-data/PHercParis4/representations/predictions/fibers/` has two runs (2026-08-01 and 2026-09-15). Each has `presence`, `nx` and `ny` at levels 3 and 4 only (19.2 / 38.4 µm), blosc-zstd, 64³ chunks. The direction is decoded as unit zyx `(sqrt(1-a²-b²), b, a)`, with `a=(nx-128)/127` and `b=(ny-128)/127` (`spiral-fitting/losses.py`).
3. **VC3D already has an interactive native fiber tracer** (beam search plus cone, in `native_fiber_trace3d`). The human-guided eval fibers were made with it on the 2026-08-01 fiber predictions. Project B's niche is therefore **fully automatic, no control points, explicit abstention**, as a bulk source of same-winding evidence.
4. **villa #1855 is mostly addressed.** Item 1 (the point-to-attachment branch step) is fixed on main (`attachment_branch_delta`, PR #1864). Item 2 (`solve_min_edge_fix` dropping equations when `allowed_edge_keys` is set) is **still present on main** (`find_inconsistent_windings.py`, around line 723); PR #1876 is open by someone else. It is not an opportunity for us. Lesson applied in A: seams are handled explicitly by cutting at θ=±π, plus seam edges with offset σ.
5. **The fiber-skeletons cubes (2025) are in old Scroll 1 (7.91 µm, "scroll1a") and Scroll 5 coordinates.** There is no published registration to the 2026 Paris4 2.4 µm scan, so the published Paris4 fiber predictions **cannot** be scored on those cubes. The cubes do ship raw CT (`imagesTr`), which is why B0 was possible.

## Formats (verified from code and data)
- **Fit/annotation coordinates:** PHercParis4 `20260411134726-2.400um-0.2m-78keV-masked.zarr` level 2 (9.6 µm voxels), shape 18946×8174×8174. PCL `p` values are `[x, y, z]` in this space. The m7 surface prediction's level 0 and the surface-recto prediction's level 2 are on the same grid.
- **Point collections** (`relative_windings.json`, `same_windings.json`, `abs_winding.json`): `{"vc_pointcollections_json_version":"1","collections":{id:{name,color,metadata:{winding_is_absolute},points:{id:{p:[x,y,z],wind_a,creation_time}}}}}`. Relative: the difference in `wind_a` between two points of a collection is their winding difference. **In every public chain, consecutive points differ by exactly +1**, and winding increases outward. Absolute: `metadata.winding_is_absolute=true`. Same-winding: `wind_a=null`. Loader: `spiral-fitting/point_collection.py::load_point_collection`. Public counts: relative 300 collections / 2,173 points; same-winding 154 / 5,413; absolute 6 / 59.
- **Dataset layout the fitter expects:** `umbilicus.json` (`control_points[{x,y,z}]`), `verified_patches/` (tifxyz), `fibers/` (vc3d_fiber JSON), `fiber_directions.npz`, `outer_shell/`, `tracks/`, `winding_inference/`, `lasagna_inputs/*`, the PCL JSONs, plus a `spiral-scroll.json` (`voxel_size_um`, `spiral_outward_sense` CW/ACW).
- **vc3d_fiber:** `type`, `version` ∈ {1,3,4}, `control_points`, `line_points` (`[x,y,z]`). The public `eval_fibers` are v3 with `line_points` in **base 2.4 µm voxels** (z up to 75k), which is 4× the PCL coordinates. **Resolved Oct 5:** fitter scales base-voxel fibers by **0.25** into PCL/fit (level-2) space (`spiral_helpers.load_fiber_point_collection`). See `out/fiber/fibers_vs_pcl_scale.json`.
- **Winding-inference store:** `manifest.json` plus shards of `ray_origin_zyx`, `ray_step_zyx`, `crossing_t`, `crossing_level`, `crossing_offsets`, `seed_winding` (npy, checksummed).

## A: method and numbers
Method (`winding/auto_winding2d.py`), for one z-slice of the m7 surface prediction:
1. Binarize, remove the thick mask-border ring, skeletonize, remove junctions.
2. Cut the skeleton radially every 5°, including the branch ray. This makes s = k + σθ/2π exact on each chunk.
3. Edges: continuity edges across cuts (offset 0, or σ at the seam) and umbilicus-ray edges between consecutive crossings (+1). Ray edges are dropped where the gap exceeds 1.6× the local median, the run is wider than 7 px, or the sheet is not roughly perpendicular to the ray (|cos| < 0.8).
4. Greedy union-find integer synchronization with cycle checks, then ICM refinement and a per-chunk agreement confidence.
5. **Spiral sense σ is detected automatically** as the sense with fewer contradictions: 53k vs 158k rejected ray support on the dev slice. It picked σ=+1 on all 8 slices.

Tuning: one decision (continuity weight 20 → 1000) was made on z=15334. The other 7 slices are held out.

| Slice set | Adjacent pairs: graph | Adjacent pairs: straight-line baseline | Long-range pairs: graph | Long-range pairs: baseline |
|---|---|---|---|---|
| dev z=15334 | 94.4% (90) | 84.4% | 77.3% (1,961) | 51.8% |
| held-out 7 slices | **91.7%** (482) | 90.0% | **65.9%** (5,762) | **86.5%** |

- Held-out abstention: see "Reviewer follow-ups" below (the old 97.1%/97.7% figures used held-out-chosen thresholds and are withdrawn).
- Held-out long-range accuracy by |Δ|: Δ 0–4: 80%; 10–14: 72%; 20–24: 60%; 30+: 15%. Errors accumulate along long graph paths.
- Caveats:
  - Human chains always step +1, so a predictor that knows the protocol scores 100%. These numbers measure *agreement of an independent method*, not discrimination.
  - Human labels may contain errors; no audit has been done.
  - 2D slices only; no z-coupling yet.
  - Runtime is ~35 s per full slice at ~1.5 GB RAM.

## Keeper decision (Oct 5, via Salvador)
- **Stop pitching auto chains as an improvement.** The submission leads with the diagnosis note and the honest negative fit result.
- All caveats are folded into `NOTE_winding_diagnosis.md` / `.pdf` (rewritten Oct 5): reduced fit, 2,000 steps, coarser grid, 28 chains at two depths, both arms used the team's neural winding from a human-labeled fit, and the three explanations for why chains hurt are marked as **untested hypotheses only**.
- The brief 3.066 GB disk overage stays on record; nothing was published.
- **Next Progress Prize deadline: Saturday, October 31, 2026, 11:59pm Pacific (PDT, UTC−7)** — confirmed via live `scrollprize.org/prizes` on Oct 5, 2026. That is the next monthly cutoff; **Oct 31 is still open.** (Sep 30 has passed. Grand Prize / First Letters / Title remain June 25, 2027, 11:59pm Pacific.)
- No further chain-fix GPU work. No Atrium GPU, no Discord/form submit, no publish from this turn.

## Opportunities (researched Oct 5 morning; **rescanned ~9:30 AM ET** — see round update above for live ranking)
Sources: live `scrollprize.org/prizes` + `2026_open_problems` (Jul 10), winners page (Aug 2026 latest listed; Sep not posted yet), archived 2024 wishlist, Substack July awards, villa help-wanted (#191–193). GitHub MCP was unauthenticated; issue titles from the public issues list only. Discord not scraped.

**What judges actually reward** (prizes page + July/August winners): released early; used by others; quantitative/qualitative gains on real data; **failure-case analytics** (July: TAUIL’s negative-result ink analysis, $1k; windcheck / TIFXYZ Doctor / scroll-data-audit all $1k); well documented. Open Problems §2 spiral callout still says relative-winding automation would help a lot — but our fit showed auto chains hurt in the reduced setting, so we lead with diagnosis, not automation.

**Saturated / avoid for Oct:** ScrollFiesta / patch-connectivity unwrapping ($20k+$2.5k Jul–Aug); consumer-GPU / Windows spiral-fitter ports (already awarded); large ink-training experiments without a clear niche.

### Ranked top 5 (prize impact ÷ effort through Oct 31)

| Rank | Opportunity | Impact | Effort | Fit | Discord? | First step |
|---|---|---|---|---|---|---|
| **1** | **Ship the diagnosis note as the lead submission** (seed-error audit of published `winding_inference` + honest negative fit). Matches “reveal insightful, actionable information” and “detect failure-cases of existing methods”; negative results have been paid. | High ($1–5k plausible; $20k unlikely alone) | Low (packaging) | Math/puzzle + already done | **Yes** — ask if anyone is already auditing winding_inference / wants it upstream | MIT README + public repo stub + one-command `checker` CLI; form only when Salvador says |
| **2** | **More confirmed diagnosis cases from data we already have** ✅ (Oct 5: +10 confirmed @ DR=8; totals 15/8/8) (widen DR / more human chains; same m7 + winding_inference on box). Strengthens Part A without pitching chains. | Med–high | Low–med (CPU) | Same stack | Optional | Re-run `chain_offsets` at DR=8; verify next candidates with existing `case_figures` / `verify_cc` |
| **3** | **Reproducibility polish** ✅ (Oct 5: README, LICENSE/DATA_LICENSE, checker CLI, case02 GIF, STATUS/note) README, `run_all.sh` for checker+rescore, short GIF of one confirmed case, license headers, disk/VRAM ledger. Required to accept a prize; early release favored. | Med (multiplies #1) | Low | Docs | No | Write `scrypt_vc/README.md` + 30s GIF from `checker_cases/case02` |
| **4** | **Turn the checker into an evaluation suite** ✅ CLI+self-check Oct 5 for spiral supervision (Open Problems: “better evaluation suites … for the spiral fit”). JSON schema + CLI that scores any `winding_inference/` dir; report seed-consistency metrics. | Med | Med | Math / tooling | **Yes** — ask spiral/Annotation folks if they’d use it | Spec `winding_inference_audit.v1.json` from current `geometric_check.json` |
| **5** | **Fiber tracer B salvage** | Med–low | — | — | scale ✅; Sep15 1-crop worse than Aug01 | Prefer Aug-01 preds; Discord still for Annotation interest |

### Also note (not top 5)
- **Auto-chain fix work:** Keeper said stop pitching; only zero-cost analysis of existing wrong-chain fraction is in the note. Do not spend Atrium GPU on chain ablations unless Salvador reverses.
- **villa help-wanted #191–193** (compressed-region surface/fiber, 3D ink labels, label generation): large-data / training; poor fit for 3 weeks + 8 GB + no >50 GB downloads.
- **First Letters / Title / Grand Prize:** different track; needs VC3D workflow + ink; out of scope for this Progress submission.

## Submission note status
- Files: `NOTE_winding_diagnosis.md` (source), `.html`, `.pdf` (**13 pages**, regenerated Oct 5 ~9:30 AM ET).
- Content: Part A = neural winding seed-error diagnosis (**15 confirmed / 8 probable / 8 ambiguous**) + dropped label-free checker + population-stats addendum; Part B = negative Atrium fit (78.9% vs 84.1% adjacent pairs) with full caveats.
- Case 02 GIF: `checker_cases/case02_wrong_direction.gif`.
- Zero-cost addendum in the note: among held-out adjacent pairs our export filter (conf ≥0.99) also scored, 12 of 408 disagreed with humans (97.1% agreement) — descriptive of the filter, not of the fit-range slices.
- **Submission-ready as a draft technical note: yes**, for content and honesty. Still needed before a real submit: public/open-source packaging (repo URL, MIT), a short usage doc for the checker scripts, and the Google Form / Discord registration. **Do not submit until Salvador says so.**

## Atrium reduced spiral fit (Oct 4, 9:30–10:16 PM ET): DONE
**Setup**
- One folder: `C:\Users\salva\scrypt_vesuvius`.
- Venv on the system Python 3.12.10; nothing installed system-wide.
- Trimmed torch 2.11.0+cu130 streamed out of the remote wheel (2.09 GB; script `atrium/install_torch_min.py`), plus the fitter's dependencies installed with `--no-cache-dir`.

**GPU check**
- RTX 2070, sm_75 is in the build's arch list.
- fp16 matmul 5.1 TFLOPS (relative error 3e-4); fp16 autocast with GradScaler works; bf16 is reported unsupported.
- triton-windows 3.6.0 compiles and runs a kernel correctly.
- The fitter itself is fp32: no bf16, autocast or FlashAttention, so no patch was needed.

**Run setup**
- Fitter: villa `5a4388f` `fit_spiral.py`, unmodified, run through `run_fit.py` (cuDNN disabled, peak memory reported).
- One extra file was needed: `vesuvius/src/vc3d_fiber_format`.
- Every run ends with a `RuntimeError` in the final patch-satisfaction step, because that step needs the native extension. This happens after the checkpoint is saved, so scoring used our own evaluator.

**Data on Atrium (23 MB)**
- `winding_inference` subset to the rays crossing z 10868–11332: 66k rays, 11 MB, with fingerprint and checksums recomputed.
- Outer shell, umbilicus, `same_windings.json`, `abs_winding.json` (unused, since it needs patches).
- `spiral-scroll.json`: sense CW, derived from our auto σ=+1 and VC3D's chirality rule; voxel size 9.6 µm.
- **No human relative chains on Atrium.** Arm 1's `relative_windings.json` holds only our auto chains: 4,682 chains / 25.8k points from z = 10950, 11050, 11150, 11250, export rule conf ≥0.99 as before.

**Config (both arms identical)**
- z 10900–11300 (400 slices), 2,000 steps, `model_flow_voxel_resolution` 20 instead of 16. The coarser grid halves the checkpoint (511 → 269 MB) so it fits the disk budget.
- Turned off: patches, tracks, fibers, fiber directions, normals, gradient magnitude, absolute PCLs.
- Supervision left: the winding-inference model, outer shell, umbilicus, same-winding PCLs. Arm 1 also gets our auto relative chains as unattached strips.
- Arm 0: `input_use_pcl_relative=false`. Arm 1: our auto chains only.

**Scoring (`atrium/eval_heldout.py`)**
- 28 human relative chains / 137 points / 109 consecutive pairs, with every point in z [10900, 11300). Never given to either fit.
- Metrics:
  - Pair accuracy: the fitted winding difference is within 0.5 of the human difference.
  - Point satisfaction, using the official `satisfaction_metrics` thresholds: 0.45 dr in spiral space and 6 voxels in scan space.
  - Chains fully satisfied.
- Nothing was tuned on these labels. Three seeds per arm; the seed count was fixed before seeing results.

| Arm | Adjacent pairs (s1/s2/s3, mean) | All within-chain pairs (mean) | Points satisfied (mean) | Chains fully satisfied (s1/s2/s3) |
|---|---|---|---|---|
| 0: no relative constraints | 85.3 / 85.3 / 81.7 → **84.1%** | 55.9% | 44.5% | 4 / 4 / 5 of 28 |
| 1: only our auto chains | 78.9 / 78.0 / 79.8 → **78.9%** | 51.0% | 40.4% | 1 / 3 / 3 of 28 |
| (smoke test: 30 steps, auto chains, flow resolution 16) | 64.2% | 34.6% | 38.0% | 0 |

- **Result: our auto chains made the reduced fit worse, by −5.2 points on adjacent pairs.** Arm 1 is lower than arm 0 on every seed and every metric.
- Likely reasons (untested):
  - About 5% wrong chains, from 2D-only and slice-local errors, conflicting with the winding model.
  - 4,682 chains spread over only 4 slices.
  - The relative chains enter only as unattached-strip losses, because there are no patches.
- Caveats:
  - Tiny test set: 28 chains, clustered at z≈11044 and 11227.
  - A reduced fit with no patches, normals or tracks, a coarser flow grid and 2,000 steps; not comparable to the team's fits.
  - The winding inference used by both arms comes from a fit that used human labels (circular).
  - The same-winding human PCLs were in both arms.

**Resources**
- Speed: about 9.5 iterations/s. A 2,000-step run takes about 3.5 min, after about 8 min of one-time Triton compilation on the first run.
- **Peak VRAM:**
  - At flow resolution 20: torch 0.41 GB reserved; nvidia-smi showed 2,118 MiB total against about 1,480 MiB idle.
  - Smoke run at the default resolution 16: 0.72 GB reserved, 2,351 MiB total.
  - No out-of-memory error.
- **Disk:** final **2.567 GB** (venv 2.528, work 0.028, cache 0.010, logs and eval JSONs under 1 MB). Each checkpoint was deleted after scoring.
  - **Peak 3.066 GB for a few minutes:** the smoke run's 511 MB checkpoint at the default resolution briefly exceeded the 3 GB budget by 0.07 GB. I deleted it straight after scoring and switched to resolution 20; the peak afterwards was 2.83 GB.

## Atrium spiral-fit attempt (Oct 4, ~9:10–9:25 PM ET): STOPPED at a refused action
**What ran on Atrium:**
- One read-only check, which was approved:
  - Drives: C: 770 GB free / 161 GB used; D: 218 GB free; G: 54.5 GB free.
  - Python 3.12.10 (system), pip 25.0.1; no torch installed.
  - No uv, no MSVC `cl`, no nvcc; git present.
  - RTX 2070, 8192 MiB with 1,636 MiB in use, driver 591.86, compute capability 7.5.
- Then I tried to copy 3 small setup files into `C:\Users\salva\scrypt_vesuvius\setup\`.
  - `verify_gpu.py` (2.1 KB) was approved and written.
  - `install_torch_min.py` and `req_nontorch.txt` were **refused** ("not approved on the user's computer").
  - Per instructions I stopped and did not retry.

**Current state of Atrium:**
- Disk used: **~2 KB** (`C:\Users\salva\scrypt_vesuvius\setup\verify_gpu.py`; harmless, can be deleted).
- No venv, no torch, no fit run. Peak VRAM: n/a.

**Feasibility findings (worked out on the box, ready to run once approved):**
- **Disk budget:**
  - torch 2.11 cu130 cp312 Windows wheel: 1.92 GB download, **2.83 GB installed**.
  - cu126/cu128 wheels: 4.1 GB installed.
  - The fitter's other dependencies (triton-windows 3.6, scipy, numpy, wandb, pyro, kornia, trimesh, rustworkx, zarr, …): 155 MB of wheels, **0.46 GB installed**.
  - A plain install is therefore ≈3.3 GB plus data, which is **over the 3 GB budget**.
  - Plan that fits: stream only the needed files out of the remote torch wheel (no wheel or pip cache on disk; `install_torch_min.py`). Skip the cuDNN sub-libraries (the fitter has no cuDNN ops; cuDNN disabled at runtime), cusolverMg, the duplicate nvrtc .alt DLL, nvperf_host, headers and .lib files.
  - That gives torch ≈2.09 GB, about **2.6 GB** of software, plus ~0.2 GB data (`winding_inference` 168 MB, PCLs, outer shell 10.5 MB) plus outputs: **≈2.8–2.9 GB**, tight but within budget.
  - The cu130 build should include sm_75 (CUDA 13 supports Turing); `verify_gpu.py` checks `get_arch_list()`.
- **Triton:** the fitter needs Triton (`flow_triton.py`, `gap_triton.py`). On Windows the `triton-windows` 3.6 community wheel is what the fitter's `pyproject` already specifies; it bundles TinyCC and ptxas. Whether its kernels run on sm_75 is unverified.
- **Precision:** the spiral fitter has no bf16, autocast or FlashAttention; it runs fp32, which is fine on Turing. No config patch is needed. fp16 + GradScaler is tested in `verify_gpu.py` anyway.
- **Python:** `pyproject` requires 3.14, but every fitter `.py` compiles under 3.12. Runtime stdlib use is unverified.
- **Main limitation:** the fitter's native extension `vc_spiral` (nanobind, built with CMake) needs a C++ compiler. Atrium has no MSVC, and installing Build Tools system-wide is not allowed. Without it, verified-patch sampling is unavailable, so a local fit would run with `input_use_verified_patches=false`. Absolute-winding PCLs are then disabled too, and relative chains act only as unattached strips. The remaining supervision would be the winding inference, the outer shell, same-winding PCLs and relative PCLs. Tracks (12–17 GB) and lasagna normals (32 GB) are also excluded by the budget.
  - So a local fit would be a **reduced** fit, suitable only for an A/B comparison. It would not be comparable to the team's full fits.
- **Planned test, not run:**
  - z = 10900–11300 (400 slices, the README's example range; ~38 human relative chains).
  - Arm 0: no relative PCLs. Arm 1: our auto chains only (human relative chains removed from the input).
  - Score: fitted winding differences at all human relative chain points in range, all held out, never used for fitting.
  - Caveat: the neural winding inference used by both arms was produced by a fit that used human labels.

## Reviewer follow-ups, round 2 (Oct 4, ~6:45 PM ET)
Same standard: no threshold or cutoff is chosen with test labels. Results: `out/winding/rescore2.json` (script `winding/rescore2.py`), `out/checker_labelfree_*.json`, `NOTE_winding_diagnosis.md` / `.pdf`.

**Correction to the baseline.** In round 1 the straight-line baseline took its sign (inward or outward) from the human label, which was a small leak in its favour. It now takes the sign from the umbilicus: the point farther from the centre is outward. All baseline numbers below use this. The round-1 hybrid figures (baseline 85.7%) are superseded.

**1. Same 424 accepted held-out adjacent pairs (threshold 0.98):**
- Ours: **95.3%**. Baseline: **90.1%** (identical whether signed or |Δ| only).
- Both right 366; only ours right 38; only baseline right 16; both wrong 4.
- On all 509 held-out adjacent pairs, the baseline gets 86.1%.

**Why "no skipping" covers 94.7% (482/509), not 100%.**
- 27 adjacent pairs are lost, all for one reason: a human point could not be matched to a skeleton chunk within 4 px. No pairs were lost to the "different graph component" reason.
- The 19 unmatched points break down as:
  - 15 have no m7 sheet within 4 px; the human clicked where the surface prediction has no sheet. These cluster in z=11714 chain 48, z=8879 and z=11432.
  - 3 have a sheet present but its skeleton was removed by junction removal or pruning.
  - 1 was removed by the thick-blob / border-ring filter.
- The baseline gets only **14.8% (4/27)** of these pairs right, because the sheet is missing for it too.

**2. Leave-one-slice-out cutoff (8 folds; graph if distance < D, else baseline; D picked on the other 7 slices from 0–1200 px or ∞).**
- Chosen cutoff: **25 px** in 7 folds, **100 px** in the fold that holds out z=16920.

| Band | n | Hybrid | Baseline | Ours alone (on scored pairs) | Our coverage |
|---|---|---|---|---|---|
| <50 px | 950 | 84.2% | 83.4% | 88.7% | 94.3% |
| 50–200 px | 2,477 | 80.6% | 81.8% | 79.0% | 97.3% |
| 200–800 px | 4,350 | 74.7% | 74.7% | 67.9% | 98.5% |
| >800 px | 726 | 69.0% | 69.0% | 33.1% | 97.4% |
| **Overall** | **8,503** | **77.0%** | **77.2%** | 70.4% | 97.6% |
| Adjacent pairs only | 603 | 87.6% | 85.2% | 92.1% | 94.9% |

- The hybrid always has 100% coverage, because it falls back to the baseline.
- Per fold, the hybrid and baseline are within ±3 points. The hybrid wins in 6 of 8 folds; it loses on z=16920 (84.9% vs 88.0%) and z=11432 (54.8% vs 55.6%).
- **Conclusion:** ours adds value only for nearby or adjacent pairs (<50 px, about +2 points). Beyond that, the baseline is as good or better. Overall the hybrid equals the baseline (−0.3 points).

**3. Technical note:** `NOTE_winding_diagnosis.md` plus an 8-page PDF, with all 10 case figures and the circularity caveat stated plainly.

**4. Checker without human labels.**
- Rule: ray-vs-ray consistency, where a ray is flagged if most neighbouring rays disagree at shared crossings.
- Parameters were fixed by a label-free coverage rule: neighbour radius 6 px, window 100 px. A second setting (12 px) was also run.
- Scored afterwards against a strict human-anchored reference: 171 rays, 29 off.

| Setting | Verdict coverage | Precision | Recall | Base rate of errors |
|---|---|---|---|---|
| 6 px | 48.5% | 42.9% | 63.2% | 22.9% |
| 12 px | 81% | 47.2% | 65.4% | 18.7% |

- It catches 3 of the 5 confirmed cases.
- **Verdict:** it doesn't work as a standalone tool. It is about 2–2.5× better than chance, but more than half its flags are false. **Dropped as standalone**; keep only for triage, with human-chain confirmation.

**5.** Nothing was run on Atrium and no GPU was rented.

## Reviewer follow-ups, round 1 (the Keeper, Oct 4 evening)
Results: `out/winding/rescore.json` (items 1–3), `checker_cases/` (item 4). Script: `winding/rescore.py`.

**2. Disjoint labels: yes.** Tuning slice z=15334: 3 collections, 97 points. Held-out 7 slices: 44 collections, 553 points. Shared collections: 0; shared points: 0; nearest held-out slice is 542 slices away.
But the old 97.7% used a threshold (conf 1.0) read off the held-out curve, so it is **withdrawn**. Re-scored with a rule fixed in advance on dev only (smallest threshold giving ≥97% dev adjacent accuracy), which picked **0.98**.

**1. Skip-uncertain coverage (threshold 0.98; denominator = all human pairs, including points that don't snap to a sheet)**
| Slice | Adjacent coverage | Adjacent accuracy |
|---|---|---|
| 15334 (dev) | 85.1% | 97.5% |
| 8750 | 90.0% | 100% |
| 16920 | 78.6% | 93.9% |
| 8450 | 94.0% | 94.9% |
| 11432 | 77.8% | 85.7% |
| 15876 | 85.3% | 96.6% |
| 8879 | 76.9% | 98.0% |
| 11714 | 75.0% | 95.2% |
| **Held-out overall** | **83.3% (424/509), 16.7% skipped** | **95.3%** |
- Non-adjacent held-out pairs at 0.98: 69.7% accuracy, 84.4% coverage.
- No skipping: 91.7% accuracy, 94.7% coverage (482/509).

**3. Hybrid (graph for near pairs, straight-line sheet count for far pairs; cutoff chosen on dev only)**
- On dev, the graph beat the baseline at every distance, so the dev-chosen cutoff was ∞ (graph everywhere).
- Held-out result with that choice, all 6,361 pairs scored (100% coverage; baseline fallback where the graph can't score):
  - **Overall 67.2%** (near 67.2%, far n=0); baseline alone **85.7%**.
  - Adjacent pairs 87.6%; non-adjacent 65.4%.
- Informational only (uses held-out labels, so not a valid score), graph vs baseline by distance:
  - <50 px: 88.5% vs 85.3%
  - 50–100: 81.7% vs 85.0%
  - 100–200: 76.7% vs 86.9%
  - 200–400: 71.0% vs 84.6%
  - 400–800: 55.9% vs 83.5%
  - >800: 12.1% vs 96.5%
- Conclusion: one dev slice is not representative (dev baseline >800 px is only 28.8%). The hybrid cutoff needs several tuning slices (e.g. 3 dev / 5 test, or leave-one-slice-out). Honest current answer: the hybrid as specified does **not** beat the baseline. (Superseded by the round-2 leave-one-slice-out test; note that round 1 gave the baseline the human sign.)

**4. Contradiction checker on the team's published neural winding output (`winding_inference`)**
- Label-free flag: nearby rays' winding spread >0.5. It is noisy: at 12 px, 63 of 70 neural/human disagreements are flagged, but so are 137 pairs where neural and human agree.
- Confirmation method: anchor on human chains. For each chain, u = neural w − wind_a must be constant, so a ray whose u differs from the chain consensus (≥3 rays) is a candidate.
  - 238 rays scored, 30 off-consensus, 10 where another ray at the same human point agrees with consensus.
  - Each candidate was then checked by figure plus a 3D sheet-connected-component test on the m7 prediction.
- **5 CONFIRMED cases**, figures in `checker_cases/` with a README:
  - case01 col172 z8879: −1
  - case02 wraps2 z16920: a ray whose levels run opposite to the sheet order, off by +4…+18
  - case03 col22 z15080: −1
  - case07 col58 z9185: −1
  - case08 col63 z9407: +1
- 2 more are likely: case00 (−2) and case06 (−1). A second neural ray is also off at those points.
- 3 rejected as ambiguous: col262 ×2, col88.
- All 10 points are flagged by the label-free checker, but only the human chain says which ray is wrong.
- Single-ray relative counts agree with humans in 93 of 94 cases, so the neural errors are in absolute seed windings across rays, not in per-ray crossing detection.
- Caveat: the neural seeds come from a fit that already used these human constraints.

**5. Local spiral fit on Atrium (RTX 2070): BLOCKED.**
- The first harmless command (nvidia-smi plus free disk) was refused: "not approved on the user's computer, so nothing ran". It was not retried.
- Nothing ran on Atrium: 0 GB used, no PyTorch/Triton sm_75 check, no fit.
- To unblock: approve local execution for Atrium (Settings → Bot → Execution on Local Computer). Then: one folder, ≤3 GB, 200–500 slices with and without our constraints, stop on OOM.
- No rented GPU used.

**6. Licensing.**
- Nothing built from CC-BY-NC scan data (auto PCLs, traces, checker outputs, figures) goes into any Scrypt product.
- It stays in the prize submission. Code is MIT, as Scrypt.

## B: method and numbers
Method (`fiber/pred_tracer.py`) on the L3 presence and direction volumes:
- Seeds: presence maxima ≥220.
- Each step: advance one voxel along the decoded axis, then re-centre on presence within a ±1 voxel cross-section.
- Stop and abstain on: weak presence (<140), low local axis coherence (<0.85 by default, <0.93 in the conservative setting), a turn >30°, a fork (a second ridge 2–3 voxels away with a dip in between), a collision, or the border.

Evaluation (`fiber/eval_paris4.py`) against eval fibers inside 4 crops of 256³ at L3 (4.9 mm cubes): dev crop (23,5,8); held-out crops (24,7,5), (22,9,8), (20,4,8).

| Held-out (282 GT-seeded half-traces, 3 crops) | Deviation rate | Mean correct steps (L3) | Auto: clean / GT-touching | Auto: GT recall (length-weighted) |
|---|---|---|---|---|
| permissive (no fork rule, coherence 0.7, presence 110) | 53.9% | 36.1 (693 µm) | 32.6% of 267 | 21.3% |
| default | 34.8% | 23.3 | 55.7% of 442 | 34.7% |
| conservative (coherence 0.93) | **29.4%** | 19.9 (382 µm) | **60.8%** of 487 | 36.5% |

- Caveat: GT was traced with the same 2026-08-01 predictions, so this measures how much of the human-guided tracing can be automated. It is not independent ground truth.
- At L3, 1 voxel is about 19 µm; neighbouring fibers are ~2–3 voxels apart, so τ = 1.5 voxels.

B0 negative result (`fiber/tracer.py`, `eval_fibers.py`):
- Raw-CT Hessian and structure-tensor tracers on cube s1_8997 failed: in-region precision 19–30% against a 25–28% chance level.
- One finding is useful: the sheet normal plus the vertical/horizontal prior explains GT fiber direction well. 86% of GT tangents are within 30° of the in-sheet V or H direction, compared with 55% for the raw structure-tensor axis.

## Compute: what fits the RTX 2070 8 GB (sm_75, fp16 only)
| Step | Needs a GPU? | Fits 8 GB? |
|---|---|---|
| A constraint generation, B tracing, all evaluation | No (CPU, <2 GB RAM) | n/a; runs anywhere |
| `fit_spiral.py` on a small z-range (to test whether auto constraints help the fit; the main missing evidence) | Yes (NVIDIA required) | **Unverified.** The tutorial recommends ~1,000 slices for "smaller GPUs"; a community patch targets 12 GB. Plan: 200–500 slices with reduced `sample_count_*`, `WANDB_MODE=disabled`. Uses Triton kernels; no bf16 or autocast found in non-test spiral-fitting code. **Check Triton/sm_75 and `torch.cuda.get_arch_list()` for the cu128 wheel first.** |
| winding-model / fiber-model / surface-model inference | Not needed: the outputs are published | If needed, change bf16 to fp16 (see audit) |
| Training any model | Not planned | Would need fp16 plus GradScaler |

**bf16 / FlashAttention audit (villa `5a4388f`):**
- `winding_models/infer_winding_volume.py:2863` hard-codes `torch.autocast("cuda", dtype=torch.bfloat16)`. A patch to fp16 is needed, plus an overflow check.
- `winding_models/train_config*.json` and `fiber_trace_3d/configs/train_*.json` use `"mixed_precision": "bf16"`.
- `fiber_trace_3d/infer.py` has `--inference-precision auto|fp32|fp16|bf16`. Pass `fp16`; "auto" reads the checkpoint's setting.
- lasagna `train_unet_3d.py` / `eval_unet_3d.py` default to `--precision bf16`. fp16 is available, and training asserts bf16 support.
- Attention uses `F.scaled_dot_product_attention` (`winding_model.py`, dinovol, `autoreg_mesh`). On Turing this falls back to the math or mem-efficient kernels with no FA2 requirement. `models/build/transformers/flash_rope.py` was not inspected in detail.
- `spiral-fitting`: no bf16 or autocast in non-test code.

**Rental (user said no; estimate only).** Spiral-fit ablations (with vs without human relative windings, with auto constraints, a few z-ranges): about 10 runs × ~1 h. That is roughly **$15–25 on an A100 80GB** ($1.19–1.59/h) or **$5–10 on an RTX 4090 24GB** ($0.34–0.74/h), plus idle time. RunPod prices are from the Sep 27 notes. What it buys: whole-range fits and the fitter-level evidence ("auto constraints improve or replace human constraints") that judges weight most.

## Disk and download ledger (box, /workspace/vesuvius = 5.9 GB)
- Downloaded so far: **~2.5 GB total** (adds winding_inference 168 MB and checker crops 3 MB), with no single download over 0.45 GB. Atrium: 2.567 GB used in `C:\Users\salva\scrypt_vesuvius` (peak 3.066 GB for a few minutes, see the Atrium section).
  - fiber-skeletons.zip: 442 MB (1.1 GB unpacked)
  - m7 surface planes: 8 × 146–202 MB of compressed chunks, about 1.4 GB fetched; stored 510 MB as .npy
  - eval_fibers: 287 MB (645 files)
  - fiber-prediction L3 crops: about 0.1 GB fetched; stored 161 MB
  - annotations: 2.5 MB
- Other disk use: villa clone 1.7 GB (`--depth 1`; could be sparse), venv 0.5 GB, outputs 1.4 GB (the solution pickles can be deleted).
- **For the user's nearly full PC:** only `scrypt_vc/` (<1 MB) plus whatever inputs are rerun are needed. A minimal rerun needs ~2.3 GB. Avoid: `fiber_directions.npz` (2.6 GB), tracks DBMs (12–17 GB), lasagna respool (32.6 GB). Full CT and prediction volumes are TB-scale; never pull them. No download over 50 GB was attempted.

## Rules: eligibility, payment, license (villa `scrollprize.org/docs` at `5a4388f`, matching the live prizes page as of Oct 4)
- **Eligibility:** worldwide, as long as VC can legally pay (no US sanctions). The VC team is ineligible. The team leader submits and receives payment.
- **Payment:** "Prize winner must provide payment information … within 30 days of prize announcement." **The rules name no tax form (W-9/W-8BEN) or KYC step: UNKNOWN; expect one at payout.** The FAQ says prizes are generally taxable.
- **License:** code need not be open at submission, but to accept a prize it must be open-sourced under a **permissive license** (e.g. MIT), publicly. VC data is CC-BY-NC 4.0, so derived datasets such as auto PCLs and traces should carry NC terms. **Scrypt policy:** nothing built from CC-BY-NC scan data goes into any Scrypt product; it stays in the prize submission; code MIT, as Scrypt.
- **Submission:** Google Form "October 2026 Progress Prizes" (name, team, optional Discord, public URL, essay). Submitting as "Scrypt" is fine; the team-leader name is required.

## Blockers
1. Only a reduced local fit exists (no patches, because there is no compiler for the native extension). In it, our auto chains **hurt** (adjacent pairs 78.9% vs 84.1% with no relative constraints, 3 seeds). There is no full-fit evidence.
2. A's long-range consistency is worse than plain straight-ray counting on held-out slices.
3. The coordinate scale for `fibers/` vs PCL coordinates in the fitter is unresolved.
4. Discord check (is someone else doing this?) was not done; it can't be done from here.

## Next steps (week of Oct 5–11)
- **A:**
  - Replace greedy sync with a robust solver: cycle-basis ILP or L1 on chunk offsets, weighted by path length.
  - Use straight-ray counts as a local prior.
  - Couple slices in z by linking chunks across neighbouring slices.
  - Score against the neural `winding_inference` crossings (download only the shard rays inside our slices) as a second independent reference.
  - Add a "contradiction report" (inconsistent cycles with images) as a reviewer tool.
- **B:**
  - Run on the 2026-09-15 predictions (not used for the GT), as a more independent test.
  - Calibrate a per-trace confidence from the end reasons and the fork/coherence margins.
  - Turn the V/H prior into a tracker constraint.
  - Emit same-winding PCLs from traces.
  - Load the outputs in VC3D (needs a VC3D build).
- **GPU (user PC):** install torch cu12x and run the spiral-fitting `uv sync`. Fit a 300-slice range around z=15334 three ways: (i) human constraints, (ii) no relative PCLs (`configs/no_relative_pcls.json`), (iii) our auto PCLs. Compare `satisfaction_metrics_fitted.json`.
- Publish a repo early (week 2), **only after the user approves.**

## Decisions needed from the user
1. Given the existing neural winding generator, repositioning A as the CPU/interpretable generator plus cycle-consistency checker for neural crossings (recommended), or dropping A in favour of B.
2. Running the spiral-fit test on the RTX 2070 (driver, CUDA, disk ~3 GB for env plus the small dataset subset).
3. When and under which name or license to publish (MIT for code, CC-BY-NC for derived data), and when to post on Discord. Nothing has been published.
