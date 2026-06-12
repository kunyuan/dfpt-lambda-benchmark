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

## Scoring (uncertainty-normalized, not a flat tolerance)

Per case: `z = (λ_pred − λ_exp) / σ_eff`, `σ_eff = max(σ_exp, 0.05·λ_exp)`; credit
`exp(−z²/2)`. **PASS requires every case within 2σ_eff AND mean credit ≥ 0.50.**
Literature-grade first-principles values pass with mean credit ≈ 0.67 — beating that
margin means out-computing the published state of the art. `core_hours` is reported
(accuracy × cost axis), not gated.
