#!/bin/sh
set -e

python3 fetch.py

( while true; do sleep "${SCRAPE_INTERVAL:-1200}"; python3 fetch.py; done ) &

exec python3 -m http.server 8000 --directory site
