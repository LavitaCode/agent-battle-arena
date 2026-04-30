#!/bin/bash
set -e

# This script creates the basic directory structure for the Agent Battle Arena project
# and then invokes the backend setup script. Each script in this series will
# invoke the next one at the end, so running the first script is sufficient
# to set up the entire project.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Creating directory structure..."
# Root level directories
mkdir -p "$ROOT_DIR/backend/app/api/v1"
mkdir -p "$ROOT_DIR/backend/app/core"
mkdir -p "$ROOT_DIR/frontend/src/app"
mkdir -p "$ROOT_DIR/quests/quest_hello_world"
mkdir -p "$ROOT_DIR/docs"

echo "Directory structure created."

# Proceed to backend setup
bash "$SCRIPT_DIR/02_setup_backend.sh"