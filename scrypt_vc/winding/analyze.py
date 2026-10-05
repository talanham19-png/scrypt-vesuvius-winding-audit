"""Summaries for STATUS.md: graph method vs straight-line crossing-count baseline on identical pairs,
dev (z=15334, used for the one tuning decision) vs held-out slices, and confidence abstention curve."""
import json, math, sys, os, collections
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from eval_slices import human_chains, baseline_count, DATA
from auto_winding2d import preprocess
E = json.load(open(f"{DATA}/../out/winding/eval.json"))
rows = E["rows"]
by_z = collections.defaultdict(list)
for r in rows: by_z[r[0]].append(r)
out = {}
base = {}
for z in sorted(by_z):
    mask = preprocess(np.load(f"{DATA}/planes/m7_z{z}.npy"))
    ch = {cid: pts for cid, name, pts in human_chains(z)}
    for r in by_z[z]:
        if not r[6]: continue
        (xa, ya, _), wa = ch[r[1]][r[2]]; (xb, yb, _), wb = ch[r[1]][r[3]]
        base[(z, r[1], r[2], r[3])] = baseline_count(mask, ya, xa, yb, xb)
    del mask
def summarize(sel, name):
    c = [r for r in sel if r[6]]; l = [r for r in sel if not r[6]]
    s = dict(consec_n=len(c), consec_graph_acc=np.mean([r[4] == r[5] for r in c]) if c else None,
             consec_baseline_acc=np.mean([base[(r[0], r[1], r[2], r[3])] == abs(r[4]) for r in c]) if c else None,
             long_n=len(l), long_graph_acc=np.mean([r[4] == r[5] for r in l]) if l else None)
    # long-range accuracy vs |delta|
    bins = collections.defaultdict(list)
    for r in l: bins[min(abs(r[4]) // 5 * 5, 30)].append(r[4] == r[5])
    s["long_acc_by_absdelta"] = {f"{k}-{k+4}" if k < 30 else "30+": (round(float(np.mean(v)), 3), len(v)) for k, v in sorted(bins.items())}
    out[name] = s
summarize(rows, "all_slices")
summarize([r for r in rows if r[0] == 15334], "dev_z15334")
summarize([r for r in rows if r[0] != 15334], "heldout_7_slices")
# abstention curve on held-out consecutive + long pairs by min chunk confidence
ho = [r for r in rows if r[0] != 15334]
curve = []
for t in (0.0, 0.8, 0.9, 0.95, 0.99, 1.0):
    sel = [r for r in ho if r[7] >= t]
    c = [r for r in sel if r[6]]; l = [r for r in sel if not r[6]]
    curve.append(dict(min_conf=t, consec_kept=len(c), consec_acc=round(float(np.mean([r[4] == r[5] for r in c])), 3) if c else None,
                      long_kept=len(l), long_acc=round(float(np.mean([r[4] == r[5] for r in l])), 3) if l else None))
out["heldout_conf_curve"] = curve
print(json.dumps(out, indent=1, default=float))
json.dump(out, open(f"{DATA}/../out/winding/summary.json", "w"), indent=1, default=float)
