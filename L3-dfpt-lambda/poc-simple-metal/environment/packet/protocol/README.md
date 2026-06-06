# QE electron-phonon protocol (open-source, no VASP)

Compute λ and ω_log with **Quantum ESPRESSO** (free / GPL):

1. **SCF** — `pw.x < structures/<name>.scf.in` (ground state on a coarse k-grid).
2. **Dense non-SCF k-grid** — a second `pw.x` run on a much denser k-mesh for the
   electron-phonon Fermi-surface double-delta sum (metals need this dense).
3. **Phonons + el-ph** — `ph.x < ph.in` with `electron_phonon='interpolated'` on a
   coarse q-grid (`nq1 nq2 nq3`); writes the dynamical matrices, `elph_dir/`, and the
   α²F data. (`el_ph_sigma`/`el_ph_nsigma` set the double-delta smearing scan.)
4. **λ, ω_log** — assemble α²F(ω) and integrate:
   - `lambda.x` (reads `a2Fsave`) prints **λ** and **ω_log**, OR
   - read `a2F.dos*` / the per-q λ in the `ph.x` output and integrate
     λ = 2∫α²F/ω dω, ω_log = exp[(2/λ)∫ln ω·α²F/ω dω].

Report the **converged** λ and ω_log (extrapolate the el_ph smearing scan), and the
**core-hours** spent.

**Pseudopotentials:** free PBE sets — [SSSP](https://www.materialscloud.org/discover/sssp)
or [PSlibrary](https://dalcorso.github.io/pslibrary/). Put the `.UPF` files in
`./pseudo`. The filenames in each `*.scf.in` are representative; swap for your set.

This is the same physics the WF-6 papers used (DFPT linear response); the reference
λ/ω_log were read from those papers.
