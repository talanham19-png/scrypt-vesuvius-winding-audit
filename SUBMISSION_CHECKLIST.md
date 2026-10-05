# Progress Prize packaging checklist (Scrypt)

**Deadline:** Saturday, October 31, 2026, 11:59pm Pacific.

## Lead package
1. Technical note: `NOTE_winding_diagnosis.pdf` (+ `.md` / figures in `checker_cases/`)
2. Case 02 GIF: `checker_cases/case02_wrong_direction.gif`
3. Code (MIT): `scrypt_vc/` — especially `python -m checker`
4. Licenses: `LICENSE` + `DATA_LICENSE.md`
5. Audit demos: `out/winding_inference_audit.v1.json`, `out/demos/audit_report_demo.md`

## Reproduce
```bash
cd scrypt_vc && python -m checker self-check
```
(Requires local `winding_inference/` + `relative_windings.json`.)

## Pitch framing
- Lead with **diagnosis of published `winding_inference` seed errors** (15 confirmed) + honest negative auto-chain fit.
- **Do not** pitch auto relative-winding chains as an improvement.
- Niche: seed consistency **upstream of the fit** (≠ spiralcheck / windcheck).

## Submission steps
- [ ] Public GitHub repo (this tree)
- [ ] Discord post (`DISCORD_POST.md`)
- [ ] Progress Prize Google Form (`GOOGLE_FORM_DRAFT.md`)
