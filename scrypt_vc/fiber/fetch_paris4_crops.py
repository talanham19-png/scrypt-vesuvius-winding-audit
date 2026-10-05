import sys, os, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.fetch_crop import fetch_crop
S3 = "https://vesuvius-challenge-open-data.s3.us-east-1.amazonaws.com/PHercParis4/representations/predictions/fibers"
# Aug 2026-08-01 (GT-era) default; Sep 2026-09-15: set FIBER_RUN to
# 20260411134726-fibers-20260915212757-L1/PHercParis4-20260411134726-las-sd1-7ff0ce6c
# and OUT via FIBER_OUT. One 256^3 x3-channel crop ≈ 38 MB download.
RUN = os.environ.get("FIBER_RUN", "20260411134726-fibers-20260801084232-L1/PHercParis4-20260411134726-las-sd1-d74cca79")
OUT = os.environ.get("FIBER_OUT", "/workspace/vesuvius/data/paris4_fiber_crops")
cells = [(23, 5, 8), (24, 7, 5), (22, 9, 8), (20, 4, 8)]
os.makedirs(OUT, exist_ok=True)
for c in cells:
    box = [(c[i] * 256, c[i] * 256 + 256) for i in range(3)]
    dst = f"{OUT}/L3_{c[0]}_{c[1]}_{c[2]}.npz"
    if os.path.exists(dst): continue
    arrs = {ch: fetch_crop(f"{S3}/{RUN}_{ch}.ome.zarr/3", box) for ch in ("presence", "nx", "ny")}
    np.savez_compressed(dst, origin_L3=np.array([b[0] for b in box]), **arrs)
    print(dst, {k: (v.mean().round(1), (v > 0).mean().round(3)) for k, v in arrs.items()}, flush=True)
