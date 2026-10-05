"""Score neural winding vs human relative chains with the interpolated ray field, and run the label-free
ray-disagreement checker at every human point."""
import json, sys, os, collections
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from ray_field import Rays
D = "/workspace/vesuvius/data/spiral"
DMAX = float(os.environ.get("DMAX", 6.0)); SPREAD = 0.5
R = Rays()
rel = json.load(open(f"{D}/relative_windings.json"))["collections"]
res = {}
for cid, c in rel.items():
    pts = sorted([p for p in c["points"].values() if p.get("wind_a") is not None], key=lambda p: p["wind_a"])
    rows = []
    for p in pts:
        x, y, z = p["p"]; q = R.query([z, y, x], DMAX)
        if len(q) < 2: rows.append(None); continue
        ws = np.array([w for _, _, w in q]); dd = np.array([d for _, d, _ in q])
        med = float(np.median(ws)); spread = float(np.percentile(ws, 90) - np.percentile(ws, 10))
        rows.append(dict(p=p["p"], wind_a=p["wind_a"], n=len(q), w=med, spread=spread, flag=spread > SPREAD,
                         rays=[(int(r), round(d, 2), round(w, 3)) for r, d, w in q][:40]))
    res[cid] = dict(name=c["name"], rows=rows)
st = collections.Counter(); cases = []
for cid, v in res.items():
    rows = v["rows"]
    for i in range(len(rows) - 1):
        a, b = rows[i], rows[i + 1]
        if a is None or b is None: st["pairs_unscored"] += 1; continue
        st["pairs_scored"] += 1
        dh = b["wind_a"] - a["wind_a"]; dn = b["w"] - a["w"]
        bad = abs(dn - dh) > 0.5; flag = a["flag"] or b["flag"]
        st["disagree"] += bad; st["flagged"] += flag; st["disagree_flagged"] += bad and flag; st["agree_flagged"] += (not bad) and flag
        if bad: cases.append(dict(collection=cid, name=v["name"], i=i, a=a, b=b, human_delta=dh, neural_delta=round(dn, 3), checker_flagged=bool(flag)))
pts = [r for v in res.values() for r in v["rows"]]
st["points"] = len(pts); st["points_scored"] = sum(r is not None for r in pts); st["points_flagged"] = sum(1 for r in pts if r and r["flag"])
print(json.dumps(dict(DMAX=DMAX, **st), indent=1))
json.dump(dict(stats=dict(st), cases=cases), open("/workspace/vesuvius/out/checker_chains.json", "w"), indent=1)
print(len(cases), "disagreements;", sum(c["checker_flagged"] for c in cases), "flagged by label-free checker")
