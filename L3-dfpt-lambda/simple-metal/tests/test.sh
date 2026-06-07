#!/bin/bash
set -uo pipefail
mkdir -p /logs/verifier /tmp/preds /tmp/ri
chmod -R a+rwX /tmp/preds /tmp/ri; chmod -R go-rwx /tests/hidden /tests/gold; chmod go-rwx /tests/test.sh /tests/score.py; chmod -R a+rX /app
cp /tests/hidden/cases.csv /tmp/ri/cases.csv; chmod -R a+rX /tmp/ri
run_as_nobody(){ python3 - "$@" <<'PY'
import os,pwd,subprocess,sys
pw=pwd.getpwnam("nobody"); os.setgid(pw.pw_gid); os.setuid(pw.pw_uid)
raise SystemExit(subprocess.run(sys.argv[1:]).returncode)
PY
}
fail=0
run_as_nobody python3 /app/run_lambda.py --params /tmp/ri/cases.csv --out /tmp/preds/out.csv || { echo "[verifier] runner failed"; fail=1; }
python3 /tests/score.py --pred /tmp/preds/out.csv --gold /tests/gold/ref.csv --json /logs/verifier/result.json; pass=$?
if [ "$fail" -eq 0 ] && [ "$pass" -eq 0 ]; then echo 1 > /logs/verifier/reward.txt; else echo 0 > /logs/verifier/reward.txt; fi
echo "[verifier] reward=$(cat /logs/verifier/reward.txt)"; exit $((1-$(cat /logs/verifier/reward.txt)))
