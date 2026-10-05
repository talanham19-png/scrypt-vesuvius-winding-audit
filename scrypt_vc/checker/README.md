# winding_inference seed-audit suite

CPU-only audit of a published `winding_inference/` directory (neural ray crossings
+ per-ray `seed_winding`). Brand: Scrypt. MIT code; scan-derived outputs stay CC-BY-NC.

## What it does

1. **Population stats** (always): ray/crossing counts, integer seeds, crossings/ray.
2. **With human `relative_windings.json`:**
   - **Single-ray** relative counts (seed-free): does one ray agree with human Δw?
   - **Chain offsets:** rays whose (neural w − wind_a) disagrees with the chain consensus.
   - **Candidates:** strong chain-offset flags for triage.
3. **Optional:** attach a prior `case_catalog.json` of geometrically **CONFIRMED** cases.

## What it does NOT claim

**Confirmation of a seed error requires human chains and a 3D same-sheet geometric
test** (see `verify_cc.py` / the diagnosis note). Label-free and population
disagreement rates are **triage only**. Running without `--relative-windings`
emits population stats only.

## CLI

```bash
cd scrypt_vc
# Full Paris4 self-check (asserts known numbers)
python -m checker self-check

# Generic audit
python -m checker audit \
  --winding-inference /path/to/winding_inference \
  --relative-windings /path/to/relative_windings.json \
  --out ../out/winding_inference_audit.v1.json

# Population only (no human labels — no confirmation)
python -m checker audit --winding-inference /path/to/wi --no-human \
  --out ../out/audit_population_only.json
```

Schema: `winding_inference_audit.v1.schema.json`.

## Library

```python
from checker.audit import AuditPaths, run_audit
report = run_audit(AuditPaths(".../winding_inference", ".../relative_windings.json"))
```
