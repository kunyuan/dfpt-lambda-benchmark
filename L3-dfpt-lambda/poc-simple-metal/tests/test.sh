#!/usr/bin/env bash
# Run the agent's run_lambda.py on concealed cases, then score.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
python /app/run_lambda.py --params "$HERE/hidden/cases.csv" --out /app/out.csv
python "$HERE/score.py" --pred /app/out.csv --gold "$HERE/gold/ref.csv"
