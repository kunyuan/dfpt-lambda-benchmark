# L3 — electron-phonon λ for hydride superconductors

Compute the electron-phonon coupling constant **λ** and the logarithmic-average
phonon frequency **ω_log (K)** from first principles for each hydride material, then
output them. The HPC runs **off-sandbox** with open-source **Quantum ESPRESSO**
(`pw.x`/`ph.x`; see `packet/pseudos/` for the SG15 pseudopotentials). **Choose the
method** appropriate to this material class yourself (typically DFPT+anharmonic/SSCHA).

## Two case modes (`packet/cases.csv` column `mode`)
- **structure-ready** — a ready QE input is in `packet/structures/<structure_file>`
  (already a proper `ibrav`). For a high-pressure `condition`, relax to that pressure.
- **build-from-spec** — no ready structure; `packet/structure_hints.json` gives the
  paper's space group, prototype, lattice constants, any coordinates/bond lengths and
  pressure. **Construct the crystal structure from that spec**, then run.

## I/O
Input per case: `case_id, mode, structure_file, condition, mu_star`. Write
**`run_lambda.py`** that emits `out.csv` with `case_id,lambda,omega_log_K,core_hours`
(one row per input case). The verifier runs it on concealed held-out cases.
`packet/dev_gold.csv` gives reference λ/ω_log for the development cases to calibrate.

## Scoring
Each `lambda` and (where a gold ω_log exists) `omega_log_K` must be within **15 %** of
the paper reference. `core_hours` is the reported cost axis (not gated). PASS requires
all held-out cases within tolerance.
