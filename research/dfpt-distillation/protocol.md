# Run protocol — distillation track (deltas vs the qe-eph-lambda recipe)

## Pseudopotentials and functional

- ONCV **LDA** (PZ) for the distillation ladder: the cancellation theorem anchors the
  ALDA f_xc; PBE's gradient kernel would blur the F-knob attribution.
- Keep the L4-train PBE runs as-is (benchmark protocol). For Na run both LDA and PBE
  (cheap) and record the kernel delta in the ledger.
- d metals additionally need the NL knob: rerun with the local part only
  (`lloc` manipulation or a locally-generated semilocal pseudo) — flagged per manifest.

## Semicore (measured 2026-06-13, smoke test)

SG15 pseudos are systematically semicore-rich: Na z_valence = 9, Al z_valence = 11.
The analytic-end UEG mapping screens with the *conduction* density (Na 1e, Al 3e), so
SG15 bare potentials and the model screening are charge-mismatched — confirmed
numerically: the acoustic sum-rule check g(q→0) = −(2/3)E_F passes at 0.0% when
n_val = z_valence and fails by exactly the charge ratio otherwise.

**Decision: the distillation track uses small-core LDA NC pseudos with z = chemical
valence (e.g. QE PSlibrary vbc set: Na z=1, Al z=3), the SAME pseudo on both the DFPT
(A0) and model sides.** Matched comparison is the only hard requirement; benchmark-grade
pseudo quality is not — this is theory-vs-theory. The frozen-semicore response is
thereby a documented additional knob (SC): SG15-vs-smallcore A0 runs price it where
needed (Na cheap → do both). L4-train benchmark runs keep SG15-PBE; the two tracks
share structures and grids but not pseudos.

## QE settings (per material, on top of the standard recipe)

- `ph.x`: `fildvscf = 'dvscf'` (retain; 1-atom cells → small files), `fildyn` as usual.
  Explicit q-grid per the material's converged grid from the L4 train campaign.
- SCF: same ecut/k-grid as the L4 train run for the material, so A-ladder deltas are
  not confounded with convergence deltas.
- EPW stage (where used): `prtgkk = .true.` to dump |g(k,q,ν)| on explicit grids
  **before** Wannier interpolation; retain `*.epb` files. A1 statistics work on these.

## Artifact retention (add to the LBG bundle download list)

```
scf.out, ph.out, *.dyn*, dvscf*, lambda.dat, epw.out, *.epb, prtgkk dumps
```

These are the inputs to scripts/{analyze_g_anisotropy,model_vertex,screened_phonons}.py.
Everything else (wavefunctions, *.save) is cleaned as usual.

## Comparison discipline

- One knob per comparison; matched ecut/k/q/smearing everywhere.
- λ recomputed from the SAME ω_qν when pricing vertex knobs (A1–A4), and from the SAME
  g when pricing the P knob — never mix.
- Per-rung record in ledger.csv: lambda, delta vs A0 (absolute and %), plus the
  matrix-element-level RMS deviation of g (more sensitive than λ, catches cancellations
  inside the FS average).
