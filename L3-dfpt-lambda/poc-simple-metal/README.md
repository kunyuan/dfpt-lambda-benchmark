# L3 PoC — simple/elemental metals (compute λ via DFPT)

A runnable proof-of-concept L3 task: given a crystal **structure** + condition,
compute the electron-phonon **λ** and **ω_log** from first principles, report them
plus the **core-hours** spent; graded on accuracy (|λ−λ_ref|, |ω_log−ω_log_ref| ≤
15 %) with cost reported (accuracy × cost).

5 elemental/simple-metal cases (clean Bravais lattices), each with a real reference
λ/ω_log read from LKM:

| case | material | condition | λ_ref | ω_log_ref (K) |
|---|---|---|---:|---:|
| lam242 | bcc Ta | ambient | 0.877 | 150.8 |
| lam245 | fcc Li | 30 GPa | 0.83 | 274 |
| lam249 | fcc La | ambient | 1.06 | 85 |
| lam251 | hcp Fe | 100 GPa | 0.33 | 450 |
| lam261 | sc P | 20 GPa | 0.795 | 418 |

```
poc-simple-metal/
├── task.toml
├── instruction.md                 # method WITHHELD-as-choice; I/O contract; scoring
├── environment/
│   ├── Dockerfile                 # python+numpy (cheap verifier; real DFPT runs off-image)
│   └── packet/
│       ├── cases.csv              # case_id, structure_file, condition, mu_star  (NO λ)
│       └── structures/*.poscar    # 5 crystal structures
├── solution/
│   ├── run_lambda.py              # oracle stand-in (emits cached DFPT result)
│   ├── precomputed.csv            # the cached reference
│   └── solve.sh
├── tests/
│   ├── test.sh
│   ├── score.py                   # accuracy + cost; exit 0 iff all pass
│   ├── hidden/cases.csv
│   └── gold/ref.csv               # root-only reference
└── selfcheck.sh                   # oracle PASS, perturbed-λ FAIL  (run in CI)
```

Run: `bash selfcheck.sh` → oracle passes all 5; a λ+50 % perturbation fails all 5.

**Scope.** The verifier compares reported numbers to a cached reference (the oracle
stands in for a correct DFPT run, which executes off-sandbox on HPC). The hardened
version requires submitting DFPT artifacts (dynamical matrices / α²F) and recomputes
λ server-side — see the note in `instruction.md`. The pressure-case lattice params
are representative; relax to the stated pressure for a live run.
