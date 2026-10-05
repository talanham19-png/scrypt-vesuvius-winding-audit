"""Fetch a 3D crop [z0:z1, y0:y1, x0:x1] from a public zarr-v2 array over HTTPS (chunk by chunk)."""
import numpy as np, requests, numcodecs
from concurrent.futures import ThreadPoolExecutor

def fetch_crop(array_url, box, workers=16):
    meta = requests.get(f"{array_url}/.zarray", timeout=60).json()
    shape, ch = meta["shape"], meta["chunks"]; dt = np.dtype(meta["dtype"])
    codec = numcodecs.get_codec(meta["compressor"]) if meta["compressor"] else None
    sep = meta.get("dimension_separator", ".")
    (z0, z1), (y0, y1), (x0, x1) = box
    out = np.full((z1 - z0, y1 - y0, x1 - x0), meta.get("fill_value") or 0, dt)
    jobs = [(a, b, c) for a in range(z0 // ch[0], (z1 - 1) // ch[0] + 1)
            for b in range(y0 // ch[1], (y1 - 1) // ch[1] + 1) for c in range(x0 // ch[2], (x1 - 1) // ch[2] + 1)]
    s = requests.Session(); s.mount("https://", requests.adapters.HTTPAdapter(pool_maxsize=workers))
    def work(j):
        r = s.get(f"{array_url}/{sep.join(map(str, j))}", timeout=120)
        if r.status_code == 404: return
        r.raise_for_status()
        a = np.frombuffer(codec.decode(r.content) if codec else r.content, dt).reshape(ch)
        lo = [j[i] * ch[i] for i in range(3)]
        src, dst = [], []
        for i, (b0, b1) in enumerate(box):
            u0, u1 = max(lo[i], b0), min(lo[i] + ch[i], b1, shape[i])
            src.append(slice(u0 - lo[i], u1 - lo[i])); dst.append(slice(u0 - b0, u1 - b0))
        out[tuple(dst)] = a[tuple(src)]
    with ThreadPoolExecutor(workers) as ex: list(ex.map(work, jobs))
    return out
