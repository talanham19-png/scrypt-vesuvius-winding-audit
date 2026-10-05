"""Trace a fiber-prediction crop and write each trace as a VC3D fiber JSON (vc3d_fiber, version 1:
control_points + line_points as [x, y, z] in full-resolution base voxels), validated with the
official villa parser (vesuvius/src/vc3d_fiber_format). Usage: export_vc3d.py CROP.npz OUTDIR [kw-json]"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, "/workspace/vesuvius/villa/vesuvius/src")
from pred_tracer import decode_dir, coherence, trace
from vc3d_fiber_format import parse_vc3d_fiber_format

def main(crop, outdir, kw, scale=8.0, min_len=15, cp_every=20):
    d = np.load(crop); pr = d["presence"]; dirs = decode_dir(d["nx"], d["ny"]); coh = coherence(dirs, pr)
    traces, info = trace(pr, dirs, coh, **kw)
    os.makedirs(outdir, exist_ok=True); n = 0
    for k, (T, inf) in enumerate(zip(traces, info)):
        if len(T) < min_len: continue
        base = (T + d["origin_L3"]) * scale + (scale - 1) / 2.0  # L3 voxel centre -> base voxel coords
        xyz = base[:, ::-1]
        cps = xyz[::cp_every].tolist()
        if len(T) - 1 not in range(0, len(T), cp_every): cps.append(xyz[-1].tolist())
        t = T[-1] - T[0]; tz = abs(t[0]) / (np.linalg.norm(t) + 1e-9)
        obj = {"type": "vc3d_fiber", "version": 1, "generation": 1, "control_points": cps,
               "line_points": xyz.tolist(),
               "hv_classification": {"automatic_tag": "V" if tz > 0.7 else "H", "automatic_certainty": float(abs(tz - 0.5) * 2), "manual_tag": ""},
               "scrypt": {"tool": "scrypt_vc pred_tracer v0", "end_reasons": [inf["end_bwd"], inf["end_fwd"]],
                          "mean_presence": inf["mean_presence"], "source_level": 3, "unverified": True}}
        parse_vc3d_fiber_format(obj)  # raises if VC3D/spiral-fit parser would reject it
        json.dump(obj, open(f"{outdir}/auto_{k:05d}.json", "w")); n += 1
    print(f"wrote {n} fibers to {outdir} (all passed parse_vc3d_fiber_format)")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], json.loads(sys.argv[3]) if len(sys.argv) > 3 else {"min_coherence": 0.93})
