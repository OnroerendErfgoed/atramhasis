#!/usr/bin/env bash
#
# start_services.sh - start the PostgreSQL service of docker-compose.yml, unless
# something is already listening on port 5432.
#
# That way it is safe to run when you already have a PostgreSQL server running
# another way (a native install or another container): no port clashes, and
# the atramhasis database is simply created on that server. Used by
# `mise run docker`.
#
# PostgreSQL is not required to run or test Atramhasis; see the header of
# docker-compose.yml.
#
set -euo pipefail

cd "$(dirname "$0")/.."

# bash builtin /dev/tcp - no nc/curl needed
if (exec 3<>/dev/tcp/127.0.0.1/5432) 2>/dev/null; then
    echo "✓ Something is already listening on :5432 - not starting postgres."
else
    docker compose up -d --wait postgres
fi
