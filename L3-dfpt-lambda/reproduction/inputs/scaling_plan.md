# L3 Scaling Reproduction Plan

This folder defines the next detailed QE reproduction batch. It intentionally does
not rerun cases that already reproduced successfully in `VALIDATION.md`; the goal is
to test convergence on a small, representative set of new paper-matched structures.

## Target Property

Converge the electron-phonon observables against the paper reference:

- total electron-phonon coupling `lambda`
- `omega_log_K`
- the `top_q_share` diagnostic from `extract_lambda.py`

Convergence gates:

- `lambda` changes by <= 10 percent between the two densest q-grids, or the remaining
  discrepancy is explained by a dominant phonon anomaly.
- `omega_log_K` changes by <= 10 percent between the two densest q-grids when present.
- `top_q_share` should be below 25 percent for production; above that means a single
  `(q, nu)` dominates and the q-grid is probably still too coarse.

## Already Successful: Do Not Rerun

The following cases/families already have successful QE reproduction evidence and
are excluded from this batch:

- bcc Ta
- sc P at 20 GPa
- fcc Li at 30 GPa
- bcc V and fcc Y
- non-magnetic hcp Fe at 100 GPa
- MgB2
- NbC, VC, and HfN
- YIn3

## Selected Batch

The selected cases are in `inputs/selected_cases.csv`.

Tier A is the first lbg/QE batch:

- high-pressure one-atom systems: `lam262`, `lam263`, `lam264`, `lam150`
- a new antiperovskite: `lam138`
- an A15 intermetallic: `lam253`
- a not-yet-run B1 carbide/nitride analogue: `lam154`

Tier B is for follow-up once Tier A is stable:

- `lam052`/`lam053` for SOC vs non-SOC heavy-element comparison; true SOC requires
  fully relativistic pseudopotentials and `noncolin/lspinorb` inputs.
- `lam104` as a harmonic hydride smoke test; the paper-class method is harder than
  plain harmonic DFPT, so do not mix it into the Tier A convergence conclusion.

## Scaling Protocol

For each Tier A case:

1. Run fixed-structure SCF plus `ph.x electron_phonon='simple'` on q-grids listed in
  `inputs/selected_cases.csv`.
2. For high-pressure cases, run a `vc-relax` to the target pressure before final
   production. The fixed-structure sweep is still useful as a cheap preflight, but
   the reported reproduction value should come from the relaxed cell.
3. Use the el-ph Gaussian broadening scan from QE and report the plateau at
   `sigma=0.025 Ry`.
4. If `lambda(2x2x2)` is much larger than `lambda(4x4x4)`, run the next q-grid and
   inspect `top_q_share`.
5. Only compare to the paper once the q-grid trend is stable.

The primary sweep is q-grid scaling. If q-grid is stable but the value is still off,
then run k-grid and `ecutwfc` sweeps one parameter at a time.

## Generated Runs

Run:

```bash
python L3-dfpt-lambda/reproduction/scripts/prepare_scaling_runs.py
```

This creates `inputs/scaling_runs/<case_id>/q<qgrid>/` directories containing:

- `scf.in`
- `ph.in`
- `run.sh`

`run.sh` expects QE (`pw.x`, `ph.x`) and MPI in PATH, and a populated SG15 pseudo
directory at `L3-dfpt-lambda/pseudos/pseudo`. Fetch pseudos once with:

```bash
cd L3-dfpt-lambda/pseudos
bash fetch_sg15.sh
```

After runs finish, summarize convergence with:

```bash
python L3-dfpt-lambda/reproduction/scripts/summarize_scaling_results.py
```

This writes `results/scaling_summary.csv` with `lambda`, `omega_log_K`,
paper-reference relative errors, the densest-vs-previous q-grid delta, and
`top_q_share_pct`.
