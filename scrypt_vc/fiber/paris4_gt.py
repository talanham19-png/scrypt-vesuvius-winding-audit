"""Load VC3D eval fibers (spiral-input eval_fibers/*.json, line_points [x,y,z] base 2.4um voxels)
as polylines in a given L3 crop's local zyx coordinates."""
import json, glob, numpy as np
EF = "/workspace/vesuvius/data/spiral/eval_fibers"
_cache = None
def all_fibers():
    global _cache
    if _cache is None:
        _cache = []
        for f in sorted(glob.glob(EF + "/*.json")):
            d = json.load(open(f))
            _cache.append(dict(file=f.split("/")[-1], tag=d["hv_classification"].get("manual_tag") or d["hv_classification"]["automatic_tag"],
                               zyx=np.array(d["line_points"], float)[:, ::-1]))
    return _cache
def fibers_in_crop(origin_L3, size=256, scale=8.0, margin=2):
    out = []
    for fi, f in enumerate(all_fibers()):
        p = f["zyx"] / scale - np.asarray(origin_L3)
        ins = np.all((p >= margin) & (p < size - margin), axis=1)
        if ins.sum() < 5: continue
        # split into contiguous inside runs
        idx = np.nonzero(ins)[0]; br = np.nonzero(np.diff(idx) > 1)[0]
        for run in np.split(idx, br + 1):
            if len(run) >= 5: out.append(dict(fid=fi, tag=f["tag"], pts=p[run]))
    return out
