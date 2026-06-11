# L3 Train/Validation Splits

This directory defines the public split policy for the L3
`structure -> DFPT -> lambda` benchmark.

## Split Contract

The first stable split is `l3-validation-core@0.1.0`:

| split | cases | purpose |
|---|---:|---|
| `train` | 251 | public workflow tuning, structure recovery, convergence debugging |
| `validation_core` | 25 | stable cross-material validation set, 5 cases per material class |

The split is case-level, not material-class-level. Each material class contributes
five validation cases so that validation still tests the full benchmark surface:
simple metals, intermetallics, heavy/SOC systems, 2D/layered systems, and
high-pressure hydrides.

## Files

| file | content |
|---|---|
| `l3_case_splits.csv` | all 276 L3 cases with `train` or `validation_core` label |
| `l3_validation_core.csv` | validation metadata and selection reasons |

The train set is the complement of `validation_core` in
`l3_case_splits.csv`. This avoids maintaining duplicate train-only metadata that
can drift from `data/lambda_reference.csv`.

## Why These Validation Cases

The validation set was selected to be representative but not overfit to the
existing reproduction notes:

- every material class has exactly five cases;
- already public, tuned reproduction cases are kept in `train`;
- validation includes both `structure-ready` and `build-from-spec` cases;
- high-confidence build-from-spec cases are allowed because paper-specific
  structure construction is part of L3;
- clear material/condition mismatches stay in `train` until repaired.

## Scoring

Harbor verifier rewards should be numeric. The recommended `reward.json` shape is:

```json
{
  "reward": 1,
  "structure_ok": 1,
  "lambda_pass": 1,
  "lambda_strong": 0,
  "omega_pass": 1,
  "diagnostic": 0,
  "lambda_rel_err": 0.18,
  "omega_rel_err": 0.09
}
```

Primary pass rule:

```text
structure_ok == 1
and abs(lambda_calc - lambda_ref) <= max(0.05, 0.20 * lambda_ref)
```

`omega_log` is an auxiliary gate and diagnostic signal. It should be recorded
systematically, but it should not become the only pass/fail rule for hydrides or
soft-mode systems without a material-class-specific note.

## Harbor Packaging

Harbor has dataset/version semantics rather than a first-class `split` field.
The intended mapping is:

- `dfpt-lambda-l3-train@0.1.0`: generated from rows labeled `train`;
- `dfpt-lambda-l3-validation-core@0.1.0`: generated from rows labeled
  `validation_core`;
- future `dfpt-lambda-l3-validation-full@0.2.0`: larger approximately 20 percent
  validation set after more structure repairs.

Current L3 tasks are material-type tasks containing many case rows internally.
For fully Harbor-native task filtering, the next step is to materialize split
variants or case-level tasks from this manifest.
