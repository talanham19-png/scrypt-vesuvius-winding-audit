"""Load the published neural winding-inference crossing store (spiral_datasets/PHercParis4/winding_inference)
into flat numpy arrays: per crossing position zyx (fit / reference coords), level, ray id."""
import json, os, numpy as np
WI = "/workspace/vesuvius/data/spiral/winding_inference"
def load(z_range=None):
    m = json.load(open(f"{WI}/manifest.json"))
    pos, lev, ray, seedw, rayo = [], [], [], [], 0
    for s in m["shards"]:
        r = f"{WI}/{s['name']}"
        o = np.load(f"{r}/ray_origin_zyx.npy"); st = np.load(f"{r}/ray_step_zyx.npy")
        t = np.load(f"{r}/crossing_t.npy"); l = np.load(f"{r}/crossing_level.npy"); off = np.load(f"{r}/crossing_offsets.npy")
        sw = np.load(f"{r}/seed_winding.npy")
        rid = np.repeat(np.arange(len(o)), np.diff(off))
        p = o[rid] + t[:, None] * st[rid]
        if z_range is not None:
            k = (p[:, 0] >= z_range[0]) & (p[:, 0] < z_range[1])
            p, l, rid = p[k], l[k], rid[k]
        pos.append(p.astype(np.float32)); lev.append(l.astype(np.int16)); ray.append(rid + rayo); seedw.append(sw); rayo += len(o)
    return np.concatenate(pos), np.concatenate(lev), np.concatenate(ray), np.concatenate(seedw)
