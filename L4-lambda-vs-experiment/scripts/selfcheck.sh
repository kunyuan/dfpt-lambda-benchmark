#!/usr/bin/env bash
set -uo pipefail
H="$(cd "$(dirname "$0")/.." && pwd)"
echo "== oracle (literature first-principles λ) on hidden =="
python3 "$H/solution/run_lambda.py" --params "$H/tests/hidden/cases.csv" --out /tmp/l4_out.csv
python3 "$H/tests/score.py" --pred /tmp/l4_out.csv --gold "$H/tests/gold/ref.csv"; O=$?
echo ""; echo "== perturbed (λ+50%) must FAIL =="
python3 - "$H" <<'PY'
import csv, sys
H = sys.argv[1]
rows = list(csv.DictReader(open(f"{H}/solution/precomputed.csv")))
with open("/tmp/l4_bad.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["case_id", "lambda", "core_hours"])
    for r in rows:
        w.writerow([r["case_id"], float(r["lambda"]) * 1.5, r["core_hours"]])
PY
python3 "$H/tests/score.py" --pred /tmp/l4_bad.csv --gold "$H/tests/gold/ref.csv"; B=$?
echo "----------------------------------------"
[ $O -eq 0 ] && [ $B -ne 0 ] && { echo "SELFCHECK PASSED"; exit 0; } || { echo "SELFCHECK FAILED (o=$O b=$B)"; exit 1; }
