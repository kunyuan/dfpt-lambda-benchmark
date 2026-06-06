#!/usr/bin/env bash
# Host-side self-check: oracle passes; a perturbed λ fails.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
echo "== oracle on hidden cases =="
python "$HERE/solution/run_lambda.py" --params "$HERE/tests/hidden/cases.csv" --out /tmp/poc_out.csv
python "$HERE/tests/score.py" --pred /tmp/poc_out.csv --gold "$HERE/tests/gold/ref.csv"
ORACLE=$?
echo ""
echo "== perturbed prediction (λ +50%) must FAIL =="
python - "$HERE" <<'PY'
import csv, sys
HERE=sys.argv[1]
rows=list(csv.DictReader(open(f"{HERE}/tests/gold/ref.csv")))
with open("/tmp/poc_bad.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["case_id","lambda","omega_log_K","core_hours"])
    for r in rows: w.writerow([r["case_id"], float(r["lambda_ref"])*1.5, r["omega_log_K_ref"], 100])
PY
python "$HERE/tests/score.py" --pred /tmp/poc_bad.csv --gold "$HERE/tests/gold/ref.csv"
BAD=$?
echo ""
echo "----------------------------------------"
if [ $ORACLE -eq 0 ] && [ $BAD -ne 0 ]; then echo "SELFCHECK PASSED (oracle PASS, perturbed FAIL)"; exit 0
else echo "SELFCHECK FAILED (oracle=$ORACLE perturbed=$BAD)"; exit 1; fi
