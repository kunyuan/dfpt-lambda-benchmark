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
| simple / elemental metal | `simple-metal/` | 40 | DFPT-direct | 10²–10³ |
| intermetallic compound | `intermetallic/` | 107 | DFPT-direct | 10³–10⁴ |
| heavy-element (SOC) | `heavy-soc/` | 38 | DFPT + SOC | 10³–10⁴ |
| 2D / layered | `2d-layered/` | 38 | DFPT + Wannier/EPW | 10³–10⁴ |
| high-pressure hydride | `hydride/` | 53 | DFPT + anharmonic/SSCHA | 10⁴–10⁵ |

Each `cases.csv` row: `case_id, paper_id, material, condition, lambda_ref,
omega_log_K/theta_D_K, mu_star, expected_method, cost_tier_coreh`.

## Scoring (intended)

`|λ_pred − λ_ref| / λ_ref` within tolerance (e.g. 15 %, matching the
computed-vs-experimental spread), **and** the agent self-reports core-hours used —
graded on the accuracy × cost Pareto frontier.

## Status — packaged Harbor tracks

The 276 L3 cases are packaged as five runnable Harbor-style tasks. Each track has
`task.toml`, `instruction.md`, an `environment/packet/`, a baseline `solution/`, and
`tests/` that compare submitted λ/ω_log values against root-only gold at 15 %
tolerance while recording reported core-hours.

| track | cases | dev | hidden | structure-ready | build-from-spec |
|---|---:|---:|---:|---:|---:|
| `simple-metal` | 40 | 26 | 14 | 11 | 29 |
| `intermetallic` | 107 | 71 | 36 | 55 | 52 |
| `heavy-soc` | 38 | 25 | 13 | 13 | 25 |
| `2d-layered` | 38 | 25 | 13 | 0 | 38 |
| `hydride` | 53 | 35 | 18 | 1 | 52 |
| **total** | **276** | **182** | **94** | **80** | **196** |

Two execution modes are present:

1. **`structure-ready`** — the packet includes a proper-`ibrav` QE input in
   `environment/packet/structures/`. The agent runs SCF → phonon/electron-phonon →
   λ extraction.
2. **`build-from-spec`** — the packet includes structural hints from the paper
   (`structure_hints.json` / `.csv`) but no trusted ready coordinates. Some rows were
   explicitly demoted after the LKM audit because their OpenLAM/MP candidate did not
   match the paper's target phase, pressure, formula, or material family.

Validated host-side self-checks cover all five tracks. The full target-structure
audit is in `../data/structure_targets.csv` and
`../data/structure_targets_summary.md`. Real QE reproductions on a 192-core server
are summarized in `VALIDATION.md`. The first organized LBG/QE batch, including
job ledgers, selected scaling inputs, QE 7.1 `ph.x` build notes, and curated
material-type result summaries, is in `reproduction/`. The remaining hardening
work is to rebuild the demoted cases from paper-specific structures, run these
packages through the real Harbor runner, and replace the cached-gold verifier with
an artifact-aware verifier for submitted DFPT outputs.
