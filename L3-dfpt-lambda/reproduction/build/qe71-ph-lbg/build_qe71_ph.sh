#!/usr/bin/env bash
set -euo pipefail

QE_VERSION="${QE_VERSION:-7.1}"
NP="${NP:-$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 2)}"
SUBMIT_DIR="${SUBMIT_DIR:-$PWD}"
BUILD_ROOT="${BUILD_ROOT:-/tmp/qe71_build_${USER:-lbg}_$$}"
PREFIX="${PREFIX:-$BUILD_ROOT/qe-${QE_VERSION}-ph-lbg}"
ARTIFACT_DIR="${ARTIFACT_DIR:-$SUBMIT_DIR/artifacts}"
SRC_URL="${SRC_URL:-https://gitlab.com/QEF/q-e/-/archive/qe-${QE_VERSION}/q-e-qe-${QE_VERSION}.tar.gz}"
SRC_URL_FALLBACK="${SRC_URL_FALLBACK:-https://github.com/QEF/q-e/archive/refs/tags/qe-${QE_VERSION}.tar.gz}"
FOX_COMMIT="3453648e6837658b747b895bb7bef4b1ed2eac40"
MBD_COMMIT="82005cbb65bdf5d32ca021848eec8f19da956a77"
DEVXLIB_COMMIT="a6b89ef77b1ceda48e967921f1f5488d2df9226d"
FOX_ARCHIVE="${FOX_ARCHIVE:-fox-${FOX_COMMIT}.tar.gz}"
MBD_ARCHIVE="${MBD_ARCHIVE:-mbd-${MBD_COMMIT}.tar.gz}"
DEVXLIB_ARCHIVE="${DEVXLIB_ARCHIVE:-devxlib-${DEVXLIB_COMMIT}.tar.gz}"

export OMP_NUM_THREADS="${OMP_NUM_THREADS:-1}"
export DEBIAN_FRONTEND=noninteractive

log() {
  printf '[qe-build] %s\n' "$*"
}

source_oneapi() {
  if [ -f /opt/intel/oneapi/setvars.sh ]; then
    # Keep LBG logs parseable and avoid shell banners in non-interactive jobs.
    source /opt/intel/oneapi/setvars.sh >/dev/null 2>&1 || true
  fi
}

on_exit() {
  status=$?
  if [ "$status" -eq 0 ]; then
    return
  fi

  log "build failed with exit status $status; collecting diagnostics"
  mkdir -p "$ARTIFACT_DIR/debug"
  qe_dir="$BUILD_ROOT/q-e-qe-${QE_VERSION}"
  if [ -d "$qe_dir" ]; then
    cp -f "$qe_dir/make.inc" "$ARTIFACT_DIR/debug/make.inc" 2>/dev/null || true
    cp -f "$qe_dir/configure.msg" "$ARTIFACT_DIR/debug/configure.msg" 2>/dev/null || true
    cp -f "$qe_dir/install/config.log" "$ARTIFACT_DIR/debug/config.log" 2>/dev/null || true
    find "$qe_dir/external" -maxdepth 3 -type d -print > "$ARTIFACT_DIR/debug/external_dirs.txt" 2>/dev/null || true
    find "$qe_dir/bin" -maxdepth 1 -type f -ls > "$ARTIFACT_DIR/debug/bin_files.txt" 2>/dev/null || true
    find "$qe_dir" -maxdepth 4 \( -name config.log -o -name make.inc -o -name configure.msg \) -print > "$ARTIFACT_DIR/debug/diagnostic_paths.txt" 2>/dev/null || true
  fi
}

trap on_exit EXIT

install_deps() {
  if [ "${SKIP_APT:-0}" = "1" ]; then
    log "SKIP_APT=1; using dependencies already present in the image"
    return
  fi
  if command -v apt-get >/dev/null 2>&1; then
    log "installing build dependencies with apt"
    apt-get update
    apt-get install -y --no-install-recommends \
      ca-certificates wget tar gzip make gcc g++ gfortran \
      openmpi-bin libopenmpi-dev \
      libfftw3-dev libblas-dev liblapack-dev \
      pkg-config python3 file
  else
    log "apt-get not available; assuming build dependencies are already present"
  fi
}

fetch_source() {
  log "fetching QE ${QE_VERSION} source"
  rm -rf "q-e-qe-${QE_VERSION}"
  if [ -f "$SUBMIT_DIR/q-e-qe-${QE_VERSION}.tar.gz" ] && [ ! -f "q-e-qe-${QE_VERSION}.tar.gz" ]; then
    log "copying pre-supplied source tarball to $BUILD_ROOT"
    cp "$SUBMIT_DIR/q-e-qe-${QE_VERSION}.tar.gz" .
  fi
  if [ -f "q-e-qe-${QE_VERSION}.tar.gz" ]; then
    log "using pre-supplied q-e-qe-${QE_VERSION}.tar.gz"
  elif ! timeout "${FETCH_TIMEOUT:-300}" wget "$SRC_URL" -O "q-e-qe-${QE_VERSION}.tar.gz"; then
    log "primary source download failed or timed out; trying fallback"
    rm -f "q-e-qe-${QE_VERSION}.tar.gz"
    timeout "${FETCH_TIMEOUT:-300}" wget "$SRC_URL_FALLBACK" -O "q-e-qe-${QE_VERSION}.tar.gz"
  fi
  tar -xzf "q-e-qe-${QE_VERSION}.tar.gz"
  if [ ! -d "q-e-qe-${QE_VERSION}" ] && [ -d "q-e-qe-${QE_VERSION#qe-}" ]; then
    mv "q-e-qe-${QE_VERSION#qe-}" "q-e-qe-${QE_VERSION}"
  fi
  stage_externals
}

archive_path() {
  archive_name="$1"
  if [ -f "$SUBMIT_DIR/$archive_name" ]; then
    printf '%s\n' "$SUBMIT_DIR/$archive_name"
  elif [ -f "$BUILD_ROOT/$archive_name" ]; then
    printf '%s\n' "$BUILD_ROOT/$archive_name"
  else
    return 1
  fi
}

stage_external_one() {
  name="$1"
  archive_name="$2"
  archive_file="$(archive_path "$archive_name" || true)"
  if [ -z "$archive_file" ]; then
    log "no pre-supplied archive for external/$name; QE may try online git fetch"
    return
  fi

  log "staging external/$name from $(basename "$archive_file")"
  dest="$BUILD_ROOT/q-e-qe-${QE_VERSION}/external/$name"
  tmp="$BUILD_ROOT/external_unpack_$name"
  rm -rf "$dest" "$tmp"
  mkdir -p "$tmp"
  tar -xzf "$archive_file" -C "$tmp"
  root="$(find "$tmp" -mindepth 1 -maxdepth 1 -type d | sed -n '1p')"
  if [ -z "$root" ]; then
    log "archive $archive_name did not unpack to a directory"
    exit 20
  fi
  mv "$root" "$dest"

  # QE 7.1 source archives do not include git submodule metadata. A present
  # .git path tells install/install_utils that this external source is staged.
  mkdir -p "$dest/.git"
}

stage_externals() {
  stage_external_one fox "$FOX_ARCHIVE"
  stage_external_one mbd "$MBD_ARCHIVE"
  stage_external_one devxlib "$DEVXLIB_ARCHIVE"
}

configure_build() {
  cd "q-e-qe-${QE_VERSION}"
  log "configuring QE ${QE_VERSION}"

  if [ "${USE_INTEL:-0}" = "1" ]; then
    source_oneapi
    export MPIF90="${MPIF90:-mpiifort}"
    export CC="${CC:-mpiicc}"
    export F90="${F90:-ifort}"
    export FC="${FC:-ifort}"
    export I_MPI_F90="${I_MPI_F90:-ifort}"
    export I_MPI_FC="${I_MPI_FC:-ifort}"
    export I_MPI_CC="${I_MPI_CC:-icc}"
    if [ -n "${MKLROOT:-}" ]; then
      BLAS_LIBS="${BLAS_LIBS:--L${MKLROOT}/lib/intel64 -lmkl_intel_lp64 -lmkl_sequential -lmkl_core -lpthread -lm -ldl}"
      LAPACK_LIBS="${LAPACK_LIBS:--L${MKLROOT}/lib/intel64 -lmkl_intel_lp64 -lmkl_sequential -lmkl_core -lpthread -lm -ldl}"
    fi
    log "USE_INTEL=1; MPIF90=$MPIF90 CC=$CC F90=$F90 FC=$FC I_MPI_F90=$I_MPI_F90 I_MPI_FC=$I_MPI_FC"
  fi

  config_env=(
    "MPIF90=${MPIF90:-mpif90}"
    "CC=${CC:-mpicc}"
    "F90=${F90:-${I_MPI_F90:-mpif90}}"
    "FC=${FC:-${I_MPI_FC:-mpif90}}"
  )
  if [ -n "${BLAS_LIBS:-}" ]; then
    config_env+=("BLAS_LIBS=${BLAS_LIBS}")
  fi
  if [ -n "${LAPACK_LIBS:-}" ]; then
    config_env+=("LAPACK_LIBS=${LAPACK_LIBS}")
  fi
  if [ -n "${FFT_LIBS:-}" ]; then
    config_env+=("FFT_LIBS=${FFT_LIBS}")
  fi
  env "${config_env[@]}" ./configure --prefix="$PREFIX" ${QE_CONFIGURE_ARGS:-}

  if [ "${USE_DFTI:-${USE_INTEL:-0}}" = "1" ]; then
    if [ -z "${MKLROOT:-}" ]; then
      log "USE_DFTI=1 but MKLROOT is not set"
      exit 30
    fi
    log "enabling MKL DFTI FFT path in make.inc"
    cp make.inc make.inc.before-dfti
    sed -i.bak -E 's/-D__FFTW3?/-D__DFTI/g' make.inc
    if ! grep -q -- '-D__DFTI' make.inc; then
      log "failed to enable -D__DFTI in make.inc"
      exit 31
    fi
  fi

  if [ -n "${EXTRA_FFLAGS:-}" ]; then
    log "appending EXTRA_FFLAGS to make.inc: $EXTRA_FFLAGS"
    cp make.inc make.inc.before-extra-fflags
    sed -i.extra-fflags -E "s|^(FFLAGS[[:space:]]*=.*)|\\1 ${EXTRA_FFLAGS}|" make.inc
  fi

  log "building pw and ph with ${NP} parallel jobs"
  make -j "$NP" pw ph

  log "installing to $PREFIX"
  make install || true
  mkdir -p "$PREFIX/bin"
  [ -x bin/pw.x ] && cp -f bin/pw.x "$PREFIX/bin/pw.x"
  [ -x bin/ph.x ] && cp -f bin/ph.x "$PREFIX/bin/ph.x"
  cd ..
}

verify_and_pack() {
  mkdir -p "$ARTIFACT_DIR"

  if [ ! -x "$PREFIX/bin/pw.x" ]; then
    log "missing $PREFIX/bin/pw.x"
    exit 10
  fi
  if [ ! -x "$PREFIX/bin/ph.x" ]; then
    log "missing $PREFIX/bin/ph.x"
    exit 11
  fi

  log "collecting build manifest"
  {
    echo "QE_VERSION=$QE_VERSION"
    echo "PREFIX=$PREFIX"
    echo "DATE_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo
    echo "## tools"
    command -v mpif90 || true
    command -v mpiifort || true
    command -v mpiicc || true
    command -v mpirun || true
    command -v ifort || true
    command -v ifx || true
    command -v gfortran || true
    echo "USE_INTEL=${USE_INTEL:-0}"
    echo "I_MPI_F90=${I_MPI_F90:-}"
    echo "I_MPI_FC=${I_MPI_FC:-}"
    echo "I_MPI_CC=${I_MPI_CC:-}"
    echo "MKLROOT=${MKLROOT:-}"
    echo "MPIF90=${MPIF90:-mpif90}"
    echo "CC=${CC:-mpicc}"
    echo "F90=${F90:-${I_MPI_F90:-mpif90}}"
    echo "FC=${FC:-${I_MPI_FC:-mpif90}}"
    echo "USE_DFTI=${USE_DFTI:-${USE_INTEL:-0}}"
    echo "EXTRA_FFLAGS=${EXTRA_FFLAGS:-}"
    mpif90 --version 2>&1 | head -5 || true
    mpif90 -show 2>&1 || true
    mpiifort --version 2>&1 | head -5 || true
    mpiifort -show 2>&1 || true
    ifort --version 2>&1 | head -5 || true
    echo
    echo "## make.inc selected flags"
    if [ -f "$BUILD_ROOT/q-e-qe-${QE_VERSION}/make.inc" ]; then
      grep -E '^(DFLAGS|FFT_LIBS|BLAS_LIBS|LAPACK_LIBS|LD_LIBS|F90|MPIF90|FFLAGS)[[:space:]]*=' "$BUILD_ROOT/q-e-qe-${QE_VERSION}/make.inc" || true
    fi
    echo
    echo "## binaries"
    ls -l "$PREFIX/bin/pw.x" "$PREFIX/bin/ph.x"
    if command -v file >/dev/null 2>&1; then
      file "$PREFIX/bin/pw.x" "$PREFIX/bin/ph.x" || true
    else
      echo "file command unavailable"
    fi
    echo
    echo "## staged external commits"
    echo "fox=$FOX_COMMIT"
    echo "mbd=$MBD_COMMIT"
    echo "devxlib=$DEVXLIB_COMMIT"
    echo
    echo "## ldd pw.x"
    ldd "$PREFIX/bin/pw.x" || true
    echo
    echo "## ldd ph.x"
    ldd "$PREFIX/bin/ph.x" || true
  } > "$ARTIFACT_DIR/qe-7.1-ph-lbg-manifest.txt"

  log "packing QE runtime"
  tar -C "$(dirname "$PREFIX")" -czf "$ARTIFACT_DIR/qe-7.1-ph-lbg.tar.gz" "$(basename "$PREFIX")"
  ls -lh "$ARTIFACT_DIR/qe-7.1-ph-lbg.tar.gz" "$ARTIFACT_DIR/qe-7.1-ph-lbg-manifest.txt"
}

main() {
  log "starting QE ${QE_VERSION} PHonon build"
  install_deps
  log "SUBMIT_DIR=$SUBMIT_DIR"
  log "BUILD_ROOT=$BUILD_ROOT"
  log "PREFIX=$PREFIX"
  mkdir -p "$BUILD_ROOT"
  cd "$BUILD_ROOT"
  fetch_source
  if [ "${FETCH_ONLY:-0}" = "1" ]; then
    log "FETCH_ONLY=1; stopping after source and external staging"
    return
  fi
  configure_build
  verify_and_pack
  log "done"
}

main "$@"
