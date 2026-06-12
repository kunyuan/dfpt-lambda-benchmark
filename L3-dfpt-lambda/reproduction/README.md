# L3 Reproduction Results and LBG Infrastructure

This directory contains the reproducible record for the first LBG/QE validation
batch of the L3 `structure -> DFPT -> lambda` benchmark. It is intentionally
separate from the benchmark task packets: task packets define what agents should
solve, while this directory records how the current reference workflow was tested.

## What Is Included

| path | purpose |
|---|---|
| `results/lbg_qe71_np8_sigma0025.csv` | curated comparison table: reproduced lambda, paper lambda, omega_log, top-q share, and verdict |
| `results/summary_by_material_type.md` | human-readable status by material class |
| `results/lbg_results_20260610_mpiifort_np8_batch1.raw.csv` | raw parsed LBG result ledger before material metadata enrichment |
| `jobs/` | LBG job ledgers, including failed compiler/runtime trials and successful NP=8 batches |
| `inputs/selected_cases.csv` | selected non-duplicative cases for q-grid scaling and cross-category smoke tests |
| `inputs/scaling_runs/` | generated QE `scf.in`, `ph.in`, and `run.sh` inputs for Tier A scaling cases |
| `inputs/cross_category_runs/` | generated smoke-test inputs for hydride, 2D/layered, heavy-SOC proxy, and intermetallic cases |
| `scripts/` | helpers to regenerate inputs, build compact LBG bundles, summarize `lambda.dat`, and curate result tables |
| `build/qe71-ph-lbg/` | QE 7.1 `ph.x` build and Docker/custom-image notes for LBG |

Generated scratch, `*.save`, wavefunction files, downloaded LBG output bundles, and
Python bytecode are ignored. The committed files are small enough to review on
GitHub.

## Current Status

The curated table reports the `sigma=0.025 Ry` row from `lambda.dat`. A run is
called `reproduced` only when:

- lambda is within 15 percent of the paper reference;
- omega_log is within 15 percent when a reference value is available;
- `top_q_share_pct` is not above 25 percent.

As of this snapshot:

| material type | status |
|---|---|
| `simple-metal` | strong fixed-structure reproductions for high-pressure sulfur: `lam263` q4/q6 and `lam264` q4/q6; `lam262` q4 is close but q6 drift remains unresolved |
| `intermetallic` | workflow is running, but this batch has not produced a clean new reproduction yet; `lam154` is q-grid dominated and `lam138` finished without a compact lambda artifact |
| `2d-layered` | smoke tests ran for `lam009` and `lam035`, but both are q-grid/structure-source limited |
| `hydride` | harmonic DFPT smoke tests ran for `lam104` and `lam123`; `lam123` has lambda close to the paper but omega_log is far off |
| `heavy-SOC` | scalar/non-SOC smoke jobs were submitted in the job ledgers; true SOC reproduction still needs fully relativistic pseudopotentials and `noncolin/lspinorb` inputs |

This should be read as an internal reproduction record, not as a final leaderboard
result set. The strongest current conclusion is that the LBG/QE workflow is now
usable across material classes, while production-quality agreement is presently
concentrated in the simple-metal/high-pressure-element subset.

## Runtime Used for the Successful Batch

The stable LBG execution mode for the parsed rows was:

```bash
NP=8
NK=1
PW_BIN=/opt/qe-7.1/bin/pw.x
PH_BIN=./qe-7.1-ph-lbg/bin/ph.x
SIGMA=0.025
CLEAN_QE_SCRATCH=1
CLEAN_RUNTIME=1
bash run_lbg.sh
```

The base image was `registry.dp.tech/dptech/quantum-espresso:7.1`. That image has
`pw.x` but not a usable `ph.x` for these DFPT jobs, so the `ph.x` runtime was built
separately under `build/qe71-ph-lbg/` and uploaded with the job bundle. Larger MPI
layouts were less stable for these small cells because QE can hit FFT/k+q
partitioning limits.

## Regenerating Inputs

From the repository root:

```bash
python L3-dfpt-lambda/reproduction/scripts/prepare_scaling_runs.py
```

This reads `inputs/selected_cases.csv` and writes `inputs/scaling_runs/<case>/q*/`.
The generated `run.sh` scripts expect `pw.x`, `ph.x`, MPI, and the SG15 pseudo
directory at `L3-dfpt-lambda/pseudos/pseudo`.

To build a compact LBG input bundle for a generated run:

```bash
python L3-dfpt-lambda/reproduction/scripts/make_lbg_bundle.py lam263 6 \
  --qe-runtime-tarball /path/to/qe-7.1-ph-lbg.tar.gz
```

## Updating Results

After downloading a finished LBG job, parse `ph.out` into `lambda.dat` with the
QE electron-phonon extractor, then append the parsed row to the raw CSV. Rebuild
the benchmark-facing tables with:

```bash
python L3-dfpt-lambda/reproduction/scripts/curate_lbg_results.py
```

For local, non-LBG runs that already have `lambda.dat` under
`inputs/scaling_runs/<case>/q*/`, use:

```bash
python L3-dfpt-lambda/reproduction/scripts/summarize_scaling_results.py
```

That writes `results/scaling_summary.csv`.

## Known Gaps

- The remaining long-running jobs in the ledgers should be refreshed before this
  snapshot is treated as current.
- `lam138` and `lam253` finished on LBG, but their full output bundles were too large
  to download as a whole, so the compact `lambda.dat` artifact was not retrieved.
- Hydride and 2D cases need method-specific production paths before their smoke runs
  should be used as benchmark-grade reproductions.
- True heavy-SOC validation requires a separate fully relativistic QE input path.
