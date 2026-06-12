#!/usr/bin/env bash
set -euo pipefail

echo "PATH=$PATH"
for exe in gcc gfortran ifort ifx mpif90 mpirun make wget tar cmake pw.x ph.x; do
  printf '%-8s ' "$exe"
  command -v "$exe" || true
done
echo
echo "== /opt QE binaries and sources =="
find /opt -maxdepth 6 -type f \( -name configure -o -name CMakeLists.txt -o -name ph.x -o -name pw.x -o -name q2r.x -o -name lambda.x \) 2>/dev/null | sort | head -200

echo
echo "== /opt/qe-7.1/bin =="
ls -la /opt/qe-7.1/bin 2>/dev/null || true

echo
echo "== official pw.x =="
if [ -x /opt/qe-7.1/bin/pw.x ]; then
  ldd /opt/qe-7.1/bin/pw.x || true
  strings /opt/qe-7.1/bin/pw.x | grep -Ei 'quantum espresso|ifort|gfortran|intel|mkl|openmpi|mpich|fftw' | head -80 || true
fi

echo
echo "== MPI wrappers =="
mpif90 --version 2>&1 | sed -n '1,20p' || true
mpif90 -show 2>&1 || true
mpicc -show 2>&1 || true

echo
echo "== oneAPI =="
if [ -f /opt/intel/oneapi/setvars.sh ]; then
  source /opt/intel/oneapi/setvars.sh >/dev/null 2>&1 || true
fi
echo "MKLROOT=${MKLROOT:-}"
echo "I_MPI_ROOT=${I_MPI_ROOT:-}"
ifort --version 2>&1 | sed -n '1,8p' || true
ifx --version 2>&1 | sed -n '1,8p' || true
