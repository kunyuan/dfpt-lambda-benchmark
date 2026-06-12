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

## ⚠️ The six gotchas (each cost hours to find)

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
3. **q-grid under-convergence is the #1 cause of a computed λ that is 2–5× too high.**
   Coarse 2×2×2 grossly overestimates λ for any material with a sharp acoustic/optical
   **phonon anomaly** (Kohn anomaly / Fermi-surface nesting / soft mode), because the
   few coarse q-points land on and over-weight the anomalous q whose true phase-space
   is tiny. **Validated convergence (λ at 2×2×2 → 4×4×4 vs paper):**
   NbC 2.44→**0.99** (0.87) · VC 4.39→**1.20** (0.78, needs 6×6×6) · MgB₂ 1.44→**0.66**
   (0.75) · HfN **0.59** already-OK (0.67, no anomaly). **Always do a 2×2×2 then 4×4×4
   convergence check**; if λ drops a lot, it is anomaly-driven → go to 6×6×6 (or EPW).
   Anomaly-free systems (simple metals, HfN) are fine at 2×2×2. ω_log also tightens with
   denser q (Ta 175→153 K). Cost ∝ #irreducible q (≈ linear).
   *Diagnostic:* dump the per-mode `lambda(ν)` per q — λ_qν ≳ 1 on acoustic modes flags
   an anomaly that a coarse grid will over-weight (NbC/VC showed 1.2–4.1 vs HfN's 0.5).
4. **OpenLAM: pick the ground state by energy PER ATOM, not total energy.** Total
   energy favors larger cells (more formula units) and selects the wrong polymorph
   (picked a 6-atom P-1 MgB₂ over the 3-atom P6/mmm). Prefer the structure whose space
   group matches the LKM-reported prototype; else min(energy/n_atoms).
5. **QE 7.x el-ph needs `fildvscf` with `electron_phonon='simple'`.** Without it,
   `ph.x` can fail during input parsing with
   `Error in routine phq_readin (1): El-ph needs a DeltaVscf file`. Add a stable
   prefix such as `fildvscf='dvscf'` in `&inputph`; this writes the first-order
   self-consistent potential that the el-ph path expects.
6. **Remote ops:** never `pkill -f "ph.x"` over SSH — the pattern matches your own
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
  fildvscf='dvscf'
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

## Failure-mode triage (symptom → cause → fix)

When a run fails or λ is far off, match the symptom — most are fixable, not pipeline bugs:

| symptom (in scf.out / ph.out) | cause | fix |
|---|---|---|
| `ph.x` SIGSEGV right after "Dynamical matrices for (n,n,n)" | `ibrav=0` + multi-atom | use proper Bravais `ibrav` |
| `El-ph needs a DeltaVscf file` during `phq_readin` | QE 7.x el-ph input missing first-order potential file prefix | add `fildvscf='dvscf'` to `&inputph` |
| **λ 2–5× too high**, per-mode λ_qν≳1 on acoustic modes | phonon anomaly under-converged on coarse q | denser q (4×4×4→6×6×6); convergence-check |
| computed λ off **and** structure phase/composition ≠ paper (e.g. dhcp vs fcc, doped, off-stoich); **soft phonons (ω≲30 cm⁻¹)** | wrong/auto-fetched structure — not the paper's phase | get the paper's exact phase/pressure/ordering; relax to condition |
| `Error in routine readpp` / `stopping` | a pseudopotential file won't read (corrupt/format) | re-download or swap that element's UPF |
| `cdiaghg: S matrix not positive definite` (MPI_ABORT) at a k+q band recalc | ill-conditioned overlap (e.g. WC-type NbN) | retune ecutwfc / try a different pseudo |
| scf prints "iteration #1" then no progress for hours | cell too big/heavy (e.g. 10 atoms, 3600 k, ecut 90) | more cores/time, or it genuinely needs HPC |
| `vc-relax`/scf "convergence NOT achieved" | metal mixing/smearing | raise `electron_maxstep`, lower `mixing_beta`, check `degauss` |

**Always sanity-check the phonon spectrum first**: large imaginary/negative or very soft
(<30 cm⁻¹) frequencies mean the structure is dynamically unstable *as computed* → λ is
spurious → the structure (phase/volume) is wrong, not the el-ph.

## Validation evidence (this benchmark)

| material | λ computed / gold | note |
|---|---|---|
| bcc Ta | 0.927 / 0.877 (+6%) | simple metal, 4×4×4 ✅ |
| sc P (relaxed 20 GPa) | 0.808 / 0.795 (+2%) | relaxation essential ✅ |
| fcc Li (relaxed 30 GPa) | 0.862 / 0.83 (+4%) | ✅ |
| bcc V / fcc Y | 1.01/1.12 · 0.63/0.75 | simple metals ✅ |
| YIn₃ | 0.362 / 0.36 (+0.6%) | ✅ |
| hcp Fe (ibrav=4, 4×4×4) | 0.27 / 0.33 (−18%) | crash fixed by ibrav ✅ |
| MgB₂ (ibrav=4) | 1.44→**0.66** (2×2×2→4×4×4) / 0.75 | q-convergence ✅ |
| NbC / VC (B1) | 2.44→**0.99** · 4.39→**1.20** / 0.87,0.78 | acoustic Kohn anomaly, q-convergence |
| HfN (B1) | 0.59 / 0.67 (−12%) | anomaly-free, 2×2×2 OK ✅ |
| fcc La | 1.4–3.1 / 1.06 | 4f + soft modes + phase (fcc vs dhcp) ⚠️ |

**Bottom line:** the pipeline runs end-to-end; accuracy is gated by (1) proper `ibrav`,
(2) the structure matching the paper's phase/condition, and (3) a q-grid dense enough
for the material's phonon anomalies. Those three — not the el-ph method — explain every
mismatch we saw. That difficulty gradient is exactly why "compute λ" is a meaningful
agent benchmark.
