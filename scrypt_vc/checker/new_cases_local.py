"""Verify NEW DR=8 candidates on already-downloaded m7 planes (S3 m7 zarr gone).
Same-sheet test: at each human chain point near the plane, take R.query feet;
if the foot lands on the same 2D sheet component as the human (unique label),
compare neural winding to human-anchored absolute (wind_a + chain_mode).
CONFIRMED: |dz|<=5, >=1 red hit disagrees by >=0.75, every other-ray hit agrees,
no merged multi-label components among used hits."""
import json, sys, os, collections
import numpy as np
from scipy import ndimage
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from checker.ray_field import Rays

PLANES = "/workspace/vesuvius/data/planes"; OUT = "/workspace/vesuvius/checker_cases"; DR = 8.0
PREV = {('col115', 3136), ('col172', 186900), ('wraps2', 134617), ('col22', 391270),
        ('col262', 194672), ('col262', 169422), ('col270', 223229),
        ('col58', 187628), ('col63', 272472), ('col88', 734549)}
plane_zs = sorted(int(f[4:-4]) for f in os.listdir(PLANES) if f.startswith("m7_z") and f.endswith(".npy"))
R = Rays(); rel = json.load(open("/workspace/vesuvius/data/spiral/relative_windings.json"))["collections"]
cases = json.load(open("/workspace/vesuvius/out/checker_chain_offsets_dr8.json"))["cases"]
strong = [c for c in cases if c["other_rays_same_points_agree_with_mode"] >= 1 and c["mode_support_rays"] >= 3]

def nearest_plane(z): return min(plane_zs, key=lambda pz: abs(pz - z))
cands = []
for c in strong:
    if (c["name"], c["ray"]) in PREV: continue
    clean = c["other_rays_same_points"] > 0 and c["other_rays_same_points_agree_with_mode"] == c["other_rays_same_points"]
    multi = len(c["chain_points"]) >= 2
    if not (clean or multi): continue
    pz = nearest_plane(c["z"]); dz = abs(pz - c["z"])
    if dz > 25: continue
    cands.append((dz, 0 if clean and multi else (1 if clean else 2), -len(c["chain_points"]), c["name"], c["ray"], c, pz))
cands.sort()
print(f"{len(cands)} candidates near downloaded planes")
H = 160; results = []
for n, (dz, _, _, _, _, c, pz) in enumerate(cands):
    plane = np.load(f"{PLANES}/m7_z{pz}.npy")
    x0, y0, z0 = [int(round(v)) for v in c["points"][0]]
    tag = f"case{10+n:02d}_{c['name']}_ray{c['ray']}_z{z0}"
    pts = sorted([p for p in rel[c["collection"]]["points"].values() if p.get("wind_a") is not None], key=lambda p: p["wind_a"])
    others = {r for q in c["points"] for r, d, w in R.query(np.array(q[::-1], float), DR) if r != c["ray"]}
    # figure
    y0c, x0c = max(0, y0 - H), max(0, x0 - H)
    y1c, x1c = min(plane.shape[0], y0 + H), min(plane.shape[1], x0 + H)
    img = plane[y0c:y1c, x0c:x1c]
    fig, axs = plt.subplots(1, 2, figsize=(15, 7.5))
    for ax, half in zip(axs, (H, 48)):
        ax.imshow(img, cmap="gray", extent=(x0c, x1c, y1c, y0c))
        ax.set_xlim(x0 - half, x0 + half); ax.set_ylim(y0 + half, y0 - half)
        fs = 7 if half == H else 9
        for p in pts:
            x, y, z = p["p"]
            if abs(z - pz) <= 5 and abs(x - x0) < half and abs(y - y0) < half:
                ax.plot(x, y, "o", mfc="none", mec="yellow", ms=8, mew=1.5)
                ax.text(x + 2, y - 2, f"H{p['wind_a'] + c['chain_mode']:.0f}", color="yellow", fontsize=fs, weight="bold")
        for r, col in [(o, "cyan") for o in sorted(others)] + [(c["ray"], "red")]:
            for q in c["points"]:
                qz = np.array(q[::-1], float)
                for rr, d, w in R.query(qz, DR):
                    if rr != r: continue
                    t = ((qz - R.O[r]) * R.S[r]).sum(); foot = R.O[r] + t * R.S[r]
                    px, py = float(foot[2]), float(foot[1])
                    if abs(px - x0) < half and abs(py - y0) < half:
                        ax.plot(px, py, "x", color=col, ms=7, mew=1.5)
                        ax.text(px + 2, py + 6, f"{w:.0f}", color=col, fontsize=fs)
    fig.suptitle(f"{tag}: ray {c['ray']} (red) off by {c['ray_offset_windings']:+d} (DR=8); plane z{pz} (|dz|={dz})\n"
                 f"x = query foot near human points; yellow = human; 2D same-sheet (S3 m7 zarr unavailable)", fontsize=9)
    plt.tight_layout(); plt.savefig(f"{OUT}/{tag}.png", dpi=110); plt.close()

    win = 120
    yw0, xw0 = max(0, y0 - win), max(0, x0 - win)
    yw1, xw1 = min(plane.shape[0], y0 + win), min(plane.shape[1], x0 + win)
    lab, _ = ndimage.label(plane[yw0:yw1, xw0:xw1] > 0, structure=np.ones((3, 3)))
    dist, idx = ndimage.distance_transform_edt(lab == 0, return_indices=True)
    def comp(y, x):
        i = np.round([y - yw0, x - xw0]).astype(int)
        if np.any(i < 0) or np.any(i >= lab.shape) or dist[tuple(i)] > 3: return 0
        return int(lab[tuple(idx[:, i[0], i[1]])])

    red_d, oth_d, used_merged = [], [], 0
    for p in pts:
        if abs(p["p"][2] - pz) > 5: continue
        kh = comp(p["p"][1], p["p"][0])
        if not kh: continue
        # collect all human labels on this component in-window
        labels_on = set()
        for p2 in pts:
            if abs(p2["p"][2] - pz) > 5: continue
            if comp(p2["p"][1], p2["p"][0]) == kh:
                labels_on.add(p2["wind_a"] + c["chain_mode"])
        if len(labels_on) != 1:
            used_merged += 1; continue
        Lab = next(iter(labels_on))
        qz = np.array(p["p"][::-1], float)
        for rr, d, w in R.query(qz, DR):
            t = ((qz - R.O[rr]) * R.S[rr]).sum(); foot = R.O[rr] + t * R.S[rr]
            if comp(foot[1], foot[2]) != kh: continue
            delta = float(w) - Lab
            if rr == c["ray"]: red_d.append(delta)
            else: oth_d.append(delta)

    ok = bool(red_d) and all(abs(d) >= 0.75 for d in red_d)
    others_ok = bool(oth_d) and all(abs(d) < 0.75 for d in oth_d)
    if ok and others_ok and used_merged == 0 and dz <= 5: verdict = "CONFIRMED"
    elif ok and dz <= 5: verdict = "probable"
    elif ok and others_ok and dz <= 25: verdict = "probable"
    else: verdict = "ambiguous"
    row = dict(case=10+n, tag=tag, name=c["name"], ray=int(c["ray"]), z=z0, plane_z=int(pz), dz=int(dz),
               red_vs_human=[round(d, 2) for d in red_d], other_rays_vs_human=[round(d, 2) for d in oth_d],
               merged_skips=used_merged, geometric_confirm=bool(ok and others_ok and used_merged == 0),
               verdict=verdict, ray_offset_windings=c["ray_offset_windings"],
               other_agree=f"{c['other_rays_same_points_agree_with_mode']}/{c['other_rays_same_points']}",
               note="2D same-sheet on downloaded plane; S3 m7 zarr unavailable for 3D boxes")
    results.append(row)
    print(verdict, tag, "dz", dz, "red", row["red_vs_human"], "other", row["other_rays_vs_human"], flush=True)

json.dump(dict(DR=8, plane_zs=plane_zs, n=len(results), results=results,
               confirmed=[r for r in results if r["verdict"]=="CONFIRMED"],
               probable=[r for r in results if r["verdict"]=="probable"],
               ambiguous=[r for r in results if r["verdict"]=="ambiguous"]),
          open(f"{OUT}/geometric_check_dr8_new.json", "w"), indent=1)
print("SUMMARY", dict(collections.Counter(r["verdict"] for r in results)))
# also list far candidates we could not verify for honesty
far = []
for c in strong:
    if (c["name"], c["ray"]) in PREV: continue
    clean = c["other_rays_same_points"] > 0 and c["other_rays_same_points_agree_with_mode"] == c["other_rays_same_points"]
    multi = len(c["chain_points"]) >= 2
    if not (clean or multi): continue
    pz = nearest_plane(c["z"]); dz = abs(pz - c["z"])
    if dz > 25:
        far.append(dict(name=c["name"], ray=c["ray"], z=c["z"], nearest_plane=pz, dz=dz,
                        off=c["ray_offset_windings"], agree=f"{c['other_rays_same_points_agree_with_mode']}/{c['other_rays_same_points']}"))
json.dump(far, open(f"{OUT}/unverified_far_from_planes.json", "w"), indent=1)
print(f"{len(far)} additional strong candidates skipped (no downloaded plane within 25 slices)")
