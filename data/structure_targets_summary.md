# DFPT Lambda Benchmark Structure Target Audit

Source: full `data/lambda_reference.csv` (276 cases), LKM paper graph/markdown, repo structure hints/build status, and current QE structures.

## Coverage

- Total cases: 276 / 276
- Missing / extra / duplicate case_ids: none
- Confidence: high=127, medium=114, low=35

| material_type | cases | high | medium | low |
| --- | ---: | ---: | ---: | ---: |
| 2d-layered | 38 | 30 | 5 | 3 |
| heavy-soc | 38 | 29 | 6 | 3 |
| hydride | 53 | 9 | 40 | 4 |
| intermetallic | 107 | 49 | 43 | 15 |
| simple-metal | 40 | 10 | 20 | 10 |

## Current Packaging Status

- structure-ready: 80 cases (OpenLAM 55, MP 10, LKM 15)
- build-from-spec: 196 cases

| material_type | structure-ready | build-from-spec |
| --- | ---: | ---: |
| intermetallic | 55 | 52 |
| simple-metal | 11 | 29 |
| 2d-layered | 0 | 38 |
| hydride | 1 | 52 |
| heavy-soc | 13 | 25 |

## First Repair Batch

These high-confidence paper/prototype structures are now packaged as proper-`ibrav` QE inputs and removed from `structure_hints`:

- lam138: CdCNi3 / Pm-3m / CdCNi3, mu*=0.12 -> `CdCNi3__lam138.scf.in`
- lam148: I / Fm-3m / FCC iodine, 103 GPa -> `I__lam148.scf.in`
- lam149: I / Fm-3m / FCC iodine, 64 GPa -> `I__lam149.scf.in`
- lam150: I / Fm-3m / FCC iodine, 81 GPa -> `I__lam150.scf.in`
- lam248: La / P6_3/mmc / dhcp La -> `La__lam248.scf.in`
- lam250: Li / P6_3/mmc / (single) -> `Li__lam250.scf.in`
- lam253: Mo3Os / Pm-3n / Mo3Os (A-15) -> `Mo3Os__lam253.scf.in`
- lam261: P / Pm-3m / sc P, 20 GPa (P_calc) -> `P__lam261.scf.in`
- lam262: P / Pm-3m / sc P, 70 GPa (P_calc) -> `P__lam262.scf.in`
- lam263: S / R-3m / beta-Po 160 GPa -> `S__lam263.scf.in`
- lam264: S / Pm-3m / sc 280 GPa -> `S__lam264.scf.in`

## Remaining Non-Exclusive Action Buckets

- fix_reference_or_case_mapping: 27 cases. lam020, lam021, lam026, lam041, lam106, lam107, lam117, lam139, lam158, lam179, lam180, lam181, lam198, lam199, lam214, lam215, lam216, lam217, lam218, lam242 ... (+7)
- rebuild_wrong_structure_candidate: 75 cases. lam006, lam009, lam010, lam011, lam012, lam013, lam014, lam015, lam031, lam035, lam041, lam050, lam051, lam068, lam078, lam081, lam084, lam100, lam101, lam102 ... (+55)
- needs_manual_paper_supplement_or_coordinates: 142 cases. lam001, lam002, lam003, lam004, lam005, lam006, lam007, lam008, lam009, lam010, lam011, lam012, lam013, lam014, lam015, lam016, lam017, lam018, lam019, lam020 ... (+122)
- review_medium_confidence: 102 cases. lam005, lam006, lam009, lam031, lam034, lam066, lam067, lam077, lam078, lam079, lam080, lam081, lam082, lam083, lam084, lam085, lam086, lam087, lam088, lam089 ... (+82)
- low_confidence_manual: 34 cases. lam020, lam021, lam026, lam058, lam068, lam076, lam106, lam107, lam117, lam124, lam139, lam158, lam179, lam180, lam181, lam198, lam199, lam200, lam201, lam202 ... (+14)

## Highest-Priority Remaining Issues

- lam158 (intermetallic): (single) -> target kappa-(BEDT-TTF)2I3 / beta*-(BEDT-TTF)2I3 P2_1 P=; flags=condition_material_description_inconsistent;repo_current_formula_mismatch:BF->BEDT-TTF;manual_required
- lam268 (simple-metal): Cmcm-AtH2 50 GPa -> target AtH2 Cmcm P=50; flags=condition_material_mismatch;same_paper_id_cross_family_suspected;lkm_paper_title_mismatch;repo_current_sg_mismatch:P6_3/mmc->Cmcm;manual_required
- lam273 (simple-metal): Pnma-AtH2 200 GPa -> target AtH2 Pnma P=200; flags=condition_material_mismatch;same_paper_id_cross_family_suspected;lkm_paper_title_mismatch;repo_current_sg_mismatch:P6_3/mmc->Pnma;manual_required
- lam139 (intermetallic): (single) -> target NaB1.1C0.9 / hole-doped NaBC  P=; flags=condition_material_description_inconsistent;same_paper_id_condition_suspected_cross_family;lkm_has_lambda_but_no_structure;manual_required
- lam179 (intermetallic): P1 H5S2, 112 GPa -> target P1H5S2 P1 P=112; flags=condition_material_description_inconsistent;same_paper_id_condition_suspected_cross_family;manual_required
- lam180 (intermetallic): P1 H5S2, 120 GPa -> target P1H5S2 P1 P=120; flags=condition_material_description_inconsistent;same_paper_id_condition_suspected_cross_family;manual_required
- lam181 (intermetallic): P1 H5S2, 130 GPa -> target P1H5S2 P1 P=130; flags=condition_material_description_inconsistent;same_paper_id_condition_suspected_cross_family;manual_required
- lam198 (intermetallic): (single) -> target (Ce,La)H9 P-6m2 P=200; flags=material_type_mismatch_hydride;lkm_has_lambda_but_incomplete_structure;manual_required
- lam199 (intermetallic): benzene P2_1/c, 190 GPa, mu*=0.10 -> target C6H6 P2_1/c P=190; flags=material_type_mismatch_organic;lkm_has_lambda_but_incomplete_structure;manual_required
- lam216 (intermetallic): monolayer AlB2 (single Al on honeycomb B) -> target AlB2 monolayer P6/mmm P=; flags=condition_material_description_inconsistent;same_paper_id_condition_suspected_cross_family;manual_required
- lam217 (intermetallic): H-diamond(111) FET n=6e14 cm-2, full-BZ Wannier -> target H-terminated diamond(111) surface  P=; flags=condition_material_description_inconsistent;lkm_has_lambda_but_no_structure;manual_required
- lam218 (intermetallic): H-diamond(111) FET n=6e14 cm-2, q=Gamma approx -> target H-terminated diamond(111) surface  P=; flags=condition_material_description_inconsistent;lkm_has_lambda_but_no_structure;manual_required
- lam242 (simple-metal): (single) -> target Ta Im-3m P=; flags=lkm_paper_title_mismatch;condition_material_mismatch;manual_required
- lam252 (simple-metal): rock-salt SnAs -> target SnAs Fm-3m P=; flags=lkm_paper_title_mismatch;condition_material_mismatch;manual_required
- lam269 (simple-metal): Cmmm-AtH4 250 GPa -> target AtH4 Cmmm P=250; flags=condition_material_mismatch;same_paper_id_cross_family_suspected;lkm_paper_title_mismatch;repo_absent_structure;manual_required
- lam270 (simple-metal): P6/mmm-AtH4 100 GPa -> target AtH4 P6/mmm P=100; flags=condition_material_mismatch;same_paper_id_cross_family_suspected;lkm_paper_title_mismatch;repo_absent_structure;manual_required
- lam271 (simple-metal): P6/mmm-AtH4 200 GPa with SOC -> target AtH4 P6/mmm P=200; flags=condition_material_mismatch;same_paper_id_cross_family_suspected;lkm_paper_title_mismatch;repo_absent_structure;manual_required
- lam272 (simple-metal): P6/mmm-AtH4 200 GPa without SOC -> target AtH4 P6/mmm P=200; flags=condition_material_mismatch;same_paper_id_cross_family_suspected;lkm_paper_title_mismatch;repo_absent_structure;manual_required
- lam020 (2d-layered): CeH10 (Fm-3m) 94 GPa, mu*=0.10 -> target CeH10 Fm-3m P=94; flags=condition_material_mismatch;same_paper_condition_suspect_wrong_family;LKM_has_lambda_no_structure;material_type_should_be_hydride_or_paper_id_wrong
- lam021 (2d-layered): CeH9 (F-43m) 94 GPa, mu*=0.10 -> target CeH9 F-43m P=94; flags=condition_material_mismatch;same_paper_condition_suspect_wrong_family;LKM_has_lambda_no_structure;material_type_should_be_hydride_or_paper_id_wrong
- lam026 (2d-layered): I-4m2 SnH8 250 GPa (mu*=0.10) -> target SnH8 I-4m2 P=250; flags=condition_material_mismatch;same_paper_condition_suspect_wrong_family;LKM_has_lambda_no_structure;material_type_should_be_hydride_or_paper_id_wrong
- lam106 (hydride): SrAu2Si2 (I4/mmm) -> target INVALID: condition SrAu2Si2; paper is H5S2 sulfur hydride  P=; flags=condition_material_description_inconsistent|same_paper_id_condition_suspected_cross_family|condition_is_not_hydride
- lam107 (hydride): SrAuSi3 (I4mm) -> target INVALID: condition SrAuSi3; paper is H5S2 sulfur hydride  P=; flags=condition_material_description_inconsistent|same_paper_id_condition_suspected_cross_family|condition_is_not_hydride
- lam117 (hydride): CaAlSi AF-like stacking -> target INVALID: condition CaAlSi AF-like; paper is XC6 carbon sodalite  P=; flags=condition_material_description_inconsistent|material_type_hydride_but_no_hydrogen|same_paper_id_condition_suspected_cross_family|repo_structure_absent
- lam041 (heavy-soc): ScRuSi -> target ScRuSi Pnma P=0; flags=condition_material_inconsistent;repo_current_structure_space_group_mismatch;repo_current_formula_mismatch
- lam214 (intermetallic): Im-3m H3P, a=3.0 A (~220 GPa), mu*=0 (H-point unstable modes omitted) -> target H3P Im-3m P=220; flags=material_type_mismatch_hydride
- lam215 (intermetallic): Im-3m H3S, a=3.0 A (~220 GPa), mu*=0 -> target H3S Im-3m P=220; flags=material_type_mismatch_hydride
- lam058 (heavy-soc): SrPt3P -> target SrPt3P P4/nmm P=0; flags=LKM_has_lambda_but_no_structure;repo_no_current_structure
- lam068 (heavy-soc): OsN2 hole-doped 0.5 holes/cell -> target OsN2 / Os0.75Re0.25N2 virtual hole-doped target Pnnm P=0; flags=LKM_has_lambda_but_no_structure;repo_current_structure_space_group_mismatch;doping_not_encoded_in_repo_structure
- lam076 (heavy-soc): TlTaSe2 -> target TlTaSe2 P-6m2 P=0; flags=LKM_has_lambda_but_no_structure;repo_no_current_structure
- lam200 (intermetallic): Be-Al 24:976 -> target Be-Al alloy  P=; flags=lkm_has_lambda_but_no_structure;repo_structure_is_database_candidate_not_ground_truth;manual_required
- lam201 (intermetallic): Be-In 31:69 -> target Be-In alloy  P=; flags=lkm_has_lambda_but_no_structure;repo_structure_is_database_candidate_not_ground_truth;manual_required
- lam202 (intermetallic): Be-Nb 23:77 -> target Be-Nb alloy  P=; flags=lkm_has_lambda_but_no_structure;repo_structure_is_database_candidate_not_ground_truth;manual_required
- lam203 (intermetallic): Be43Bi20Pb37 (ternary) -> target Be43Bi20Pb37  P=; flags=lkm_has_lambda_but_no_structure;repo_structure_absent;manual_required
- lam204 (intermetallic): Be43Pb57 -> target Be43Pb57  P=; flags=lkm_has_lambda_but_no_structure;repo_structure_absent;manual_required

## Files

- `data/structure_targets.csv`
- `L3-dfpt-lambda/build_status.csv`
- `L3-dfpt-lambda/structure_hints.json` / `.csv`
