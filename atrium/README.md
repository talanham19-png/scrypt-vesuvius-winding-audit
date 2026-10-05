# Atrium reduced spiral-fit helpers

Small CPU/GPU helper scripts used for the **negative result** in the diagnosis note
(auto relative-winding chains hurt a reduced local fit). Not required to run the
seed-audit checker.

- `run_fit.py` — launch reduced fit (needs spiral-fitting env + GPU machine)
- `eval_heldout.py` — score held-out human adjacent pairs from a checkpoint
- `subset_wi.py` — subset winding_inference to a z-range

Full data and Torch installers are intentionally omitted from this release.
