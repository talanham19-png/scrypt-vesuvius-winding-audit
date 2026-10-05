"""Auto relative-winding chains for the Atrium fit range (z 10900-11300): 4 slices, same method and
export rule (conf >= 0.99, fixed earlier on the dev slice). Writes out/winding/fit_slices/auto_rel_z10900_11300.json."""
import sys, os, json, pickle, time
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from auto_winding2d import run_slice, umbilicus_yx
from export_pcl import chains_from_solution, to_pcl
D = "/workspace/vesuvius/data"; O = "/workspace/vesuvius/out/winding/fit_slices"
ZS = [10950, 11050, 11150, 11250]
allc = []
for z in ZS:
    t0 = time.time(); plane = np.load(f"{D}/planes/m7_z{z}.npy"); cy, cx = umbilicus_yx(f"{D}/spiral/umbilicus.json", z)
    sol = run_slice(plane, cy, cx); del plane
    ch = chains_from_solution(sol, z); allc += [(z, c) for c in ch]
    print(z, "sigma", sol["sigma"], len(ch), "chains", sum(len(c) for c in ch), "points", f"{time.time()-t0:.0f}s", flush=True)
    del sol
js = to_pcl(allc, "scrypt_auto")
json.dump(js, open(f"{O}/auto_rel_z10900_11300.json", "w"))
print("wrote", len(js["collections"]), "collections")
