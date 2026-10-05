"""Export automatically derived relative-winding chains as a VC3D point-collection JSON
(same schema as spiral-input relative_windings.json: vc_pointcollections_json_version "1",
collections{id:{name,color,metadata{winding_is_absolute:false},points{id:{p:[x,y,z],wind_a,creation_time}}}}).
Points are in full-resolution fit coordinates (PHercParis4 2.4um level-2 / 'reference' voxels)."""
import json, math, pickle, sys, glob, os, re
import numpy as np

def chains_from_solution(sol, z, every=40, min_conf=0.99, min_pts=3):
    y0, x0 = sol["offset"]; root, k, conf, sg = sol["root"], sol["k"], sol["conf"], sol["sigma"]
    out = []
    for ri in range(0, len(sol["ray_records"]), every):
        cr = sol["ray_records"][ri]
        cur = []
        def flush():
            if len(cur) >= min_pts: out.append(list(cur))
            cur.clear()
        for (t, L, run, iy, ix) in cr:
            if L <= 0 or root[L] < 0 or conf[L] < min_conf:
                flush(); continue
            th = math.atan2(iy - sol["cy"], ix - sol["cx"])
            s = k[L] + sg * th / (2 * math.pi)
            if cur and (root[cur[-1][3]] != root[L] or round(s - cur[-1][2]) != 1):
                flush()  # only emit strictly consecutive (+1) chains in one solved component
            cur.append((float(ix + x0), float(iy + y0), s, L))
        flush()
    return out

def to_pcl(all_chains, name_prefix="auto"):
    cols = {}; pid = 1
    for ci, (z, ch) in enumerate(all_chains, 1):
        s0 = ch[0][2]
        pts = {}
        for (x, y, s, L) in ch:
            pts[str(pid)] = {"p": [x, y, float(z)], "wind_a": float(round(s - s0)), "creation_time": 0}; pid += 1
        cols[str(ci)] = {"name": f"{name_prefix}{ci}", "color": [1.0, 0.5, 0.0],
                         "metadata": {"winding_is_absolute": False, "source": "scrypt auto_winding2d v0"}, "points": pts}
    return {"vc_pointcollections_json_version": "1", "collections": cols}

if __name__ == "__main__":
    allc = []
    for f in sorted(glob.glob("/workspace/vesuvius/out/winding/sol_z*.pkl")):
        z = int(re.search(r"z(\d+)", f).group(1))
        sol = pickle.load(open(f, "rb"))
        ch = chains_from_solution(sol, z)
        allc += [(z, c) for c in ch]
        print(z, len(ch), "chains", sum(len(c) for c in ch), "points")
    js = to_pcl(allc)
    json.dump(js, open("/workspace/vesuvius/out/winding/auto_relative_windings.json", "w"))
    print("wrote", len(js["collections"]), "collections")
