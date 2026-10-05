# Contradiction-checker cases: published neural winding vs human relative-winding chains (PHercParis4)

Pipeline (`scrypt_vc/checker/`): `ray_field.py` (interpolated neural winding = seed_winding + crossing level),
`chain_offsets.py` (per human chain, u = neural w − wind_a must be constant; rays whose rounded u differs from the
chain consensus are candidates), `case_figures.py` (PNG), `verify_cc.py` (3D sheet-component check → `geometric_check.json`).
One-command: `python -m checker` from `scrypt_vc/` (see `run_checker.sh`).

**Confirmation standard:** in a 17×96×96 m7 box, label 26-connected sheet components. On components that hold
exactly one human-anchored label, red crossings differ by ≥0.75 winding and every other-ray hit agrees (|Δ|<0.75).

Figures: m7 surface prediction (fit coords); yellow = human chain points labelled wind_a + chain consensus offset;
red = offending neural ray; cyan = other neural rays. `*_box3d.npz` = 17×96×96 m7 box for the 3D test.
`case02_wrong_direction.gif` ≈ 30 s animation of the wrong-direction ray.

## DR=6 primary set (original 10 candidates)

| case | chain | ray | z | red vs human | other rays vs human | verdict |
|---|---|---|---|---|---|---|
| 01 | col172 | 186900 | 8879 | −1, −1 | 0, 0, 0 | CONFIRMED |
| 02 | wraps2 | 134617 | 16920 | +4 … +18 (level order opposite sheet order) | 0 (×12) | CONFIRMED |
| 03 | col22 | 391270 | 15080 | −1, −1, −1 | 0 (×4) | CONFIRMED |
| 07 | col58 | 187628 | 9185 | −1 | 0, 0, 0 | CONFIRMED |
| 08 | col63 | 272472 | 9407 | +1, +1 | 0, 0, 0 | CONFIRMED |
| 00 | col115 | 3136 | 12862 | −2, −2 | 0, −1 | probable |
| 06 | col270 | 223229 | 12529 | −1 | 0, +1 | probable |
| 04 | col262 | 194672 | 11825 | +1, +1, +2 | mixed | ambiguous |
| 05 | col262 | 169422 | 11825 | +1 … +3 | mixed | ambiguous |
| 09 | col88 | 734549 | 8750 | +1 | 0, 0 | ambiguous (merged sheet) |

## DR=8 expansion (Oct 5; same 3D standard; see `geometric_check_dr8_new.json`)

21 new strong candidates after excluding the DR=6 ten → **10 CONFIRMED, 6 probable, 5 ambiguous**.

| case | chain | ray | z | red vs human | other | verdict |
|---|---|---|---|---|---|---|
| 10 | col147 | 7036 | 8980 | −1 (×6) | 0 (×6) | CONFIRMED |
| 11 | col22 | 356196 | 15092 | −1 (×3) | 0 | CONFIRMED |
| 12 | col289 | 8031 | 10195 | −1 | 0, 0 | CONFIRMED |
| 13 | col68 | 474925 | 7674 | +1 | 0 (×3) | CONFIRMED |
| 14 | col70 | 214071 | 9185 | −1, −1 | 0 (×4) | CONFIRMED |
| 18 | col126 | 144441 | 11228 | −1 (×4) | 0 (×5) | CONFIRMED |
| 22 | col67 | 482054 | 9357 | +1 | 0, 0 | CONFIRMED |
| 23 | col67 | 737710 | 9376 | +1 | 0 | CONFIRMED |
| 27 | col43 | 68143 | 11714 | −1 | 0, 0 | CONFIRMED |
| 29 | col89 | 440658 | 8750 | −1, −1 | 0, 0 | CONFIRMED |

Probable (DR=8): 16/col17, 17/col63, 20/col160, 24/col166, 25/col221, 26/col118.
Ambiguous (DR=8): 15/col147, 19/col173, 21/col67, 28/col60, 30/col89.

**Totals:** 15 CONFIRMED, 8 probable, 8 ambiguous.

Caveats: human chains assumed correct; neural seeds come from a fit that already used the human constraints
(circularity — see the note). Single-ray relative counts agree with humans in 93/94 cases: errors are in
absolute seed windings across rays, not in per-ray crossing detection.
