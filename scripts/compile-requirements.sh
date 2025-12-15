#!/bin/bash
set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR/.."

BASE_PIP_COMPILE_ARGS="-q --no-header --strip-extras --resolver=backtracking --no-emit-options --no-emit-trusted-host --no-emit-find-links"
PYTHON_VERSIONS="3.10 3.11 3.12 3.13.10"

for version in $PYTHON_VERSIONS; do
    PIP_COMPILE_ARGS="$BASE_PIP_COMPILE_ARGS --python-version ${version}"
    echo "Compiling $version requirements-dev-py$version.txt..."
    uv pip compile $PIP_COMPILE_ARGS --all-extras -o "$SCRIPT_DIR/../lockfiles/requirements-dev-py$version.txt" pyproject.toml
    echo " └Done"
done

cd -
