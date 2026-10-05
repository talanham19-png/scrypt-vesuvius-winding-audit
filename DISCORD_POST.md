# Discord announcement (draft) — Scrypt

**Suggested channel:** spiral / Annotation / progress-prize (pick the one your team uses for tooling shares).

---

Hi all — **Scrypt** here with a Progress Prize package on published PHercParis4 `winding_inference`.

**What we found.** Along a single ray, crossing counts match human relative-winding chains **93/94** times. The failures we could confirm are in **per-ray seed windings**, not in the crossing detector. With human chains + a 3D same-sheet check we have **15 confirmed** seed-error cases (probable/ambiguous kept separate). One case has level order running the wrong way along the sheet (GIF in the repo).

**Honest negative.** We also tried feeding our own automatic relative-winding chains into a *reduced* local spiral fit: they **hurt** held-out adjacent-pair accuracy vs no relative chains. We are **not** pitching auto chains as an improvement — the lead is the diagnosis.

**Tooling.** CPU seed-audit CLI: `python -m checker audit|self-check` — emits population stats, single-ray checks, and chain-offset **candidates**. Confirmation still needs human labels + 3D geometry; we don’t claim label-free confirmation.

Repo: **REPO_URL**

Note + figures + case catalog are in the tree. If Annotation / spiral folks would find a seed-consistency report useful on new `winding_inference` exports, we’d love feedback on the schema (`winding_inference_audit.v1`).

— Scrypt

---

**Notes for Salvador:** replace `REPO_URL` after the GitHub repo is public. Keep tone as-is (no auto-chain pitch, no hype).
