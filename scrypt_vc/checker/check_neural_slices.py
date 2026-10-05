"""Label-free contradiction checker for the neural winding-inference crossings, on our 8 z-slices.
Neural crossings within |dz|<=DZ of a slice are snapped (<=2 px) to sheet chunks of our skeleton
(winding/auto_winding2d.py). Absolute neural winding w = seed_winding + crossing_level.
Checker flags (no human labels used):
  C1 'chunk conflict' : a chunk receives different w from >= 2 rays each (same sheet piece, two windings)
  C2 'adjacency conflict' : chunks a->b linked by our radial ray edge (b is the next sheet outward, support >= 10
       rays, agreement >= 0.9) whose neural majority windings differ by != 1
Confirmation: human relative chains (consecutive points exactly +1). A human pair whose neural Delta != human
Delta is a confirmed neural error; it is checker-confirmed if the chunks involved carry a C1/C2 flag."""
import json, math, pickle, sys, os, collections
import numpy as np
sys.path.insert(0, os.path.dirname(__file__)); sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "winding"))
from load_wi import load
from eval_slices import human_chains
from auto_winding2d import s_value
DZ = 1.0
ZS = [15334, 8750, 16920, 8450, 11432, 15876, 8879, 11714]
P, L, RAY, SEED = load()
W = SEED[RAY].astype(np.int32) + L.astype(np.int32)
out_cases, stats = [], collections.Counter()
for z in ZS:
    sol = pickle.load(open(f"/workspace/vesuvius/out/winding/sol_z{z}.pkl", "rb"))
    lab = sol["lab"]; y0, x0 = sol["offset"]; Hh, Ww = lab.shape
    k = np.abs(P[:, 0] - z) <= DZ
    p, w, r = P[k], W[k], RAY[k]
    iy = np.rint(p[:, 1] - y0).astype(int); ix = np.rint(p[:, 2] - x0).astype(int)
    lab_of = np.zeros(len(p), np.int64)
    best = np.full(len(p), 99.0)
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            yy, xx = iy + dy, ix + dx; ok = (yy >= 0) & (yy < Hh) & (xx >= 0) & (xx < Ww)
            Lc = np.zeros(len(p), np.int64); Lc[ok] = lab[yy[ok], xx[ok]]
            d = dy * dy + dx * dx; upd = (Lc > 0) & (d < best)
            lab_of[upd] = Lc[upd]; best[upd] = d
    votes = collections.defaultdict(lambda: collections.defaultdict(set))  # chunk -> w -> rays
    for Lc, wc, rc in zip(lab_of, w, r):
        if Lc: votes[Lc][wc].add(rc)
    maj = {}; c1 = set()
    for Lc, d in votes.items():
        cnt = {wc: len(rs) for wc, rs in d.items()}
        maj[Lc] = max(cnt, key=cnt.get)
        if len([v for v in cnt.values() if v >= 2]) >= 2: c1.add(Lc)
    # C2 on strong radial edges
    c2 = set(); c2_edges = []
    for (a, b), c in sol["ray_edges"].items():
        back = sol["ray_edges"].get((b, a), 0)
        if c >= 10 and c >= 0.9 * (c + back) and a in maj and b in maj and maj[b] - maj[a] != 1:
            c2.add(a); c2.add(b); c2_edges.append((int(a), int(b), int(c), int(maj[a]), int(maj[b])))
    stats[f"z{z}_crossings"] = int(k.sum()); stats[f"z{z}_chunks_with_votes"] = len(maj)
    stats[f"z{z}_C1"] = len(c1); stats[f"z{z}_C2_edges"] = len(c2_edges)
    stats["strong_edges_checked"] += sum(1 for (a, b), c in sol["ray_edges"].items() if c >= 10 and a in maj and b in maj)
    for cid, name, pts in human_chains(z):
        S = [s_value(sol, pp[0][1], pp[0][0], snap=3) for pp in pts]
        for i in range(len(pts) - 1):
            a, b = S[i], S[i + 1]
            if a is None or b is None or a[3] not in maj or b[3] not in maj: stats["pairs_unscored"] += 1; continue
            stats["pairs_scored"] += 1
            dh = pts[i + 1][1] - pts[i][1]; dn = maj[b[3]] - maj[a[3]]
            flag = bool({a[3], b[3]} & (c1 | c2))
            stats["pairs_flagged"] += flag
            if dn != dh:
                stats["pairs_disagree"] += 1; stats["disagree_flagged"] += flag
                out_cases.append(dict(z=z, collection=cid, name=name, i=i, xy_a=pts[i][0][:2], xy_b=pts[i + 1][0][:2],
                    human_delta=dh, neural_delta=int(dn), chunk_a=int(a[3]), chunk_b=int(b[3]),
                    votes_a={int(k_): len(v) for k_, v in votes[a[3]].items()}, votes_b={int(k_): len(v) for k_, v in votes[b[3]].items()},
                    flags=[f for f, s in (("C1", c1), ("C2", c2)) if a[3] in s or b[3] in s], checker_flagged=flag))
            elif flag: stats["flagged_agree"] += 1
print(json.dumps(dict(stats), indent=1))
print(len(out_cases), "human-confirmed neural disagreements;", sum(c["checker_flagged"] for c in out_cases), "flagged by checker")
json.dump(dict(stats=dict(stats), cases=out_cases), open("/workspace/vesuvius/out/checker_slices.json", "w"), indent=1, default=float)
