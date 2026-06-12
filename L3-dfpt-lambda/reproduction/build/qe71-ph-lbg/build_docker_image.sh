#!/usr/bin/env bash
set -euo pipefail

IMAGE_TAG="${IMAGE_TAG:-registry.dp.tech/dptech/dp/native/prod-576590/903079/qe-7.1-ph:20260609193307}"
RUNTIME_TARBALL="${RUNTIME_TARBALL:-qe-7.1-ph-lbg.tar.gz}"
DOCKERFILE="${DOCKERFILE:-Dockerfile}"

if [ ! -f "$RUNTIME_TARBALL" ]; then
  echo "missing runtime tarball: $RUNTIME_TARBALL" >&2
  exit 2
fi

docker build \
  --build-arg "QE_RUNTIME_TARBALL=$RUNTIME_TARBALL" \
  -f "$DOCKERFILE" \
  -t "$IMAGE_TAG" \
  .

docker run --rm "$IMAGE_TAG" bash -lc 'pw.x < /dev/null || true; ph.x < /dev/null || true'

echo "$IMAGE_TAG"
