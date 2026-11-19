#!/bin/zsh
cd -- "$(dirname "$0")/.." || exit 1
exec python3 lab/review_server.py --run runs/r2412007 --port 8765 --open
