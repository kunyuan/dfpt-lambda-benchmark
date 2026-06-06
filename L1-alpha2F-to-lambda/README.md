# L1 — α²F(ω) → λ, ω_log  (code-submission, McMillan-style)

A runnable Harbor task in the same mold as
[`allen-dynes-tc-benchmark`](https://github.com/kunyuan/allen-dynes-tc-benchmark):
the agent submits a generic **`run_lambda.py`**; the **formula is withheld**; it is
graded on **concealed held-out** spectra. Pure post-processing (no DFT/HPC),
deterministic, sub-second verifier — fully validatable end-to-end under Harbor.

**Task:** given the Eliashberg spectral function α²F(ω) (a digitized ω-grid in meV),
compute λ = 2∫α²F/ω dω and ω_log = exp[(2/λ)∫lnω·α²F/ω dω] (output ω_log in K).

```
L1-alpha2F-to-lambda/
├── task.toml                       # Harbor v1.0 schema
├── instruction.md                  # formula WITHHELD; I/O contract; scoring (2%)
├── environment/
│   ├── Dockerfile                  # python:3.12-slim
│   └── packet/
│       ├── cases.csv               # case_id, spectrum_file (10 dev)
│       ├── spectra/*.dat           # α²F(ω): "omega_meV  a2F"
│       └── dev_gold.csv            # dev λ, ω_log (validate your impl)
├── solution/{run_lambda.py, solve.sh}   # reference integrator (oracle)
├── tests/
│   ├── test.sh                     # Harbor verifier: nobody + root-only gold + reward.txt
│   ├── score.py                    # λ,ω_log within 2%; result.json
│   ├── hidden/{cases.csv,spectra/} # 4 held-out spectra
│   └── gold/gold.csv               # root-only reference
└── scripts/selfcheck.sh            # host-side (no Docker): oracle PASS, perturbed FAIL
```

Dev/hidden span λ ≈ 0.8–2.8, ω_log ≈ 87–524 K. `tests/test.sh` follows the Harbor
contract (runs the agent's code as `nobody`, locks `/tests/hidden`+`/tests/gold`
root-only, writes `/logs/verifier/reward.txt`). `scripts/selfcheck.sh` validates the
oracle+scoring on the host without Docker.

> The α²F(ω) curves are model spectra (sums of Gaussian phonon peaks) with gold from
> exact moment integration — they test the **integration/units**, the same way the
> Tc benchmark tests the closed-form. Anchoring curves to per-material reference
> moments is a future refinement.
