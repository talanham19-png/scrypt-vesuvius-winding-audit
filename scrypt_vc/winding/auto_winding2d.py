"""Prototype A: automatic relative-winding constraints from a surface-prediction slice.

Pipeline (one z-slice, reference/fit coordinates = PHercParis4 2.4um level-2, ~9.6um):
  1. binarize surface prediction, drop thick mask-border artefacts, skeletonize
  2. remove skeleton junctions -> sheet pieces; cut pieces at the branch ray (theta = +-pi)
     so theta is continuous on every piece: s(p) = k_piece + sigma*theta(p)/2pi
  3. cast rays from the umbilicus; consecutive sheet crossings give edges k_b - k_a = 1
     (skipped if the gap is suspiciously large or the crossing run is too wide = merged sheets)
     seam continuity edges: piece at theta~+pi -> same sheet at theta~-pi: k_b - k_a = sigma
  4. robust integer synchronisation: greedy union-find with offsets in decreasing support
     order; an edge contradicting the already-built component is rejected (cycle check)
  5. sigma (spiral sense) is chosen automatically as the one with fewer contradictions
Outputs per-piece integer offsets + a VC3D point-collection JSON of generated chains.
"""
import json, math, os, sys, time, collections
import numpy as np
from scipy import ndimage as ndi
from skimage.morphology import skeletonize

def umbilicus_yx(umb_json, z):
    cp = json.load(open(umb_json))["control_points"]
    a = np.array(sorted([(c["z"], c["y"], c["x"]) for c in cp]), float)
    return float(np.interp(z, a[:, 0], a[:, 1])), float(np.interp(z, a[:, 0], a[:, 2]))

def preprocess(plane, thick_radius=4):
    m = plane > 127
    # thick blobs (mask border ring) survive an opening; sheets (1-3 px) don't
    st = np.ones((2 * thick_radius + 1,) * 2, bool)
    thick = ndi.binary_opening(m, structure=st)
    thick = ndi.binary_dilation(thick, iterations=3)
    m &= ~thick
    return m

class UF:
    def __init__(s, n):
        s.p = np.arange(n); s.o = np.zeros(n, np.int64)  # k[i] = k[root] + o[i]
    def find(s, i):
        path = []
        while s.p[i] != i:
            path.append(i); i = s.p[i]
        root = i; acc = 0
        for j in reversed(path):  # compress
            acc += s.o[j]; s.o[j] = acc; s.p[j] = root
        return root
    def off(s, i):
        s.find(i); return s.o[i] if s.p[i] != i else 0
    def union(s, a, b, d):
        """impose k_b - k_a = d. returns True (added/consistent) or False (contradiction)."""
        ra, rb = s.find(a), s.find(b)
        oa, ob = s.off(a), s.off(b)
        if ra == rb:
            return (ob - oa) == d, (ob - oa) - d
        # k_b = k_rb + ob ; k_a = k_ra + oa ; want k_rb = k_ra + oa + d - ob
        s.p[rb] = ra; s.o[rb] = oa + d - ob
        return True, 0

def run_slice(plane, cy, cx, n_rays=7200, gap_factor=1.6, max_run=7, min_piece=8, sigma=None, verbose=True,
              snap_lab=2.0, min_support=3, min_agree=0.9, prune_rounds=0, prune_conflicts=1, min_cos=0.8, st_sigma=3.0,
              cut_deg=5.0, cont_weight=int(os.environ.get("CONT_W", 1000)), icm_sweeps=10):
    t0 = time.time()
    m = preprocess(plane)
    ys, xs = np.nonzero(m)
    y0, y1, x0, x1 = ys.min() - 2, ys.max() + 3, xs.min() - 2, xs.max() + 3
    m = m[y0:y1, x0:x1]; cy -= y0; cx -= x0
    sk = skeletonize(m)
    # local sheet normal from the structure tensor of the (smoothed) mask
    mf = ndi.gaussian_filter(m.astype(np.float32), 1.0)
    gy = ndi.sobel(mf, 0); gx = ndi.sobel(mf, 1); del mf
    Jyy = ndi.gaussian_filter(gy * gy, st_sigma); Jxx = ndi.gaussian_filter(gx * gx, st_sigma)
    Jxy = ndi.gaussian_filter(gx * gy, st_sigma); del gx, gy
    nang = (0.5 * np.arctan2(2 * Jxy, Jxx - Jyy)).astype(np.float32)  # dominant gradient dir = sheet normal
    del Jyy, Jxx, Jxy
    nb = ndi.convolve(sk.astype(np.uint8), np.ones((3, 3), np.uint8), mode="constant") - 1
    junction = sk & (nb >= 3)
    pieces = sk & ~ndi.binary_dilation(junction, iterations=1)
    # radial cuts every cut_deg degrees (incl. the branch ray theta=+-pi): every chunk has a
    # continuous theta in [-pi, pi) and spans <= cut_deg, so s(p) = k + sigma*theta/2pi is exact
    H, W = m.shape
    py_, px_ = np.nonzero(pieces)
    th = np.arctan2(py_ - cy, px_ - cx)
    rr = np.hypot(py_ - cy, px_ - cx)
    dphi = math.radians(cut_deg)
    j = np.rint((th + math.pi) / dphi)
    near = rr * np.abs(th + math.pi - j * dphi) < 0.75
    lab0, _ = ndi.label(pieces, np.ones((3, 3)))
    cut = np.zeros_like(pieces); cut[py_[near], px_[near]] = True
    pieces_c = pieces & ~cut
    lab, n = ndi.label(pieces_c, np.ones((3, 3)))
    sizes = ndi.sum(np.ones_like(lab), lab, index=np.arange(n + 1))
    small = sizes < min_piece; small[0] = True
    lab[small[lab]] = 0
    # continuity edges across every cut
    seam = []  # (a, b, kind) : kind 'cont' => k_b-k_a=0 ; 'seam' => k_b-k_a=sigma
    cl, ncl = ndi.label(cut, np.ones((3, 3)))
    objs = ndi.find_objects(cl)
    for ci, sl in enumerate(objs, 1):
        if sl is None: continue
        y0_, y1_ = max(0, sl[0].start - 2), min(H, sl[0].stop + 2)
        x0_, x1_ = max(0, sl[1].start - 2), min(W, sl[1].stop + 2)
        win = lab[y0_:y1_, x0_:x1_]
        Ls = np.unique(win[win > 0])
        if len(Ls) < 2: continue
        cyy, cxx = np.nonzero(cl[y0_:y1_, x0_:x1_] == ci)
        cy0, cx0 = cyy.mean() + y0_, cxx.mean() + x0_
        phic = math.atan2(cy0 - cy, cx0 - cx)
        side = {}
        for L in Ls:
            yy_, xx_ = np.nonzero(win == L)
            t_ = np.arctan2(yy_ + y0_ - cy, xx_ + x0_ - cx)
            side[L] = math.atan2(math.sin(t_.mean() - phic), math.cos(t_.mean() - phic)) if False else np.mean(np.angle(np.exp(1j * (t_ - phic))))
        lo = [L for L in Ls if side[L] < 0]; hi = [L for L in Ls if side[L] >= 0]
        is_seam = abs(abs(phic) - math.pi) < dphi / 2
        for a in lo:
            for b in hi:
                if is_seam:
                    # lo side = theta just below +pi ; hi side = just above -pi
                    seam.append((a, b, "seam"))
                else:
                    seam.append((a, b, "cont"))
    n = lab.max()
    if verbose: print(f"  skeleton px={sk.sum()} junctions={junction.sum()} chunks={int((~small[1:]).sum())} ({time.time()-t0:.0f}s)")
    # dilated label map for lookup
    dist, (iyn, ixn) = ndi.distance_transform_edt(lab == 0, return_indices=True)
    labd = lab[iyn, ixn].astype(np.int32)
    labd[dist > snap_lab] = 0
    del dist, iyn, ixn
    # --- rays
    ray_edges = {}  # (a,b) -> count ; meaning k_b - k_a = 1 (b outward of a)
    rmax = int(math.hypot(H, W))
    t = np.arange(0, rmax, 0.5)
    crossings_per_ray = []
    ray_records = []
    for i in range(n_rays):
        phi = -math.pi + 2 * math.pi * (i + 0.5) / n_rays
        py = cy + t * math.sin(phi); px = cx + t * math.cos(phi)
        ok = (py >= 0) & (py < H - 1) & (px >= 0) & (px < W - 1)
        py, px, tt = py[ok], px[ok], t[ok]
        iy, ix = np.rint(py).astype(int), np.rint(px).astype(int)
        v = m[iy, ix]
        if not v.any(): ray_records.append([]); continue
        dv = np.diff(np.r_[0, v.astype(np.int8), 0])
        starts, ends = np.nonzero(dv == 1)[0], np.nonzero(dv == -1)[0]
        cr = []
        for s_, e_ in zip(starts, ends):
            c = (s_ + e_ - 1) // 2
            run_len = (e_ - s_) * 0.5
            L = labd[iy[c], ix[c]]
            cosv = abs(math.cos(nang[iy[c], ix[c]] - phi))
            if cosv < min_cos: L = -1  # sheet not crossing the ray ~perpendicularly: unknown, breaks chain
            cr.append((tt[c], L, run_len, iy[c], ix[c]))
        ray_records.append(cr)
        crossings_per_ray.append(len(cr))
        tc = np.array([c_[0] for c_ in cr]); gaps = np.diff(tc)
        for q, ((ta, la, ra, *_), (tb, lb, rb, *_)) in enumerate(zip(cr[:-1], cr[1:])):
            if la <= 0 or lb <= 0 or la == lb: continue
            loc = np.median(gaps[max(0, q - 5):q + 6])
            if tb - ta > gap_factor * loc or ra > max_run or rb > max_run: continue
            ray_edges[(la, lb)] = ray_edges.get((la, lb), 0) + 1
    if verbose: print(f"  rays done: {len(ray_edges)} ray edges, {len(seam)} seam edges, median crossings/ray={np.median(crossings_per_ray):.0f} ({time.time()-t0:.0f}s)")
    results = {}
    filt = {}
    for (a, b), c in ray_edges.items():
        back = ray_edges.get((b, a), 0)
        if c >= min_support and c >= min_agree * (c + back):
            filt[(a, b)] = c
    if verbose: print(f"  edge filter: {len(filt)}/{len(ray_edges)} ray edges kept (support>={min_support}, agree>={min_agree})")
    for sg in ([sigma] if sigma else [1, -1]):
      banned = set()
      for rnd in range(prune_rounds + 1):
        edges = [(c, a, b, 1, "ray") for (a, b), c in filt.items() if a not in banned and b not in banned]
        # an opposite-direction ray edge (b,a) is itself a contradiction; let support decide
        edges += [(cont_weight, a, b, (sg if kd == "seam" else 0), kd) for a, b, kd in seam if a not in banned and b not in banned]
        edges.sort(key=lambda e: -e[0])
        uf = UF(lab.max() + 1)
        rej_w = acc_w = 0; rejected = []
        conflicts = collections.Counter()
        for w, a, b, d, kind in edges:
            ok, res = uf.union(a, b, d)
            if ok: acc_w += w if kind == "ray" else 0
            else:
                rej_w += w if kind == "ray" else 0; rejected.append((a, b, d, kind, w, res))
                conflicts[a] += 1; conflicts[b] += 1
        if verbose: print(f"  sigma={sg:+d} round {rnd}: accepted ray support={acc_w}, rejected={rej_w} ({len(rejected)} edges, {sum(r[3]=='seam' for r in rejected)} seam), banned={len(banned)}")
        results[sg] = dict(uf=uf, rej_w=rej_w, acc_w=acc_w, rejected=rejected, banned=set(banned), first_rej=results.get(sg, {}).get('first_rej', rej_w))
        new = {p for p, c in conflicts.items() if c >= prune_conflicts}
        if not new: break
        banned |= new
    best = min(results, key=lambda s: results[s]["first_rej"])
    R = results[best]
    uf = R["uf"]
    nlab = lab.max() + 1
    root = np.array([uf.find(i) for i in range(nlab)])
    k = np.array([uf.off(i) for i in range(nlab)])
    for p in R["banned"]: root[p] = -1 - p  # isolated, unusable
    # ICM refinement: k_i <- weighted mode of neighbour predictions (all edges, incl. rejected)
    sg = best
    E = [(a, b, 1, c) for (a, b), c in filt.items()] + [(a, b, (sg if kd == "seam" else 0), cont_weight) for a, b, kd in seam]
    nbrs = collections.defaultdict(list)
    for a, b, d, w in E:
        if root[a] == root[b]:
            nbrs[b].append((a, d, w)); nbrs[a].append((b, -d, w))
    def agree():
        return sum(w for a, b, d, w in E if root[a] == root[b] and k[b] - k[a] == d), sum(w for a, b, d, w in E if root[a] == root[b])
    if verbose: print(f"  before ICM: agreeing weight {agree()}")
    for sweep in range(icm_sweeps):
        changed = 0
        for i, lst in nbrs.items():
            votes = collections.Counter()
            for j_, d, w in lst: votes[k[j_] + d] += w
            kb, wb = votes.most_common(1)[0]
            if kb != k[i] and wb > votes.get(k[i], 0):
                k[i] = kb; changed += 1
        if verbose: print(f"  ICM sweep {sweep}: changed {changed}, agreeing {agree()}")
        if not changed: break
    # per-chunk confidence: fraction of incident edge weight that agrees
    conf = np.zeros(nlab, np.float32)
    for i, lst in nbrs.items():
        tot = sum(w for _, _, w in lst); ok = sum(w for j_, d, w in lst if k[j_] + d == k[i])
        conf[i] = ok / tot if tot else 0
    return dict(lab=lab, labd=labd, root=root, k=k, conf=conf, sigma=best, offset=(y0, x0), cy=cy, cx=cx,
                ray_edges=ray_edges, seam=seam, results={s: {kk: v for kk, v in r.items() if kk != "uf"} for s, r in results.items()},
                ray_records=ray_records, n_rays=n_rays)

def s_value(sol, y, x, snap=4):
    """global spiral coordinate (up to component constant) of point (y,x) in plane coords."""
    y0, x0 = sol["offset"]; y -= y0; x -= x0
    lab = sol["lab"]; H, W = lab.shape
    iy, ix = int(round(y)), int(round(x))
    best = None
    for dy in range(-snap, snap + 1):
        for dx in range(-snap, snap + 1):
            yy, xx = iy + dy, ix + dx
            if 0 <= yy < H and 0 <= xx < W and lab[yy, xx]:
                d = dy * dy + dx * dx
                if best is None or d < best[0]: best = (d, lab[yy, xx], yy, xx)
    if best is None: return None
    _, L, yy, xx = best
    th = math.atan2(yy - sol["cy"], xx - sol["cx"])
    return sol["root"][L], sol["k"][L] + sol["sigma"] * th / (2 * math.pi), th, L
