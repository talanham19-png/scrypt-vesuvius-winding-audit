"""Figures for chain-offset checker cases: m7 surface prediction (fit coords, level 0) around the case point,
human chain points labelled with human-anchored absolute winding (wind_a + chain consensus offset),
the offending ray's crossings (red, labelled seed+level) and other rays near the same chain points (cyan)."""
import json, sys, os
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from common.fetch_crop import fetch_crop
from checker.ray_field import Rays
M7 = "https://vesuvius-challenge-open-data.s3.us-east-1.amazonaws.com/PHercParis4/representations/predictions/surfaces/20260411134726-surface-20260413222639-surface-m7-L2-th0.2.zarr/0"
OUT = "/workspace/vesuvius/checker_cases"; H = 160; DZ = 6
R = Rays(); rel = json.load(open("/workspace/vesuvius/data/spiral/relative_windings.json"))["collections"]
cases = json.load(open("/workspace/vesuvius/out/checker_chain_offsets.json"))["cases"]
sel = [c for c in cases if c["other_rays_same_points_agree_with_mode"] >= 1]
def crossings(r, zc):
    s, e = R.off[r], R.off[r + 1]; t = R.T[s:e]; p = R.O[r] + t[:, None] * R.S[r]; w = R.SW[r] + R.L[s:e]
    k = np.abs(p[:, 0] - zc) <= DZ; return p[k], w[k]
for n, c in enumerate(sel):
    x0, y0, z0 = [int(round(v)) for v in c["points"][0]]
    tag = f"case{n:02d}_{c['name']}_ray{c['ray']}_z{z0}"
    npz = f"{OUT}/{tag}.npz"
    if os.path.exists(npz): crop = np.load(npz)["m7"]
    else:
        crop = fetch_crop(M7, ((z0 - 2, z0 + 3), (y0 - H, y0 + H), (x0 - H, x0 + H))); np.savez_compressed(npz, m7=crop)
    img = crop.max(0)
    pts = [p for p in rel[c["collection"]]["points"].values() if p.get("wind_a") is not None]
    others = set()
    for q in c["points"]:
        for r, d, w in R.query(np.array(q[::-1], float), 6.0):
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
                 f"(chain mode supported by {c['mode_support_rays']} rays; {c['other_rays_same_points_agree_with_mode']}/{c['other_rays_same_points']} other rays at same point agree)\n"
                 f"yellow = human chain points, label = wind_a + consensus offset; cyan = other rays; m7 surface pred, z{z0-2}..{z0+2} max-proj", fontsize=9)
    plt.tight_layout(); plt.savefig(f"{OUT}/{tag}.png", dpi=110); plt.close()
    print(tag, flush=True)
