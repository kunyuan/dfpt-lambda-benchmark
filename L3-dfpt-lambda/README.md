# L3 — structure → DFPT → λ

The first-principles level: given a relaxed crystal structure (+ pseudopotentials +
a protocol), run density-functional perturbation theory (phonons + electron-phonon
matrix elements) and return the electron-phonon coupling **λ** and the
logarithmic-average phonon frequency **ω_log**.

Organized into **material-type tracks** — the agent is told the material and
conditions and must **choose** the appropriate method; the expected method and cost
tier are hidden metadata (in each `cases.csv`), not given to the agent.

| track | dir | cases | method (hidden) | cost tier (core-h) |
|---|---|---:|---|---|
| simple / elemental metal | `simple-metal/` | 42 | DFPT-direct | 10²–10³ |
| intermetallic compound | `intermetallic/` | 105 | DFPT-direct | 10³–10⁴ |
| heavy-element (SOC) | `heavy-soc/` | 38 | DFPT + SOC | 10³–10⁴ |
| 2D / layered | `2d-layered/` | 38 | DFPT + Wannier/EPW | 10³–10⁴ |
| high-pressure hydride | `hydride/` | 53 | DFPT + anharmonic/SSCHA | 10⁴–10⁵ |

Each `cases.csv` row: `case_id, paper_id, material, condition, lambda_ref,
omega_log_K/theta_D_K, mu_star, expected_method, cost_tier_coreh`.

## Scoring (intended)

`|λ_pred − λ_ref| / λ_ref` within tolerance (e.g. 15 %, matching the
computed-vs-experimental spread), **and** the agent self-reports core-hours used —
graded on the accuracy × cost Pareto frontier.

## Status — TODO to make runnable

Each case currently carries the **reference λ/ω_log** but **not** the crystal
structure. To make these runnable Harbor tasks:

1. Attach a relaxed structure per case (from the source paper or Materials Project)
   → `environment/packet/structure.cif` (+ conditions: pressure/doping/strain).
2. Add an HPC-aware verifier: either run the DFPT pipeline, or compare against a
   cached reference λ; emit accuracy + core-hour cost.
3. Wrap each track as standard Harbor tasks (`task.toml`, `instruction.md` with the
   **method withheld**, `environment/`, `solution/`, `tests/`).
