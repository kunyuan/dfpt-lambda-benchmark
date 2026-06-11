#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-$(cd "$(dirname "$0")/../../../../.." && pwd)}"
NP="${NP:-48}"
NK="${NK:-4}"
SIGMA="${SIGMA:-0.025}"
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-1}"

if [ ! -d "$REPO_ROOT/L3-dfpt-lambda/pseudos/pseudo" ]; then
  echo "[run] missing pseudos: $REPO_ROOT/L3-dfpt-lambda/pseudos/pseudo" >&2
  echo "[run] run: cd $REPO_ROOT/L3-dfpt-lambda/pseudos && bash fetch_sg15.sh" >&2
  exit 2
fi
if [ ! -e pseudo ]; then
  ln -s "$REPO_ROOT/L3-dfpt-lambda/pseudos/pseudo" pseudo
fi

echo "[run] case=lam253 q=3 NP=$NP NK=$NK"
mpirun --oversubscribe -np "$NP" pw.x -nk "$NK" -in scf.in > scf.out
mpirun --oversubscribe -np "$NP" ph.x -nk "$NK" -in ph.in > ph.out
python "$REPO_ROOT/.claude/skills/qe-eph-lambda/references/extract_lambda.py" ph.out --sigma "$SIGMA" > lambda.dat
tail -n +1 lambda.dat
