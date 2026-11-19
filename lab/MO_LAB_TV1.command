#!/bin/zsh
set -e
cd -- "$(dirname "$0")/.." || exit 1
python3 lab/tv1.py prepare --run runs/r2412007
exec python3 lab/review_server.py --run runs/r2412007 --port 8765 --open
