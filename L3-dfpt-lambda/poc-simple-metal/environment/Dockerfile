FROM python:3.12-slim
# Cheap verifier image: λ comparison only. A real DFPT solve runs off-image
# (Quantum ESPRESSO on HPC); the agent reports λ, ω_log, core_hours.
RUN pip install --no-cache-dir numpy
WORKDIR /app
