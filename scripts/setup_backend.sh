#!/usr/bin/env bash
#
# setup_backend.sh - set up the Atramhasis development database.
#
# Runs the database part of the development setup that docs/source/development.rst
# describes: `alembic upgrade head`, `initialize_atramhasis_db` (demo data) and
# `dump_rdf` (a first RDF datadump).
#
# Non-destructive by default: an existing database is left alone, only migrated
# to head. Pass --overwrite (or set OVERWRITE=1) to wipe and rebuild it,
# including the demo data.
#
# Both database flavours supported by development.ini work:
#
#   * sqlite (the default)  - the database is a plain file, so "create" and
#     "drop" are just creating/removing that file.
#   * postgresql            - the database is created through
#     `docker exec postgis psql` (see docker-compose.yml), so no local psql
#     client is needed. Override the container with PG_CONTAINER.
#
# Used by `mise run setup` (setup:backend:db) and `mise run db:reset`. Relies on
# the venv already existing (produced by `mise install && mise run setup`).
#
set -euo pipefail

cd "$(dirname "$0")/.."

INI="${INI:-development.ini}"
OVERWRITE="${OVERWRITE:-0}"
for arg in "$@"; do
    case "$arg" in
        --overwrite|--force) OVERWRITE=1 ;;
        *) echo "Unknown argument: $arg (supported: --overwrite)" >&2; exit 2 ;;
    esac
done

# This script only sets up the database; it relies on the venv already existing
# (normally produced by `mise install && mise run setup`). Fail clearly when run
# standalone before that is in place.
if [[ ! -x .venv/bin/alembic ]]; then
    echo "Error: .venv not found - run 'mise install && mise run setup' first." >&2
    exit 1
fi
if [[ ! -f "${INI}" ]]; then
    echo "Error: ${INI} not found." >&2
    exit 1
fi

# Read a setting from the [app:main] section and expand pyramid's %(here)s.
ini_get() {
    local value
    value="$(sed -n "s/^[[:space:]]*$1[[:space:]]*=[[:space:]]*//p" "${INI}" | head -1)"
    echo "${value//%(here)s/${PWD}}"
}

db_url="$(ini_get 'sqlalchemy\.url')"
if [[ -z "${db_url}" ]]; then
    echo "Error: no sqlalchemy.url found in ${INI}." >&2
    exit 1
fi

db_created=0

case "${db_url}" in
    sqlite:*)
        db_file="${db_url#sqlite:///}"
        if [[ -f "${db_file}" && "${OVERWRITE}" == "0" ]]; then
            echo "SQLite database '${db_file}' already exists - skipping create + seed (use --overwrite to recreate)."
        else
            [[ -f "${db_file}" ]] && echo "Overwriting SQLite database '${db_file}'..." \
                                  || echo "Creating SQLite database '${db_file}'..."
            rm -f "${db_file}"
            db_created=1
        fi
        ;;
    postgresql*|postgres:*)
        PG_CONTAINER="${PG_CONTAINER:-postgis}"
        db_name="${db_url##*/}"
        db_name="${db_name%%\?*}"
        pg() { docker exec "${PG_CONTAINER}" psql -U postgres "$@"; }
        if pg -tAc "SELECT 1 FROM pg_database WHERE datname='${db_name}'" | grep -q 1 \
           && [[ "${OVERWRITE}" == "0" ]]; then
            echo "Database '${db_name}' already exists - skipping create + seed (use --overwrite to recreate)."
        else
            [[ "${OVERWRITE}" != "0" ]] && echo "Overwriting database '${db_name}'..." \
                                        || echo "Creating database '${db_name}'..."
            pg -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='${db_name}'" >/dev/null
            pg -c "DROP DATABASE IF EXISTS ${db_name}"
            pg -c "CREATE DATABASE ${db_name}"
            db_created=1
        fi
        ;;
    *)
        echo "Error: unsupported sqlalchemy.url '${db_url}' (expected sqlite or postgresql)." >&2
        exit 1
        ;;
esac

# Always migrate to head, also for a database that already existed, so an older
# development database picks up new migrations without losing its data.
echo "Running alembic migrations..."
.venv/bin/alembic upgrade head

if [[ "${db_created}" -eq 1 ]]; then
    echo "Seeding the database with the demo vocabularies..."
    .venv/bin/initialize_atramhasis_db "${INI}"

    dump_location="$(ini_get 'atramhasis\.dump_location')"
    if [[ -n "${dump_location}" ]]; then
        echo "Generating a first RDF datadump in '${dump_location}'..."
        mkdir -p "${dump_location}"
        # Best effort: the datadumps are only needed for the RDF downloads and
        # the optional LDF server, and dumping some of the demo vocabularies
        # currently trips over an upstream bug. Never fail the whole setup on it.
        .venv/bin/dump_rdf "${INI}" || echo "Warning: dump_rdf failed - the RDF datadumps are incomplete. Re-run '.venv/bin/dump_rdf ${INI}' yourself if you need them." >&2
    fi
fi

echo "Backend setup done."
