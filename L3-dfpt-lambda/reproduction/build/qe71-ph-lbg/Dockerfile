FROM registry.dp.tech/dptech/quantum-espresso:7.1

ARG QE_RUNTIME_TARBALL=qe-7.1-ph-lbg.tar.gz
ARG QE_PREFIX=/opt/qe-7.1-ph-lbg

COPY ${QE_RUNTIME_TARBALL} /opt/qe-7.1-ph-lbg.tar.gz

RUN set -eux; \
    tar -C /opt -xzf /opt/qe-7.1-ph-lbg.tar.gz; \
    test -x "${QE_PREFIX}/bin/pw.x"; \
    test -x "${QE_PREFIX}/bin/ph.x"; \
    ln -sf "${QE_PREFIX}/bin/pw.x" /usr/local/bin/pw.x; \
    ln -sf "${QE_PREFIX}/bin/ph.x" /usr/local/bin/ph.x; \
    rm -f /opt/qe-7.1-ph-lbg.tar.gz

ENV PATH="/opt/qe-7.1-ph-lbg/bin:${PATH}"

LABEL org.opencontainers.image.title="Quantum ESPRESSO 7.1 with PHonon"
LABEL org.opencontainers.image.description="LBG QE 7.1 runtime with pw.x and ph.x for DFPT lambda reproduction"
