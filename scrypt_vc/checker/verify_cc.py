"""Objective geometric check per case: in a 3D m7 surface-prediction box (+-8 z, +-48 yx) around the case point,
label 26-connected sheet components. For the offending ray's crossings and for human chain points, find the component
(nearest sheet voxel within 3 px). Confirmed if some red crossing shares a component with exactly one human point
(component holds no human points of different label) and red label != human-anchored label."""
import json, sys, os, numpy as np
from scipy import ndimage
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from common.fetch_crop import fetch_crop
from checker.ray_field import Rays
M7 = "https://vesuvius-challenge-open-data.s3.us-east-1.amazonaws.com/PHercParis4/representations/predictions/surfaces/20260411134726-surface-20260413222639-surface-m7-L2-th0.2.zarr/0"
R = Rays(); rel = json.load(open("/workspace/vesuvius/data/spiral/relative_windings.json"))["collections"]
cs = [c for c in json.load(open("/workspace/vesuvius/out/checker_chain_offsets.json"))["cases"] if c["other_rays_same_points_agree_with_mode"] >= 1]
HZ, HY = 8, 48; res = []
for n, c in enumerate(cs):
    x0, y0, z0 = [int(round(v)) for v in c["points"][0]]
    box = ((z0 - HZ, z0 + HZ + 1), (y0 - HY, y0 + HY), (x0 - HY, x0 + HY))
    f = f"/workspace/vesuvius/checker_cases/case{n:02d}_box3d.npz"
    if os.path.exists(f): m = np.load(f)["m7"]
    else: m = fetch_crop(M7, box); np.savez_compressed(f, m7=m)
    lab, _ = ndimage.label(m > 0, structure=np.ones((3, 3, 3)))
    dist, idx = ndimage.distance_transform_edt(lab == 0, return_indices=True)
    def comp(zyx):
        i = np.round(np.array(zyx) - [box[0][0], box[1][0], box[2][0]]).astype(int)
        if np.any(i < 0) or np.any(i >= lab.shape) or dist[tuple(i)] > 3: return 0
        return int(lab[tuple(idx[:, i[0], i[1], i[2]])])
    hum = {}
    for p in rel[c["collection"]]["points"].values():
        if p.get("wind_a") is None: continue
        k = comp(p["p"][::-1])
        if k: hum.setdefault(k, set()).add(p["wind_a"] + c["chain_mode"])
    def ray_hits(r):
        s, e = R.off[r], R.off[r + 1]; out = []
        for t, l in zip(R.T[s:e], R.L[s:e]):
            k = comp(R.O[r] + t * R.S[r])
            if k in hum and len(hum[k]) == 1: out.append((float(R.SW[r] + l), next(iter(hum[k]))))
        return out
    red = ray_hits(c["ray"])
    others = {r for q in c["points"] for r, d, w in R.query(np.array(q[::-1], float), 6.0) if r != c["ray"]}
    oth = [h for r in others for h in ray_hits(r)]
    rd = [w - h for w, h in red]; od = [w - h for w, h in oth]
    ok = bool(rd) and all(abs(d) >= 0.75 for d in rd)
    ambiguous_comps = sum(len(v) > 1 for v in hum.values())
    r_ = dict(case=n, name=c["name"], ray=c["ray"], z=z0, red_vs_human=[round(d, 1) for d in rd], other_rays_vs_human=[round(d, 1) for d in od],
              merged_components_with_multiple_human_labels=ambiguous_comps, geometric_confirm=ok and all(abs(d) < 0.75 for d in od) if od else ok)
    res.append(r_); print(r_, flush=True)
json.dump(res, open("/workspace/vesuvius/checker_cases/geometric_check.json", "w"), indent=1)
