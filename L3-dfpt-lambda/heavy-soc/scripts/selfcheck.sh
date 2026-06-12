#!/usr/bin/env bash
set -uo pipefail
H="$(cd "$(dirname "$0")/.." && pwd)"
TMP_SELF="$(mktemp -d "${TMPDIR:-/tmp}/dfpt-l3-selfcheck.XXXXXX")"
trap 'rm -rf "$TMP_SELF"' EXIT
OUT="$TMP_SELF/t_out.csv"
BAD="$TMP_SELF/t_bad.csv"
echo "== oracle on hidden =="
python3 "$H/solution/run_lambda.py" --params "$H/tests/hidden/cases.csv" --out "$OUT"; R=$?
[ $R -eq 0 ] || { echo "SELFCHECK FAILED (oracle command failed: $R)"; exit 1; }
python3 "$H/tests/score.py" --pred "$OUT" --gold "$H/tests/gold/ref.csv"; O=$?
echo ""; echo "== perturbed (λ+50%) must FAIL =="
python3 - "$H" "$BAD" <<'PY'
import csv,sys; H=sys.argv[1]; rows=list(csv.DictReader(open(f"{H}/tests/gold/ref.csv")))
out=sys.argv[2]
with open(out,"w",newline="") as f:
    w=csv.writer(f); w.writerow(["case_id","lambda","omega_log_K","core_hours"])
    for r in rows: w.writerow([r["case_id"],float(r["lambda"])*1.5,r.get("omega_log_K",""),100])
PY
python3 "$H/tests/score.py" --pred "$BAD" --gold "$H/tests/gold/ref.csv"; B=$?
echo "----------------------------------------"
[ $O -eq 0 ] && [ $B -ne 0 ] && { echo "SELFCHECK PASSED"; exit 0; } || { echo "SELFCHECK FAILED (o=$O b=$B)"; exit 1; }
