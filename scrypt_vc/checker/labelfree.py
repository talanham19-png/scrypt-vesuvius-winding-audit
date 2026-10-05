"""Item 4: does the checker work WITHOUT human labels?
Label-free rule (parameters fixed a priori, never tuned on labels):
  for ray r, take its crossings within WIN px of the region of interest; at each crossing c, every other ray passing
  within NB px gives an interpolated winding; per neighbour ray, vote v = median(round(w_r(c) - w_nb(c))).
  Flag r as 'wrong' if >= MINV neighbour rays vote and the majority vote is nonzero (r disagrees with most neighbours).
Scoring afterwards against the human-anchored reference from chain_offsets.py: a ray is 'off' if its rounded
u = w - wind_a differs from the chain consensus (consensus supported by >= 3 rays at >= 2 points)."""
import json, sys, os, collections
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from ray_field import Rays
NB, WIN, MINV, DR = float(os.environ.get("NB", 3)), float(os.environ.get("WIN", 30)), 2, 6.0
R = Rays(); rel = json.load(open("/workspace/vesuvius/data/spiral/relative_windings.json"))["collections"]
# --- human-anchored reference (same as chain_offsets.py), keep ALL scored rays
ref = {}
for cid, c in rel.items():
    pts = sorted([p for p in c["points"].values() if p.get("wind_a") is not None], key=lambda p: p["wind_a"])
    obs = []
    for k, p in enumerate(pts):
        for r, d, w in R.query(np.array(p["p"][::-1], float), DR): obs.append((k, r, w - p["wind_a"]))
    if not obs: continue
    ru = [int(np.rint(o[2])) for o in obs]; mode = collections.Counter(ru).most_common(1)[0][0]
    rays_mode = {o[1] for o, v in zip(obs, ru) if v == mode}; pts_mode = {o[0] for o, v in zip(obs, ru) if v == mode}
    if len(rays_mode) < 3 or len(pts_mode) < 2: continue
    by = collections.defaultdict(list)
    for o, v in zip(obs, ru): by[o[1]].append((v, o[2]))
    for r, vs in by.items():
        dev = abs(float(np.median([u for _, u in vs])) - mode)
        if 0.25 < dev < 0.75: continue   # strict reference: ambiguous (fractional) rays excluded
        ref[(cid, r)] = dict(off=dev >= 0.75, pts=[pts[o[0]]["p"][::-1] for o in obs if o[1] == r])
# --- label-free votes
def labelfree(r, centers):
    s, e = R.off[r], R.off[r + 1]; t = R.T[s:e]; P = R.O[r] + t[:, None] * R.S[r]; W = R.SW[r] + R.L[s:e]
    C = np.array(centers, float)
    keep = np.min(np.linalg.norm(P[:, None, :] - C[None], axis=2), axis=1) <= WIN
    votes = collections.defaultdict(list)
    for p, w in zip(P[keep], W[keep]):
        for nb, d, wn in R.query(p, NB):
            if nb != r: votes[nb].append(int(np.rint(w - wn)))
    vv = [int(np.median(v)) for v in votes.values()]
    if len(vv) < MINV: return None, len(vv)
    maj = collections.Counter(vv).most_common(1)[0][0]
    return maj != 0, len(vv)
if os.environ.get("COVERAGE_ONLY"):  # label-free: only how many rays get a verdict; labels not looked at
    n = sum(labelfree(r, info["pts"])[0] is not None for (cid, r), info in ref.items())
    print(f"NB={NB} WIN={WIN} verdict coverage {n}/{len(ref)} = {n/len(ref):.3f}"); sys.exit()
cm = collections.Counter(); rows = []
for (cid, r), info in ref.items():
    flag, nv = labelfree(r, info["pts"])
    if flag is None: cm["abstain"] += 1; cm["abstain_off" if info["off"] else "abstain_ok"] += 1; continue
    cm[("TP" if info["off"] else "FP") if flag else ("FN" if info["off"] else "TN")] += 1
    rows.append(dict(collection=cid, ray=int(r), off=bool(info["off"]), flagged=bool(flag), n_neighbour_rays=nv))
TP, FP, FN, TN = (cm[k] for k in ("TP", "FP", "FN", "TN"))
res = dict(params=dict(NB=NB, WIN=WIN, MINV=MINV), reference_rays=len(ref), reference_off=sum(v["off"] for v in ref.values()),
           confusion=dict(cm), precision=round(TP / max(TP + FP, 1), 3), recall=round(TP / max(TP + FN, 1), 3),
           flag_rate=round((TP + FP) / max(TP + FP + FN + TN, 1), 3), base_rate_off=round((TP + FN) / max(TP + FP + FN + TN, 1), 3))
# old spread rule at the same human points (point-level): flagged if spread>0.5; 'positive' if any ray there is off
print(json.dumps(res, indent=1))
json.dump(dict(result=res, rows=rows), open(f"/workspace/vesuvius/out/checker_labelfree_NB{NB:g}_WIN{WIN:g}.json", "w"), indent=1)
