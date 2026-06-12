# LBG QE 7.1 `ph.x` Runtime

This bundle builds a reusable Quantum ESPRESSO 7.1 runtime containing `ph.x` for
the DFPT lambda reproduction jobs.

The public LBG `registry.dp.tech/dptech/quantum-espresso:7.1` image contains
`pw.x` but not `ph.x`, so DFPT electron-phonon calculations need a separate
runtime for the phonon/electron-phonon step. The successful reproduction batch
used the official image's `/opt/qe-7.1/bin/pw.x` plus this runtime's `ph.x`.

## Build on LBG

Submit this directory as the job input together with the QE 7.1 source archive
and the pinned external archives:

```text
q-e-qe-7.1.tar.gz
fox-3453648e6837658b747b895bb7bef4b1ed2eac40.tar.gz
mbd-82005cbb65bdf5d32ca021848eec8f19da956a77.tar.gz
devxlib-a6b89ef77b1ceda48e967921f1f5488d2df9226d.tar.gz
```

The external archives avoid runtime `git fetch` calls on LBG. Run:

```bash
SKIP_APT=1 NP=64 bash build_qe71_ph.sh
```

Expected artifact:

```text
artifacts/qe-7.1-ph-lbg.tar.gz
artifacts/qe-7.1-ph-lbg-manifest.txt
```

The tarball is intended to be uploaded with later scaling jobs and unpacked into
the job working directory.

For a cheap packaging check without compiling, run:

```bash
FETCH_ONLY=1 bash build_qe71_ph.sh
```

For a runtime smoke test after downloading `qe-7.1-ph-lbg.tar.gz`, submit the
tarball with this directory and run:

```bash
bash smoke_runtime.sh qe-7.1-ph-lbg.tar.gz
```

## Build a Docker Image

The stable mpiifort LBG build produced:

```text
/tmp/qe71_mpiifort_build_out/22835738/unzipped/artifacts/qe-7.1-ph-lbg.tar.gz
```

Place that tarball next to `Dockerfile`, then build on any host that has
Docker or a compatible builder:

```bash
cp /tmp/qe71_build_out/22834686/unzipped/artifacts/qe-7.1-ph-lbg.tar.gz .

IMAGE_TAG=registry.dp.tech/dptech/dp/native/prod-576590/903079/qe-7.1-ph:20260609193307 \
  bash build_docker_image.sh
```

Bohrium's public documentation currently says direct Docker push is not
supported. The documented Bohrium-native route for this artifact is:

1. Start a management node from `registry.dp.tech/dptech/quantum-espresso:7.1`.
2. Upload `qe-7.1-ph-lbg.tar.gz` and `node_install_runtime.sh` to the node.
3. Run:

   ```bash
   bash node_install_runtime.sh qe-7.1-ph-lbg.tar.gz
   ```

4. In Bohrium Image Center, create a custom image based on that existing node.

This avoids the Bohrium Dockerfile-builder limitation that local `COPY` inputs
are not supported there yet.

### Current Bohrium Seed Node

The prepared seed node is:

```text
project: gaia-knowledge-base / 576590
node: qe71-ph-image-seed-20260609 / 1474313
base image: registry.dp.tech/dptech/quantum-espresso:7.1
node image id: 1645
sku: c2_m4_cpu / 388
runtime prefix: /opt/qe-7.1-ph-lbg
```

Use `lbgImageId=1645` from `lbg image ls -t "Quantum Espresso" --json` when
creating a management node. The plain `id` field from that public-image listing
does not identify the node image correctly.

The node has already been prepared with:

```bash
cd /root/qe71-ph-image
bash node_install_runtime.sh qe-7.1-ph-lbg.tar.gz
```

Verification on the seed node:

```text
command -v pw.x -> /opt/qe-7.1-ph-lbg/bin/pw.x
command -v ph.x -> /opt/qe-7.1-ph-lbg/bin/ph.x
```

`/root/.bashrc` was also adjusted to silence the oneAPI `setvars.sh` banner for
non-interactive SSH sessions. Without that, `scp` and `sftp` fail with
`Received message too long` because the banner corrupts the transfer protocol.

## Use the Image

The parsed reproduction rows in `../../results/lbg_qe71_np8_sigma0025.csv` used
the tarball-upload path rather than relying on the custom image being globally
available. The stable command shape was:

```bash
NP=8 NK=1 \
PW_BIN=/opt/qe-7.1/bin/pw.x \
PH_BIN=./qe-7.1-ph-lbg/bin/ph.x \
SIGMA=0.025 \
CLEAN_QE_SCRATCH=1 CLEAN_RUNTIME=1 \
bash run_lbg.sh
```

After a custom image exists in Bohrium, use the custom image address in LBG jobs:

```bash
lbg job submit \
  -c 'pw.x < scf.in; ph.x < ph.in' \
  -im registry.dp.tech/dptech/dp/native/prod-576590/903079/qe-7.1-ph:20260609193307 \
  -sc c128_m512_cpu \
  -pjid 576590 \
  -p ./job_input
```
