# Working environment

You are in a container with Python 3. Public development data is in `./packet/`:
`packet/spectra/*.dat` (Eliashberg spectral functions) and `packet/cases.csv` (the
manifest). Write your solution as **`run_lambda.py`** in the working directory
(`/app`). The verifier invokes it as

```
python run_lambda.py --params <cases.csv> --out <out.csv>
```

on **concealed held-out spectra** (not the ones in `./packet/`). Do not hardcode
per-case answers — the graded spectra differ from the development set.

---

# L1 — α²F(ω) → λ, ω_log

From the **Eliashberg spectral function α²F(ω)**, compute the **electron-phonon
coupling constant λ** and the **logarithmic-average phonon frequency ω_log**.

The defining integrals are intentionally **not** reproduced here — recall the
standard Eliashberg moment definitions yourself (λ from the inverse-frequency
moment of α²F; ω_log from the logarithmic moment) and implement them in a generic
`run_lambda.py`.

## Input

`cases.csv` columns: `case_id, spectrum_file`. Each `spectrum_file` lives in a
`spectra/` directory next to `cases.csv` and is a two-column text file:

```
# omega_meV    a2F
0.200  0.000001
0.400  0.000002
...
```

ω is in **meV**; α²F is dimensionless.

## Output (`out.csv`)

Columns: `case_id,lambda,omega_log_K` — exactly one row per input `case_id`:

- `lambda` — the electron-phonon coupling λ (dimensionless);
- `omega_log_K` — ω_log in **Kelvin** (note the meV→K conversion).

## Development data (`./packet/`)

- `packet/cases.csv` + `packet/spectra/*.dat` — 10 development spectra.
- `packet/dev_gold.csv` — their reference `lambda, omega_log_K`, to validate your
  implementation. Reproduce closely.

## Scoring

Run on concealed spectra; each `lambda` and each `omega_log_K` must be within **2%**
(relative) of the gold. PASS requires every held-out case to clear both bars,
exactly one prediction each.
