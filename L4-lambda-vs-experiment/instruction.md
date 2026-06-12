# L4 — electron-phonon λ graded against EXPERIMENT

Compute the electron-phonon coupling constant **λ** from first principles for each
material and output it. Unlike L3 (gold = the source paper's computed λ), **L4 gold is
the experimentally-inferred λ** (tunneling inversion, specific-heat mass enhancement,
point-contact spectroscopy, Tc-inversion), with a per-case uncertainty σ.

All materials in this level are ones where first-principles theory and experiment are
known to agree — the task measures whether **your** calculation reaches that agreement.
The method (code, functional, SOC, magnetic state, multiband treatment, q/k meshes) is
entirely **your choice**; choosing it correctly per material is the skill being tested.

## I/O

Input per case (`packet/cases.csv`): `case_id, material, material_type, condition`.
Nominal starting structures are in `packet/structure_hints.json` (relax them first).
Write **`run_lambda.py`** that emits `out.csv` with `case_id,lambda,core_hours` (one
row per input case). The verifier runs it on concealed held-out cases drawn from the
same material types. HPC runs **off-sandbox** (open-source codes, e.g. Quantum
ESPRESSO); `run_lambda.py` may read your cached results.

## Train / calibration set

`packet/dev_gold.csv` gives, for every development case: the experimental λ with its
σ and method, **and** the best literature first-principles λ with its method. Use it
to calibrate your workflow per material class before touching the held-out cases.
Lessons are deliberately embedded: Pb requires spin-orbit coupling (1.08 → 1.56);
V's tunneling value is corrupted by surface oxidation (trust specific-heat); NbN's σ
is wide because samples are stoichiometry-sensitive; Th's γ-route gold carries extra
non-phonon renormalization (worst pair in the set — kept as a calibration warning).

## Scoring (scaled by the SOTA theory-experiment gap, not by experimental error)

The yardstick is how well state-of-the-art first-principles theory matches experiment
on this dataset: the mean relative gap |λ_sota − λ_exp|/λ_exp over all 21 pairs is
**G = 11.7%** (per-pair table in the dev gold). Per case the verifier computes
`d = |λ_pred − λ_exp| / λ_exp`; the leaderboard number is **ratio = mean(d) / G**
(below 1 means you out-compute the published state of the art). **PASS requires
mean(d) ≤ G AND every case d ≤ 3G** (the cap kills single catastrophic misses — a
forgotten SOC or a wrong magnetic state). Submitting the literature values verbatim
gives ratio ≈ 0.79. `core_hours` is reported (accuracy × cost axis), not gated.
