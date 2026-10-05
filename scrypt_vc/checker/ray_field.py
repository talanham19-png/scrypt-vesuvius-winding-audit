"""Interpolated neural winding coordinate at arbitrary points from the published crossing rays.
For a query point q, every ray whose line passes within DMAX voxels of q (and whose crossing span covers the
projection of q) gives w_ray(q) = seed + interpolated (fractional) level at the projected t.
Label-free checker: rays near the same point that disagree by > 0.5 winding  -> contradiction flag.
"""
import json, numpy as np
WI = "/workspace/vesuvius/data/spiral/winding_inference"
class Rays:
    def __init__(self):
        m = json.load(open(f"{WI}/manifest.json")); O, S, T, Lv, OFF, SW = [], [], [], [], [], []; base = 0
        for s in m["shards"]:
            r = f"{WI}/{s['name']}"
            O.append(np.load(f"{r}/ray_origin_zyx.npy")); S.append(np.load(f"{r}/ray_step_zyx.npy"))
            t = np.load(f"{r}/crossing_t.npy"); T.append(t); Lv.append(np.load(f"{r}/crossing_level.npy"))
            off = np.load(f"{r}/crossing_offsets.npy"); OFF.append(off[:-1] + base); base += off[-1]
            SW.append(np.load(f"{r}/seed_winding.npy"))
        self.O = np.concatenate(O).astype(np.float64); self.S = np.concatenate(S).astype(np.float64)
        self.T = np.concatenate(T); self.L = np.concatenate(Lv).astype(np.float64); self.SW = np.concatenate(SW).astype(np.float64)
        self.off = np.r_[np.concatenate(OFF), base]
        t0 = self.T[self.off[:-1]]; t1 = self.T[self.off[1:] - 1]
        self.A = self.O + t0[:, None] * self.S; self.B = self.O + t1[:, None] * self.S
        self.zlo = np.minimum(self.A[:, 0], self.B[:, 0]); self.zhi = np.maximum(self.A[:, 0], self.B[:, 0])
        o = np.argsort(self.zlo); self.zorder = o; self.zlo_sorted = self.zlo[o]
        self.maxspan = float((self.zhi - self.zlo).max())
    def query(self, q, dmax=6.0):
        q = np.asarray(q, float)
        a = np.searchsorted(self.zlo_sorted, q[0] - dmax - self.maxspan); b = np.searchsorted(self.zlo_sorted, q[0] + dmax)
        cand = self.zorder[a:b]; cand = cand[self.zhi[cand] >= q[0] - dmax]
        if not len(cand): return []
        t = ((q - self.O[cand]) * self.S[cand]).sum(1)
        foot = self.O[cand] + t[:, None] * self.S[cand]
        d = np.linalg.norm(foot - q, axis=1)
        out = []
        for ri, tt, dd in zip(cand[d <= dmax], t[d <= dmax], d[d <= dmax]):
            s, e = self.off[ri], self.off[ri + 1]
            ts = self.T[s:e]
            if tt < ts[0] or tt > ts[-1]: continue
            lv = np.interp(tt, ts, self.L[s:e])
            out.append((int(ri), float(dd), float(self.SW[ri] + lv)))
        return out
