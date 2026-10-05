"""Score automatic relative windings vs human relative_windings.json chains on the same z-slices."""
import json, math, sys, os, time, collections, pickle
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from auto_winding2d import run_slice, s_value, umbilicus_yx, preprocess

DATA = "/workspace/vesuvius/data"
def wrap(a): return (a + math.pi) % (2 * math.pi) - math.pi

def human_chains(z, tol=2.0):
    d = json.load(open(f"{DATA}/spiral/relative_windings.json"))["collections"]
    out = []
    for cid, c in d.items():
        pts = [(p["p"], p["wind_a"]) for p in c["points"].values() if p.get("wind_a") is not None]
        if len(pts) < 2 or any(abs(p[0][2] - z) > tol for p in pts): continue
        pts.sort(key=lambda t: t[1])
        out.append((cid, c["name"], pts))
    return out

def baseline_count(mask, ya, xa, yb, xb, ext=2.0):
    L = math.hypot(yb - ya, xb - xa)
    if L < 1e-6: return 0
    uy, ux = (yb - ya) / L, (xb - xa) / L
    t = np.arange(-ext, L + ext, 0.5)
    iy = np.rint(ya + uy * t).astype(int); ix = np.rint(xa + ux * t).astype(int)
    ok = (iy >= 0) & (iy < mask.shape[0]) & (ix >= 0) & (ix < mask.shape[1])
    v = mask[iy[ok], ix[ok]].astype(np.int8)
    runs = int((np.diff(np.r_[0, v]) == 1).sum())
    return max(runs - 1, 0)

def evaluate(z, sol, mask):
    chains = human_chains(z)
    st = collections.Counter()
    rows = []
    for cid, name, pts in chains:
        S = []
        for (x, y, _), w in pts:
            S.append(s_value(sol, y, x))
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                consec = (j == i + 1)
                tag = "consec" if consec else "long"
                (xa, ya, _), wa = pts[i]; (xb, yb, _), wb = pts[j]
                dh = wb - wa
                st[tag + "_total"] += 1
                if consec:
                    b = baseline_count(mask, ya, xa, yb, xb)
                    st["base_abs_correct"] += (b == abs(dh))
                if S[i] is None or S[j] is None:
                    st[tag + "_unsnapped"] += 1; continue
                if S[i][0] != S[j][0]:
                    st[tag + "_diffcomp"] += 1; continue
                ds = S[j][1] - S[i][1] - sol["sigma"] * wrap(S[j][2] - S[i][2]) / (2 * math.pi)
                dp = int(round(ds))
                st[tag + "_eval"] += 1
                st[tag + "_signed_correct"] += (dp == dh)
                st[tag + "_flip_correct"] += (dp == -dh)
                st[tag + "_abs_correct"] += (abs(dp) == abs(dh))
                rows.append((z, cid, i, j, dh, dp, consec, float(min(sol['conf'][S[i][3]], sol['conf'][S[j][3]])), float(math.hypot(yb-ya, xb-xa))))
    return st, rows

if __name__ == "__main__":
    zs = [int(a) for a in sys.argv[1:]] or [15334]
    allst = collections.Counter(); allrows = []
    os.makedirs(f"{DATA}/../out/winding", exist_ok=True)
    for z in zs:
        t0 = time.time()
        plane = np.load(f"{DATA}/planes/m7_z{z}.npy")
        cy, cx = umbilicus_yx(f"{DATA}/spiral/umbilicus.json", z)
        print(f"z={z} umbilicus yx=({cy:.0f},{cx:.0f})")
        sol = run_slice(plane, cy, cx)
        mask = preprocess(plane)
        del plane
        st, rows = evaluate(z, sol, mask)
        del mask
        print(f"  sigma={sol['sigma']} eval: {dict(st)} ({time.time()-t0:.0f}s)", flush=True)
        allst.update(st); allrows += rows
        pickle.dump({k: v for k, v in sol.items() if k not in ("labd",)}, open(f"{DATA}/../out/winding/sol_z{z}.pkl", "wb"))
        del sol
    print("TOTAL", dict(allst))
    json.dump({"stats": dict(allst), "rows": allrows}, open(f"{DATA}/../out/winding/eval.json", "w"))
