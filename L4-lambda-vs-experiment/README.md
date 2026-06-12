# L4 — λ vs experiment: design notes

L1/L3 grade against the **source paper's computed λ** (reproduction). L4 grades against
the **experimentally-inferred λ** — the harder "vs-experiment" anchor foreshadowed in
the top-level README. An agent passing L4 is not reproducing a calculation; it is
independently reaching the experimentally-verified answer.

## Why these materials (and not others)

The dataset is restricted to materials where first-principles ↔ experiment agreement is
*established and physically meaningful*. A dedicated LKM knowledge-graph survey
(2026-06-11, `data/lambda_dfpt_vs_experiment_survey.csv`, ~37 material points) showed
agreement is controlled by three criteria, none of which is "orbital character":

1. **Itinerancy** — Fermi-surface quasiparticles well described by DFT (U/W ≪ 1, Z ≈ 1).
   d-electron metals qualify: Nb/V/Ta/A15/carbides agree at ~10% with λ up to 1.85.
2. **Distance to magnetic instability** — Stoner I·N(0) far from 1. Near-ferromagnetic
   metals (Pd, Pt, Sc, MgCNi₃) fail the γ-route comparison by 50–100% because a
   spin-fluctuation channel λ_sf ≈ λ_ph contaminates the experimental mass enhancement.
3. **Experimental route** — tunneling (McMillan-Rowell inversion) measures λ_ep itself
   (gold standard); specific-heat γ measures λ_ep + λ_sf + λ_ee (total mass); Tc/θ_D
   inversion is model-dependent. σ in the gold reflects this hierarchy.

**Excluded by these criteria** (documented in the survey CSV, deliberately *not* cases):
near-magnetic d metals (Pd, Pt, Sc, MgCNi₃), Hund-correlated multibands (FeSe,
pnictides — DFPT λ low by 3–4×), Mott systems (cuprates — band theory *over*estimates),
Ba₁₋ₓKₓBiO₃ (LDA matrix-element failure, needs GW), localized-f Kondo lattices
(γ-ratio 10–235×, unrelated to phonons), α-Ce and α-U (boundary), ZrN (partial optical-mode
λ only), amorphous/alloy systems (no first-principles side).

## Dataset: 21 materials, 8 material types

| type | train (13) | validation (8) |
|---|---|---|
| alkali-sp | Na | K |
| simple-sp | Al, Sn | In |
| simple-sp-heavy (SOC) | Pb | Hg |
| bcc-transition (3d/4d/5d) | V, Ta, Mo | Nb, Cr (AFM) |
| A15-intermetallic | Nb3Sn, V3Si | Nb3Ge |
| rocksalt carbide/nitride | NbC, NbN | TaC |
| diboride-multiband | MgB2 | — |
| f-band-metal | Th (boundary, flagged) | La |

Split is **stratified by material type**: every validation case has a same-type train
case that discloses both the experimental value (with method and σ) and the literature
first-principles value (with method). Embedded lessons: Pb (train) teaches SOC → Hg
(validation) tests it; V (train) teaches "distrust oxidized tunneling junctions" → Nb
(validation) has the same pathology; Cr (validation) tests magnetic-ground-state choice
with no train example — judged a fair material-knowledge probe, same philosophy as L3's
hidden method metadata. Th is kept in train *with a warning flag* as the honest example
of γ-route contamination at the f-band boundary.

All numbers were read from LKM knowledge-graph claims (paper ids in the CSVs); none are
filled from model memory. Two LKM claims had corrupted paper-title metadata; affected
materials were either excluded or carry ids verified through a second claim.

## Metric

Flat relative tolerance (L3's 15%) is wrong here: experimental σ ranges from ~3%
(Pb tunneling) to ~30% (Na point-contact, where λ≈0.1 and the e-e mass correction is
comparable). Instead:

```
z_i     = (λ_pred − λ_exp) / σ_eff,   σ_eff = max(σ_exp, 0.05·λ_exp)
credit_i = exp(−z_i²/2)
PASS    = all |z_i| ≤ 2  AND  mean(credit) ≥ 0.50
```

- The 0.05·λ floor keeps razor-thin σ from demanding better-than-physics precision.
- Gaussian credit makes the score continuous — the leaderboard axis — while the 2σ
  gate kills any single blown case (e.g. forgetting SOC on Hg: 1.08 vs 1.60 → z = −5.2).
- **Calibration**: submitting the literature first-principles values verbatim passes at
  mean credit ≈ 0.67 (oracle baseline; `solution/precomputed.csv`). Headroom to 1.0 is
  real signal — e.g. anisotropic Migdal-Eliashberg on Nb3Ge (z = −1.5 at the
  literature value) or a better-converged TaC (z = −1.6).
- `core_hours` is reported, not gated, preserving the repo's accuracy × cost frontier.

## Files

Standard Harbor layout, byte-aligned with L3 conventions: `environment/packet/`
(cases + dev_gold + structure_hints), `tests/hidden` + `tests/gold` + `score.py` +
`test.sh`, `solution/` (oracle = literature values), `scripts/selfcheck.sh`
(oracle must PASS, λ×1.5 perturbation must FAIL).
