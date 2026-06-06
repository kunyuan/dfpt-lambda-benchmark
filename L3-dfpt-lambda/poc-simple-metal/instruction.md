# Working environment

You are given crystal structures in `./packet/structures/` (VASP POSCAR format) and
a manifest `./packet/cases.csv`. Write your solution as **`run_lambda.py`** in the
working directory. The verifier invokes it as

```
python run_lambda.py --params <cases.csv> --out <out.csv>
```

on **concealed held-out cases** (different structures from `./packet/`).

---

# L3 (PoC) — compute the electron-phonon coupling λ from first principles

For each material, compute the **electron-phonon coupling constant λ** and the
**logarithmic-average phonon frequency ω_log (in K)** from first principles for the
given crystal structure and condition.

This is the expensive, first-principles step (not a closed-form plug-in): run
density-functional perturbation theory — SCF ground state → phonons → electron-phonon
matrix elements → Brillouin-zone double-delta average to assemble α²F(ω), then

- λ = 2 ∫ α²F(ω) / ω dω
- ω_log = exp[ (2/λ) ∫ ln(ω) α²F(ω)/ω dω ]

**Choose the method appropriate to the material yourself** (this PoC track is simple /
elemental metals → direct DFPT on a coarse q-grid with a dense k double-delta is
normally sufficient; you decide grids, smearing, pseudopotentials, cutoffs).

You are given, per case:

- `structure_file` — a POSCAR in `./packet/structures/` (lattice + basis). Relax to
  the stated condition if needed; the cell is representative.
- `condition` — pressure / phase context (e.g. "30 GPa", "ambient").
- `mu_star` — the Coulomb pseudopotential μ\* (provided for reference; not needed for λ).

## Output (`out.csv`)

Columns: `case_id,lambda,omega_log_K,core_hours` — one row per input `case_id`:

- `lambda` — computed electron-phonon coupling λ;
- `omega_log_K` — computed ω_log in Kelvin;
- `core_hours` — CPU core-hours you spent on that case (the **cost** axis).

## Scoring

Per case, PASS iff `|λ − λ_ref|/λ_ref ≤ 0.15` **and**
`|ω_log − ω_log_ref|/ω_log_ref ≤ 0.15` against the paper's first-principles
reference. All held-out cases must pass, exactly one prediction each. Total
`core_hours` is reported as the cost axis (accuracy × cost), not a pass/fail gate in
this PoC.

> **Note (PoC scope & anti-cheat).** The structure reveals the material, so reported
> λ could in principle be recalled rather than computed. The hardened version will
> require submitting the DFPT artifacts (dynamical matrices / α²F(ω)) and recompute λ
> from them server-side. Here the reported numbers are graded against a cached
> reference to prove the task + verifier plumbing.
