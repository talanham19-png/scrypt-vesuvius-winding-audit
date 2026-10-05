"""Score traced fibers against the hand-traced fiber-skeletons NML (WEBKNOSSOS) dataset."""
import glob, json, os, re, sys, time
import numpy as np, tifffile
from scipy.spatial import cKDTree
sys.path.insert(0, os.path.dirname(__file__))
from nml import parse_nml, densify
from tracer import hessian_tubularity, trace_all, st_field, trace_all_st

D = "/workspace/vesuvius/data/fiber-skeletons/Dataset001_sk-fibers-20250124"
OUT = "/workspace/vesuvius/out/fiber"

def cubes():
    out = []
    for f in sorted(glob.glob(D + "/nml/*.nml")):
        m = re.search(r"fibers_(s\d)a?_(\d+)z_(\d+)y_(\d+)x_(\d+)", f)
        sc, z, y, x, s = m.group(1), *map(int, m.groups()[1:])
        img = f"{D}/imagesTr/{sc}_{z:05d}_{y:05d}_{x:05d}_{s}_0000.tif"
        out.append(dict(name=f"{sc}_{z}_{y}_{x}_{s}", nml=f, img=img, off=(z, y, x), size=s))
    return out

def score(traces, confs, gt_pts, gt_ids, shape, tau=3.0, margin=3, conf_min=0.0, region=8.0):
    """GT cubes annotate the fibers of only some sheets, so we score inside the annotated region:
    predicted points within `region` vox of any GT fiber. Within it a point is correct if <= tau from GT.
    Trace-level: a trace with >=80% of points in-region is 'scored'; it is correct if >=90% of its
    points are within tau AND >=90% of those map to a single GT fiber (no fiber jumps)."""
    inside = np.all((gt_pts >= margin) & (gt_pts < np.array(shape) - margin), axis=1)
    G, Gi = gt_pts[inside], gt_ids[inside]
    tree = cKDTree(G)
    keep = [t for t, c in zip(traces, confs) if c >= conf_min]
    res = dict(n_traces=len(keep))
    if not keep:
        res.update(point_precision=float("nan"), recall=0.0, trace_correct=0, traced_len=0.0, correct_len=0.0)
        return res
    P = np.concatenate(keep)
    d, idx = tree.query(P, distance_upper_bound=region)
    inreg = np.isfinite(d)
    res["frac_points_in_region"] = float(inreg.mean())
    res["point_precision"] = float(np.mean(d[inreg] <= tau)) if inreg.any() else float("nan")
    ptree = cKDTree(P)
    dg, _ = ptree.query(G, distance_upper_bound=tau)
    res["recall"] = float(np.mean(np.isfinite(dg)))
    correct = 0; jumps = 0; L_all = 0.0; L_ok = 0.0; nscored = 0
    for t in keep:
        dr, _ = tree.query(t, distance_upper_bound=region)
        if np.isfinite(dr).mean() < 0.8: continue
        nscored += 1
        dt, it = tree.query(t, distance_upper_bound=tau)
        ok = np.isfinite(dt)
        L = float(np.linalg.norm(np.diff(t, axis=0), axis=1).sum()); L_all += L
        if ok.mean() < 0.9: continue
        ids = Gi[it[ok]]
        top = np.bincount(ids).max() / len(ids)
        if top >= 0.9: correct += 1; L_ok += L
        else: jumps += 1
    res.update(trace_scored=nscored, trace_correct=correct, trace_jump=jumps, trace_precision=correct / max(nscored, 1),
               traced_len=L_all, correct_len=L_ok, len_precision=L_ok / max(L_all, 1e-9),
               gt_len=float(len(G) * 0.5))
    return res

if __name__ == "__main__":
    which = sys.argv[1:]  # substrings of cube names; default all
    os.makedirs(OUT, exist_ok=True)
    allres = {}
    for c in cubes():
        if which and not any(w in c["name"] for w in which): continue
        t0 = time.time()
        vol = tifffile.imread(c["img"])
        crop = (0, 0, 0)
        if vol.shape[0] > 256:  # 512 cubes: central 256^3 crop (memory)
            crop = (128, 128, 128); vol = vol[128:384, 128:384, 128:384]
        fb = parse_nml(c["nml"], tuple(np.array(c["off"]) + np.array(crop)))
        gp, gi = densify(fb)
        if os.environ.get("METHOD", "st") == "hessian":
            V, A = hessian_tubularity(vol); traces, confs, reasons = trace_all(V, A); del V, A
        else:
            kw = json.loads(os.environ.get("TRACE_KW", "{}"))
            I, F, A, LN = st_field(vol); traces, confs, reasons = trace_all_st(I, F, A, LN, **kw); del I, F, A, LN
        res = score(traces, confs, gp, gi, vol.shape)
        # abstention curve over confidence quantiles
        curve = []
        if len(confs):
            for q in (0, 25, 50, 75, 90):
                cm = float(np.percentile(confs, q))
                r = score(traces, confs, gp, gi, vol.shape, conf_min=cm)
                curve.append(dict(q=q, **{k: r[k] for k in ("n_traces", "trace_scored", "point_precision", "recall", "trace_precision", "len_precision", "correct_len")}))
        res["stop_reasons"] = reasons; res["curve"] = curve; res["secs"] = time.time() - t0
        allres[c["name"]] = res
        print(c["name"], json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in res.items() if k != "curve"}), flush=True)
        for row in curve: print("   ", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in row.items()})
        np.save(f"{OUT}/{c['name']}_traces.npy", np.array([np.c_[t + np.array(crop), np.full(len(t), i)] for i, t in enumerate(traces)], dtype=object), allow_pickle=True)
    tag = os.environ.get("TAG", "run")
    json.dump(allres, open(f"{OUT}/eval_{tag}.json", "w"), indent=1)
