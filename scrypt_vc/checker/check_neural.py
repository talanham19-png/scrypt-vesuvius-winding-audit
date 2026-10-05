"""Contradiction checker for the published neural winding-inference crossings.
Absolute neural winding of a crossing = seed_winding[ray] + crossing_level.
Checker (label-free): at a location, crossings from >= 2 different rays that lie within R voxels of each
other must carry the same absolute winding; disagreement = contradiction (at least one is wrong).
Confirmation (label-based): human relative-winding chains (consecutive points are exactly +1 apart) and
human absolute windings. A flagged location is CONFIRMED when the neural windings at two human points of
the same chain disagree with the human +1/+k relation and the checker flagged contradiction at >=1 of them."""
import json, sys, os, collections
import numpy as np
from scipy.spatial import cKDTree
sys.path.insert(0, os.path.dirname(__file__))
from load_wi import load
D = "/workspace/vesuvius/data/spiral"
R = float(os.environ.get("R", 2.0))
P, L, RAY, SEED = load()
W = SEED[RAY].astype(np.int32) + L.astype(np.int32)
rel = json.load(open(f"{D}/relative_windings.json"))["collections"]
absw = json.load(open(f"{D}/abs_winding.json"))["collections"]
hp = []  # (kind, cid, pid, zyx, wind_a)
for kind, cols in (("rel", rel), ("abs", absw)):
    for cid, c in cols.items():
        for pid, p in c["points"].items():
            if p.get("wind_a") is None: continue
            x, y, z = p["p"]; hp.append((kind, cid, int(pid), np.array([z, y, x]), float(p["wind_a"])))
H = np.array([h[3] for h in hp])
# restrict crossings to z-bands near human points to bound memory
zs = np.unique(np.round(H[:, 0]))
keep = np.zeros(len(P), bool)
order = np.argsort(P[:, 0]); Pz = P[order, 0]
for z in zs:
    a, b = np.searchsorted(Pz, [z - R - 1, z + R + 1]); keep[order[a:b]] = True
P, W, RAY = P[keep], W[keep], RAY[keep]
print("crossings near human z-planes:", len(P), flush=True)
tree = cKDTree(P)
info = []
for k, h in enumerate(hp):
    idx = tree.query_ball_point(h[3], R)
    if not idx: info.append(None); continue
    idx = np.array(idx)
    # one vote per ray (closest crossing of that ray)
    d = np.linalg.norm(P[idx] - h[3], axis=1)
    best = {}
    for i, dd in zip(idx, d):
        r = RAY[i]
        if r not in best or dd < best[r][1]: best[r] = (i, dd)
    ws = collections.Counter(int(W[i]) for i, _ in best.values())
    maj, nmaj = ws.most_common(1)[0]
    info.append(dict(n_rays=len(best), votes=dict(ws), maj=maj, frac=nmaj / len(best),
                     contradiction=len(ws) > 1 and sorted(ws.values())[-2] >= 2))
# confirmation against human chains
cases = []; stats = collections.Counter()
by = collections.defaultdict(list)
for k, h in enumerate(hp): by[(h[0], h[1])].append(k)
for (kind, cid), ks in by.items():
    if kind != "rel": continue
    ks = sorted(ks, key=lambda k: hp[k][4])
    for a, b in zip(ks[:-1], ks[1:]):
        ia, ib = info[a], info[b]
        if ia is None or ib is None: stats["pair_no_neural"] += 1; continue
        stats["pair_scored"] += 1
        dh = hp[b][4] - hp[a][4]; dn = ib["maj"] - ia["maj"]
        flagged = ia["contradiction"] or ib["contradiction"]
        stats["flagged_pairs"] += flagged
        if dn != dh:
            stats["pair_disagree"] += 1; stats["disagree_and_flagged"] += flagged
            cases.append(dict(collection=cid, name=rel[cid]["name"], pid_a=hp[a][2], pid_b=hp[b][2],
                              zyx_a=hp[a][3].tolist(), zyx_b=hp[b][3].tolist(), human_delta=dh, neural_delta=dn,
                              neural_a=ia, neural_b=ib, checker_flagged=bool(flagged)))
        elif flagged: stats["flagged_but_agree"] += 1
# absolute check
for (kind, cid), ks in by.items():
    if kind != "abs": continue
    for k in ks:
        if info[k] is None: stats["abs_no_neural"] += 1; continue
        stats["abs_scored"] += 1; stats["abs_agree"] += (info[k]["maj"] == hp[k][4])
pts_with = sum(i is not None for i in info); pts_contra = sum(1 for i in info if i and i["contradiction"])
print(json.dumps(dict(R=R, human_points=len(hp), points_with_neural=pts_with, points_flagged=pts_contra, **stats), indent=1))
json.dump(dict(stats=dict(stats), cases=cases), open("/workspace/vesuvius/out/checker_cases.json", "w"), indent=1, default=int)
print(len(cases), "disagreeing human pairs;", sum(c["checker_flagged"] for c in cases), "also flagged by the label-free checker")
