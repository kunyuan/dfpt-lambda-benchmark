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

## Metric: scaled by the SOTA theory-experiment gap

The tolerance is **not** the experimental error bar — the benchmark question is "can
you match experiment as well as state-of-the-art theory does?", so the natural scale
is the **SOTA gap**: the relative deviation of the best literature first-principles λ
from experiment, averaged over **all 21 dataset pairs**:

| pair | gap | pair | gap | pair | gap |
|---|---:|---|---:|---|---:|
| Th | 66.7% | Nb3Ge | 14.0% | Nb3Sn | 5.7% |
| Na | 30.0% | Mo | 8.9% | Sn | 4.0% |
| V3Si | 25.5% | K | 7.7% | NbN | 4.0% |
| La | 18.2% | Cr | 7.7% | Al | 2.3% |
| TaC | 15.6% | Ta | 7.6% | In | 2.0% |
| MgB2 | 14.3% | Nb | 6.9% | Hg | 1.9% |
| | | | | NbC, V, Pb | ≤1.3% |

```
G_SOTA  = mean_i |λ_sota,i − λ_exp,i| / λ_exp,i = 0.117   (median 0.076)
d_i     = |λ_pred,i − λ_exp,i| / λ_exp,i
ratio   = mean(d_i) / G_SOTA          ← leaderboard axis (＜1 beats published SOTA)
PASS    = mean(d_i) ≤ G_SOTA  AND  all d_i ≤ 3·G_SOTA
```

- The per-case 3G cap (35.1%) kills single catastrophic misses without letting one
  case dominate the mean: a Pb-like SOC omission lands ~30% low (right at the cap on
  a heavy element), and computing Cr in the paramagnetic state (λ = 0.35 vs gold
  0.13) gives d = 169% → hard fail.
- **Calibration**: submitting the literature first-principles values verbatim gives
  ratio = 0.79 on the held-out set (oracle baseline; `solution/precomputed.csv`).
  Pushing ratio below 0.79 is real signal — e.g. anisotropic Migdal-Eliashberg on
  Nb3Ge (literature gap 14%) or a better-converged TaC (15.6%).
- σ_exp and exp_method stay in the gold CSVs as metadata (route quality documentation),
  but do not enter the score: heterogeneous experimental error is folded into G_SOTA
  itself, since the SOTA gap *includes* experimental scatter by construction.
- `core_hours` is reported, not gated, preserving the repo's accuracy × cost frontier.

## Files

Standard Harbor layout, byte-aligned with L3 conventions: `environment/packet/`
(cases + dev_gold + structure_hints), `tests/hidden` + `tests/gold` + `score.py` +
`test.sh`, `solution/` (oracle = literature values), `scripts/selfcheck.sh`
(oracle must PASS, λ×1.5 perturbation must FAIL).
