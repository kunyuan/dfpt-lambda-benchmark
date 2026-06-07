---
name: qe-eph-lambda
description: Compute the electron-phonon coupling λ (and ω_log) from first principles with Quantum ESPRESSO for the dfpt-lambda-benchmark — fetch a structure from OpenLAM, relax to the target pressure, run DFPT electron-phonon, extract λ, and compare to the paper reference. Use when reproducing/filling λ gold values or turning a material track into a runnable L3 task. Encodes the hard-won gotchas (ibrav, pressure relaxation, q-grid convergence, MPI & remote-ops pitfalls) found while validating this benchmark.
---

# Computing electron-phonon λ with Quantum ESPRESSO (for dfpt-lambda-benchmark)

End-to-end recipe to go **material → λ, ω_log**, and the traps that cost real time
to discover. Validated on a 192-core server against WF-6 paper references.

## Pipeline

```
LKM            -> formula, condition (pressure), functional, λ/ω_log GOLD, polymorph
OpenLAM        -> crystal structure (lattice + atomic coordinates) by formula
QE (pw.x/ph.x) -> vc-relax to pressure -> scf -> ph el-ph -> λ, ω_log
compare        -> λ_computed vs paper gold
```

The benchmark **gold is the paper's reported λ** (already in `data/lambda_reference.csv`);
running QE is to *validate* that gold is reachable and to fill missing values.

## Environment (one-time)

- **QE**: `conda create -n qe -c conda-forge qe openmpi` → native, includes
  `pw.x ph.x lambda.x q2r.x matdyn.x` + Open MPI. (On Apple Silicon use
  `CONDA_SUBDIR=osx-64 conda create ...` to run Intel binaries via Rosetta.)
- **OpenLAM** (structures): `pip install git+https://github.com/deepmodeling/openlam.git`
  in a **dedicated conda env** — it pins old `numpy==1.26 / ase==3.22 / pymatgen==2024.3`
  and will wreck a modern base env (breaks chgnet/gpaw/pyxtal/gaia-lang…). Auth:
  `export BOHRIUM_ACCESS_KEY=$DP_ACCESS_KEY` (DP Technology key == Bohrium key).
- **Pseudopotentials**: per-element on demand. **Norm-conserving SG15 ONCV PBE** is the
  default for el-ph:
  `http://www.quantum-simulation.org/potentials/sg15_oncv/upf/<El>_ONCV_PBE-1.2.upf`.

## ⚠️ The five gotchas (each cost hours to find)

1. **`ibrav=0` + a multi-atom cell makes `ph.x` SIGSEGV at phonon setup.** This is the
   big one. 1-atom cells with `ibrav=0` are fine; ≥2 atoms crash *before the first q*
   (right after "Dynamical matrices for (n,n,n)"). **Use the proper Bravais `ibrav`**
   (e.g. hexagonal→`ibrav=4`, A15/cubic→`ibrav=1`/`2`/`3`) for any multi-atom phonon
   run. It is **not** the pseudopotential and **not** k-point pools — both were
   wrongly blamed before the real cause (ibrav) was isolated by direct test.
2. **High-pressure cases must be `vc-relax`-ed to the target pressure.** An un-relaxed
   "representative" cell gave λ **2–3× too high** (sc-P, fcc-Li). After
   `vc-relax (&cell press=<kbar>)`, λ landed within +2–4 %. λ is extremely
   volume-sensitive for compressed/soft systems.
3. **q-grid convergence is material-dependent.** Simple metals are fine at 2×2×2–4×4×4
   (λ within a few %; ω_log needs ≥4×4×4 — Ta ω_log went 175→153 K from 2×2×2→4×4×4).
   **Strong-coupling systems (MgB₂) badly overestimate on coarse grids** (λ≈1.4–2 on
   2×2×2 vs 0.75 converged) because the E₂g coupling peaks near Γ — they need 6×6×6+
   or EPW/Wannier interpolation. Cost ∝ number of irreducible q (≈ linear).
4. **OpenLAM: pick the ground state by energy PER ATOM, not total energy.** Total
   energy favors larger cells (more formula units) and selects the wrong polymorph
   (picked a 6-atom P-1 MgB₂ over the 3-atom P6/mmm). Prefer the structure whose space
   group matches the LKM-reported prototype; else min(energy/n_atoms).
5. **Remote ops:** never `pkill -f "ph.x"` over SSH — the pattern matches your own
   command line and kills the shell mid-script. Use `pkill -9 -x ph.x` (exact name).
   Run jobs with `nohup … &` + a flag file and poll; **don't run heavy cases
   concurrently** (core contention stalls them — the Γ DFPT silently hangs).

## QE settings that work

```
&system
  ibrav=<proper Bravais>, celldm(...)=...     ! NOT ibrav=0 for >1 atom
  ecutwfc=80, ecutrho=320                       ! SG15 NC: ecutrho≈4×ecutwfc; B/Fe need ≥80–90
  occupations='smearing', smearing='methfessel-paxton', degauss=0.02
  nspin=1                                        ! "nm" cases (e.g. hcp Fe @100GPa is non-magnetic)
&inputph
  electron_phonon='simple', el_ph_sigma=0.005, el_ph_nsigma=10
  ldisp=.true., nq1=nq2=nq3=4, tr2_ph=1.0d-14
```
- SCF k-grid 24³ (denser for the el-ph double-delta if λ unconverged).
- MPI: `mpirun --oversubscribe -np N pw.x -nk N` (k-pools). `OMP_NUM_THREADS=1`.

## λ / ω_log extraction (from `ph.x` el-ph output)

`electron_phonon='simple'` prints, per irreducible q, the **star multiplicity**
("Number of q in the star = M") and, for each Gaussian-broadening σ, the per-mode
`lambda(ν)`. The totals:

```
λ_total(σ)  = Σ_q (M_q / N) Σ_ν λ_qν             , N = Σ_q M_q  (= total q in the grid)
ω_log(σ)    = exp[ Σ_q (M_q/N) Σ_ν λ_qν ln(ω_qν) / λ_total ]   , ω from "freq (..) = .. [cm-1]"
```
Evaluate at the **el_ph σ plateau** (~0.020–0.025 Ry, near the SCF degauss). Skip the
Γ acoustic modes (ω≈0). Convert cm⁻¹→K ×1.43877. See
[`references/extract_lambda.py`](references/extract_lambda.py).

## Cost model (per material, DFPT el-ph)

Cost ≈ (#irreducible q) × (cost/q). Measured @48 cores: MgB₂ 2×2×2 (4 q) ≈ 11 min;
Fe 2×2×2 (4 q) ≈ 23 min. Scaling 2×2×2→6×6×6 ≈ ×7. Tiers: simple metal 10²–10³,
intermetallic/2D/heavy 10³–10⁴, hydride (anharmonic/SSCHA) 10⁴–10⁵ core-h.

## Validation evidence (this benchmark)

| material | λ computed / gold | note |
|---|---|---|
| bcc Ta | 0.927 / 0.877 (+6%) | simple metal, 4×4×4 ✅ |
| sc P (relaxed 20 GPa) | 0.808 / 0.795 (+2%) | relaxation essential ✅ |
| fcc Li (relaxed 30 GPa) | 0.862 / 0.83 (+4%) | ✅ |
| fcc La | 1.393 / 1.06 (+31%) | 4f, physics-hard |
| hcp Fe (ibrav=4) | 0.42 / 0.33 (+27%) | crash fixed by ibrav |
| MgB₂ (ibrav=4) | 1.44 (2×2×2) / 0.75 | needs dense q (E₂g) |

**Bottom line:** the pipeline runs end-to-end; accuracy is gated by per-material
convergence — proper `ibrav`, pressure relaxation, q-grid density, and f-electron
treatment. That difficulty gradient is exactly why "compute λ" is a meaningful agent
benchmark.
