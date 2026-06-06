#!/usr/bin/env bash
# Host-side check (no container/Docker): oracle PASS, perturbed-λ FAIL.
set -uo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
echo "== oracle on hidden spectra =="
python3 "$HERE/solution/run_lambda.py" --params "$HERE/tests/hidden/cases.csv" --out /tmp/l1_out.csv
python3 "$HERE/tests/score.py" --pred /tmp/l1_out.csv --gold "$HERE/tests/gold/gold.csv"
ORACLE=$?
echo ""
echo "== perturbed (λ +20%) must FAIL =="
python3 - "$HERE" <<'PY'
import csv, sys
H=sys.argv[1]; rows=list(csv.DictReader(open(f"{H}/tests/gold/gold.csv")))
with open("/tmp/l1_bad.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["case_id","lambda","omega_log_K"])
    for r in rows: w.writerow([r["case_id"], float(r["lambda"])*1.2, r["omega_log_K"]])
PY
python3 "$HERE/tests/score.py" --pred /tmp/l1_bad.csv --gold "$HERE/tests/gold/gold.csv"
BAD=$?
echo "----------------------------------------"
if [ $ORACLE -eq 0 ] && [ $BAD -ne 0 ]; then echo "SELFCHECK PASSED (oracle PASS, perturbed FAIL)"; exit 0
else echo "SELFCHECK FAILED (oracle=$ORACLE perturbed=$BAD)"; exit 1; fi
