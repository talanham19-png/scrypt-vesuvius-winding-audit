"""Keeper follow-ups round 2.
1. Straight-line baseline on exactly the 424 accepted held-out adjacent pairs (graph conf >= 0.98, threshold from dev).
   Baseline sign: from the umbilicus (outward = +), NOT from the human label. Also |delta| only.
   Diagnosis of pairs lost without skipping (unsnapped points) and baseline on them.
2. Leave-one-slice-out (8 folds) cutoff for hybrid (graph if dist < D else baseline); bands; per-fold cutoffs."""
import json, math, sys, os, pickle, collections
import numpy as np
from scipy import ndimage as ndi
sys.path.insert(0, os.path.dirname(__file__))
from eval_slices import human_chains, baseline_count, DATA
from auto_winding2d import preprocess, umbilicus_yx, s_value
DEV = 15334; T = 0.98
ZS = [15334, 8750, 16920, 8450, 11432, 15876, 8879, 11714]
E = json.load(open(f"{DATA}/../out/winding/eval.json"))["rows"]
G = {(r[0], r[1], r[2], r[3]): r for r in E}
pairs = []; lost_pts = collections.Counter(); lost_detail = []
for z in ZS:
    plane = np.load(f"{DATA}/planes/m7_z{z}.npy"); raw = plane > 127; mask = preprocess(plane); del plane
    cy, cx = umbilicus_yx(f"{DATA}/spiral/umbilicus.json", z)
    sol = pickle.load(open(f"{DATA}/../out/winding/sol_z{z}.pkl", "rb"))
    oy, ox = sol["offset"]; skel = sol["lab"] > 0
    draw = ndi.distance_transform_edt(~raw); dmask = ndi.distance_transform_edt(~mask)
    for cid, name, P in human_chains(z):
        snapped = [s_value(sol, p[0][1], p[0][0]) is not None for p in P]
        why = []
        for k, ((x, y, _), w) in enumerate(P):
            if snapped[k]: why.append(None); continue
            iy, ix = int(round(y)), int(round(x))
            if draw[iy, ix] > 4: r = "no m7 sheet within 4 px (point off the prediction)"
            elif dmask[iy, ix] > 4: r = "m7 sheet removed by thick-blob/border-ring filter"
            else: r = "sheet present but no skeleton chunk within 4 px (junction removal / skeleton pruning)"
            why.append(r)
        for i in range(len(P)):
            for j in range(i + 1, len(P)):
                (xa, ya, _), wa = P[i]; (xb, yb, _), wb = P[j]
                b = baseline_count(mask, ya, xa, yb, xb)
                sgn = 1 if math.hypot(yb - cy, xb - cx) >= math.hypot(ya - cy, xa - cx) else -1
                r = G.get((z, cid, i, j))
                pairs.append(dict(z=z, cid=cid, adj=j == i + 1, dh=wb - wa, dist=math.hypot(xb - xa, yb - ya),
                                  base=b * sgn, base_abs=b, g=None if r is None else r[5], conf=None if r is None else r[7]))
                if j == i + 1 and r is None and z != DEV:
                    for k in (i, j):
                        if why[k]: lost_detail.append((z, cid, k, why[k]))
    del raw, mask, sol, skel, draw, dmask
    print("slice", z, "done", flush=True)
ho = [p for p in pairs if p["z"] != DEV]
def acc(sel, key):
    return dict(n=len(sel), acc=round(float(np.mean([p[key] == p["dh"] for p in sel])), 4) if sel else None)
def acc_abs(sel): return round(float(np.mean([p["base_abs"] == abs(p["dh"]) for p in sel])), 4) if sel else None
# ---- 1
acc_adj = [p for p in ho if p["adj"] and p["g"] is not None and p["conf"] >= T]
unsc = [p for p in ho if p["adj"] and p["g"] is None]
r1 = dict(accepted_pairs=len(acc_adj), graph=acc(acc_adj, "g"), baseline_signed_by_umbilicus=acc(acc_adj, "base"),
          baseline_abs_only=acc_abs(acc_adj),
          both_right=sum(p["g"] == p["dh"] and p["base"] == p["dh"] for p in acc_adj),
          graph_only_right=sum(p["g"] == p["dh"] and p["base"] != p["dh"] for p in acc_adj),
          base_only_right=sum(p["g"] != p["dh"] and p["base"] == p["dh"] for p in acc_adj),
          both_wrong=sum(p["g"] != p["dh"] and p["base"] != p["dh"] for p in acc_adj),
          all_heldout_adjacent=dict(n=sum(p["adj"] for p in ho), baseline=acc([p for p in ho if p["adj"]], "base")),
          noskip_unscored_pairs=len(unsc), baseline_on_unscored=acc(unsc, "base"), baseline_abs_on_unscored=acc_abs(unsc),
          lost_point_reasons=dict(collections.Counter(d[3] for d in set(lost_detail))),
          lost_points_unique=len(set(lost_detail)))
# ---- 2. LOSO cutoff
Ds = [0, 25, 50, 100, 150, 200, 300, 400, 600, 800, 1200, 1e9]
def hyb(p, D):
    if p["dist"] < D and p["g"] is not None: return p["g"]
    return p["base"]
folds = {}
for z in ZS:
    tr = [p for p in pairs if p["z"] != z]
    tab = [(D, float(np.mean([hyb(p, D) == p["dh"] for p in tr]))) for D in Ds]
    Dz = max(tab, key=lambda t: (t[1], -t[0]))[0]   # ties -> smaller cutoff
    folds[z] = Dz
for p in pairs: p["h"] = hyb(p, folds[p["z"]])
bands = [("<50", 0, 50), ("50-200", 50, 200), ("200-800", 200, 800), (">800", 800, 1e12), ("overall", 0, 1e12)]
r2 = dict(per_fold_cutoff={str(z): (None if D == 1e9 else D) for z, D in folds.items()}, bands={})
for nm, lo, hi in bands:
    for tag, sel0 in (("all", pairs), ("adjacent", [p for p in pairs if p["adj"]])):
        sel = [p for p in sel0 if lo <= p["dist"] < hi]
        gs = [p for p in sel if p["g"] is not None]
        r2["bands"][f"{nm}|{tag}"] = dict(n=len(sel), hybrid=acc(sel, "h")["acc"], baseline=acc(sel, "base")["acc"],
            A_on_scored=acc(gs, "g")["acc"], A_coverage=round(len(gs) / max(len(sel), 1), 4),
            A_with_baseline_fallback=round(float(np.mean([(p["g"] if p["g"] is not None else p["base"]) == p["dh"] for p in sel])), 4) if sel else None)
r2["per_fold_scores"] = {str(z): dict(n=len(s := [p for p in pairs if p["z"] == z]), hybrid=acc(s, "h")["acc"], baseline=acc(s, "base")["acc"]) for z in ZS}
out = dict(item1=r1, item2=r2, lost_detail=sorted(set(lost_detail)))
json.dump(out, open(f"{DATA}/../out/winding/rescore2.json", "w"), indent=1, default=float)
print(json.dumps(dict(item1=r1, item2=r2), indent=1, default=float))
