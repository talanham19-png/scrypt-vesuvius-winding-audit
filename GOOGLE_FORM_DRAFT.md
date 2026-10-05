# Progress Prize Google Form — draft answers (Scrypt)

**Team name:** Scrypt  
**Team leader / contact:** Salvador Satoshi  
**Repo:** https://github.com/talanham19-png/scrypt-vesuvius-winding-audit  
**Deadline month:** October 2026 (submit by Oct 31, 11:59pm Pacific)

---

## Which scroll / data did you use?

PHerc. Paris 4 (Scroll 1), primarily:

- Published `spiral_datasets/PHercParis4/winding_inference/` (1.15M rays, 22.7M crossings)
- Human `relative_windings.json` (and related spiral PCLs)
- m7 surface prediction (tiny crops for 3D same-sheet verification and figures)
- For the negative fit: a reduced local spiral-fit setup on Atrium (RTX 2070), z 10900–11300, using the team’s neural winding supervision plus/minus our auto relative chains

Scan-derived figures and crops in the submission are CC-BY-NC; code is MIT.

---

## What problem does this address? How does it help reading the scrolls?

Open Problems call out better evaluation for the spiral fit and the outsized impact of relative-winding constraints. The fitter already consumes published neural `winding_inference` as dense supervision. We show that this stream can be **locally inconsistent in absolute seed windings** even when **per-ray crossing detection agrees with humans**.

That is actionable for anyone using `winding_inference` in a fit or as labels: seed errors of ±1 (and one reversed-level case) on the same sheet as human chains are failure modes that can pull the global spiral. A small CPU audit CLI makes the check reproducible on new exports.

We also report an honest negative: our automatic relative-winding chains **did not** improve a reduced fit. We do not pitch them as an automation win.

---

## What does this newly enable?

1. **A documented failure-case analysis** of published Paris4 `winding_inference` seeds: 15 geometrically confirmed cases, catalogs, figures, and a short GIF of the wrong-direction ray.
2. **A reusable seed-audit suite** (`python -m checker`) with a versioned JSON report (`winding_inference_audit.v1`), population stats, candidate flags, and an explicit non-claim: confirmation requires human chains + 3D same-sheet geometry.
3. **Clear caveats** (circularity of seeds from a human-informed fit; reduced fit limitations) so the result is hard to over-interpret.
4. Secondary: fiber-tracer metrics and a resolved **fibers ↔ PCL scale factor of 0.25** for feeding `vc3d_fiber` into the fitter — not the lead.

---

## Evidence / results (short)

- Single-ray relative counts vs humans: **93/94** agree; the one miss is the reversed-level case.
- Chain-anchored candidates + 3D same-sheet verify: **15 confirmed**, 8 probable, 8 ambiguous (DR=6 primary + DR=8 expansion).
- Population triage (not confirmation): at human points with ≥2 nearby rays, rounded windings disagree ~50% of the time.
- Reduced fit (3 seeds): held-out human adjacent pairs **84.1%** (no relative chains) vs **78.9%** (auto chains only).
- Reproduce checker: `cd scrypt_vc && python -m checker self-check` (with local `winding_inference`).

Full write-up: `NOTE_winding_diagnosis.pdf` in the repo.

---

## Anything else we should know?

- Circularity: seeds come from a fit that already used these human labels — finding 1 shows local inconsistency with those labels, not an independent test of the phase model alone.
- We deliberately do **not** lead with automatic winding-chain generation.
- Niche vs community tools: spiralcheck scores fit meshes; windcheck scores tifxyz self-intersections; we audit **seed consistency of `winding_inference` upstream of the fit**.
