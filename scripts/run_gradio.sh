#!/usr/bin/env bash
# Launch one of the public Gradio review interfaces.
#
# Usage:
#   ./scripts/run_gradio.sh agents_playground
#   ./scripts/run_gradio.sh pipeline_demo

set -e

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 [demo_name]"
  echo "Available demos: agents_playground, pipeline_demo"
  exit 1
fi

SCRIPT_DIR="$(dirname "$0")"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

case "$1" in
  agents_playground|pipeline_demo)
    DEMO_PATH="ui/gradio/$1.py"
    ;;
  *)
    echo "Unknown demo: $1"
    echo "Available demos: agents_playground, pipeline_demo"
    exit 1
    ;;
esac

if [ -x "$PROJECT_ROOT/venv/bin/python" ]; then
  PYTHON="$PROJECT_ROOT/venv/bin/python"
else
  PYTHON="python3"
fi

exec "$PYTHON" "$DEMO_PATH"
