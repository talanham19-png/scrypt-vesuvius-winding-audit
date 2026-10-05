"""Cross-ray consistency anchored on human chains.
For every point k of a human relative chain and every neural ray r passing within DR voxels:
    u = w_r(point) - wind_a(point)
If the neural output is consistent with the human chain, u is the same constant for all (point, ray) in that chain
(it is the chain's unknown absolute offset). A ray whose rounded u differs from the chain's consensus (supported
by >= MINSUP other rays at >= 2 other chain points) carries a wrong absolute winding (seed_winding) at that place.
The label-free checker independently flags points where nearby rays disagree (spread > 0.5)."""
import json, sys, os, collections
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from ray_field import Rays
D = "/workspace/vesuvius/data/spiral"; DR = float(os.environ.get("CHECKER_DR", os.environ.get("DR", 6.0))); MINSUP = 3
R = Rays()
rel = json.load(open(f"{D}/relative_windings.json"))["collections"]
st = collections.Counter(); cases = []
for cid, c in rel.items():
    pts = sorted([p for p in c["points"].values() if p.get("wind_a") is not None], key=lambda p: p["wind_a"])
    obs = []  # (k, ray, d, w, u)
    for k, p in enumerate(pts):
        q = np.array(p["p"][::-1], float)
        for r, d, w in R.query(q, DR):
            obs.append((k, r, d, w, w - p["wind_a"]))
    if not obs: continue
    st["chains_with_obs"] += 1
    U = np.array([o[4] for o in obs]); ru = np.rint(U).astype(int)
    cnt = collections.Counter(ru); mode, nmode = cnt.most_common(1)[0]
    rays_mode = {o[1] for o, v in zip(obs, ru) if v == mode}; pts_mode = {o[0] for o, v in zip(obs, ru) if v == mode}
    st["obs"] += len(obs); st["obs_at_mode"] += int((ru == mode).sum())
    if len(rays_mode) < MINSUP or len(pts_mode) < 2: continue
    st["chains_scored"] += 1
    byray = collections.defaultdict(list)
    for o, v in zip(obs, ru): byray[o[1]].append((o, v))
    for r, lst in byray.items():
        vals = collections.Counter(v for _, v in lst)
        v, nv = vals.most_common(1)[0]
        st["rays_scored"] += 1
        if v != mode and abs(lst[0][0][4] - mode) >= 0.75:
            st["rays_off"] += 1
            ks = sorted({o[0] for o, _ in lst})
            # independent check: do OTHER rays at the same chain points agree with the mode?
            others = [(o, vv) for o, vv in zip(obs, ru) if o[0] in ks and o[1] != r]
            n_other_mode = int(sum(int(vv == mode) for _, vv in others))
            cases.append(dict(collection=cid, name=c["name"], ray=int(r), chain_points=ks, z=round(pts[ks[0]]["p"][2]),
                              ray_offset_windings=int(v - mode), u_ray=round(float(np.median([o[4] for o, _ in lst])), 2),
                              chain_mode=int(mode), mode_support_rays=len(rays_mode), mode_support_points=len(pts_mode),
                              other_rays_same_points_agree_with_mode=n_other_mode, other_rays_same_points=len(others),
                              points=[pts[k]["p"] for k in ks]))
print(json.dumps(dict(DR=DR, **st), indent=1))
strong = [c for c in cases if c["other_rays_same_points_agree_with_mode"] >= 1 and c["mode_support_rays"] >= MINSUP]
print(len(cases), "rays off vs chain consensus;", len(strong), "where another ray at the SAME chain point agrees with the human-anchored consensus")
out_path = os.environ.get("CHECKER_OUT", "/workspace/vesuvius/out/checker_chain_offsets.json")
json.dump(dict(DR=DR, stats=dict(st), cases=cases), open(out_path, "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else list(o))
print("wrote", out_path)
for c in strong[:30]: print(c["name"], "ray", c["ray"], "z", c["z"], "pts", c["chain_points"], "off", c["ray_offset_windings"], "mode sup", c["mode_support_rays"], "same-pt agree", c["other_rays_same_points_agree_with_mode"], "/", c["other_rays_same_points"])
