#!/usr/bin/env bash
# Oracle: emit the cached reference result (stand-in for a correct DFPT run).
set -euo pipefail
cp "$(dirname "$0")/run_lambda.py" ./run_lambda.py
python run_lambda.py --params ./packet/cases.csv --out ./out.csv
