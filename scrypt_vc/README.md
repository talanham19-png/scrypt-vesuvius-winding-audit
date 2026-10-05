# scrypt_vc — Scrypt × Vesuvius Challenge (CPU prototypes)

MIT-licensed code for diagnosing the published PHercParis4 `winding_inference`
output, building automatic relative-winding chains, and a conservative fiber
tracer. Released for the Vesuvius Challenge Progress Prize (Scrypt).

Derived scan crops / figures are **CC-BY-NC 4.0** — see `../DATA_LICENSE.md`.

## Setup

```bash
cd /path/to/vesuvius
python -m venv .venv && . .venv/bin/activate
pip install -r scrypt_vc/requirements.txt
# optional villa volume helper:
# pip install -e "villa/vesuvius[volume-only]"
```

Inputs expected under `../data/spiral/` (small JSONs + `winding_inference/`)
and optional m7 planes under `../data/planes/`. Public sources:

- spiral PCLs / winding_inference: `https://dl.ash2txt.org/datasets/spiral_datasets/PHercParis4/`
- m7 surface zarr: `s3://vesuvius-challenge-open-data/PHercParis4/representations/predictions/surfaces/20260411134726-surface-20260413222639-surface-m7-L2-th0.2.zarr`

## One-command checker (diagnosis lead)

From `scrypt_vc/`:

```bash
python -m checker self-check     # Paris4 audit + assert known numbers
python -m checker audit --winding-inference DIR [--relative-windings JSON] --out audit.json
./run_checker.sh                 # same as self-check
```

See `checker/README.md`. Candidates are **not** confirmed without human chains + 3D geometry.

Outputs: `../out/checker_*.json`, figures + `geometric_check*.json` under
`../checker_cases/`. Interpretation and the confirmation standard are in
`../NOTE_winding_diagnosis.md` and `../checker_cases/README.md`.

## Reproduce note figures / winding slice eval

```bash
# Original 8-slice auto-winding + fiber prototype (larger downloads):
./run_all.sh

# Diagnosis-only (after winding_inference is local):
python -m checker --dr 6 --verify
# Optional DR=8 expansion + 3D verify of new candidates:
#   DR=8 python checker/chain_offsets.py
#   python checker/new_cases_dr8.py   # or the inline 3D verify used for Oct 5 cases
```

Case 02 animation (wrong-direction ray): `../checker_cases/case02_wrong_direction.gif` (~30 s).

Case catalog: `../checker_cases/case_catalog.csv` (all DR=6/DR=8 verdicts).
Population / audit JSON: `../out/winding_inference_population_stats.json`, `../out/winding_inference_audit.v1.json` (schema in `checker/winding_inference_audit.v1.schema.json`).

## Layout

| Path | Role |
|---|---|
| `checker/` | Human-anchored seed-error audit of `winding_inference` |
| `winding/` | 2D auto relative-winding chains (not pitched as an improvement) |
| `fiber/` | Conservative auto fiber tracer on published L3 preds |
| `common/` | Small crop / plane fetch helpers |
| `../atrium/` | Reduced spiral-fit + held-out eval (Windows GPU machine) |
| `../NOTE_winding_diagnosis.*` | Lead technical note (md/html/pdf) |
| `../STATUS.md` | Running project status |

## License

- **Code:** MIT — `LICENSE`
- **Scan-derived artifacts:** CC-BY-NC 4.0 — `../DATA_LICENSE.md`
