"""Reviewer follow-ups 1-3: label disjointness, dev-only threshold choice, per-slice coverage, hybrid."""
import json, math, sys, os, collections
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from eval_slices import human_chains, baseline_count, DATA
from auto_winding2d import preprocess
DEV = 15334
ZS = [15334, 8750, 16920, 8450, 11432, 15876, 8879, 11714]
E = json.load(open(f"{DATA}/../out/winding/eval.json"))["rows"]
# ---- 2. disjointness of labels
chains = {z: human_chains(z) for z in ZS}
ids = {z: {c[0] for c in chains[z]} for z in ZS}
pts = {z: {tuple(np.round(p[0], 3)) for c in chains[z] for p in c[2]} for z in ZS}
ho_ids = set().union(*[ids[z] for z in ZS if z != DEV]); ho_pts = set().union(*[pts[z] for z in ZS if z != DEV])
dis = dict(dev_collections=len(ids[DEV]), heldout_collections=len(ho_ids), shared_collections=len(ids[DEV] & ho_ids),
           dev_points=len(pts[DEV]), heldout_points=len(ho_pts), shared_points=len(pts[DEV] & ho_pts),
           pairwise_slice_collection_overlap=sum(len(ids[a] & ids[b]) for i, a in enumerate(ZS) for b in ZS[i+1:]))
# also: any held-out collection within +-50 slices of dev? (same annotator session nearby)
dz = sorted(abs(z - DEV) for z in ZS if z != DEV); dis["min_dz_heldout_to_dev"] = dz[0]
# ---- all human pairs (incl. those the graph could not score) with baseline
allpairs = []  # z, cid, i, j, dh, consec, dist, base
for z in ZS:
    mask = preprocess(np.load(f"{DATA}/planes/m7_z{z}.npy"))
    for cid, name, P in chains[z]:
        for i in range(len(P)):
            for j in range(i + 1, len(P)):
                (xa, ya, _), wa = P[i]; (xb, yb, _), wb = P[j]
                allpairs.append((z, cid, i, j, wb - wa, j == i + 1, math.hypot(xb - xa, yb - ya), baseline_count(mask, ya, xa, yb, xb)))
    del mask
G = {(r[0], r[1], r[2], r[3]): r for r in E}  # graph-scored rows: dh, dp, consec, conf, dist
def gpred(p, tconf):
    r = G.get(p[:4])
    if r is None or r[7] < tconf: return None
    return r[5]
# ---- 1. dev-only threshold choice for "skip uncertain"
# criterion fixed a priori: smallest threshold reaching >=97% on dev adjacent pairs; else max dev accuracy
cands = [0.0, 0.9, 0.95, 0.98, 0.99, 0.995, 1.0]
dev_adj = [p for p in allpairs if p[0] == DEV and p[5]]
dev_tab = []
for t in cands:
    s = [(gpred(p, t), p[4]) for p in dev_adj]; s = [(a, b) for a, b in s if a is not None]
    dev_tab.append((t, len(s) / len(dev_adj), np.mean([a == b for a, b in s]) if s else 0))
ok = [r for r in dev_tab if r[2] >= 0.97]
T = ok[0][0] if ok else max(dev_tab, key=lambda r: r[2])[0]
def cov_table(t, consec):
    rows = {}
    for z in ZS + ["heldout_all"]:
        sel = [p for p in allpairs if p[5] == consec and (p[0] == z if z != "heldout_all" else p[0] != DEV)]
        sc = [(gpred(p, t), p[4]) for p in sel]; kept = [(a, b) for a, b in sc if a is not None]
        rows[str(z)] = dict(pairs=len(sel), scored=len(kept), coverage=round(len(kept) / max(len(sel), 1), 3),
                            skipped=round(1 - len(kept) / max(len(sel), 1), 3),
                            acc=round(float(np.mean([a == b for a, b in kept])), 3) if kept else None)
    return rows
# point-level coverage: share of human points that snapped to a chunk with conf >= t (from graph rows availability)
# ---- 3. hybrid: graph for dist < D, baseline for dist >= D; D chosen on dev (all dev pairs) only
Ds = [25, 50, 75, 100, 150, 200, 300, 400, 600, 1e9]
def hybrid(p, D, t=0.0):
    if p[6] < D:
        g = gpred(p, t)
        return g if g is not None else p[7] * np.sign(p[4])  # fall back to baseline if graph cannot score
    return p[7] * np.sign(p[4])  # baseline gives |delta|; sign from chain order (outward) - see note
dev_all = [p for p in allpairs if p[0] == DEV]
dtab = [(D, float(np.mean([hybrid(p, D) == p[4] for p in dev_all]))) for D in Ds]
Dbest = max(dtab, key=lambda r: (r[1], -r[0]))[0]
ho = [p for p in allpairs if p[0] != DEV]
def acc(sel, f): return dict(n=len(sel), acc=round(float(np.mean([f(p) == p[4] for p in sel])), 3) if sel else None)
near = [p for p in ho if p[6] < Dbest]; far = [p for p in ho if p[6] >= Dbest]
hyb = dict(D_chosen_on_dev=Dbest, dev_table=dtab,
           heldout=dict(near_hybrid=acc(near, lambda p: hybrid(p, Dbest)), far_hybrid=acc(far, lambda p: hybrid(p, Dbest)),
                        overall_hybrid=acc(ho, lambda p: hybrid(p, Dbest)),
                        overall_graph_with_baseline_fallback=acc(ho, lambda p: hybrid(p, 1e9)),
                        overall_baseline_only=acc(ho, lambda p: p[7] * np.sign(p[4])),
                        near_graph_scored_frac=round(np.mean([gpred(p, 0) is not None for p in near]), 3) if near else None,
                        adjacent_only_hybrid=acc([p for p in ho if p[5]], lambda p: hybrid(p, Dbest)),
                        nonadjacent_hybrid=acc([p for p in ho if not p[5]], lambda p: hybrid(p, Dbest))))
out = dict(disjointness=dis, skip_uncertain=dict(rule="smallest conf threshold with >=97% dev adjacent accuracy (else max dev acc)",
           dev_table=dev_tab, threshold_chosen_on_dev=T, adjacent=cov_table(T, True), nonadjacent=cov_table(T, False),
           no_skip_adjacent=cov_table(0.0, True)), hybrid=hyb)
print(json.dumps(out, indent=1, default=float))
json.dump(out, open(f"{DATA}/../out/winding/rescore.json", "w"), indent=1, default=float)
