# Scrypt — Vesuvius Challenge: winding_inference seed-error diagnosis

**Author:** Scrypt (Salvador Satoshi)  
**Target:** Vesuvius Challenge Progress Prize (October 2026)  
**License:** MIT for code (`LICENSE`); CC-BY-NC 4.0 for scan-derived figures/crops (`DATA_LICENSE.md`)

## Headline

The team’s published PHercParis4 `winding_inference` output **counts sheet crossings correctly along a single ray (93/94)** against human relative-winding chains, but its **absolute seed windings are locally wrong**. We confirmed **15** seed-error cases with human chains plus a 3D same-sheet geometric check (8 probable and 8 ambiguous kept separate).

We also tested automatic relative-winding chains in a **reduced** spiral fit: they **hurt** held-out adjacent-pair accuracy (**78.9%** with auto chains vs **84.1%** without). We are **not** pitching auto chains as an improvement — the lead contribution is the diagnosis and the reusable seed-audit tooling.

## Quick start (CPU)

```bash
# Needs a local copy of spiral_datasets/PHercParis4/winding_inference/ (~170 MB)
# and relative_windings.json from the same spiral dataset.
cd scrypt_vc
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python -m checker self-check   # asserts known Paris4 numbers when data is present
```

Generic audit:

```bash
python -m checker audit \
  --winding-inference /path/to/winding_inference \
  --relative-windings /path/to/relative_windings.json \
  --out ../out/winding_inference_audit.v1.json
```

**Confirmation** of seed errors requires human chains and a 3D same-sheet test. Without human labels the suite emits population stats only — it does not claim confirmation.

## What’s in this repo

| Path | Contents |
|---|---|
| `NOTE_winding_diagnosis.pdf` | Technical note (diagnosis + negative fit + caveats) |
| `NOTE_winding_diagnosis.md` / `.html` | Source / HTML |
| `checker_cases/` | Case figures, case02 GIF, catalogs, geometric checks |
| `scrypt_vc/checker/` | Seed-audit CLI (`python -m checker`) |
| `scrypt_vc/winding/` | 2D auto-chain prototype (documented; not pitched as improvement) |
| `scrypt_vc/fiber/` | Conservative fiber tracer (secondary) |
| `out/` | Small audit JSON demos + fiber metric summaries |
| `SUBMISSION_CHECKLIST.md` | Progress Prize packaging checklist |
| `STATUS.md` | Internal project ledger (optional reading) |

## Case 02 (wrong-direction ray)

`checker_cases/case02_wrong_direction.gif` — ~30 s animation of a ray whose level order runs opposite the sheet.

## Niche (vs related tools)

- **spiralcheck** — evaluates whole-scroll *fit meshes*
- **windcheck** — tifxyz self-intersection
- **This work** — audits **`winding_inference` seed consistency upstream of the fit**

## Data

Public Vesuvius Challenge spiral / open-data assets (CC-BY-NC). See `DATA_LICENSE.md`. This repo does **not** ship the full `winding_inference` dump or CT volumes.

## Contact

Scrypt — Progress Prize submission materials. Feedback welcome from Annotation / spiral-fitting folks on whether the seed-audit CLI is useful on new `winding_inference` exports.
