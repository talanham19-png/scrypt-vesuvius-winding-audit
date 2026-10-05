"""Parse WEBKNOSSOS NML fiber skeletons -> list of polylines (N,3) zyx in cube-local voxels."""
import re, xml.etree.ElementTree as ET
import numpy as np

def parse_nml(path, offset_zyx=(0, 0, 0)):
    root = ET.parse(path).getroot()
    fibers = []
    for th in root.iter("thing"):
        nodes = {int(n.get("id")): (float(n.get("z")), float(n.get("y")), float(n.get("x"))) for n in th.iter("node")}
        edges = [(int(e.get("source")), int(e.get("target"))) for e in th.iter("edge")]
        if not nodes: continue
        fibers.append(dict(id=int(th.get("id")), name=th.get("name"), nodes=nodes, edges=edges))
    off = np.array(offset_zyx, float)
    for f in fibers:
        f["nodes"] = {k: np.array(v) - off for k, v in f["nodes"].items()}
    return fibers

def densify(fibers, step=0.5):
    """sample every edge at `step` voxels -> (M,3) points and (M,) fiber index"""
    pts, ids = [], []
    for fi, f in enumerate(fibers):
        for a, b in f["edges"]:
            pa, pb = f["nodes"][a], f["nodes"][b]
            n = max(int(np.ceil(np.linalg.norm(pb - pa) / step)), 1)
            t = np.linspace(0, 1, n + 1)[:, None]
            pts.append(pa + t * (pb - pa)); ids.append(np.full(n + 1, fi))
        if not f["edges"]:
            for p in f["nodes"].values(): pts.append(p[None]); ids.append(np.array([fi]))
    return np.concatenate(pts), np.concatenate(ids)
