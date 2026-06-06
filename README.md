# dfpt-lambda-benchmark — first-principles electron-phonon λ benchmark

A [Harbor](https://github.com/harbor-framework/harbor)-style agent benchmark for
**computing the electron-phonon coupling constant λ (and ω_log) from first
principles**, derived from **WF-6 (McMillan–Allen-Dynes Tc estimation)** of the
Paper2ARM superconductivity cluster.

This is the **sibling** of
[`allen-dynes-tc-benchmark`](https://github.com/kunyuan/allen-dynes-tc-benchmark):

| | what it tests | cost |
|---|---|---|
| `allen-dynes-tc-benchmark` | the **cheap** closed-form step: (λ, ω_log, μ\*) → Tc | milliseconds |
| **this repo** | the **expensive** step: structure → DFPT → **λ, ω_log** | 10²–10⁵ core-hours |

λ is the quantity that actually requires a supercomputer; the Tc formula on top of
it is free. This benchmark targets that expensive step, and grades on the
**accuracy × cost** frontier (how close to the reference λ, at how many core-hours).

## Levels

Two levels, mirroring how λ is actually obtained:

- **L1 — α²F(ω) → λ, ω_log** (cheap, auto-gradable at scale). Given the Eliashberg
  spectral function α²F(ω), compute λ = 2∫α²F(ω)/ω dω and the logarithmic-average
  ω_log. Pure post-processing; sub-second verifier. *(Reference α²F spectra still to
  be harvested — see Status.)*
- **L3 — structure → DFPT → λ** (the real first-principles task; HPC). Given a
  relaxed crystal structure + pseudopotentials + a protocol, run DFPT (phonons +
  electron-phonon) and return λ, ω_log.

(L2 = "assemble α²F from given DFPT intermediates" and L4 = "predict structure then
DFPT" are deliberately omitted to keep the ladder to the two rungs that matter:
post-processing vs full first-principles.)

## L3 is organized by material type — method + cost are hidden metadata

Different materials genuinely require different methods to compute λ. The agent is
given the **material + conditions** and must **choose** the right method (this is
the scientific skill); the expected method and cost tier are carried as **hidden
metadata** for the verifier/budgeter, not revealed to the agent.

| material-type track | cases | papers | method (hidden) | cost tier (core-h) |
|---|---:|---:|---|---|
| simple / elemental metal | 42 | — | DFPT-direct | 10²–10³ |
| intermetallic compound | 105 | — | DFPT-direct | 10³–10⁴ |
| heavy-element (needs SOC) | 38 | — | DFPT + SOC | 10³–10⁴ (×SOC) |
| 2D / layered | 38 | — | DFPT + Wannier/EPW | 10³–10⁴ |
| high-pressure hydride | 53 | — | DFPT + anharmonic/SSCHA | 10⁴–10⁵ |
| **total** | **276** | **123** | | |

(`data/lambda_reference.csv` carries, per case: `material`, `condition`,
`material_type`, `lambda_ref`, `omega_log_K`/`theta_D_K`, `mu_star`,
`expected_method`, `cost_tier_coreh`.) Material type is determined from the
chemical formula + structure name alone — no paper reading required.

## Why material-type (not method) is the agent-facing axis

Organizing the agent-facing tracks **by material** (method withheld) tests "choose
**and** execute the right method" — the real scientific skill — and matches the
benchmark's purpose (compare λ-methods on shared materials). Organizing by method
would give away the method choice and test only execution. Cost-homogeneity is
preserved by tiering on the **material-implied** cost (`cost_tier_coreh`), which is
metadata, not a label shown to the agent. This mirrors `qp-eft-agent-benchmark`,
which gives the material and withholds the physics.

## Reference values & validation

- **Gold = the paper's reported first-principles λ** (and ω_log), read from LKM
  knowledge-graph nodes by parallel subagents — not regex. Multi-condition papers
  (pressure / doping / SOC / phase) are split into one reference point per
  self-consistent condition.
- **Cross-check vs experiment** (`data/lambda_computed_vs_experimental.csv`): for
  the 15 papers that also report an experimentally-inferred λ (mostly from the
  specific-heat mass enhancement γ_exp/γ_band = 1+λ), computed-vs-experimental λ
  agree to a **median ~9 %** (mean ~15 %), with computed λ running slightly low —
  consistent with harmonic DFPT omitting anharmonic/correlation enhancement. This
  set can serve as a harder "vs-experiment" anchor for L3.

## Provenance (`data/`)

| file | what |
|---|---|
| `lambda_reference.csv` / `.json` | 276 reference points (material, condition, λ, ω, μ\*, type, method, cost) |
| `lkm_extraction.json` | full per-paper LKM records (243 papers) |
| `lambda_per_condition.json` | the per-condition split that produced the reference points |
| `lambda_computed_vs_experimental.csv` | 15-paper computed-vs-experimental λ comparison |

All derive from WF-6 (243 papers). λ is reported first-principles in ~150 of them;
DFPT/linear-response dominates, with Wannier/EPW, SOC, and anharmonic/SSCHA as the
method variants above.

## Status

- ✅ **Reference data assembled** (276 λ points / 123 materials, classified into the
  5 material-type tracks; computed-vs-experimental cross-check).
- ✅ **L3 PoC** — a runnable Harbor task,
  [`L3-dfpt-lambda/poc-simple-metal/`](L3-dfpt-lambda/poc-simple-metal/): 5 elemental
  metals with real structures + reference λ/ω_log, a verifier scoring accuracy
  (|λ−λ_ref|, |ω_log−ω_log_ref| ≤ 15 %) + reported core-hours, and a self-check
  (oracle PASS, perturbed-λ FAIL) wired into CI.
- ⬜ **Scale L3** — attach structures for the remaining cases (paper / Materials
  Project) and harden the verifier (submit DFPT artifacts, recompute λ server-side).
- ⬜ **L1** needs reference α²F(ω) spectra harvested.

## License

MIT — see [`LICENSE`](LICENSE).
