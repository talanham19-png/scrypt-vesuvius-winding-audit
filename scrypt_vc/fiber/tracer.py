"""Prototype B: conservative classical fiber tracer (CPU, numpy/scipy).

Fibers = bright tubes inside papyrus sheets. We compute a multi-scale Hessian tubularity
(Frangi-style, bright-on-dark) and its tube axis (eigenvector of the smallest-|lambda| eigenvalue),
then track from strong seeds with explicit stop-when-uncertain rules:
  * tubularity below t_stop (relative to the seed's own strength and an absolute floor)
  * direction change between steps > max_turn degrees
  * ambiguity: a second, comparably strong ridge in the cross-section plane (crossing/branch)
  * collision with an already accepted trace (no duplicates; we never merge through junctions)
  * out of volume
Each trace keeps a confidence (mean tubularity * mean straightness); short traces are dropped.
Outputs: list of (N,3) zyx float polylines in volume voxels + confidence.
"""
import math
import numpy as np
from scipy import ndimage as ndi

def hessian_tubularity(vol, sigmas=(1.5, 2.0, 2.5), alpha=0.5, beta=0.5, block=64):
    v = vol.astype(np.float32)
    v = (v - v.mean()) / (v.std() + 1e-6)
    best = np.zeros(v.shape, np.float32)
    axis = np.zeros(v.shape + (3,), np.float32)
    for s in sigmas:
        H = {}
        for (i, j) in [(0, 0), (1, 1), (2, 2), (0, 1), (0, 2), (1, 2)]:
            order = [0, 0, 0]; order[i] += 1; order[j] += 1
            H[(i, j)] = (ndi.gaussian_filter(v, s, order=order) * s * s).astype(np.float32)
        # eigen-decomposition blockwise along z to bound memory
        for z0 in range(0, v.shape[0], block):
            sl = slice(z0, z0 + block)
            M = np.empty(H[(0, 0)][sl].shape + (3, 3), np.float32)
            for (i, j), a in H.items():
                M[..., i, j] = a[sl]; M[..., j, i] = a[sl]
            w, U = np.linalg.eigh(M)  # ascending
            order = np.argsort(np.abs(w), axis=-1)
            w = np.take_along_axis(w, order, -1)
            U = np.take_along_axis(U, order[..., None, :], -1)
            l1, l2, l3 = w[..., 0], w[..., 1], w[..., 2]
            Ra = np.abs(l2) / (np.abs(l3) + 1e-6)          # plate vs line
            Rb = np.abs(l1) / (np.sqrt(np.abs(l2 * l3)) + 1e-6)  # blob vs line
            S = np.sqrt(l1 ** 2 + l2 ** 2 + l3 ** 2)
            c = 0.5 * float(np.percentile(S, 99)) + 1e-6
            V = (1 - np.exp(-Ra ** 2 / (2 * alpha ** 2))) * np.exp(-Rb ** 2 / (2 * beta ** 2)) * (1 - np.exp(-S ** 2 / (2 * c ** 2)))
            V[(l2 > 0) | (l3 > 0)] = 0  # bright tube only
            V = V.astype(np.float32)
            upd = V > best[sl]
            best[sl][upd] = V[upd]
            axis[sl][upd] = U[..., :, 0][upd]
            del M, w, U, V
        del H
    return best, axis

def _interp(a, p):
    return ndi.map_coordinates(a, np.asarray(p, float).T.reshape(3, -1), order=1, mode="nearest")

def _axis_at(axis, p):
    i = np.clip(np.rint(p).astype(int), 0, np.array(axis.shape[:3]) - 1)
    return axis[i[0], i[1], i[2]]

def trace_all(V, axis, seed_q=99.0, stop_frac=0.35, abs_stop_q=90.0, max_turn=30.0, step=1.0,
              xr=2.0, ambig_ratio=0.8, min_len=15, max_len=2000, claim_r=1.5, margin=3):
    shape = np.array(V.shape)
    t_seed = np.percentile(V, seed_q)
    t_abs = np.percentile(V, abs_stop_q)
    mx = ndi.maximum_filter(V, size=5)
    seeds = np.argwhere((V == mx) & (V >= t_seed))
    seeds = seeds[np.argsort(-V[tuple(seeds.T)])]
    claimed = np.zeros(V.shape, bool)
    cos_turn = math.cos(math.radians(max_turn))
    # cross-section sampling grid offsets (in plane basis)
    g = np.arange(-xr, xr + 0.01, 0.5)
    GU, GV = np.meshgrid(g, g, indexing="ij")
    disk = (GU ** 2 + GV ** 2) <= xr ** 2 + 1e-6
    GU, GV = GU[disk], GV[disk]
    traces, confs, reasons = [], [], {}
    def basis(d):
        a = np.array([1.0, 0, 0]) if abs(d[0]) < 0.9 else np.array([0, 1.0, 0])
        u = np.cross(d, a); u /= np.linalg.norm(u); w = np.cross(d, u)
        return u, w
    def walk(p0, d0, vseed):
        pts, vals = [], []
        p, d = p0.copy(), d0.copy()
        why = "max_len"
        for _ in range(max_len):
            q = p + step * d
            if np.any(q < margin) or np.any(q > shape - 1 - margin): why = "border"; break
            u, w = basis(d)
            cand = q[None] + GU[:, None] * u[None] + GV[:, None] * w[None]
            vals_c = _interp(V, cand)
            k = int(np.argmax(vals_c)); vbest = vals_c[k]
            # ambiguity: another strong local max in cross-section, well separated from the best
            sep = np.hypot(GU - GU[k], GV - GV[k])
            far = sep >= 2.0
            if far.any() and vals_c[far].max() > ambig_ratio * vbest and vals_c[far].max() > t_seed:
                why = "ambiguous"; break
            qn = cand[k]
            vq = float(_interp(V, qn[None])[0])
            if vq < max(stop_frac * vseed, t_abs): why = "weak"; break
            dn = _axis_at(axis, qn).astype(float)
            dn /= (np.linalg.norm(dn) + 1e-9)
            if np.dot(dn, d) < 0: dn = -dn
            mv = qn - p; mv /= (np.linalg.norm(mv) + 1e-9)
            if np.dot(dn, d) < cos_turn or np.dot(mv, d) < cos_turn: why = "turn"; break
            iq = tuple(np.rint(qn).astype(int))
            if claimed[iq]: why = "collision"; break
            pts.append(qn); vals.append(vq)
            d = dn * 0.7 + d * 0.3; d /= np.linalg.norm(d)
            p = qn
        return pts, vals, why
    for s in seeds:
        if claimed[tuple(s)]: continue
        p0 = s.astype(float)
        d0 = _axis_at(axis, p0).astype(float); d0 /= (np.linalg.norm(d0) + 1e-9)
        vseed = float(V[tuple(s)])
        f, fv, wf = walk(p0, d0, vseed)
        b, bv, wb = walk(p0, -d0, vseed)
        pts = b[::-1] + [p0] + f
        if len(pts) < min_len: continue
        P = np.array(pts)
        segl = np.linalg.norm(np.diff(P, axis=0), axis=1).sum()
        straight = np.linalg.norm(P[-1] - P[0]) / (segl + 1e-9)
        conf = float(np.mean(bv[::-1] + [vseed] + fv)) * (0.5 + 0.5 * straight)
        traces.append(P); confs.append(conf)
        reasons[wf] = reasons.get(wf, 0) + 1; reasons[wb] = reasons.get(wb, 0) + 1
        # claim a tube around the trace
        r = int(math.ceil(claim_r))
        for q in np.rint(P).astype(int):
            claimed[max(0, q[0] - r):q[0] + r + 1, max(0, q[1] - r):q[1] + r + 1, max(0, q[2] - r):q[2] + r + 1] = True
    return traces, np.array(confs), reasons

def st_field(vol, smooth=1.0, grad_sigma=1.0, int_sigma=2.5, block=32):
    """Structure-tensor fiber field. Returns (I, F, axis, lin):
    I    smoothed, standardized intensity (ridge used for re-centring)
    axis eigenvector of the smallest ST eigenvalue (least intensity variation = fiber direction)
    lin  linear anisotropy (l2-l1)/(l2+l1): ~1 when one in-sheet direction clearly dominates
    F    seed/strength feature = relu(I) * lin
    """
    v = vol.astype(np.float32)
    v = (v - v.mean()) / (v.std() + 1e-6)
    I = ndi.gaussian_filter(v, smooth)
    g = [ndi.gaussian_filter(v, grad_sigma, order=[int(a == b) for b in range(3)]) for a in range(3)]
    del v
    J = {}
    for i in range(3):
        for j in range(i, 3):
            J[(i, j)] = ndi.gaussian_filter(g[i] * g[j], int_sigma)
    del g
    axis = np.zeros(I.shape + (3,), np.float32)
    lin = np.zeros(I.shape, np.float32)
    for z0 in range(0, I.shape[0], block):
        sl = slice(z0, z0 + block)
        M = np.empty(J[(0, 0)][sl].shape + (3, 3), np.float32)
        for (i, j), a in J.items():
            M[..., i, j] = a[sl]; M[..., j, i] = a[sl]
        w, U = np.linalg.eigh(M)
        axis[sl] = U[..., :, 0]
        lin[sl] = (w[..., 1] - w[..., 0]) / (w[..., 1] + w[..., 0] + 1e-6)
        del M, w, U
    F = np.maximum(I, 0) * lin
    return I, F, axis, lin

def trace_all_st(I, F, axis, lin, seed_q=98.0, stop_I=0.3, min_lin=0.25, max_turn=45.0, soft_turn=25.0,
                 soft_n=3, step=1.0, xr=1.0, min_len=20, max_len=2000, claim_r=1.5, margin=3, ambig=True,
                 inertia=0.7):
    """Ridge-following tracker on the structure-tensor field with abstention."""
    shape = np.array(I.shape)
    t_seed = np.percentile(F, seed_q)
    mx = ndi.maximum_filter(F, size=5)
    seeds = np.argwhere((F == mx) & (F >= t_seed))
    seeds = seeds[np.argsort(-F[tuple(seeds.T)])]
    claimed = np.zeros(I.shape, bool)
    cos_turn = math.cos(math.radians(max_turn)); cos_soft = math.cos(math.radians(soft_turn))
    g = np.arange(-xr, xr + 0.01, 0.5)
    GU, GV = np.meshgrid(g, g, indexing="ij")
    disk = (GU ** 2 + GV ** 2) <= xr ** 2 + 1e-6
    GU, GV = GU[disk], GV[disk]
    g2 = np.arange(-4, 4.01, 1.0)
    RU, RV = np.meshgrid(g2, g2, indexing="ij"); ring = (np.hypot(RU, RV) >= 2.5) & (np.hypot(RU, RV) <= 4)
    RU, RV = RU[ring], RV[ring]
    traces, confs, reasons = [], [], {}
    def basis(d):
        a = np.array([1.0, 0, 0]) if abs(d[0]) < 0.9 else np.array([0, 1.0, 0])
        u = np.cross(d, a); u /= np.linalg.norm(u); w = np.cross(d, u)
        return u, w
    def walk(p0, d0):
        pts, vals = [], []
        p, d = p0.copy(), d0.copy(); why = "max_len"; nsoft = 0
        for _ in range(max_len):
            q = p + step * d
            if np.any(q < margin) or np.any(q > shape - 1 - margin): why = "border"; break
            u, w = basis(d)
            cand = q[None] + GU[:, None] * u[None] + GV[:, None] * w[None]
            vc = _interp(I, cand); k = int(np.argmax(vc)); qn = cand[k]; iv = float(vc[k])
            if iv < stop_I: why = "weak"; break
            iq = tuple(np.clip(np.rint(qn).astype(int), 0, shape - 1))
            if lin[iq] < min_lin: why = "ambiguous_dir"; break
            if ambig:
                # a neighbouring ridge as bright as ours within 2.5-4 vox in the cross-section and
                # *closer to our predicted path than our own maximum* -> could be a merge/crossing
                rc = _interp(I, q[None] + RU[:, None] * u[None] + RV[:, None] * w[None])
                if rc.max() > 1.15 * iv: why = "brighter_neighbour"; break
            dn = axis[iq].astype(float); dn /= (np.linalg.norm(dn) + 1e-9)
            if np.dot(dn, d) < 0: dn = -dn
            cd = np.dot(dn, d)
            if cd < cos_turn: why = "turn"; break
            nsoft = nsoft + 1 if cd < cos_soft else 0
            if nsoft >= soft_n: why = "turn_persistent"; break
            if claimed[iq]: why = "collision"; break
            pts.append(qn); vals.append(iv * float(lin[iq]))
            d = d * inertia + dn * (1 - inertia); d /= np.linalg.norm(d); p = qn
        return pts, vals, why
    for s in seeds:
        if claimed[tuple(s)]: continue
        p0 = s.astype(float)
        d0 = axis[tuple(s)].astype(float); d0 /= (np.linalg.norm(d0) + 1e-9)
        f, fv, wf = walk(p0, d0); b, bv, wb = walk(p0, -d0)
        pts = b[::-1] + [p0] + f
        if len(pts) < min_len: continue
        P = np.array(pts)
        segl = np.linalg.norm(np.diff(P, axis=0), axis=1).sum()
        straight = np.linalg.norm(P[-1] - P[0]) / (segl + 1e-9)
        conf = float(np.mean(bv + fv + [float(F[tuple(s)])])) * straight
        traces.append(P); confs.append(conf)
        reasons[wf] = reasons.get(wf, 0) + 1; reasons[wb] = reasons.get(wb, 0) + 1
        r = int(math.ceil(claim_r))
        for q in np.rint(P).astype(int):
            claimed[max(0, q[0] - r):q[0] + r + 1, max(0, q[1] - r):q[1] + r + 1, max(0, q[2] - r):q[2] + r + 1] = True
    return traces, np.array(confs), reasons

# ---------------------------------------------------------------------------------------------
# HV tracer: papyrus fibers are either vertical (along the scroll axis z) or horizontal, and both
# lie in the sheet plane. The sheet normal n (structure-tensor major axis) is robust, so the
# fiber direction at any point is one of two known in-plane directions:
#     v = normalize(z - (z.n) n)      (vertical fibers)       h = n x v   (horizontal fibers)
# A V-fiber is a bright ridge across h; an H-fiber is a bright ridge across v.
def hv_field(vol, grad_sigma=1.0, int_sigma=4.0, hess_sigma=1.5, block=32):
    v0 = vol.astype(np.float32); v0 = (v0 - v0.mean()) / (v0.std() + 1e-6)
    I = ndi.gaussian_filter(v0, 1.0)
    g = [ndi.gaussian_filter(v0, grad_sigma, order=[int(a == b) for b in range(3)]) for a in range(3)]
    J = {}
    for i in range(3):
        for j in range(i, 3):
            J[(i, j)] = ndi.gaussian_filter(g[i] * g[j], int_sigma)
    del g
    nrm = np.zeros(I.shape + (3,), np.float32)
    for z0 in range(0, I.shape[0], block):
        sl = slice(z0, z0 + block)
        M = np.empty(J[(0, 0)][sl].shape + (3, 3), np.float32)
        for (i, j), a in J.items():
            M[..., i, j] = a[sl]; M[..., j, i] = a[sl]
        _, U = np.linalg.eigh(M); nrm[sl] = U[..., :, 2]; del M, U
    del J
    zax = np.array([1.0, 0, 0], np.float32)
    vdir = zax[None, None, None] - (nrm @ zax)[..., None] * nrm
    vdir /= (np.linalg.norm(vdir, axis=-1, keepdims=True) + 1e-6)
    hdir = np.cross(nrm, vdir).astype(np.float32)
    Hs = {}
    for (i, j) in [(0, 0), (1, 1), (2, 2), (0, 1), (0, 2), (1, 2)]:
        o = [0, 0, 0]; o[i] += 1; o[j] += 1
        Hs[(i, j)] = ndi.gaussian_filter(v0, hess_sigma, order=o) * hess_sigma ** 2
    del v0
    def quad(a):  # a^T H a
        r = np.zeros(I.shape, np.float32)
        for (i, j), Hij in Hs.items():
            r += (1 if i == j else 2) * Hij * a[..., i] * a[..., j]
        return r
    hh, vv = quad(hdir), quad(vdir)
    del Hs
    RV = np.maximum(-hh, 0) - 0.5 * np.abs(vv)   # ridge across h, flat along v
    RH = np.maximum(-vv, 0) - 0.5 * np.abs(hh)
    bright = I > 0
    RV *= bright; RH *= bright
    return dict(I=I, n=nrm, v=vdir, h=hdir, RV=RV.astype(np.float32), RH=RH.astype(np.float32))

def trace_hv(fld, seed_q=99.0, stop_frac=0.3, abs_q=85.0, dom=1.0, max_turn=30.0, step=1.0, xr=1.0,
             min_len=20, max_len=2000, claim_r=1.5, margin=3, cross_stop=True):
    I = fld["I"]; shape = np.array(I.shape)
    R = {"V": fld["RV"], "H": fld["RH"]}; D = {"V": fld["v"], "H": fld["h"]}
    best = np.maximum(R["V"], R["H"])
    t_seed = np.percentile(best, seed_q)
    t_abs = {f: np.percentile(R[f][R[f] > 0], abs_q) * 0 + np.percentile(best, abs_q) for f in "VH"}
    mx = ndi.maximum_filter(best, size=5)
    seeds = np.argwhere((best == mx) & (best >= t_seed))
    seeds = seeds[np.argsort(-best[tuple(seeds.T)])]
    claimed = np.zeros(I.shape, bool)
    cos_turn = math.cos(math.radians(max_turn))
    g = np.arange(-xr, xr + 0.01, 0.5)
    traces, confs, fams, reasons = [], [], [], {}
    def walk(p0, d0, fam, rseed):
        other = "H" if fam == "V" else "V"
        pts, vals = [], []; p, d = p0.copy(), d0.copy(); why = "max_len"
        for _ in range(max_len):
            q = p + step * d
            if np.any(q < margin) or np.any(q > shape - 1 - margin): why = "border"; break
            iq = tuple(np.rint(q).astype(int))
            nq = fld["n"][iq].astype(float)
            across = np.cross(nq, d); across /= (np.linalg.norm(across) + 1e-9)
            U, W = np.meshgrid(g, g, indexing="ij")
            cand = q[None] + U.ravel()[:, None] * across[None] + W.ravel()[:, None] * nq[None]
            rv = _interp(R[fam], cand); k = int(np.argmax(rv)); qn = cand[k]; r = float(rv[k])
            if r < max(stop_frac * rseed, t_abs[fam]): why = "weak"; break
            iq = tuple(np.clip(np.rint(qn).astype(int), 0, shape - 1))
            if cross_stop and R[other][iq] > dom * r: why = "crossing"; break
            dn = D[fam][iq].astype(float); dn /= (np.linalg.norm(dn) + 1e-9)
            if np.dot(dn, d) < 0: dn = -dn
            if np.dot(dn, d) < cos_turn: why = "turn"; break
            if claimed[iq]: why = "collision"; break
            pts.append(qn); vals.append(r)
            d = 0.5 * d + 0.5 * dn; d /= np.linalg.norm(d); p = qn
        return pts, vals, why
    for s in seeds:
        if claimed[tuple(s)]: continue
        fam = "V" if R["V"][tuple(s)] >= R["H"][tuple(s)] else "H"
        p0 = s.astype(float); d0 = D[fam][tuple(s)].astype(float); d0 /= (np.linalg.norm(d0) + 1e-9)
        rseed = float(R[fam][tuple(s)])
        f, fv, wf = walk(p0, d0, fam, rseed); b, bv, wb = walk(p0, -d0, fam, rseed)
        pts = b[::-1] + [p0] + f
        if len(pts) < min_len: continue
        P = np.array(pts)
        conf = float(np.mean(bv + fv + [rseed]))
        traces.append(P); confs.append(conf); fams.append(fam)
        reasons[wf] = reasons.get(wf, 0) + 1; reasons[wb] = reasons.get(wb, 0) + 1
        rr = int(math.ceil(claim_r))
        for q in np.rint(P).astype(int):
            claimed[max(0, q[0] - rr):q[0] + rr + 1, max(0, q[1] - rr):q[1] + rr + 1, max(0, q[2] - rr):q[2] + rr + 1] = True
    return traces, np.array(confs), reasons, fams
