"""Evaluate the prediction-based tracer against VC3D human-guided eval fibers (PHercParis4).
Two protocols, per L3 crop:
  (1) GT-seeded tracking: seed at the middle of each GT run, trace both ways (no claims); walk along the
      trace and count steps until it leaves the GT polyline by > tau (deviation = error) or the tracer stops
      itself (abstention). Report correct length, deviation rate, abstention rate.
  (2) Automatic mode: seeds from presence maxima. For traces that touch GT (>= 5 pts within tau), check whether
      every point of the trace inside GT's neighbourhood band stays on the SAME GT fiber (no jumps); report
      the fraction of GT length recovered and the 'jump' rate.
"""
import glob, json, os, sys, collections
import numpy as np
from scipy.spatial import cKDTree
sys.path.insert(0, os.path.dirname(__file__))
from paris4_gt import fibers_in_crop
from pred_tracer import decode_dir, coherence, trace

def walk_eval(T, tree, gid, own, tau):
    """steps along T (from its seed index) that stay within tau of GT fiber `own`."""
    d, i = tree.query(T)
    on = (d <= tau) & (gid[i] == own)
    if on.all(): return len(T), False
    return int(np.argmin(on)), True

def run(crop, kw, tau=1.5, region=4.0):
    d = np.load(crop)
    pr, dirs = d["presence"], decode_dir(d["nx"], d["ny"])
    coh = coherence(dirs, pr)
    G = fibers_in_crop(d["origin_L3"])
    gp = np.concatenate([g["pts"] for g in G]); gid = np.concatenate([np.full(len(g["pts"]), k) for k, g in enumerate(G)])
    tree = cKDTree(gp)
    gt_len = sum(np.linalg.norm(np.diff(g["pts"], axis=0), axis=1).sum() for g in G)
    # (1) GT-seeded
    st = collections.Counter(); corr_len = 0.0; ends = collections.Counter()
    for k, g in enumerate(G):
        if len(g["pts"]) < 10: continue
        s = g["pts"][len(g["pts"]) // 2]
        _, inf = None, None
        tr, info = trace(pr, dirs, coh, seeds=[s], use_claims=False, min_len=1, **kw)
        if not tr: st["no_trace"] += 1; continue
        T = tr[0]; si = int(np.argmin(np.linalg.norm(T - s, axis=1)))
        for half, endr in ((T[si:], info[0]["end_fwd"]), (T[:si + 1][::-1], info[0]["end_bwd"])):
            n_ok, dev = walk_eval(half, tree, gid, k, tau)
            corr_len += n_ok; st["halves"] += 1
            if dev: st["deviated"] += 1; ends["deviation"] += 1
            else: ends["abstain:" + endr] += 1
    # (2) automatic
    traces, info = trace(pr, dirs, coh, **kw)
    touched = clean = 0; covered = np.zeros(len(gp), bool); auto_len = 0.0
    for T in traces:
        auto_len += np.linalg.norm(np.diff(T, axis=0), axis=1).sum()
        dd, ii = tree.query(T)
        near = dd <= tau
        if near.sum() < 5: continue
        touched += 1
        ids = gid[ii[near]]
        top = collections.Counter(ids).most_common(1)[0][0]
        band = dd <= region  # inside GT's neighbourhood band
        ok = np.all((gid[ii[band]] == top) & (dd[band] <= tau))
        clean += ok
        if ok:
            pt = cKDTree(T); dg, _ = pt.query(gp, distance_upper_bound=tau); covered |= np.isfinite(dg) & (gid == top)
    return dict(crop=os.path.basename(crop), n_gt_runs=len(G), gt_len=float(gt_len),
                seeded_halves=st["halves"], seeded_deviation_rate=st["deviated"] / max(st["halves"], 1),
                seeded_mean_correct_steps=corr_len / max(st["halves"], 1), seeded_end_reasons=dict(ends),
                auto_traces=len(traces), auto_len=float(auto_len), auto_touching_gt=touched,
                auto_clean_frac=clean / max(touched, 1), auto_gt_recall=float(covered.mean()))

if __name__ == "__main__":
    kw = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    crops = sorted(glob.glob("/workspace/vesuvius/data/paris4_fiber_crops/L3_*.npz"))
    which = os.environ.get("CROPS")
    if which: crops = [c for c in crops if any(w in c for w in which.split(","))]
    res = [run(c, kw) for c in crops]
    for r in res: print(json.dumps(r))
    tag = os.environ.get("TAG")
    if tag: json.dump(dict(kw=kw, results=res), open(f"/workspace/vesuvius/out/fiber/paris4_{tag}.json", "w"), indent=1)
