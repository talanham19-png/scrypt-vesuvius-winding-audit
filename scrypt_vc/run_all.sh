#!/usr/bin/env bash
# Reproduce the first-pass results (CPU only; ~15 min on 8 cores, peak RAM ~3 GB, ~2.3 GB downloads).
set -euo pipefail
cd "$(dirname "$0")"
D=../data; S3=https://vesuvius-challenge-open-data.s3.us-east-1.amazonaws.com
B=https://dl.ash2txt.org/datasets/spiral_datasets/PHercParis4
mkdir -p $D/spiral $D/planes ../out/winding ../out/fiber
# --- inputs (small) ---
for f in abs_winding.json relative_windings.json same_windings.json umbilicus.json; do
  [ -f $D/spiral/$f ] || curl -sSL -o $D/spiral/$f $B/$f; done
# --- A: surface-prediction planes (m7 surface model, level 0 = fit coordinates), ~190 MB each ---
ZS="15334 8750 16920 8450 11432 15876 8879 11714"
python -m common.fetch_plane --zarr $S3/PHercParis4/representations/predictions/surfaces/20260411134726-surface-20260413222639-surface-m7-L2-th0.2.zarr \
  --level 0 --name m7 --out $D/planes $(for z in $ZS; do echo --z $z; done)
python winding/eval_slices.py $ZS
python winding/analyze.py
python winding/export_pcl.py
# --- B: eval fibers (287 MB) + fiber-prediction crops (L3, 4 x 256^3) ---
mkdir -p $D/spiral/eval_fibers
curl -sSL $B/eval_fibers/ | grep -oE 'href="[^"]+\.json"' | sed 's/href="//;s/"//' | \
  xargs -P 8 -I{} sh -c "[ -f $D/spiral/eval_fibers/{} ] || curl -sSL -o $D/spiral/eval_fibers/{} $B/eval_fibers/{}"
python fiber/fetch_paris4_crops.py
CROPS=23_5_8 TAG=dev_default python fiber/eval_paris4.py '{}'
for cfg in 'permissive:{"stop_presence": 110, "min_coherence": 0.7, "fork_ratio": 0}' 'default:{}' 'conservative:{"min_coherence": 0.93}'; do
  CROPS=24_7_5,22_9_8,20_4_8 TAG=test_${cfg%%:*} python fiber/eval_paris4.py "${cfg#*:}"; done
python fiber/export_vc3d.py $D/paris4_fiber_crops/L3_23_5_8.npz ../out/fiber/vc3d_auto_L3_23_5_8
# --- B0 (negative result): raw-CT classical tracer vs fiber-skeletons cubes (needs the 422 MB zip unpacked in $D) ---
# TAG=raw_st python fiber/eval_fibers.py s1_8997

# --- Diagnosis checker (CPU; needs winding_inference already under data/spiral/) ---
# Skip if winding_inference is missing. Does not re-download planes.
if [ -d "$D/spiral/winding_inference" ]; then
  python -m checker --dr 6 || true
  echo "(optional) python -m checker --dr 8 && python -m checker --verify"
fi
