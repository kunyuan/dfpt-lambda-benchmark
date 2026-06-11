#!/usr/bin/env python3
"""Create QE input directories for the selected L3 scaling reproduction batch."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REPRO = ROOT / "L3-dfpt-lambda" / "reproduction"
INPUTS = REPRO / "inputs"
STRUCTURES = ROOT / "L3-dfpt-lambda" / "structures"


def replace_kpoints(text: str, kgrid: int) -> str:
    pattern = re.compile(r"K_POINTS automatic\n\s*\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+", re.M)
    replacement = f"K_POINTS automatic\n  {kgrid} {kgrid} {kgrid} 0 0 0"
    if not pattern.search(text):
        raise ValueError("SCF input has no automatic K_POINTS block")
    return pattern.sub(replacement, text)


def ph_input(qgrid: int) -> str:
    return f"""&inputph
  prefix='x',
  outdir='./out',
  fildvscf='dvscf',
  tr2_ph=1.0d-14,
  electron_phonon='simple',
  el_ph_sigma=0.005,
  el_ph_nsigma=10,
  ldisp=.true.,
  nq1={qgrid}, nq2={qgrid}, nq3={qgrid}
/
"""


def run_script(case_id: str, qgrid: int) -> str:
    return f"""#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${{REPO_ROOT:-$(cd "$(dirname "$0")/../../../../.." && pwd)}}"
NP="${{NP:-48}}"
NK="${{NK:-4}}"
SIGMA="${{SIGMA:-0.025}}"
export OMP_NUM_THREADS="${{OMP_NUM_THREADS:-1}}"

if [ ! -d "$REPO_ROOT/L3-dfpt-lambda/pseudos/pseudo" ]; then
  echo "[run] missing pseudos: $REPO_ROOT/L3-dfpt-lambda/pseudos/pseudo" >&2
  echo "[run] run: cd $REPO_ROOT/L3-dfpt-lambda/pseudos && bash fetch_sg15.sh" >&2
  exit 2
fi
if [ ! -e pseudo ]; then
  ln -s "$REPO_ROOT/L3-dfpt-lambda/pseudos/pseudo" pseudo
fi

echo "[run] case={case_id} q={qgrid} NP=$NP NK=$NK"
mpirun --oversubscribe -np "$NP" pw.x -nk "$NK" -in scf.in > scf.out
mpirun --oversubscribe -np "$NP" ph.x -nk "$NK" -in ph.in > ph.out
python "$REPO_ROOT/.claude/skills/qe-eph-lambda/references/extract_lambda.py" ph.out --sigma "$SIGMA" > lambda.dat
tail -n +1 lambda.dat
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default=str(INPUTS / "selected_cases.csv"))
    parser.add_argument("--out", default=str(INPUTS / "scaling_runs"))
    parser.add_argument("--tier", default="A", help="Comma-separated tiers to generate, e.g. A or A,B")
    args = parser.parse_args()

    tiers = {x.strip() for x in args.tier.split(",") if x.strip()}
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    generated = 0
    with open(args.manifest, newline="") as f:
        for row in csv.DictReader(f):
            if row["tier"] not in tiers:
                continue
            case_id = row["case_id"]
            structure = STRUCTURES / row["structure_file"]
            if not structure.exists():
                raise FileNotFoundError(structure)
            base_text = structure.read_text()
            kgrids = [int(x) for x in row["kgrids"].split(";")]
            qgrids = [int(x) for x in row["qgrids"].split(";")]
            default_k = max(kgrids)
            for q in qgrids:
                run_dir = out / case_id / f"q{q}"
                run_dir.mkdir(parents=True, exist_ok=True)
                (run_dir / "scf.in").write_text(replace_kpoints(base_text, default_k))
                (run_dir / "ph.in").write_text(ph_input(q))
                script = run_dir / "run.sh"
                script.write_text(run_script(case_id, q))
                script.chmod(0o755)
                generated += 1

    print(f"generated {generated} QE scaling run directories in {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
