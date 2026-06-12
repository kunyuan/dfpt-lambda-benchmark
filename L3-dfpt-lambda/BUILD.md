# L3 build status — structures & pseudopotentials

Systematic preparation of runnable structures for the L3 material tracks, following
the [`lambda-benchmark-build`](../.claude/skills/lambda-benchmark-build/SKILL.md) skill.

## What's here

- **`structures/*.scf.in`** — 127 committed QE `pw.x` inputs. After the LKM
  target-structure audit and first repair batch, 80 case rows reference these files as trusted
  `structure-ready` inputs. The remaining files are kept for provenance but are not
  handed to agents unless their case remains `structure-ready`.
- **`build_status.csv`** — per case: formula, structure source, structure file, space
  group, and status (`structure-ready` / `build-from-spec`).
- **`../data/structure_targets.csv`** — audited paper target phase/prototype, space
  group, pressure, structure completeness, confidence, and mismatch flags for all
  276 cases.
- **`pseudos/manifest.json`** + **`pseudos/fetch_sg15.sh`** — the 48 elements needed,
  with SG15 ONCV-PBE filenames + cutoffs, and a download script. The `.upf` files are
  **not committed** (run the script to fetch ~free SG15).

## Coverage After Structure Audit

276 cases / 188 non-empty unique formulas. **80 cases are structure-ready** (29 %):
55 from OpenLAM, 10 from Materials Project, and 15 from LKM-derived full/prototype
structures. The remaining 196 cases are **build-from-spec** because no trusted paper-matched
structure is currently packaged. Many were demoted from OpenLAM/MP candidates after
the audit found a phase, pressure, formula, or material-family mismatch.

| material track | structure-ready / total | build-from-spec |
|---|---:|---:|
| intermetallic | 55 / 107 | 52 |
| simple-metal | 11 / 40 | 29 |
| 2d-layered | 0 / 38 | 38 |
| hydride | 1 / 53 | 52 |
| heavy-soc | 13 / 38 | 25 |

`build-from-spec` does not always mean "missing from OpenLAM"; it also includes
cases where OpenLAM returned a plausible formula match but the paper target is a
different polymorph, pressure-stabilized phase, doped/supercell system, or even a
different material family. Check `structure_targets.csv` before launching QE.

## To run a built case (gold = paper λ in `data/lambda_reference.csv`)

```bash
cd pseudos && bash fetch_sg15.sh && cd ..          # one-time: download SG15
# pick a structure-ready case from build_status.csv -> its structures/<formula>.scf.in
# (high-pressure: vc-relax to the condition's pressure first)
# then scf -> ph.x el-ph -> extract λ  (see ../.claude/skills/qe-eph-lambda/)
```

## Tier 2 (next)

- repair the case_id ↔ paper/condition provenance mismatches flagged in
  `../data/structure_targets.csv`;
- rebuild demoted OpenLAM/MP candidates from the paper target phase, pressure,
  doping, strain, or supercell;
- recover supplemental CIFs / COD / Materials Project / prototype-from-LKM-lattice
  for the genuinely absent compounds.

## Two task modes — every case is now a task

After the database + LKM build, the 276 cases split into two modes (`build_status.csv`):

- **`structure-ready` (80)** — a ready proper-`ibrav` QE input in `structures/`
  (OpenLAM 55 / MP 10 / LKM 15). The agent just runs scf → ph → λ after any
  condition-specific relaxation.
- **`build-from-spec` (196)** — no trusted packaged coordinates exist. Instead of a
  ready structure, the agent is given the audited target information in
  [`structure_hints.json`](structure_hints.json) / `structure_hints.csv`:
  formula, condition (pressure), **space group, prototype, lattice constants**
  (where reported), any atomic coordinates / bond lengths, the μ\*, audit
  confidence, mismatch flags, and recommended next step. The agent must
  **construct or repair the crystal structure from this spec** before computing λ.

Structure construction is then part of the L3 task for these — a harder, genuinely
research-like sub-skill — with the gold still the paper's λ in
`data/lambda_reference.csv`.
