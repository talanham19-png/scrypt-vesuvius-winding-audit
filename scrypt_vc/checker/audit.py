"""winding_inference seed-audit evaluation suite (library).

Emits winding_inference_audit.v1 JSON: single-ray relative counts, chain-offset
candidates, population triage stats, and optional previously-confirmed cases.

IMPORTANT: Confirmation of seed errors requires human relative-winding chains
plus a 3D same-sheet geometric test. Label-free / population signals are triage
only — this suite does NOT claim confirmation without human labels.
"""
from __future__ import annotations

import collections
import json
import os
from dataclasses import dataclass
from typing import Any, Optional

import numpy as np

from .ray_field import Rays


@dataclass
class AuditPaths:
    winding_inference_dir: str
    relative_windings_json: Optional[str] = None
    confirmed_catalog_json: Optional[str] = None  # e.g. checker_cases/case_catalog.json
    scroll: str = "PHercParis4"


def _load_rays(wi_dir: str) -> Rays:
    # Rays class hardcodes WI; temporarily patch via env-free subclass
    class RaysAt(Rays):
        def __init__(self):
            m = json.load(open(f"{wi_dir}/manifest.json"))
            O, S, T, Lv, OFF, SW = [], [], [], [], [], []
            base = 0
            for s in m["shards"]:
                r = f"{wi_dir}/{s['name']}"
                O.append(np.load(f"{r}/ray_origin_zyx.npy"))
                S.append(np.load(f"{r}/ray_step_zyx.npy"))
                t = np.load(f"{r}/crossing_t.npy")
                T.append(t)
                Lv.append(np.load(f"{r}/crossing_level.npy"))
                off = np.load(f"{r}/crossing_offsets.npy")
                OFF.append(off[:-1] + base)
                base += off[-1]
                SW.append(np.load(f"{r}/seed_winding.npy"))
            self.O = np.concatenate(O).astype(np.float64)
            self.S = np.concatenate(S).astype(np.float64)
            self.T = np.concatenate(T)
            self.L = np.concatenate(Lv).astype(np.float64)
            self.SW = np.concatenate(SW).astype(np.float64)
            self.off = np.r_[np.concatenate(OFF), base]
            t0 = self.T[self.off[:-1]]
            t1 = self.T[self.off[1:] - 1]
            self.A = self.O + t0[:, None] * self.S
            self.B = self.O + t1[:, None] * self.S
            self.zlo = np.minimum(self.A[:, 0], self.B[:, 0])
            self.zhi = np.maximum(self.A[:, 0], self.B[:, 0])
            o = np.argsort(self.zlo)
            self.zorder = o
            self.zlo_sorted = self.zlo[o]
            self.maxspan = float((self.zhi - self.zlo).max())

    return RaysAt()


def single_ray_audit(R: Rays, rel: dict, DR: float = 4.0, flag_d: float = 12.0) -> dict:
    st = collections.Counter()
    cases = []
    spread_cache = {}

    def spread(q):
        k = tuple(np.round(q, 2))
        if k not in spread_cache:
            ws = np.array([w for _, _, w in R.query(q, flag_d)])
            spread_cache[k] = (
                float(np.percentile(ws, 90) - np.percentile(ws, 10)) if len(ws) >= 2 else None
            )
        return spread_cache[k]

    for cid, c in rel.items():
        pts = sorted(
            [p for p in c["points"].values() if p.get("wind_a") is not None],
            key=lambda p: p["wind_a"],
        )
        Q = [np.array(p["p"][::-1], float) for p in pts]
        hits = [{r: w for r, d, w in R.query(q, DR)} for q in Q]
        seen = set()
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                common = set(hits[i]) & set(hits[j])
                for r in common:
                    dh = pts[j]["wind_a"] - pts[i]["wind_a"]
                    dn = hits[j][r] - hits[i][r]
                    st["ray_pairs"] += 1
                    if abs(dn - dh) >= 0.75:
                        st["ray_pairs_bad"] += 1
                        key = (cid, r)
                        if key in seen:
                            continue
                        seen.add(key)
                        sa, sb = spread(Q[i]), spread(Q[j])
                        cases.append(
                            dict(
                                collection=cid,
                                name=c["name"],
                                ray=int(r),
                                i=i,
                                j=j,
                                p_i=pts[i]["p"],
                                p_j=pts[j]["p"],
                                human_delta=float(dh),
                                neural_delta=round(float(dn), 3),
                                spread_i=sa,
                                spread_j=sb,
                                checker_flagged=bool((sa or 0) > 0.5 or (sb or 0) > 0.5),
                            )
                        )
    return dict(DR=DR, stats=dict(st), cases=cases)


def chain_offsets_audit(R: Rays, rel: dict, DR: float = 6.0, minsup: int = 3) -> dict:
    st = collections.Counter()
    cases = []
    for cid, c in rel.items():
        pts = sorted(
            [p for p in c["points"].values() if p.get("wind_a") is not None],
            key=lambda p: p["wind_a"],
        )
        obs = []
        for k, p in enumerate(pts):
            q = np.array(p["p"][::-1], float)
            for r, d, w in R.query(q, DR):
                obs.append((k, r, d, w, w - p["wind_a"]))
        if not obs:
            continue
        st["chains_with_obs"] += 1
        U = np.array([o[4] for o in obs])
        ru = np.rint(U).astype(int)
        cnt = collections.Counter(ru)
        mode, nmode = cnt.most_common(1)[0]
        rays_mode = {o[1] for o, v in zip(obs, ru) if v == mode}
        pts_mode = {o[0] for o, v in zip(obs, ru) if v == mode}
        st["obs"] += len(obs)
        st["obs_at_mode"] += int((ru == mode).sum())
        if len(rays_mode) < minsup or len(pts_mode) < 2:
            continue
        st["chains_scored"] += 1
        byray = collections.defaultdict(list)
        for o, v in zip(obs, ru):
            byray[o[1]].append((o, v))
        for r, lst in byray.items():
            vals = collections.Counter(v for _, v in lst)
            v, nv = vals.most_common(1)[0]
            st["rays_scored"] += 1
            if v != mode and abs(lst[0][0][4] - mode) >= 0.75:
                st["rays_off"] += 1
                ks = sorted({o[0] for o, _ in lst})
                others = [(o, vv) for o, vv in zip(obs, ru) if o[0] in ks and o[1] != r]
                n_other_mode = int(sum(int(vv == mode) for _, vv in others))
                cases.append(
                    dict(
                        collection=cid,
                        name=c["name"],
                        ray=int(r),
                        chain_points=ks,
                        z=round(pts[ks[0]]["p"][2]),
                        ray_offset_windings=int(v - mode),
                        u_ray=round(float(np.median([o[4] for o, _ in lst])), 2),
                        chain_mode=int(mode),
                        mode_support_rays=len(rays_mode),
                        mode_support_points=len(pts_mode),
                        other_rays_same_points_agree_with_mode=n_other_mode,
                        other_rays_same_points=len(others),
                        points=[pts[k]["p"] for k in ks],
                    )
                )
    strong = [
        c
        for c in cases
        if c["other_rays_same_points_agree_with_mode"] >= 1 and c["mode_support_rays"] >= minsup
    ]
    return dict(DR=DR, minsup=minsup, stats=dict(st), cases=cases, strong_candidates=strong)


def population_stats(R: Rays, rel: Optional[dict], DR: float = 6.0) -> dict:
    n_cross = R.off[1:] - R.off[:-1]
    frac = np.abs(R.SW - np.rint(R.SW))
    out: dict[str, Any] = dict(
        n_rays=int(len(R.O)),
        n_crossings=int(len(R.T)),
        seed_range=[float(R.SW.min()), float(R.SW.max())],
        seeds_all_integer=bool((frac < 1e-6).all()),
        seed_frac_median=float(np.median(frac)),
        crossings_per_ray=dict(
            median=int(np.median(n_cross)),
            p10=int(np.percentile(n_cross, 10)),
            p90=int(np.percentile(n_cross, 90)),
            max=int(n_cross.max()),
        ),
    )
    if not rel:
        out["multi_ray_human_points"] = None
        out["note"] = (
            "No human relative_windings provided. Population multi-ray rates and "
            "confirmation are unavailable. Do NOT treat seed consistency as confirmed."
        )
        return out

    agree = disagree = 0
    span_hist: collections.Counter = collections.Counter()
    for c in rel.values():
        for p in c["points"].values():
            if p.get("wind_a") is None:
                continue
            hits = R.query(np.array(p["p"][::-1], float), DR)
            if len(hits) < 2:
                continue
            rw = np.array([int(round(w)) for _, _, w in hits])
            if len(set(rw.tolist())) == 1:
                agree += 1
            else:
                disagree += 1
                span_hist[int(rw.max() - rw.min())] += 1
    n = agree + disagree
    out["multi_ray_human_points"] = dict(
        DR=DR,
        n_points_with_ge2_rays=n,
        agree_rounded=agree,
        disagree_rounded=disagree,
        disagree_rate=(disagree / n) if n else None,
        span_hist={int(k): int(v) for k, v in sorted(span_hist.items())},
        note=(
            "Triage rate only at human chain points. Confirmation requires chain "
            "consensus + 3D same-sheet geometric test. Not a confirmed-error rate."
        ),
    )
    return out


def load_confirmed(catalog_path: Optional[str]) -> list:
    if not catalog_path or not os.path.exists(catalog_path):
        return []
    d = json.load(open(catalog_path))
    cases = d.get("cases", d if isinstance(d, list) else [])
    return [c for c in cases if str(c.get("verdict", "")).upper() == "CONFIRMED"]


def run_audit(paths: AuditPaths, DR: float = 6.0, single_ray_DR: float = 4.0) -> dict:
    R = _load_rays(paths.winding_inference_dir)
    rel = None
    if paths.relative_windings_json and os.path.exists(paths.relative_windings_json):
        rel = json.load(open(paths.relative_windings_json))["collections"]

    pop = population_stats(R, rel, DR=DR)
    report: dict[str, Any] = {
        "version": "winding_inference_audit.v1",
        "inputs": {
            "winding_inference_dir": os.path.abspath(paths.winding_inference_dir),
            "relative_windings_json": (
                os.path.abspath(paths.relative_windings_json) if paths.relative_windings_json else None
            ),
            "DR": DR,
            "single_ray_DR": single_ray_DR,
            "scroll": paths.scroll,
        },
        "population": pop,
        "single_ray": None,
        "chain_offsets": None,
        "candidates": [],
        "confirmed_cases": load_confirmed(paths.confirmed_catalog_json),
        "notes": (
            "Human labels are required for single-ray / chain-offset / confirmation. "
            "Population multi-ray disagreement without a 3D same-sheet test is triage only. "
            "This suite does not claim confirmation without human chains."
        ),
    }

    if rel is None:
        report["notes"] += " Ran without relative_windings: only seed/crossing population stats emitted."
        return report

    sr = single_ray_audit(R, rel, DR=single_ray_DR)
    co = chain_offsets_audit(R, rel, DR=DR)
    report["single_ray"] = {"DR": sr["DR"], "stats": sr["stats"], "n_disagreement_cases": len(sr["cases"])}
    report["chain_offsets"] = {
        "DR": co["DR"],
        "stats": co["stats"],
        "n_off": len(co["cases"]),
        "n_strong_candidates": len(co["strong_candidates"]),
    }
    # Candidate flags (strong only) — not confirmed
    report["candidates"] = [
        dict(
            name=c["name"],
            ray=c["ray"],
            z=c["z"],
            ray_offset_windings=c["ray_offset_windings"],
            mode_support_rays=c["mode_support_rays"],
            other_agree=f"{c['other_rays_same_points_agree_with_mode']}/{c['other_rays_same_points']}",
            verdict="candidate_needs_3d_confirm",
        )
        for c in co["strong_candidates"]
    ]
    report["single_ray_disagreements"] = sr["cases"]
    return report


def self_check_paris4(report: dict) -> list[str]:
    """Return list of failure messages; empty means pass. Hard-coded to known Paris4 numbers."""
    fails = []
    pop = report.get("population") or {}
    if pop.get("n_rays") != 1147551:
        fails.append(f"n_rays={pop.get('n_rays')} expected 1147551")
    if pop.get("n_crossings") != 22706484:
        fails.append(f"n_crossings={pop.get('n_crossings')} expected 22706484")
    if not pop.get("seeds_all_integer"):
        fails.append("expected all seeds integer")
    sr = (report.get("single_ray") or {}).get("stats") or {}
    if sr.get("ray_pairs") != 94:
        fails.append(f"single_ray pairs={sr.get('ray_pairs')} expected 94")
    if sr.get("ray_pairs_bad") != 1:
        fails.append(f"single_ray bad={sr.get('ray_pairs_bad')} expected 1")
    co = (report.get("chain_offsets") or {}).get("stats") or {}
    if report.get("inputs", {}).get("DR") == 6.0:
        if co.get("rays_scored") != 238:
            fails.append(f"DR6 rays_scored={co.get('rays_scored')} expected 238")
        if co.get("rays_off") != 30:
            fails.append(f"DR6 rays_off={co.get('rays_off')} expected 30")
        if report.get("chain_offsets", {}).get("n_strong_candidates") != 10:
            fails.append(
                f"DR6 strong={report.get('chain_offsets', {}).get('n_strong_candidates')} expected 10"
            )
    mp = pop.get("multi_ray_human_points") or {}
    if mp.get("n_points_with_ge2_rays") != 104:
        fails.append(f"multi-ray n={mp.get('n_points_with_ge2_rays')} expected 104")
    if mp.get("disagree_rounded") != 52:
        fails.append(f"multi-ray disagree={mp.get('disagree_rounded')} expected 52")
    return fails
