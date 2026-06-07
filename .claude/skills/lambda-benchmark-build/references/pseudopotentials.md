# Pseudopotential selection for dfpt-lambda-benchmark

## Choice: SG15 ONCV norm-conserving, PBE

Use **one consistent set** across all cases. For electron-phonon (`ph.x`),
**norm-conserving (NC)** is the safe default — ultrasoft/PAW carry augmentation
charges whose DFPT code paths are fragile (segfaults observed). SG15 ONCV is free,
curated, and covers the periodic table.

- Source: `http://www.quantum-simulation.org/potentials/sg15_oncv/upf/<El>_ONCV_PBE-1.2.upf`
  (fall back to `-1.1` / `-1.0` if a `-1.2` 404s). Verify each starts with `<UPF`.
- Alternatives: **PseudoDojo** ONCV (NC, also fine); **SSSP-efficiency** is mostly
  ultrasoft/PAW → great for energies, **avoid for `ph.x` el-ph**.

## Match the functional

WF-6 papers are overwhelmingly **PBE** → use PBE pseudos. If a specific paper used
**LDA** or **PBEsol**, swap that case to the matching set and record it. Mixing
functionals between the gold (paper) and your run biases λ.

## Cutoffs (NC: ecutrho = 4 × ecutwfc)

SG15 are moderately hard. Start here, then converge a phonon frequency / total energy:

| element class | examples | ecutwfc (Ry) |
|---|---|---|
| simple sp metals | Li, Na, Al, Mg, Ca | 50–60 |
| 2p elements | B, C, N, O, F | 80 |
| 3p / heavier sp | Si, P, S, Sn, Sb | 50–60 |
| 3d transition metals / semicore | V, Fe, Nb, Ta, Ir, Pt | 80–90 |
| compounds (mixed) | use the **max** over the elements present |

`ecutrho = 4 × ecutwfc`. For metals also use enough k-points + small `degauss`
(0.02 Ry, Methfessel-Paxton) and a **dense** k-grid for the el-ph double-delta.

## SOC (heavy-element track)

For SOC cases use a **fully-relativistic** pseudo (SG15 has `_ONCV_PBE_FR` variants
or use PseudoDojo FR) and `lspinorb=.true., noncolin=.true.`.

## Per-track manifest

Keep `element → pseudo_file, ecutwfc` per track so runs are reproducible, e.g.:

```json
{"Mg": {"upf": "Mg_ONCV_PBE-1.2.upf", "ecutwfc": 80},
 "B":  {"upf": "B_ONCV_PBE-1.2.upf",  "ecutwfc": 80}}
```
ship the `.upf` files in `environment/packet/pseudo/` and the manifest alongside.
