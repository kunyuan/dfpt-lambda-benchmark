#!/usr/bin/env bash
set -euo pipefail

TARBALL="${1:-qe-7.1-ph-lbg.tar.gz}"
PREFIX="${QE_PREFIX:-qe-7.1-ph-lbg}"
SMOKE_TIMEOUT="${SMOKE_TIMEOUT:-20}"

tar -xzf "$TARBALL"

for exe in pw.x ph.x; do
  path="$PREFIX/bin/$exe"
  if [ ! -x "$path" ]; then
    echo "missing executable: $path"
    exit 10
  fi

  out="${exe}.smoke.out"
  set +e
  timeout "$SMOKE_TIMEOUT" "$path" < /dev/null > "$out" 2>&1
  code=$?
  set -e

  echo "== $exe =="
  echo "exit=$code"
  sed -n '1,80p' "$out" || true

  if grep -E 'error while loading shared libraries|No such file|command not found' "$out"; then
    exit 20
  fi
  if [ "$code" -eq 127 ]; then
    exit 21
  fi
done
