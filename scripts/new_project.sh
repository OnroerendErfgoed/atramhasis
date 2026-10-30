#!/usr/bin/env bash
#
# new_project.sh - create a new project that uses Atramhasis as a library.
#
# Generates the project from one of the cookiecutter templates in this checkout
# (cookiecutters/demo or cookiecutters/scaffold), then installs and sets it up
# with mise: every generated project ships its own mise.toml.
#
# Used by `mise run new-project`; see `mise run new-project --help`. Arguments
# come in through the usage_* environment variables mise sets:
#
#   usage_type              demo | scaffold
#   usage_output_dir        directory to create the project in
#   usage_local_atramhasis  "true": install this checkout (editable) instead of
#                           the released atramhasis package
#
set -euo pipefail

ATRAMHASIS_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TYPE="${usage_type:?}"
OUTPUT_DIR="${usage_output_dir:-$HOME/dev}"
OUTPUT_DIR="${OUTPUT_DIR/#\~/$HOME}"
LOCAL_ATRAMHASIS="${usage_local_atramhasis:-false}"

# Let cookiecutter generate into an empty temporary directory, so the project it
# created (named after the root_folder prompt) is simply its only child.
mkdir -p "${OUTPUT_DIR}"
tmp="$(mktemp -d "${OUTPUT_DIR}/.new-project.XXXXXX")"
trap 'rm -rf "${tmp}"' EXIT

echo "➜ Generating a ${TYPE} project (cookiecutter may ask a few questions)..."
uvx cookiecutter "${ATRAMHASIS_DIR}/cookiecutters/${TYPE}" --output-dir "${tmp}"

name="$(ls -A "${tmp}")"
project="${OUTPUT_DIR}/${name}"
if [[ -e "${project}" ]]; then
    echo "Error: ${project} already exists." >&2
    exit 1
fi
mv "${tmp}/${name}" "${project}"

# Leave the atramhasis environment behind: the new project gets its own venv,
# which mise activates from the project's own mise.toml.
cd "${project}"
unset VIRTUAL_ENV
mise trust
mise install
mise run setup
if [[ "${LOCAL_ATRAMHASIS}" == "true" ]]; then
    mise run atramhasis:local "${ATRAMHASIS_DIR}"
fi

echo
echo "✔ Created ${project}"
echo "  cd ${project} && mise run server"
