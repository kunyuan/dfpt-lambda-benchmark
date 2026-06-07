#!/usr/bin/env bash
set -uo pipefail
H="$(cd "$(dirname "$0")/.." && pwd)"
echo "== oracle on hidden =="
python3 "$H/solution/run_lambda.py" --params "$H/tests/hidden/cases.csv" --out /tmp/t_out.csv
python3 "$H/tests/score.py" --pred /tmp/t_out.csv --gold "$H/tests/gold/ref.csv"; O=$?
echo ""; echo "== perturbed (λ+50%) must FAIL =="
python3 - "$H" <<'PY'
import csv,sys; H=sys.argv[1]; rows=list(csv.DictReader(open(f"{H}/tests/gold/ref.csv")))
with open("/tmp/t_bad.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["case_id","lambda","omega_log_K","core_hours"])
    for r in rows: w.writerow([r["case_id"],float(r["lambda"])*1.5,r.get("omega_log_K",""),100])
PY
python3 "$H/tests/score.py" --pred /tmp/t_bad.csv --gold "$H/tests/gold/ref.csv"; B=$?
echo "----------------------------------------"
[ $O -eq 0 ] && [ $B -ne 0 ] && { echo "SELFCHECK PASSED"; exit 0; } || { echo "SELFCHECK FAILED (o=$O b=$B)"; exit 1; }
