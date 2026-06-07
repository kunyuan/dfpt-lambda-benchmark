# L3 build status — structures & pseudopotentials

Systematic preparation of runnable structures for the L3 material tracks, following
the [`lambda-benchmark-build`](../.claude/skills/lambda-benchmark-build/SKILL.md) skill.

## What's here

- **`structures/<formula>.scf.in`** — 95 QE `pw.x` inputs (one per unique formula),
  each with a **proper `ibrav`** (never `ibrav=0`; e.g. MgB₂→4, A15→1) derived from
  the OpenLAM ground-state structure via `structure_to_qe.py`, with SG15 pseudo names
  and per-element `ecutwfc`. Add a pressure `vc-relax` step for high-pressure cases.
- **`build_status.csv`** — per case: formula, structure source, structure file, space
  group, and status (`built` / `tier2-convert` / `tier2-fallback`).
- **`pseudos/manifest.json`** + **`pseudos/fetch_sg15.sh`** — the 48 elements needed,
  with SG15 ONCV-PBE filenames + cutoffs, and a download script. The `.upf` files are
  **not committed** (run the script to fetch ~free SG15).

## Coverage (Tier 1 = OpenLAM-direct)

276 cases / 189 unique formulas. **146 cases built** from OpenLAM (53 %); 130 need a
Tier-2 fallback (complex ternary hydrides / VCA alloys absent from OpenLAM, plus a few
formula-parse edge cases).

| material track | built / total |
|---|---|
| intermetallic | 80 / 107 |
| simple-metal | 29 / 40 |
| 2d-layered | 14 / 38 |
| hydride | 12 / 53 |
| heavy-soc | 11 / 38 |

(Hydrides are worst-covered — OpenLAM's stable-structure DB lacks most high-pressure
ternary hydrides; these need COD / paper-lattice + prototype, Tier 2.)

## To run a built case (gold = paper λ in `data/lambda_reference.csv`)

```bash
cd pseudos && bash fetch_sg15.sh && cd ..          # one-time: download SG15
# pick a case from build_status.csv -> its structures/<formula>.scf.in
# (high-pressure: vc-relax to the condition's pressure first)
# then scf -> ph.x el-ph -> extract λ  (see ../.claude/skills/qe-eph-lambda/)
```

## Tier 2 (next)

- fix the handful of formula-parse artifacts (Roman numerals like `Sc-III`,
  space-group fragments) → re-query OpenLAM;
- COD / Materials-Project / prototype-from-LKM-lattice for the genuinely-absent
  compounds (most hydrides, several ternaries).
