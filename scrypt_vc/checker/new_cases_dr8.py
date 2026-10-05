"""Select NEW strong candidates from DR=8 search (not in the original DR=6 ten),
preferring clean same-point agreement, then run figures + 3D geometric verify."""
import json, sys, os, copy
import numpy as np
from scipy import ndimage
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from common.fetch_crop import fetch_crop
from checker.ray_field import Rays
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

PREV = {(c['name'] if 'name' in c else None) for c in []}  # by (collection, ray)
# Original DR=6 ten from README / geometric_check
PREV_KEYS = {
    ('col115', 3136), ('col172', 186900), ('wraps2', 134617), ('col22', 391270),
    ('col262', 194672), ('col262', 169422), ('col270', 223229),
    ('col58', 187628), ('col63', 272472), ('col88', 734549),
}
M7 = "https://vesuvius-challenge-open-data.s3.us-east-1.amazonaws.com/PHercParis4/nxt/predictions/surfaces/20260411134726-surface-20260413222639-surface-m7-L2-th0.2.zarr/0"
OUT = "/workspace/vesuvius/checker_cases"; H, DZ, HZ, HY = 160, 6, 8, 48
R = Rays(); rel = json.load(open("/workspace/vesuvius/data/spiral/relative_windings.json"))["collections"]
d = json.load(open("/workspace/vesuvius/out/checker_chain_offsets_dr8.json"))
strong = [c for c in d["cases"] if c["other_rays_same_points_agree_with_mode"] >= 1 and c["mode_support_rays"] >= 3]
# Prefer: all other rays agree, or multi-point; exclude PREV
cands = []
for c in strong:
    key = (c["name"], c["ray"])
    if key in PREV_KEYS: continue
    clean = c["other_rays_same_points"] > 0 and c["other_rays_same_points_agree_with_mode"] == c["other_rays_same_points"]
    multi = len(c["chain_points"]) >= 2
    if clean or multi:
        cands.append((0 if clean and multi else (1 if clean else 2), -len(c["chain_points"]), -c["mode_support_rays"], c))
cands.sort(key=lambda t: t[:3])
sel = [t[3] for t in cands]
print(f"{len(sel)} new candidates after filter (of {len(strong)} strong, {len(PREV_KEYS)} previous)")
for i, c in enumerate(sel):
    print(i, c["name"], c["ray"], "z", c["z"], "off", c["ray_offset_windings"], "pts", c["chain_points"],
          "agree", f"{c['other_rays_same_points_agree_with_mode']}/{c['other_rays_same_points']}", "mode", c["mode_support_rays"])

def crossings(r, zc):
    s, e = R.off[r], R.off[r + 1]; t = R.T[s:e]; p = R.O[r] + t[:, None] * R.S[r]; w = R.SW[r] + R.L[s:e]
    k = np.abs(p[:, 0] - zc) <= DZ; return p[k], w[k]

geo = []
for n, c in enumerate(sel):
    x0, y0, z0 = [int(round(v)) for v in c["points"][0]]
    tag = f"case{10+n:02d}_{c['name']}_ray{c['ray']}_z{z0}"
    npz = f"{OUT}/{tag}.npz"
    if os.path.exists(npz): crop = np.load(npz)["m7"]
    else:
        crop = fetch_crop(M7, ((z0 - 2, z0 + 3), (y0 - H, y0 + H), (x0 - H, x0 + H))); np.savez_compressed(npz, m7=crop)
    img = crop.max(0)
    pts = [p for p in rel[c["collection"]]["points"].values() if p.get("wind_a") is not None]
    others = set()
    for q in c["points"]:
        for r, d, w in R.query(np.array(q[::-1], float), 8.0):
            if r != c["ray"]: others.add(r)
    fig, axs = plt.subplots(1, 2, figsize=(15, 7.5))
    for ax, half in zip(axs, (H, 48)):
        ax.imshow(img, cmap="gray", extent=(x0 - H, x0 + H, y0 + H, y0 - H))
        ax.set_xlim(x0 - half, x0 + half); ax.set_ylim(y0 + half, y0 - half)
        fs = 7 if half == H else 9
        for p in pts:
            x, y, z = p["p"]
            if abs(z - z0) <= 3 and abs(x - x0) < half and abs(y - y0) < half:
                ax.plot(x, y, "o", mfc="none", mec="yellow", ms=8, mew=1.5)
                ax.text(x + 2, y - 2, f"H{p['wind_a'] + c['chain_mode']:.0f}", color="yellow", fontsize=fs, weight="bold")
        for r, col in [(o, "cyan") for o in sorted(others)] + [(c["ray"], "red")]:
            P, W = crossings(r, z0)
            if not len(P): continue
            ax.plot(P[:, 2], P[:, 1], "-", color=col, lw=0.6, alpha=0.7)
            for (pz, py, px), w in zip(P, W):
                if abs(px - x0) < half and abs(py - y0) < half:
                    ax.plot(px, py, "x", color=col, ms=6, mew=1.5)
                    if half != H or col == "red": ax.text(px + 2, py + 6, f"{w:.0f}", color=col, fontsize=fs)
    fig.suptitle(f"{tag}: ray {c['ray']} (red) off by {c['ray_offset_windings']:+d} vs human-anchored consensus "
                 f"(mode {c['mode_support_rays']} rays; {c['other_rays_same_points_agree_with_mode']}/{c['other_rays_same_points']} other rays agree)\n"
                 f"yellow = human; cyan = other rays; m7 z{z0-2}..{z0+2} max-proj; DR=8 search", fontsize=9)
    plt.tight_layout(); plt.savefig(f"{OUT}/{tag}.png", dpi=110); plt.close()
    # 3D geometric check
    box = ((z0 - HZ, z0 + HZ + 1), (y0 - HY, y0 + HY), (x0 - HY, x0 + HY))
    f3 = f"{OUT}/{tag}_box3d.npz"
    if os.path.exists(f3): m = np.load(f3)["m7"]
    else: m = fetch_crop(M7, box); np.savez_compressed(f3, m7=m)
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
    oth = [h for r in others for h in ray_hits(r)]
    rd = [w - h for w, h in red]; od = [w - h for w, h in oth]
    ok = bool(rd) and all(abs(d) >= 0.75 for d in rd)
    geo_ok = ok and (all(abs(d) < 0.75 for d in od) if od else True)
    # probable: red wrong, but some other also wrong
    probable = ok and od and any(abs(d) >= 0.75 for d in od) and not geo_ok
    ambiguous = (not ok) or (sum(len(v) > 1 for v in hum.values()) > 0 and not geo_ok)
    if geo_ok: verdict = "CONFIRMED"
    elif probable: verdict = "probable"
    else: verdict = "ambiguous"
    row = dict(case=10+n, tag=tag, name=c["name"], ray=c["ray"], z=z0, collection=c["collection"],
               red_vs_human=[round(d, 1) for d in rd], other_rays_vs_human=[round(d, 1) for d in od],
               merged_components_with_multiple_human_labels=sum(len(v) > 1 for v in hum.values()),
               geometric_confirm=geo_ok, verdict=verdict,
               ray_offset_windings=c["ray_offset_windings"], mode_support_rays=c["mode_support_rays"],
               other_agree=f"{c['other_rays_same_points_agree_with_mode']}/{c['other_rays_same_points']}")
    geo.append(row); print(row["verdict"], tag, "red", row["red_vs_human"], "other", row["other_rays_vs_human"], flush=True)

json.dump(dict(DR=8, n_candidates=len(sel), results=geo,
               confirmed=[g for g in geo if g["verdict"]=="CONFIRMED"],
               probable=[g for g in geo if g["verdict"]=="probable"],
               ambiguous=[g for g in geo if g["verdict"]=="ambiguous"]),
          open(f"{OUT}/geometric_check_dr8_new.json", "w"), indent=1)
print("SUMMARY confirmed", sum(g["verdict"]=="CONFIRMED" for g in geo),
      "probable", sum(g["verdict"]=="probable" for g in geo),
      "ambiguous", sum(g["verdict"]=="ambiguous" for g in geo))
