"""Fetch single z-planes from a public OME-Zarr (zarr v2, blosc/none) on the VC S3 bucket
without materialising whole chunk rows (memory-safe: decodes one chunk at a time).

Usage: python -m common.fetch_plane --zarr URL --level 0 --z 15334 [--z ...] --out DIR [--halfwidth 1]
Saves DIR/<name>_z<z>.npy containing max over [z-halfwidth, z+halfwidth] (uint8).
"""
import argparse, json, os, sys
from concurrent.futures import ThreadPoolExecutor
import numpy as np, requests
import numcodecs

S3 = "https://vesuvius-challenge-open-data.s3.us-east-1.amazonaws.com"

def get_meta(url, level):
    return requests.get(f"{url}/{level}/.zarray", timeout=60).json()

def fetch_planes(url, level, zs, halfwidth=1, workers=16, yx_box=None):
    meta = get_meta(url, level)
    shape, chunks = meta["shape"], meta["chunks"]
    codec = numcodecs.get_codec(meta["compressor"]) if meta["compressor"] else None
    sep = meta.get("dimension_separator", ".")
    dtype = np.dtype(meta["dtype"])
    y0, y1, x0, x1 = yx_box if yx_box else (0, shape[1], 0, shape[2])
    out = {z: np.zeros((y1 - y0, x1 - x0), dtype) for z in zs}
    jobs = []
    rows = {}
    for z in zs:
        for zz in range(max(0, z - halfwidth), min(shape[0], z + halfwidth + 1)):
            rows.setdefault(zz // chunks[0], set()).add((z, zz))
    for cz, zset in rows.items():
        for cy in range(y0 // chunks[1], (y1 - 1) // chunks[1] + 1):
            for cx in range(x0 // chunks[2], (x1 - 1) // chunks[2] + 1):
                jobs.append((cz, cy, cx, zset))
    sess = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_maxsize=workers)
    sess.mount("https://", adapter)
    nbytes = [0]
    def work(job):
        cz, cy, cx, zset = job
        key = sep.join(map(str, (cz, cy, cx)))
        for attempt in range(4):
            try:
                r = sess.get(f"{url}/{level}/{key}", timeout=120)
                break
            except Exception:
                if attempt == 3: raise
        if r.status_code == 404:
            return
        r.raise_for_status()
        buf = r.content
        nbytes[0] += len(buf)
        raw = codec.decode(buf) if codec else buf
        a = np.frombuffer(raw, dtype).reshape(chunks)
        # chunk spatial extent
        ys, xs = cy * chunks[1], cx * chunks[2]
        for z, zz in zset:
            pl = a[zz - cz * chunks[0]]
            yy0, xx0 = max(ys, y0), max(xs, x0)
            yy1, xx1 = min(ys + chunks[1], y1, shape[1]), min(xs + chunks[2], x1, shape[2])
            sub = pl[yy0 - ys:yy1 - ys, xx0 - xs:xx1 - xs]
            tgt = out[z][yy0 - y0:yy1 - y0, xx0 - x0:xx1 - x0]
            np.maximum(tgt, sub, out=tgt)
    with ThreadPoolExecutor(workers) as ex:
        for i, _ in enumerate(ex.map(work, jobs)):
            if i % 200 == 0:
                print(f"  {i}/{len(jobs)} chunks, {nbytes[0]/1e6:.0f} MB", flush=True)
    print(f"done: {len(jobs)} chunks, {nbytes[0]/1e6:.0f} MB downloaded", flush=True)
    return out

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--zarr", required=True)
    ap.add_argument("--level", default="0")
    ap.add_argument("--z", type=int, action="append", required=True)
    ap.add_argument("--halfwidth", type=int, default=1)
    ap.add_argument("--out", required=True)
    ap.add_argument("--name", default="plane")
    ap.add_argument("--workers", type=int, default=16)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for z in a.z:  # one z at a time keeps memory at one plane (+ one chunk per worker)
        dst = os.path.join(a.out, f"{a.name}_z{z}.npy")
        if os.path.exists(dst):
            print("skip", dst); continue
        planes = fetch_planes(a.zarr, a.level, [z], a.halfwidth, a.workers)
        np.save(dst, planes[z]); print("saved", dst, flush=True)
