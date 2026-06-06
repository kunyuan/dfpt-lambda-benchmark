#!/bin/bash
# Harbor verifier (container). Hand the runner ONLY the spectra+manifest (no gold);
# lock /tests/hidden + /tests/gold root-only; run agent code as `nobody`; score and
# write a binary reward to /logs/verifier/reward.txt (1 = PASS).
set -uo pipefail
mkdir -p /logs/verifier /tmp/preds /tmp/runner_inputs/spectra
chmod -R a+rwX /tmp/preds /tmp/runner_inputs
chmod -R go-rwx /tests/hidden /tests/gold
chmod go-rwx /tests/test.sh /tests/score.py
chmod -R a+rX /app

# runner input = manifest + spectra only (gold stays in /tests/gold, root-only)
cp /tests/hidden/cases.csv /tmp/runner_inputs/cases.csv
cp /tests/hidden/spectra/*.dat /tmp/runner_inputs/spectra/
chmod -R a+rX /tmp/runner_inputs

run_as_nobody() {
  python3 - "$@" <<'PY'
import os, pwd, subprocess, sys
pw = pwd.getpwnam("nobody")
os.setgid(pw.pw_gid); os.setuid(pw.pw_uid)
raise SystemExit(subprocess.run(sys.argv[1:]).returncode)
PY
}

fail=0
run_as_nobody python3 /app/run_lambda.py \
  --params /tmp/runner_inputs/cases.csv \
  --out /tmp/preds/out.csv \
  || { echo "[verifier] runner failed"; fail=1; }

python3 /tests/score.py \
  --pred /tmp/preds/out.csv --gold /tests/gold/gold.csv \
  --json /logs/verifier/result.json
pass=$?

if [ "$fail" -eq 0 ] && [ "$pass" -eq 0 ]; then echo 1 > /logs/verifier/reward.txt
else echo 0 > /logs/verifier/reward.txt; fi
echo "[verifier] reward=$(cat /logs/verifier/reward.txt)"
exit $((1 - $(cat /logs/verifier/reward.txt)))
