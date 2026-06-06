#!/usr/bin/env bash
set -euo pipefail
D="$(dirname "$0")"
cp "$D/run_lambda.py" /app/run_lambda.py
cp "$D/precomputed.csv" /app/precomputed.csv   # oracle's cached "DFPT result"
