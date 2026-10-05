#!/usr/bin/env bash
# One-command diagnosis checker (CPU). Does not publish or download large volumes.
set -euo pipefail
cd "$(dirname "$0")"
python -m checker self-check "$@"
echo "Generic audit: python -m checker audit --winding-inference DIR [--relative-windings JSON]"
