#!/usr/bin/env python3
"""Build a compact LBG input bundle for one generated QE scaling run."""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REPRO = ROOT / "L3-dfpt-lambda" / "reproduction"
INPUTS = REPRO / "inputs"
PSEUDOS = ROOT / "L3-dfpt-lambda" / "pseudos" / "pseudo"
EXTRACTOR = ROOT / ".claude" / "skills" / "qe-eph-lambda" / "references" / "extract_lambda.py"


def pseudo_filenames(scf_text: str) -> list[str]:
    in_species = False
    names: list[str] = []
    for line in scf_text.splitlines():
        stripped = line.strip()
        if stripped == "ATOMIC_SPECIES":
            in_species = True
            continue
        if in_species and re.match(r"^(ATOMIC_POSITIONS|K_POINTS|CELL_PARAMETERS)\b", stripped):
            break
        if in_species and stripped:
            parts = stripped.split()
            if len(parts) >= 3:
                names.append(parts[2])
    if not names:
        raise ValueError("no pseudopotentials found in ATOMIC_SPECIES")
    return names


def run_script(case_id: str, qgrid: int) -> str:
    return f"""#!/usr/bin/env bash
set -euo pipefail

NP="${{NP:-$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 1)}}"
NK="${{NK:-1}}"
SIGMA="${{SIGMA:-0.025}}"
PW_BIN="${{PW_BIN:-pw.x}}"
PH_BIN="${{PH_BIN:-ph.x}}"
RUN_PH="${{RUN_PH:-1}}"
export OMP_NUM_THREADS="${{OMP_NUM_THREADS:-1}}"
ulimit -s unlimited || true

on_exit() {{
  status=$?
  set +e
  if [ "$status" -ne 0 ]; then
    echo "[lbg-run] failed status=$status"
    for f in scf.out ph.out lambda.dat; do
      if [ -f "$f" ]; then
        echo "[lbg-run] tail $f"
        tail -n "${{TAIL_LINES:-120}}" "$f"
      fi
    done
  fi
  if [ "${{CLEAN_QE_SCRATCH:-1}}" = "1" ]; then
    find . -maxdepth 4 \\( -name "*.save" -o -name "_ph0" -o -name "*.wfc*" -o -name "*.mix*" \\) -exec rm -rf {{}} +
  fi
  if [ "${{CLEAN_RUNTIME:-1}}" = "1" ]; then
    rm -rf qe-7.1-ph-lbg qe-7.1-ph-lbg.tar.gz
  fi
  exit "$status"
}}
trap on_exit EXIT

if [ -f /opt/intel/oneapi/setvars.sh ]; then
  # The QE 7.1 image has Intel MPI/MKL in oneAPI. Non-login LBG job shells can
  # have mpirun on PATH without the full runtime environment.
  source /opt/intel/oneapi/setvars.sh >/dev/null 2>&1 || true
fi
export I_MPI_FABRICS="${{I_MPI_FABRICS:-shm}}"

if [ -f qe-7.1-ph-lbg.tar.gz ]; then
  rm -rf qe-7.1-ph-lbg
  tar -xzf qe-7.1-ph-lbg.tar.gz
  export PATH="$(pwd)/qe-7.1-ph-lbg/bin:$PATH"
fi

echo "[lbg-run] case={case_id} q={qgrid} NP=$NP NK=$NK SIGMA=$SIGMA"
echo "[lbg-run] pwd=$(pwd)"
echo "[lbg-run] PW_BIN=$PW_BIN"
echo "[lbg-run] PH_BIN=$PH_BIN"
command -v "$PW_BIN" || test -x "$PW_BIN"
if [ "$RUN_PH" = "1" ]; then
  command -v "$PH_BIN" || test -x "$PH_BIN"
fi
which mpirun

pool_args=()
if [ "$NK" != "1" ]; then
  pool_args=(-nk "$NK")
fi

mpirun -np "$NP" "$PW_BIN" "${{pool_args[@]}}" -in scf.in > scf.out
if [ "$RUN_PH" = "1" ]; then
  mpirun -np "$NP" "$PH_BIN" "${{pool_args[@]}}" -in ph.in > ph.out
  if [ "${{RUN_EXTRACT:-1}}" = "1" ]; then
    python3 extract_lambda.py ph.out --sigma "$SIGMA" > lambda.dat
    cat lambda.dat
  fi
fi
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_id")
    parser.add_argument("qgrid", type=int)
    parser.add_argument("--runs", default=str(INPUTS / "scaling_runs"))
    parser.add_argument("--out-root", default="/tmp/dfpt_lbg_bundles")
    parser.add_argument("--qe-runtime-tarball", default="")
    args = parser.parse_args()

    run_dir = Path(args.runs) / args.case_id / f"q{args.qgrid}"
    if not run_dir.exists():
        raise FileNotFoundError(run_dir)
    if not PSEUDOS.exists():
        raise FileNotFoundError(PSEUDOS)
    if not EXTRACTOR.exists():
        raise FileNotFoundError(EXTRACTOR)

    bundle = Path(args.out_root) / f"{args.case_id}_q{args.qgrid}"
    if bundle.exists():
        shutil.rmtree(bundle)
    pseudo_dir = bundle / "pseudo"
    pseudo_dir.mkdir(parents=True, exist_ok=True)

    scf_text = (run_dir / "scf.in").read_text()
    shutil.copy2(run_dir / "scf.in", bundle / "scf.in")
    shutil.copy2(run_dir / "ph.in", bundle / "ph.in")
    shutil.copy2(EXTRACTOR, bundle / "extract_lambda.py")
    if args.qe_runtime_tarball:
        shutil.copy2(args.qe_runtime_tarball, bundle / "qe-7.1-ph-lbg.tar.gz")

    for pseudo in pseudo_filenames(scf_text):
        src = PSEUDOS / pseudo
        if not src.exists():
            raise FileNotFoundError(src)
        shutil.copy2(src, pseudo_dir / pseudo)

    script = bundle / "run_lbg.sh"
    script.write_text(run_script(args.case_id, args.qgrid))
    script.chmod(0o755)
    (bundle / "bundle_meta.txt").write_text(f"case_id={args.case_id}\nqgrid={args.qgrid}\n")

    print(bundle)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
