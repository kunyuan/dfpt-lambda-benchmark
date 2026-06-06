#!/usr/bin/env bash
# Oracle: drop in the reference run_lambda.py (the agent writes their own).
set -euo pipefail
cp "$(dirname "$0")/run_lambda.py" /app/run_lambda.py
