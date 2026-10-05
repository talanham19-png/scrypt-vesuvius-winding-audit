"""Score a fitted Spiral checkpoint on held-out human relative-winding chains (never given to the fit).
Per chain (points in wind_a order): scan -> spiral transform, theta-unwrapped shifted radius u (as in
satisfaction_metrics._build_strip_spiral_context). Metrics:
  pair accuracy: |(u_j - u_i)/dr - (wind_a_j - wind_a_i)| < 0.5, for consecutive and for all pairs in a chain;
  official-style point satisfaction (satisfaction_metrics thresholds): target = round(median(u - wind_a*dr)/dr)*dr,
  point satisfied if |u - (target + wind_a*dr)| <= 0.45*dr AND the scan-space distance to that target sheet <= 6 voxels;
  chain fully satisfied if all its points are."""
import sys, os, json, math
import numpy as np, torch
SPIRAL = os.environ["SPIRAL_DIR"]; sys.path.insert(0, SPIRAL)
from pathlib import Path
from checkpoint_io import load_checkpoint_cpu
from flatten_spiral_checkpoint import _build_model, _checkpoint_config
from sample_spiral import get_theta_and_radii, unwrap_shifted_radii, radius_from_unwrapped_shifted
ckpt, test, umb, out = sys.argv[1:5]
dev = torch.device("cuda")
ck = load_checkpoint_cpu(ckpt); cfg = _checkpoint_config(ck)
model = _build_model(ck, cfg, Path(umb), dev); T = model.get_slice_to_spiral_transform(); dr = model.get_dr_per_winding().detach()
cols = json.load(open(test))["collections"]
res = dict(chains=0, points=0, adj_pairs=0, adj_correct=0, all_pairs=0, all_correct=0, pts_satisfied=0, chains_fully_satisfied=0, per_chain={})
with torch.no_grad():
    for cid, c in cols.items():
        pts = sorted([p for p in c["points"].values() if p.get("wind_a") is not None], key=lambda p: p["wind_a"])
        zyx = torch.tensor([p["p"][::-1] for p in pts], dtype=torch.float32, device=dev)
        w = torch.tensor([float(p["wind_a"]) for p in pts], device=dev)
        s = T(zyx); theta, _, sh = get_theta_and_radii(s[..., 1:], dr)
        u, adj = unwrap_shifted_radii(theta, sh, dr)
        W = (u / dr).cpu().numpy(); wa = w.cpu().numpy()
        n = len(pts); ac = sum(abs((W[i+1]-W[i]) - (wa[i+1]-wa[i])) < 0.5 for i in range(n-1))
        al = [(i, j) for i in range(n) for j in range(i+1, n)]; alc = sum(abs((W[j]-W[i]) - (wa[j]-wa[i])) < 0.5 for i, j in al)
        target = torch.round(torch.median(u - w * dr) / dr) * dr
        tsh = target + w * dr
        band = (u - tsh).abs() <= 0.45 * dr
        tr = radius_from_unwrapped_shifted(theta, tsh, adj, dr)
        tsp = torch.stack([s[..., 0], torch.sin(theta) * tr, torch.cos(theta) * tr], -1)
        dist = torch.linalg.norm(T.inv(tsp) - zyx, dim=-1)
        sat = band & (dist <= 6.0)
        res["chains"] += 1; res["points"] += n; res["adj_pairs"] += n-1; res["adj_correct"] += int(ac)
        res["all_pairs"] += len(al); res["all_correct"] += int(alc); res["pts_satisfied"] += int(sat.sum()); res["chains_fully_satisfied"] += int(sat.all())
        res["per_chain"][cid] = dict(n=n, z=round(pts[0]["p"][2]), adj_correct=int(ac), sat=int(sat.sum()), dW=[round(float(W[i+1]-W[i]), 2) for i in range(n-1)])
for k in ("adj", "all"): res[f"{k}_acc"] = round(res[f"{k}_correct"] / max(res[f"{k}_pairs"], 1), 4)
res["pts_satisfied_frac"] = round(res["pts_satisfied"] / max(res["points"], 1), 4)
res["chains_fully_satisfied_frac"] = round(res["chains_fully_satisfied"] / max(res["chains"], 1), 4)
res["dr_per_winding"] = float(dr)
json.dump(res, open(out, "w"), indent=1)
print(json.dumps({k: v for k, v in res.items() if k != "per_chain"}))
