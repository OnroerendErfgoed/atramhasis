#!/usr/bin/env bash
#
# run_frontend.sh - start the frontend (Vite) dev server for the Vue admin app.
#
# With `vue.mode = src` in development.ini (the default) the admin page loads its
# modules straight from this dev server, so you get hot reloading. Used by
# `mise run server` (alongside the backend) and by `mise run server:frontend`.
#
set -euo pipefail

cd "$(dirname "$0")/.."

echo "➜ Atramhasis frontend dev server: http://localhost:5173  (Ctrl-C to stop)"
exec pnpm --dir frontend dev
