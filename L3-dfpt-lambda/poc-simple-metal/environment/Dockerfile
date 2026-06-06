FROM python:3.12-slim
# Cheap verifier image: λ/ω_log comparison only.
RUN pip install --no-cache-dir numpy
WORKDIR /app
# For an actual first-principles run, use an image with Quantum ESPRESSO
# (open-source / GPL — no VASP licence needed), e.g.:
#   FROM debian:12
#   RUN apt-get update && apt-get install -y quantum-espresso   # provides pw.x, ph.x, lambda.x
# plus free PBE pseudopotentials from SSSP / PSlibrary in ./pseudo.
