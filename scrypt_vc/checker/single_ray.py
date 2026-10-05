"""Strict confirmation: a single neural ray passes within DR voxels of TWO points of one human relative chain.
Then the neural relative winding between them is read off that one ray (no cross-ray seed issues):
dn = interp_level(t_b) - interp_level(t_a). Human: dh = wind_a_b - wind_a_a (exact, chains step +1).
|dn - dh| >= 0.75 -> candidate neural error. Also reports whether the label-free spread checker flagged it."""
import json, sys, os, collections
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from ray_field import Rays
D = "/workspace/vesuvius/data/spiral"; DR = float(os.environ.get("DR", 4.0)); FLAGD = 12.0
R = Rays()
rel = json.load(open(f"{D}/relative_windings.json"))["collections"]
st = collections.Counter(); cases = []
spread_cache = {}
def spread(q):
    k = tuple(np.round(q, 2))
    if k not in spread_cache:
        ws = np.array([w for _, _, w in R.query(q, FLAGD)])
        spread_cache[k] = float(np.percentile(ws, 90) - np.percentile(ws, 10)) if len(ws) >= 2 else None
    return spread_cache[k]
for cid, c in rel.items():
    pts = sorted([p for p in c["points"].values() if p.get("wind_a") is not None], key=lambda p: p["wind_a"])
    Q = [np.array(p["p"][::-1], float) for p in pts]
    hits = [{r: w for r, d, w in R.query(q, DR)} for q in Q]
    seen = set()
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            common = set(hits[i]) & set(hits[j])
            for r in common:
                dh = pts[j]["wind_a"] - pts[i]["wind_a"]; dn = hits[j][r] - hits[i][r]
                st["ray_pairs"] += 1
                if abs(dn - dh) >= 0.75:
                    st["ray_pairs_bad"] += 1
                    key = (cid, r)
                    if key in seen: continue
                    seen.add(key)
                    sa, sb = spread(Q[i]), spread(Q[j])
                    cases.append(dict(collection=cid, name=c["name"], ray=int(r), i=i, j=j, p_i=pts[i]["p"], p_j=pts[j]["p"],
                                      human_delta=dh, neural_delta=round(dn, 3), spread_i=sa, spread_j=sb,
                                      checker_flagged=bool((sa or 0) > 0.5 or (sb or 0) > 0.5)))
print(json.dumps(dict(DR=DR, **st), indent=1))
print(len(cases), "distinct (chain, ray) neural-vs-human disagreements;", sum(c["checker_flagged"] for c in cases), "flagged by label-free checker")
json.dump(dict(stats=dict(st), cases=cases), open("/workspace/vesuvius/out/checker_single_ray.json", "w"), indent=1)
for c in cases[:40]: print(c["name"], c["ray"], "i,j", c["i"], c["j"], "human", c["human_delta"], "neural", c["neural_delta"], "flag", c["checker_flagged"], "z", round(c["p_i"][2]))
