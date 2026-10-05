"""Subset the published winding_inference store to rays whose crossing z-span intersects [Z0, Z1);
rewrite one shard with fresh sha256 and the manifest fingerprint exactly as winding_supervision.py checks it."""
import json, copy, hashlib, os, sys
import numpy as np
SRC = "/workspace/vesuvius/data/spiral/winding_inference"; DST = "/workspace/vesuvius/atrium/dataset/winding_inference"
Z0, Z1 = 10900 - 32, 11300 + 32
def digest(v): return hashlib.sha256(json.dumps(v, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
m = json.load(open(f"{SRC}/manifest.json"))
O, S, T, L, W, OFF = [], [], [], [], [], [np.array([0], np.int64)]; base = 0
for sh in m["shards"]:
    r = f"{SRC}/{sh['name']}"
    o = np.load(f"{r}/ray_origin_zyx.npy"); st = np.load(f"{r}/ray_step_zyx.npy"); t = np.load(f"{r}/crossing_t.npy")
    lv = np.load(f"{r}/crossing_level.npy"); off = np.load(f"{r}/crossing_offsets.npy"); sw = np.load(f"{r}/seed_winding.npy")
    zA = o[:, 0] + t[off[:-1]] * st[:, 0]; zB = o[:, 0] + t[off[1:] - 1] * st[:, 0]
    keep = np.where((np.maximum(zA, zB) >= Z0) & (np.minimum(zA, zB) < Z1))[0]
    for i in keep:
        a, b = off[i], off[i + 1]; T.append(t[a:b]); L.append(lv[a:b]); base += b - a; OFF.append(np.array([base], np.int64))
    O.append(o[keep]); S.append(st[keep]); W.append(sw[keep])
arrs = dict(ray_origin_zyx=np.concatenate(O), ray_step_zyx=np.concatenate(S), seed_winding=np.concatenate(W),
            crossing_t=np.concatenate(T), crossing_level=np.concatenate(L), crossing_offsets=np.concatenate(OFF))
proto = m["shards"][0]
os.makedirs(f"{DST}/s0", exist_ok=True)
shard = {k: copy.deepcopy(v) for k, v in proto.items() if k not in ("arrays", "name")}
shard["name"] = "s0"; shard["arrays"] = {}
for k, a in arrs.items():
    a = a.astype(np.dtype(proto["arrays"][k]["dtype"]), copy=False)
    f = f"{DST}/s0/{proto['arrays'][k]['file']}"; np.save(f, a)
    shard["arrays"][k] = dict(file=proto["arrays"][k]["file"], shape=list(a.shape), dtype=a.dtype.str, bytes=os.path.getsize(f),
                              sha256=hashlib.sha256(open(f, "rb").read()).hexdigest())
for k in list(shard):
    if k in ("num_rays", "num_crossings"): pass
if "num_rays" in shard: shard["num_rays"] = int(len(arrs["ray_origin_zyx"]))
if "num_crossings" in shard: shard["num_crossings"] = int(len(arrs["crossing_t"]))
nm = copy.deepcopy(m); nm["shards"] = [shard]; nm["num_rays"] = int(len(arrs["ray_origin_zyx"])); nm["num_crossings"] = int(len(arrs["crossing_t"]))
nm["scrypt_subset"] = f"rays intersecting z [{Z0},{Z1}) of fingerprint {m['fingerprint']}"
iv = copy.deepcopy(nm); iv.pop("fingerprint", None); iv.pop("elapsed_seconds", None); iv.pop("export_workers", None); iv.pop("rays_per_task", None)
for s in iv.get("shards", []): s.pop("elapsed_seconds", None)
nm["fingerprint"] = digest(iv)
json.dump(nm, open(f"{DST}/manifest.json", "w"), indent=1)
print("shard keys", list(proto.keys())); print("rays", nm["num_rays"], "crossings", nm["num_crossings"])
