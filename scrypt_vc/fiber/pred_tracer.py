"""Conservative fully-automatic fiber tracer on published lasagna fiber predictions
(presence + nx/ny direction, uint8 OME-Zarr). Works at any pyramid level; prototype uses L3 (19.2 um).

Stop-when-uncertain rules (each logged as the trace's end reason):
  weak        presence at the re-centred point < stop_presence
  incoherent  local direction coherence (3x3x3 second-moment of predicted axes) < min_coherence
  turn        predicted axis turns > max_turn deg vs the running direction
  fork        a second presence ridge comparable to ours appears in the cross-section (possible
              crossing/merge of fibers) -> abstain rather than guess
  collision   runs into an already accepted trace
  border
"""
import math
import numpy as np
from scipy import ndimage as ndi

def decode_dir(nx, ny):
    a = (nx.astype(np.float32) - 128) / 127; b = (ny.astype(np.float32) - 128) / 127
    c = np.sqrt(np.clip(1 - a * a - b * b, 0, None))
    d = np.stack([c, b, a], -1)
    return d / (np.linalg.norm(d, axis=-1, keepdims=True) + 1e-6)

def coherence(dirs, presence, size=3):
    w = presence.astype(np.float32) / 255.0
    M = {}
    for i in range(3):
        for j in range(i, 3):
            M[(i, j)] = ndi.uniform_filter(w * dirs[..., i] * dirs[..., j], size)
    tr = M[(0, 0)] + M[(1, 1)] + M[(2, 2)] + 1e-6
    # largest eigenvalue / trace via power iteration-free approx: use eigvalsh blockwise
    A = np.empty(dirs.shape[:3] + (3, 3), np.float32)
    for (i, j), v in M.items():
        A[..., i, j] = v; A[..., j, i] = v
    lam = np.linalg.eigvalsh(A)[..., -1]
    return (lam / tr).astype(np.float32)

def _interp(a, p):
    return ndi.map_coordinates(a, np.asarray(p, float).T, order=1, mode="nearest")

def trace(presence, dirs, coh, seed_presence=220, stop_presence=140, min_coherence=0.85, max_turn=30.0,
          step=1.0, xr=1.0, fork_ratio=0.9, fork_r=(2.0, 3.0), min_len=8, max_len=5000, claim_r=1, margin=2,
          seeds=None, use_claims=True):
    P = presence.astype(np.float32); shape = np.array(P.shape)
    if seeds is None:
        mx = ndi.maximum_filter(P, size=3)
        seeds = np.argwhere((P == mx) & (P >= seed_presence))
        seeds = seeds[np.argsort(-P[tuple(seeds.T)])]
    claimed = np.zeros(P.shape, bool)
    cos_turn = math.cos(math.radians(max_turn))
    g = np.arange(-xr, xr + 0.01, 0.5)
    ang = np.linspace(0, 2 * np.pi, 16, endpoint=False)
    def basis(d):
        a = np.array([1.0, 0, 0]) if abs(d[0]) < 0.9 else np.array([0, 1.0, 0])
        u = np.cross(d, a); u /= np.linalg.norm(u); return u, np.cross(d, u)
    def walk(p0, d0):
        pts, why = [], "max_len"; p, d = p0.copy(), d0.copy()
        for _ in range(max_len):
            q = p + step * d
            if np.any(q < margin) or np.any(q > shape - 1 - margin): why = "border"; break
            u, w = basis(d)
            U, W = np.meshgrid(g, g, indexing="ij")
            cand = q[None] + U.ravel()[:, None] * u + W.ravel()[:, None] * w
            v = _interp(P, cand); k = int(np.argmax(v)); qn, pv = cand[k], float(v[k])
            if pv < stop_presence: why = "weak"; break
            iq = tuple(np.clip(np.rint(qn).astype(int), 0, shape - 1))
            if coh[iq] < min_coherence: why = "incoherent"; break
            if fork_ratio:
                ring = np.concatenate([qn[None] + r * (np.cos(ang)[:, None] * u + np.sin(ang)[:, None] * w) for r in fork_r])
                rv = _interp(P, ring)
                # a separate ridge: bright ring sample with a dip between it and our centre
                mid = _interp(P, (ring + qn[None]) / 2)
                if np.any((rv >= fork_ratio * pv) & (mid < 0.8 * np.minimum(rv, pv))): why = "fork"; break
            dn = dirs[iq].astype(float)
            if np.dot(dn, d) < 0: dn = -dn
            if np.dot(dn, d) < cos_turn: why = "turn"; break
            if use_claims and claimed[iq]: why = "collision"; break
            pts.append(qn); d = 0.5 * d + 0.5 * dn; d /= np.linalg.norm(d); p = qn
        return pts, why
    traces, info = [], []
    for s in seeds:
        s = np.asarray(s, float)
        if use_claims and claimed[tuple(np.rint(s).astype(int))]: continue
        d0 = dirs[tuple(np.rint(s).astype(int))].astype(float)
        f, wf = walk(s, d0); b, wb = walk(s, -d0)
        pts = b[::-1] + [s] + f
        if len(pts) < min_len: continue
        T = np.array(pts); traces.append(T)
        info.append(dict(end_fwd=wf, end_bwd=wb, mean_presence=float(_interp(P, T).mean())))
        if use_claims:
            for q in np.rint(T).astype(int):
                claimed[max(0, q[0] - claim_r):q[0] + claim_r + 1, max(0, q[1] - claim_r):q[1] + claim_r + 1,
                        max(0, q[2] - claim_r):q[2] + claim_r + 1] = True
    return traces, info
