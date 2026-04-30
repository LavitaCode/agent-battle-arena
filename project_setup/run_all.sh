#!/bin/bash
set -e
# Orchestrator script that starts the project skeleton setup
# It calls the first script which in turn invokes the subsequent scripts.

echo "Starting full project setup..."
bash "$(dirname "$0")/01_create_structure.sh"
echo "Setup complete!"

# Remove legacy Angular module file after all scripts have run. The project uses
# standalone components and does not require app.module.ts. We compute the
# root directory as the parent of project_setup.
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
rm -f "$ROOT_DIR/frontend/src/app/app.module.ts"