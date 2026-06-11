# Submit Notes

Project:

```text
gaia-knowledge-base / 576590
```

Candidate build images:

```text
registry.dp.tech/dptech/ubuntu:22.04-py3.10-intel2022
registry.dp.tech/dptech/ubuntu:ubuntu24.04-py3.12
registry.dp.tech/dptech/quantum-espresso:7.1
```

The finished bundle should be tested with:

```bash
tar -xzf artifacts/qe-7.1-ph-lbg.tar.gz
./qe-7.1-ph-lbg/bin/pw.x < /dev/null || true
./qe-7.1-ph-lbg/bin/ph.x < /dev/null || true
```

LBG unpacks the contents of the submitted input directory directly into
`/home/input_lbg-<user>-<job>/`; it does not preserve the outer directory name.
Submit commands should therefore call files such as `./build_qe71_ph.sh` directly.

The QE 7.1 source archive from GitHub/GitLab does not include submodule content.
Include pinned external archives in the submitted input directory; otherwise the
build will try to fetch `external/fox`, `external/mbd`, and `external/devxlib`
from GitHub/GitLab during the LBG job.
