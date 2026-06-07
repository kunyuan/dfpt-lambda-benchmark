# L3 validation — real QE runs reproduce the paper references

The L3 PoC references were checked by **actually running Quantum ESPRESSO** end-to-end
(open-source, no VASP), on a 192-core server, fully MPI-parallel.

## Setup

- **Engine:** Quantum ESPRESSO 7.5 (native linux-64, conda-forge), Open MPI 5.0.10.
- **Parallelism:** 32 MPI ranks per case (k-point pools, `-nk 32`), 5 cases concurrent.
- **Protocol per case:** download free PBE USPP (PSlibrary `rrkjus`) → for the
  high-pressure cases, `pw.x` **`vc-relax` to the target pressure** → `pw.x` scf
  (24³ k, MP smearing 0.025 Ry, ecutwfc 50 / ecutrho 500 Ry) → `ph.x`
  `electron_phonon='simple'` on a **4×4×4 q-grid** with an el-ph smearing scan →
  λ = Σ_q (w_q Σ_ν λ_qν), ω_log = λ-weighted log-average of the mode frequencies,
  read at the smearing plateau (≈0.025 Ry).

## Results

| case | structure | computed λ | ref λ | Δλ | computed ω_log (K) | ref ω_log | Δω_log |
|---|---|---:|---:|---:|---:|---:|---:|
| **bcc Ta** | ambient | 0.927 | 0.877 | **+6 %** | 153.2 | 150.8 | **+2 %** |
| **sc P** | vc-relaxed to 20 GPa (a=2.342 Å) | 0.808 | 0.795 | **+2 %** | 423.2 | 418 | **+1 %** |
| **fcc Li** | vc-relaxed to 30 GPa (a=3.36 Å) | 0.862 | 0.83 | **+4 %** | 237.5 | 274 | −13 % |
| hcp Fe | vc-relaxed to 100 GPa | — | 0.33 | `ph.x` crashed | — | 450 | — |
| fcc La | ambient | *in progress* | 1.06 | — | — | 85 | — |

**3 of the 4 completed cases reproduce the paper λ to within 2–6 % and ω_log to
within 1–13 %.** The DFPT λ pipeline runs end-to-end under MPI.

## What this established (and fixed)

1. **Relaxing the structure to the stated pressure is essential.** On a laptop with
   the *un-relaxed* "representative" cells, sc P and fcc Li gave λ ≈ 2.1 (2–2.6×
   too high). After `vc-relax` to 20/30 GPa, λ lands at +2 %/+4 %. → **Production L3
   must ship structures relaxed to the target pressure** (the `environment/packet/`
   `*.scf.in` cells are representative starting points only).
2. **A denser q-grid converges ω_log.** bcc Ta on a coarse 2×2×2 grid gave ω_log
   ≈ 175 K (+16 %); on 4×4×4 it is 153 K (+2 %). → reference ω_log should be paired
   with a q-grid spec, or graded with a looser tolerance than λ.
3. **Hard cases need bespoke setup.** `ph.x` crashed for non-magnetic hcp Fe under
   pressure (magnetic/USPP sensitivity); La (4f) is very heavy. These need
   case-specific cutoffs/pseudos/handling and shouldn't be run concurrently with the
   light cases.

## Reproduce

On any machine with QE + MPI:
`python run_one.py <Ta|P|Li|La|Fe>` (driver: relax → scf → ph → extract). The driver
and per-case logs live in the run scratch dir, not committed here.
