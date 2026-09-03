#!/usr/bin/env bash
set -euo pipefail

# Create your own atramhasis project using cookiecutter templates. Choose between a demo app (with sample data) or
# an empty project (minimal setup).
# - https://atramhasis.readthedocs.io/en/latest/demo.html#running-a-demo-site-with-cookiecutter
# - https://atramhasis.readthedocs.io/en/latest/customisation.html#creating-your-own-project

# Variables:
#   VENV_PATH: Path to store the virtual environment (default: $HOME/Envs)
#   VENV_NAME: Name of the virtual environment (default: my_atramhasis)
#   PROJECT_DIR: Directory to create the new project in (default: $HOME/dev/atram)

# Usage:
#   VENV_PATH="$HOME/Envs" VENV_NAME="my_atramhasis" PROJECT_DIR="$HOME/dev/atram" ./scripts/setup_new_project.sh

# If environment variables are not set, defaults will be used.
# Defaults (can be overridden by environment variables)
VENV_PATH="${VENV_PATH:-$HOME/Envs}"
VENV_NAME="${VENV_NAME:-my_atramhasis}"
PROJECT_DIR="${PROJECT_DIR:-$HOME/dev/atram}"

VENV_DIR="$VENV_PATH/$VENV_NAME"

echo "VENV_PATH=$VENV_PATH"
echo "VENV_NAME=$VENV_NAME"
echo "VENV_DIR=$VENV_DIR"
echo "PROJECT_DIR=$PROJECT_DIR"

# Create venv if it doesn't exist
mkdir -p "$VENV_PATH"
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

echo "Upgrading pip and ensuring cookiecutter is installed in the venv..."
pip install --upgrade pip
pip install --upgrade cookiecutter

# Prompt user to choose between demo and empty project
echo ""
echo "Choose the type of project to scaffold:"
echo "1) Demo app (includes sample data)"
echo "2) Empty project (minimal setup)"
read -p "Enter your choice (1 or 2): " PROJECT_TYPE

case "$PROJECT_TYPE" in
  1)
	COOKIECUTTER_DIR="demo"
	IS_DEMO=true
	echo "You selected: Demo app"
	;;
  2)
	COOKIECUTTER_DIR="scaffold"
	IS_DEMO=false
	echo "You selected: Empty project"
	;;
  *)
	echo "Invalid choice. Please enter 1 or 2."
	exit 1
	;;
esac

# Ensure project directory exists and switch to it
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

echo "Recording existing directories before running cookiecutter..."
mapfile -t _before < <(find . -maxdepth 1 -mindepth 1 -type d -printf '%f\n' | sort)

echo "Running cookiecutter (this may prompt for values)..."
cookiecutter gh:OnroerendErfgoed/atramhasis --directory "cookiecutters/$COOKIECUTTER_DIR"

echo "Detecting newly created project directory (if any)..."
mapfile -t _after < <(find . -maxdepth 1 -mindepth 1 -type d -printf '%f\n' | sort)

# compute difference between _after and _before. This will help us find the newly created project directory
# that was chosen by the user.
NEW_DIR=""
for d in "${_after[@]}"; do
  skip=false
  for b in "${_before[@]}"; do
	if [ "$d" = "$b" ]; then
	  skip=true
	  break
	fi
  done
  if [ "$skip" = false ]; then
	# choose the first new directory found
	NEW_DIR="$d"
	break
  fi
done

if [ -n "$NEW_DIR" ]; then
  echo "Detected new project directory: $NEW_DIR"
  cd "$NEW_DIR"
  echo "Installing the new project in editable mode with dev extras..."
  pip install -e ."[dev]"

   # Run alembic upgrade if alembic.ini / development.ini is present
   if command -v alembic >/dev/null 2>&1 && [ -f development.ini ]; then
	echo "Running alembic upgrade head..."
	alembic upgrade head
   else
	echo "Skipping alembic upgrade: 'alembic' not found or 'development.ini' missing"
   fi

   # initialize database and dump rdf only for demo projects
   if [ "$IS_DEMO" = true ]; then
    if command -v initialize_atramhasis_db >/dev/null 2>&1; then
      echo "Initializing atramhasis DB..."
      initialize_atramhasis_db development.ini
    else
      echo "Tool 'initialize_atramhasis_db' not found in PATH; skipping DB initialization"
    fi

    if command -v dump_rdf >/dev/null 2>&1; then
      echo "Dumping RDF..."
      dump_rdf development.ini
    else
      echo "Tool 'dump_rdf' not found in PATH; skipping RDF dump"
    fi
   fi

  echo "To activate the virtual environment for this project and start the server"
  echo ". \"$VENV_DIR/bin/activate\""
  echo "cd $PROJECT_DIR/$NEW_DIR"
  echo "pserve development.ini"
  echo "[Extra]"
  echo "If you want to use a local Atramhasis branch in your new project to test code changes:"
  echo "1. Check out the desired branch in your Atramhasis project folder."
  echo "2. Install it in editable mode using the following command:"
  echo "pip install -e .\"[dev]\" --no-deps --force-reinstall"

else
  echo "Could not automatically detect the created projectw directory."
  echo "Please cd into the scaffolded project root and run these commands manually:"
  echo "  pip install -e .\"[dev]\""
  echo "  alembic upgrade head  # if alembic is available and config exists"
  echo "  initialize_atramhasis_db development.ini  # if available"
  echo "  dump_rdf development.ini  # if available"
  echo "  pserve development.ini"
fi
