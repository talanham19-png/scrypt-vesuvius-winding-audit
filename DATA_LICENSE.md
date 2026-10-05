# Derived scan data (not MIT)

The Vesuvius Challenge CT scans and many derived volumes (including the m7
surface predictions and `winding_inference` neural outputs we audit) are
released under **CC-BY-NC 4.0** by the Vesuvius Challenge / data owners.

Anything we produce that is built from those scans — for example:

- crops and max-projections in `checker_cases/`
- plane slices under `data/planes/`
- figures embedded in `NOTE_winding_diagnosis.*`
- GIFs of diagnosis cases
- auto-chain JSON that was fitted against scan-derived surfaces

— remains **CC-BY-NC 4.0** (attribution; non-commercial). It is intended for
the Progress Prize submission and related research use only.

**Code under `scrypt_vc/` is MIT** (see `LICENSE`). Do not move CC-BY-NC-derived
artifacts into a commercial Scrypt product.
