# LBG QE 7.1 Reproduction Status by Material Type

Source table: `lbg_qe71_np8_sigma0025.csv`.

Verdicts:

- `reproduced`: lambda is within 15 percent of the paper reference, omega_log is within 15 percent when available, and top-q share is not above 25 percent.
- `lambda_close_omega_off`: lambda is within 15 percent, but omega_log is outside the 15 percent gate.
- `smoke_unconverged`: the run completed, but one q/mode carries more than 25 percent of lambda.
- `finished_missing_lambda_artifact`: LBG marked the job finished, but the compact lambda artifact was not retrieved.
- `not_reproduced_yet`: completed and parsed, but lambda is still outside the 15 percent gate.

| material type | rows | parsed lambda | reproduced | lambda close only | smoke/unconverged | missing artifact | notes |
|---|---:|---:|---:|---:|---:|---:|---|
| 2d-layered | 2 | 2 | 0 | 0 | 2 | 0 | smoke_unconverged: lam009, lam035 |
| hydride | 2 | 2 | 0 | 1 | 0 | 0 | lambda_close_omega_off: lam123 |
| intermetallic | 4 | 3 | 0 | 0 | 1 | 1 | smoke_unconverged: lam154 |
| simple-metal | 10 | 8 | 5 | 0 | 2 | 1 | reproduced: lam262, lam263, lam264; smoke_unconverged: lam263, lam264 |

## Per-Case Rows

### 2d-layered

| case | material | q | lambda | ref | lambda err % | omega_log K | omega err % | top-q % | verdict |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| lam035 | B2C | 2 | 1.709 | 0.92 | 85.76 | 483.9 | 53.72 | 47 | smoke_unconverged |
| lam009 | MoS2 | 2 | 2.284 | 1.7 | 34.35 | 153.2 | -33.45 | 44 | smoke_unconverged |

### hydride

| case | material | q | lambda | ref | lambda err % | omega_log K | omega err % | top-q % | verdict |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| lam104 | GeH3 | 2 | 1.137 | 1.56 | -27.12 | 1307.3 | 77.38 | 4 | not_reproduced_yet |
| lam123 | SnH8 | 2 | 1.274 | 1.188 | 7.24 | 265.3 | -71.13 | 12 | lambda_close_omega_off |

### intermetallic

| case | material | q | lambda | ref | lambda err % | omega_log K | omega err % | top-q % | verdict |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| lam150 | I | 2 | 0.229 | 0.43 | -46.74 | 276.9 | 48.63 | 25 | not_reproduced_yet |
| lam150 | I | 4 | 0.341 | 0.43 | -20.70 | 223.3 | 19.86 | 10 | not_reproduced_yet |
| lam154 | TaC | 2 | 1.346 | 0.78 | 72.56 | 165.9 | -39.01 | 38 | smoke_unconverged |
| lam138 | CdCNi3 | 2 |  | 0.8 |  | 89.41 |  |  | finished_missing_lambda_artifact |

### simple-metal

| case | material | q | lambda | ref | lambda err % | omega_log K | omega err % | top-q % | verdict |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| lam262 | P | 4 | 0.701 | 0.676 | 3.70 | 440.0 | -6.18 | 11 | reproduced |
| lam262 | P | 6 | 0.552 | 0.676 | -18.34 | 375.2 | -20.00 | 12 | not_reproduced_yet |
| lam263 | S | 2 | 0.453 | 0.76 | -40.39 | 462.1 | 5.24 | 30 | smoke_unconverged |
| lam263 | S | 4 |  | 0.76 |  | 439.1 |  |  | failed_or_incomplete |
| lam264 | S | 2 | 0.235 | 0.53 | -55.66 | 642.7 | 14.75 | 27 | smoke_unconverged |
| lam264 | S | 4 | 0.585 | 0.53 | 10.38 | 549.1 | -1.96 | 22 | reproduced |
| lam253 | Mo3Os | 2 |  | 1.51 |  | 130.9 |  |  | finished_missing_lambda_artifact |
| lam263 | S | 4 | 0.733 | 0.76 | -3.55 | 439.9 | 0.18 | 11 | reproduced |
| lam264 | S | 6 | 0.507 | 0.53 | -4.34 | 493.8 | -11.84 | 14 | reproduced |
| lam263 | S | 6 | 0.703 | 0.76 | -7.50 | 455.8 | 3.80 | 4 | reproduced |

