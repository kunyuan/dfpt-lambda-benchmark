# L1 — α²F(ω) → λ, ω_log

The cheap post-processing level (sub-second verifier, auto-gradable at scale).

Given the Eliashberg spectral function **α²F(ω)** (as a digitized ω-grid + values),
compute:

- **λ** = 2 ∫ α²F(ω) / ω dω
- **ω_log** = exp[ (2/λ) ∫ ln(ω) α²F(ω) / ω dω ]
- (optionally ω̄₂ = [ (2/λ) ∫ ω α²F(ω) dω ]^(1/2), the second moment used by the
  Allen-Dynes f2 factor)

The formulas are the moment integrals of α²F; the task grades the integration /
post-processing, not any first-principles calculation. This is the natural cheap
counterpart to L3 (which produces the α²F in the first place) and to the
[`allen-dynes-tc-benchmark`](https://github.com/kunyuan/allen-dynes-tc-benchmark)
(which consumes the resulting λ, ω_log).

## Status — TODO

Needs reference **α²F(ω) spectra** harvested per material (these are usually figures
in the source papers, not in the LKM text). Each case = a digitized α²F(ω) curve →
gold (λ, ω_log) from the moment integrals. Until spectra are collected, L1 has no
data; the λ/ω_log **targets** for the same materials are in
[`../data/lambda_reference.csv`](../data/lambda_reference.csv).
