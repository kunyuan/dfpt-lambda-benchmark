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
  ω_log. Pure post-processing; sub-second verifier. **Built as a runnable Harbor
  code-submission task** (`run_lambda.py`, formula withheld, held-out grading) —
  same mold as `allen-dynes-tc-benchmark`. See
  [`L1-alpha2F-to-lambda/`](L1-alpha2F-to-lambda/).
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
| simple / elemental metal | 40 | — | DFPT-direct | 10²–10³ |
| intermetallic compound | 107 | — | DFPT-direct | 10³–10⁴ |
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
| `structure_targets.csv` / `_summary.md` | audited target phase/prototype, space group, pressure, confidence, and mismatch flags for all 276 L3 cases |
| `lkm_extraction.json` | full per-paper LKM records (243 papers) |
| `lambda_per_condition.json` | the per-condition split that produced the reference points |
| `lambda_computed_vs_experimental.csv` | 15-paper computed-vs-experimental λ comparison |
| `splits/l3_case_splits.csv` / `splits/l3_validation_core.csv` | Harbor-style L3 train/validation split; 251 train + 25 validation-core cases |

All derive from WF-6 (243 papers). λ is reported first-principles in ~150 of them;
DFPT/linear-response dominates, with Wannier/EPW, SOC, and anharmonic/SSCHA as the
method variants above.

## Status

- ✅ **L1 — runnable Harbor task** ([`L1-alpha2F-to-lambda/`](L1-alpha2F-to-lambda/)):
  code-submission (`run_lambda.py`), formula withheld, 10 dev + 4 held-out α²F
  spectra (λ ≈ 0.8–2.8, ω_log ≈ 87–524 K), `tests/test.sh` on the **Harbor contract**
  (runs agent code as `nobody`, root-only gold, writes `reward.txt`), 2 % tolerance.
  Deterministic + sub-second → the level that validates **end-to-end** under Harbor.
- ✅ **L3 — one Harbor task per material type** (`L3-dfpt-lambda/<track>/`): the 276
  cases are packaged into **5 runnable benchmarks**, each a full Harbor task
  (`task.toml`, `instruction.md`, `environment/packet/`, `tests/` with root-only gold +
  `reward.txt`, `scripts/selfcheck.sh`). Method is withheld (the agent picks the DFPT
  approach for the class); gold = paper λ, graded ≤ 15 % + core-hours reported.

  | track | cases | structure-ready | build-from-spec |
  |---|---:|---:|---:|
  | `intermetallic` | 107 | 55 | 52 |
  | `hydride` | 53 | 1 | 52 |
  | `simple-metal` | 40 | 11 | 29 |
  | `heavy-soc` | 38 | 13 | 25 |
  | `2d-layered` | 38 | 0 | 38 |

  Each case is either **structure-ready** (a proper-`ibrav` QE input in
  `packet/structures/`) or **build-from-spec** (construct the crystal from
  `packet/structure_hints.json` — paper space group / prototype / lattice — then run).
- ✅ **Real QE reproduction** ([`L3-dfpt-lambda/VALIDATION.md`](L3-dfpt-lambda/VALIDATION.md)):
  ran QE end-to-end on a 192-core server (MPI). With structures **relaxed to the
  stated pressure** + a **4×4×4 q-grid**, bcc Ta / sc P / fcc Li reproduce the paper
  λ within **2–6 %** and ω_log within **1–13 %**.
- ✅ **LBG/QE reproduction record** ([`L3-dfpt-lambda/reproduction/`](L3-dfpt-lambda/reproduction/)):
  organized job ledgers, selected scaling inputs, QE 7.1 `ph.x` build notes, and
  curated λ/ω_log comparisons from the first NP=8 LBG batch. The strongest new
  reproductions are high-pressure sulfur (`lam263`, `lam264`); 2D, hydride, and
  heavy-SOC entries are currently smoke/method-validation records rather than final
  leaderboard-grade results.
- ✅ **Structures audited + first repair batch** — 80/276 are trusted
  structure-ready after checking
  the paper target phase/pressure against LKM and current QE inputs
  (OpenLAM 55 / MP 10 / LKM 15). The other 196 are build-from-spec with target
  structure metadata in `structure_hints` and the full audit in
  `data/structure_targets.csv`. SG15 pseudo manifest + fetch script in each
  `packet/pseudos/`. See [`L3-dfpt-lambda/BUILD.md`](L3-dfpt-lambda/BUILD.md).
- ✅ **L3 train/validation split defined** — a case-level Harbor split is in
  [`splits/`](splits/): 251 public train cases plus a 25-case
  `validation_core` set with exactly 5 cases from each material class. The
  validation set excludes the heavily tuned public reproduction cases and mixes
  structure-ready, build-from-spec, SOC, 2D, and hydride examples.
- ⬜ **Run through real Harbor** — all tasks follow the contract and pass host-side
  self-checks, but have not been executed by the `harbor` runner (needs Docker).
- ⬜ **Harden** — fill remaining build-from-spec structures; verifier to recompute λ
  from submitted DFPT artifacts; fix the case_id↔paper provenance mismatches.

## License

MIT — see [`LICENSE`](LICENSE).
