"""CLI for the Scrypt winding_inference seed-audit suite.

Examples (from scrypt_vc/):
  python -m checker audit \\
    --winding-inference ../data/spiral/winding_inference \\
    --relative-windings ../data/spiral/relative_windings.json \\
    --out ../out/winding_inference_audit.v1.json

  python -m checker self-check   # assert known Paris4 numbers

  python -m checker legacy --dr 6   # old single_ray + chain_offsets scripts

Confirmation of seed errors requires human chains + 3D same-sheet geometry.
Without --relative-windings the suite only emits seed/crossing population stats.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(ROOT)
OUT = os.path.join(REPO, "out")
CASES = os.path.join(REPO, "checker_cases")


def cmd_audit(args: argparse.Namespace) -> int:
    sys.path.insert(0, ROOT)
    from checker.audit import AuditPaths, run_audit, self_check_paris4

    wi = args.winding_inference or os.path.join(REPO, "data/spiral/winding_inference")
    rel = args.relative_windings
    if rel is None and not args.no_human:
        default_rel = os.path.join(REPO, "data/spiral/relative_windings.json")
        rel = default_rel if os.path.exists(default_rel) else None
    if args.no_human:
        rel = None
    catalog = args.confirmed_catalog
    if catalog is None:
        cand = os.path.join(CASES, "case_catalog.json")
        catalog = cand if os.path.exists(cand) else None

    paths = AuditPaths(
        winding_inference_dir=wi,
        relative_windings_json=rel,
        confirmed_catalog_json=catalog,
        scroll=args.scroll,
    )
    print(f"auditing {wi}", flush=True)
    if rel:
        print(f"  human chains: {rel}", flush=True)
    else:
        print("  NO human chains — population stats only; no confirmation claimed", flush=True)

    report = run_audit(paths, DR=args.dr, single_ray_DR=args.single_ray_dr)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    # Write slim + full
    slim = {k: report[k] for k in report if k != "single_ray_disagreements"}
    json.dump(slim, open(args.out, "w"), indent=1)
    print(f"wrote {args.out}", flush=True)
    if args.full_out:
        json.dump(report, open(args.full_out, "w"), indent=1)
        print(f"wrote full {args.full_out}", flush=True)
    # also population sidecar
    pop_path = args.population_out or os.path.join(
        os.path.dirname(os.path.abspath(args.out)), "winding_inference_population_stats.json"
    )
    json.dump(report["population"], open(pop_path, "w"), indent=1)
    print(f"wrote {pop_path}", flush=True)

    co = report.get("chain_offsets") or {}
    sr = report.get("single_ray") or {}
    print(
        f"summary: single_ray={sr.get('stats')} strong_candidates={co.get('n_strong_candidates')} "
        f"confirmed_attached={len(report.get('confirmed_cases') or [])}",
        flush=True,
    )
    print(
        "NOTE: candidates are NOT confirmed. Human chains + 3D same-sheet required for confirmation.",
        flush=True,
    )
    if args.self_check:
        fails = self_check_paris4(report)
        if fails:
            print("SELF-CHECK FAILED:", *fails, sep="\n  ", flush=True)
            return 1
        print("SELF-CHECK PASSED (Paris4 known numbers)", flush=True)
    return 0


def cmd_self_check(args: argparse.Namespace) -> int:
    args.winding_inference = args.winding_inference or os.path.join(REPO, "data/spiral/winding_inference")
    args.relative_windings = args.relative_windings or os.path.join(REPO, "data/spiral/relative_windings.json")
    args.no_human = False
    args.confirmed_catalog = os.path.join(CASES, "case_catalog.json")
    args.scroll = "PHercParis4"
    args.dr = 6.0
    args.single_ray_dr = 4.0
    args.out = os.path.join(OUT, "winding_inference_audit.v1.selfcheck.json")
    args.full_out = None
    args.population_out = os.path.join(OUT, "winding_inference_population_stats.selfcheck.json")
    args.self_check = True
    return cmd_audit(args)


def cmd_legacy(args: argparse.Namespace) -> int:
    env = os.environ.copy()
    env["PYTHONPATH"] = ROOT + os.pathsep + env.get("PYTHONPATH", "")
    os.makedirs(OUT, exist_ok=True)
    if not args.skip_single_ray:
        rc = subprocess.call([sys.executable, os.path.join(ROOT, "checker/single_ray.py")], cwd=ROOT, env=env)
        if rc:
            return rc
    env["CHECKER_DR"] = str(args.dr)
    env["CHECKER_OUT"] = os.path.join(
        OUT, f"checker_chain_offsets{'' if args.dr == 6.0 else f'_dr{int(args.dr)}'}.json"
    )
    return subprocess.call([sys.executable, os.path.join(ROOT, "checker/chain_offsets.py")], cwd=ROOT, env=env)


def main() -> int:
    ap = argparse.ArgumentParser(description="Scrypt winding_inference seed-audit CLI")
    sub = ap.add_subparsers(dest="cmd")

    a = sub.add_parser("audit", help="Run seed-audit suite → winding_inference_audit.v1 JSON")
    a.add_argument("--winding-inference", default=None)
    a.add_argument("--relative-windings", default=None, help="Human relative_windings.json (optional)")
    a.add_argument("--no-human", action="store_true", help="Force skip human chains")
    a.add_argument("--confirmed-catalog", default=None, help="Optional case_catalog.json to attach")
    a.add_argument("--dr", type=float, default=6.0)
    a.add_argument("--single-ray-dr", type=float, default=4.0)
    a.add_argument("--scroll", default="PHercParis4")
    a.add_argument("--out", default=os.path.join(OUT, "winding_inference_audit.v1.json"))
    a.add_argument("--full-out", default=None, help="Also write report including per-disagreement cases")
    a.add_argument("--population-out", default=None)
    a.add_argument("--self-check", action="store_true", help="Assert Paris4 known numbers after run")
    a.set_defaults(func=cmd_audit)

    s = sub.add_parser("self-check", help="Audit Paris4 defaults and assert known numbers")
    s.add_argument("--winding-inference", default=None)
    s.add_argument("--relative-windings", default=None)
    s.set_defaults(func=cmd_self_check)

    leg = sub.add_parser("legacy", help="Old single_ray + chain_offsets scripts")
    leg.add_argument("--dr", type=float, default=6.0)
    leg.add_argument("--skip-single-ray", action="store_true")
    leg.set_defaults(func=cmd_legacy)

    # default: audit with self-check-friendly paths if no subcommand
    args = ap.parse_args()
    if not args.cmd:
        # backward-compat: python -m checker --dr 6
        return cmd_self_check(argparse.Namespace(winding_inference=None, relative_windings=None))
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
