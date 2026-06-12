# L3 Harbor Train/Validation Split Design

Date: 2026-06-11

## Goal

Define a Harbor-native train/validation split for the L3 DFPT lambda benchmark.
The split should support a stable final validation dataset while keeping enough
public training cases for workflow tuning, structure recovery, and convergence
debugging.

## Design

Use a case-level stratified split:

- `validation_core`: 25 cases, exactly 5 from each L3 material class.
- `train`: the remaining 251 cases.

This keeps every material system represented in validation while avoiding a
category-level split that would confound material difficulty with generalization.
Cases already used heavily in public reproduction records are assigned to
`train`, not `validation_core`, so the validation set is less tuned.

## Selection Rules

Validation cases are selected to cover:

- all five material classes;
- both `structure-ready` and `build-from-spec` workflows;
- simple direct DFPT, SOC, 2D/strain/intercalation, and hydride/high-pressure
  workflows;
- low-lambda and high-lambda regimes;
- at least a few numerically diagnostic cases without making the whole validation
  set a failure-mode collection.

Cases with clear material/condition mismatches are kept in `train` until repaired.
The validation set may include high-confidence build-from-spec cases, because
constructing the paper-specific target structure is part of the L3 task.

## Harbor Scoring Contract

The verifier should write numeric reward keys to `reward.json`:

- `reward`: primary leaderboard reward, `1` for pass and `0` otherwise.
- `structure_ok`: `1` only when structure, phase, pressure, and SOC/no-SOC
  condition match the target.
- `lambda_pass`: `1` when `abs(lambda_calc - lambda_ref) <= max(0.05, 0.20 *
  lambda_ref)`.
- `lambda_strong`: stricter diagnostic, usually 10-15 percent depending on
  material class.
- `omega_pass`: auxiliary omega-log check, normally 10-15 percent or an absolute
  floor.
- `diagnostic`: `1` when the result is not a pass but the failure is attributable
  to a known convergence or method limitation.
- continuous error fields such as `lambda_rel_err` and `omega_rel_err`.

Human-readable diagnosis belongs in verifier artifacts such as
`validation_report.json`, not in reward keys.

## Files

- `splits/l3_case_splits.csv`: all 276 L3 case IDs with split labels.
- `splits/l3_validation_core.csv`: the 25 validation cases with metadata and
  selection reasons.
- `splits/README.md`: policy, scoring rules, and Harbor packaging notes.
