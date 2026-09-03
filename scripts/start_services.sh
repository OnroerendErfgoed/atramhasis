#!/usr/bin/env bash
#
# start_services.sh - bring up the local service stack, skipping anything that is
# already reachable.
#
# Checks each service's port on localhost and only `docker compose up`s the ones
# that are not already running - so it is safe to run when you already have
# postgis / redis / minio running another way (no container-name or port
# clashes). Used by `mise run docker`.
#
# This only checks reachability (is something listening on the port), not the
# image version. Pass --force to start the full compose stack regardless.
#
# None of these services are required to run or test Atramhasis; see the header
# of docker-compose.yml for why they are here.
#
set -euo pipefail

cd "$(dirname "$0")/.."

# service:port pairs - keep in sync with docker-compose.yml
services=(
    "postgis:5432"
    "redis:6379"
    "minio:9000"
)

if [[ "${1:-}" == "--force" ]]; then
    docker compose up -d
    exit 0
fi

port_open() {
    # bash builtin /dev/tcp - no nc/curl needed
    (exec 3<>"/dev/tcp/127.0.0.1/$1") 2>/dev/null && exec 3>&- && return 0
    return 1
}

missing=()
for entry in "${services[@]}"; do
    name="${entry%%:*}"
    port="${entry##*:}"
    if port_open "${port}"; then
        echo "✓ ${name} already reachable on :${port} - skipping"
    else
        missing+=("${name}")
    fi
done

if [[ ${#missing[@]} -eq 0 ]]; then
    echo "All services already running - nothing to start."
else
    echo "Starting: ${missing[*]}"
    docker compose up -d "${missing[@]}"
fi
