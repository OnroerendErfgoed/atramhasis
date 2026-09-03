#!/usr/bin/env bash
#
# run_backend.sh - start the Atramhasis backend dev server (pserve/waitress) on
# http://localhost:6543. Atramhasis has no background workers, so this is just
# pserve. Used by `mise run server` and `mise run server:backend`.
#
set -euo pipefail

cd "$(dirname "$0")/.."

# --reload only when we have a terminal: pserve's reloader (hupper) monitors the
# controlling tty and hangs when it is started without one (from a CI job, a
# `setsid`, or a plain background job).
reload=()
if [[ -t 0 ]]; then
    reload=(--reload)
fi

echo "➜ Atramhasis dev server: http://localhost:6543  (Ctrl-C to stop)"
exec .venv/bin/pserve development.ini "${reload[@]}"
