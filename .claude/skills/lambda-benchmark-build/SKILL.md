---
name: lambda-benchmark-build
description: Turn a material-track cases.csv (formula + condition + λ gold from LKM) into runnable L3 Harbor tasks for dfpt-lambda-benchmark — fetch the crystal structure from OpenLAM, convert it to a PROPER-ibrav QE input (never ibrav=0 for multi-atom), attach the matching free pseudopotentials, relax to the target pressure, and package the task. Use when expanding a material track from data-only into a runnable task. Focuses on structure (lattice) preparation and pseudopotential selection; defer the actual QE run to the qe-eph-lambda skill.
---

# Building dfpt-lambda-benchmark L3 tasks (structures + pseudopotentials)

Each L3 case needs a **complete, runnable QE input**: a crystal structure in the
*right* lattice representation + matching pseudopotentials + the condition. The gold
(λ, ω_log) is already the paper value in `data/lambda_reference.csv`. This skill is
the data-prep half; running QE + extracting λ is the [`qe-eph-lambda`](../qe-eph-lambda/SKILL.md) skill.

## Inputs you start from (per case)
`case_id, paper_id, material, condition, material_type, lambda_ref, omega_log_K,
mu_star` from the track's `cases.csv`. You need to add: a **structure** and
**pseudopotentials**.

## Step 1 — paper target → structure candidate

Start from the audited target, not from the formula alone:

1. Read `data/structure_targets.csv` for the `case_id`.
2. Use its `target_formula_or_system`, `space_group_symbol`, `pressure_GPa`,
   `phase_or_prototype`, `atomic_positions_status`, `mismatch_flags`, and
   `recommended_next_step`.
3. If `mismatch_flags` says the reference row is cross-family, paper-title
   mismatched, or material/condition inconsistent, repair the source mapping before
   building any QE input.
4. If the current row is `build-from-spec`, prefer the paper lattice/CIF/prototype
   specified in `L3-dfpt-lambda/structure_hints.json`.

OpenLAM is only a **candidate provider**. It is acceptable when the returned
candidate matches the paper target formula, phase/prototype, space group, and
condition after any required pressure relaxation. Do not use the lowest-energy
formula match as ground truth.

```python
from lam_optimize import CrystalStructure   # env: openlam ; export BOHRIUM_ACCESS_KEY=$DP_ACCESS_KEY
items = CrystalStructure.query_by_offset(formula=clean_formula, limit=8)["items"]
# GROUND STATE = min energy PER ATOM (NOT total energy — total favours bigger cells)
cands = [(cs.energy/len(cs.structure), cs) for cs in items]
# prefer the polymorph whose space group matches the LKM-reported prototype:
pick = next((cs for _,cs in cands if cs.structure.get_space_group_info()[0]==lkm_sg), min(cands)[1])
struct = pick.structure        # pymatgen Structure: lattice + fractional coords
```
- `clean_formula` must be a real formula ("MgB2", "Nb3Sn") — extract it from LKM /
  the material name, not the descriptive string.
- Record provenance: which OpenLAM entry (space group, energy/atom) was used.
- If OpenLAM lacks it or returns the wrong polymorph / composition / dimensionality:
  fall back to the paper supplement, COD, Materials Project, or a prototype build
  from the audited LKM space group + lattice constant.

## Step 2 — structure → **proper-ibrav** QE input  ⚠️ critical

**Never emit `ibrav=0` for a multi-atom cell** — `ph.x` SIGSEGVs at phonon setup
(see qe-eph-lambda gotcha #1). ASE's QE writer defaults to `ibrav=0`, so do **not**
use it as-is. Derive the Bravais `ibrav` + `celldm` from the standardized cell:

```python
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
std = SpacegroupAnalyzer(struct).get_conventional_standard_structure()
# map crystal system + centering -> ibrav, set celldm from a,b,c,angles
```
See [`references/structure_to_qe.py`](references/structure_to_qe.py) for the mapping
(cubic P/F/I→1/2/3, hex→4, rhombohedral→5, tetragonal P/I→6/7, orthorhombic→8–11)
and the `&system`+`ATOMIC_SPECIES`+`ATOMIC_POSITIONS` emitter. High-symmetry
materials (most of this benchmark) are covered; low-symmetry (monoclinic/triclinic)
need manual check.

## Step 3 — pseudopotentials (the part that bites)

Use **one consistent, free, curated set** across all cases (fairness) that is
**stable in `ph.x` electron-phonon**:

- **Default: SG15 ONCV norm-conserving, PBE.** Norm-conserving avoids the
  augmentation machinery that makes ultrasoft/PAW `ph.x` el-ph fragile.
  `http://www.quantum-simulation.org/potentials/sg15_oncv/upf/<El>_ONCV_PBE-1.2.upf`
  (fall back to `-1.1`/`-1.0` if 404). Verify each file starts with `<UPF`.
- **Match the functional** to the paper's. WF-6 is overwhelmingly **PBE**; if a paper
  used LDA/PBEsol, swap the set for that case and note it.
- **Cutoffs**: NC → `ecutrho = 4 × ecutwfc`. SG15 are fairly hard:
  - `ecutwfc ≈ 60 Ry` for simple sp metals,
  - `ecutwfc ≈ 80 Ry` for 2p elements (B, C, N, O) and most compounds,
  - `ecutwfc ≈ 90 Ry` for 3d transition metals / semicore (V, Fe, Nb).
  When unsure, converge total energy / a phonon frequency vs ecutwfc.
- Keep a per-track **manifest**: `element → pseudo_file, ecutwfc`. See
  [`references/pseudopotentials.md`](references/pseudopotentials.md).

Avoid SSSP-efficiency for el-ph: it is mostly ultrasoft/PAW (great for energies, less
robust in `ph.x`). NC (SG15 / PseudoDojo) is the safe choice here.

## Step 4 — condition / pressure

- **High-pressure cases: `vc-relax` to the stated pressure** (`&cell press=<kbar>`,
  10 kbar = 1 GPa) before scf+ph. Un-relaxed cells give λ 2–3× off.
- **Magnetic state**: honour the case ("nm hcp Fe @100 GPa" → `nspin=1`; magnetic →
  `nspin=2` + `starting_magnetization`).
- **SOC** (heavy-element track): `lspinorb=.true., noncolin=.true.` + a
  fully-relativistic pseudo.
- One structure/input **per condition** for multi-condition papers (the `condition`
  column tells you pressure/doping/phase).

## Step 5 — package the Harbor task

Per track, mirror `poc-simple-metal/` (Harbor v1.0 contract):
`task.toml` (correct schema) · `instruction.md` (formula withheld; compute λ,ω_log;
report core-hours) · `environment/packet/` (the `*.scf.in` + `pseudo/` + manifest) ·
`tests/` (`test.sh` runs as `nobody`, writes `reward.txt`; gold root-only; `score.py`
tolerances) · `scripts/selfcheck.sh`. Gold = the paper λ/ω_log; tolerance should be
class-aware (simple metals tight; MgB₂-like / 4f looser, or pair with a q-grid spec).

## Build-time gotchas

- **ibrav** (Step 2) — the #1 cause of downstream `ph.x` crashes.
- **energy PER ATOM** for OpenLAM ground-state selection (total energy picks the
  wrong, larger cell).
- **NC pseudos + matched functional + per-element ecut** — don't mix sets.
- **provenance**: record the OpenLAM entry, pseudo set+version, and (for pressure)
  the relaxed cell, so the gold is reproducible.
- OpenLAM lives in an **isolated conda env** (it pins old numpy/ase/pymatgen).
