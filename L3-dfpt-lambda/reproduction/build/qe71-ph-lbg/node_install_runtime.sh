#!/usr/bin/env bash
set -euo pipefail

RUNTIME_TARBALL="${1:-qe-7.1-ph-lbg.tar.gz}"
QE_PREFIX="${QE_PREFIX:-/opt/qe-7.1-ph-lbg}"
BIN_DIR="${BIN_DIR:-/usr/local/bin}"
RUN_SMOKE="${RUN_SMOKE:-1}"
UPDATE_PROFILE="${UPDATE_PROFILE:-1}"
PROFILE_FILE="${PROFILE_FILE:-/root/.bashrc}"

if [ ! -f "$RUNTIME_TARBALL" ]; then
  echo "missing runtime tarball: $RUNTIME_TARBALL" >&2
  exit 2
fi

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

tar -xzf "$RUNTIME_TARBALL" -C "$tmpdir"
test -x "$tmpdir/qe-7.1-ph-lbg/bin/pw.x"
test -x "$tmpdir/qe-7.1-ph-lbg/bin/ph.x"

rm -rf "$QE_PREFIX"
mkdir -p "$(dirname "$QE_PREFIX")"
cp -a "$tmpdir/qe-7.1-ph-lbg" "$QE_PREFIX"

mkdir -p "$BIN_DIR"
ln -sf "$QE_PREFIX/bin/pw.x" "$BIN_DIR/pw.x"
ln -sf "$QE_PREFIX/bin/ph.x" "$BIN_DIR/ph.x"

export PATH="$QE_PREFIX/bin:$BIN_DIR:$PATH"
if [ "$UPDATE_PROFILE" = "1" ] && [ -f "$PROFILE_FILE" ]; then
  if ! grep -Fq "# qe-7.1-ph-lbg runtime" "$PROFILE_FILE"; then
    {
      echo ""
      echo "# qe-7.1-ph-lbg runtime"
      echo "export PATH=\"$QE_PREFIX/bin:\$PATH\""
    } >> "$PROFILE_FILE"
  fi
fi

echo "installed QE runtime at $QE_PREFIX"
echo "pw.x: $(command -v pw.x)"
echo "ph.x: $(command -v ph.x)"
if [ "$RUN_SMOKE" = "1" ]; then
  "$QE_PREFIX/bin/pw.x" < /dev/null || true
  "$QE_PREFIX/bin/ph.x" < /dev/null || true
fi
