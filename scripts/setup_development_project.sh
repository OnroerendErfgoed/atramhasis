#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   VENV_PATH="$HOME/Envs" VENV_NAME="atramhasis_dev" PROJECT_DIR="$HOME/dev/atramhasis" ./scripts/setup_development_env.sh
#
# This script sets up a local development environment for atramhasis.
# It assumes the repository is already cloned (or uses PROJECT_DIR to point to an existing clone).
#
# Steps performed:
#   1. Create (or reuse) a Python virtual environment
#   2. Install the project in editable mode with dev extras
#   3. Compile message catalogs (pybabel)
#   4. Run alembic upgrade head
#   5. Initialize the database with demo data
#   6. Dump RDF data
#   7. Install frontend dependencies (pnpm)
#   8. Build the frontend

# Defaults (can be overridden by environment variables)
VENV_PATH="${VENV_PATH:-$HOME/Envs}"
VENV_NAME="${VENV_NAME:-atramhasis_dev}"
PROJECT_DIR="${PROJECT_DIR:-$HOME/dev/atramhasis}"

VENV_DIR="$VENV_PATH/$VENV_NAME"

echo "========================================"
echo " Atramhasis - Development Environment Setup"
echo "========================================"
echo "VENV_PATH=$VENV_PATH"
echo "VENV_NAME=$VENV_NAME"
echo "VENV_DIR=$VENV_DIR"
echo "PROJECT_DIR=$PROJECT_DIR"
echo ""

# Validate repository directory
if [ ! -d "$PROJECT_DIR" ]; then
  echo "Error: Repository directory does not exist: $PROJECT_DIR" >&2
  echo "Clone the repository first:" >&2
  echo "  git clone https://github.com/OnroerendErfgoed/atramhasis.git $PROJECT_DIR" >&2
  exit 1
fi

# ── 1. Python virtual environment ────────────────────────────────────────────
echo "── Step 1: Python virtual environment ──"

if [ -d "$VENV_DIR" ]; then
  echo "Virtual environment already exists at: $VENV_DIR"
else
  if ! command -v python >/dev/null 2>&1; then
    echo "Error: python is not available in PATH" >&2
    exit 1
  fi
  python -m venv "$VENV_DIR"
  echo "Created virtual environment at: $VENV_DIR"
fi

# Activate the venv for the remainder of this script
# shellcheck disable=SC1090
. "$VENV_DIR/bin/activate"

echo "Upgrading pip..."
pip install --upgrade pip
pip install --upgrade pip-tools

# ── 2. Install project in editable mode ──────────────────────────────────────
echo ""
echo "── Step 2: Install atramhasis (editable + dev extras) ──"
cd "$PROJECT_DIR"
pip install -e ".[dev]"

# ── 3. Compile Message Catalog Files ─────────────────────────────────────────
echo ""
echo "── Step 3: Compile message catalogs (pybabel) ──"
if command -v pybabel >/dev/null 2>&1; then
  pybabel compile --directory "atramhasis/locale" --domain atramhasis --statistics true
  echo "Message catalogs compiled."
else
  echo "Skipping message catalog compile: 'pybabel' not found in PATH."
fi


# ── 4. Alembic database migration ────────────────────────────────────────────
echo ""
echo "── Step 4: Run alembic upgrade head ──"
if command -v alembic >/dev/null 2>&1; then
  alembic upgrade head
  echo "Alembic migration complete."
else
  echo "Skipping alembic upgrade: 'alembic' command not found or 'development.ini' missing."
fi

# ── 5. Initialize database ────────────────────────────────────────────────────
echo ""
echo "── Step 5: Initialize atramhasis database ──"
if command -v initialize_atramhasis_db >/dev/null 2>&1 && [ -f "$PROJECT_DIR/development.ini" ]; then
  initialize_atramhasis_db "$PROJECT_DIR/development.ini"
  echo "Database initialized."
else
  echo "Skipping DB initialization: 'initialize_atramhasis_db' not found or 'development.ini' missing."
fi

# ── 6. Dump RDF ───────────────────────────────────────────────────────────────
echo ""
echo "── Step 6: Dump RDF ──"
if command -v dump_rdf >/dev/null 2>&1 && [ -f "$PROJECT_DIR/development.ini" ]; then
  dump_rdf "$PROJECT_DIR/development.ini"
  echo "RDF dump complete."
else
  echo "Skipping RDF dump: 'dump_rdf' not found or 'development.ini' missing."
fi

echo "Open a new terminal to start the server. The current terminal will be used to start the frontend dev server."
echo "To activate the virtual environment for this project and start the server"
echo ". \"$VENV_DIR/bin/activate\""
echo "cd $PROJECT_DIR"
echo "pserve development.ini --reload"
echo ""
read -n 1 -s -r -p "Press any key to continue to frontend setup..."


# ── 7. Frontend dependencies ──────────────────────────────────────────────────
echo ""
echo "── Step 7: Install frontend dependencies ──"
FRONTEND_DIR="$PROJECT_DIR/frontend"

if [ ! -d "$FRONTEND_DIR" ]; then
  echo "Warning: frontend directory not found at $FRONTEND_DIR; skipping frontend setup."
else
  if command -v pnpm >/dev/null 2>&1; then
    echo "Using pnpm to install frontend dependencies..."
    (cd "$FRONTEND_DIR" && pnpm install)
  else
    echo "Warning: pnpm not found in PATH; skipping frontend dependency installation."
    echo "Install Node.js and pnpm, then run 'pnpm install' in $FRONTEND_DIR manually."
  fi

  # ── 8. Start frontend dev mode ──────────────────────────────────────────────────────
  echo ""
  echo "── Step 8: Start frontend ──"
  if command -v pnpm >/dev/null 2>&1; then
    (cd "$FRONTEND_DIR" && pnpm dev)
    echo "Frontend started in dev mode."
  else
    echo "Warning: Cannot start frontend without pnpm."
    echo "Run 'pnpm dev' in $FRONTEND_DIR manually after installing Node.js and pnpm."
  fi
fi

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo "========================================"
echo " Setup complete!"
echo "========================================"
echo ""
echo "To start developing:"
echo "  . \"$VENV_DIR/bin/activate\""
echo "  cd \"$PROJECT_DIR\""
echo "  pserve development.ini"
echo ""
echo "For frontend development (hot-reload):"
echo "  cd \"$FRONTEND_DIR\""
echo "  pnpm run dev"

