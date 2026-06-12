#!/usr/bin/env python3
"""Score L4 λ predictions against EXPERIMENTAL gold, scaled by the SOTA theory-experiment gap.

The yardstick is NOT the experimental error bar: it is how well state-of-the-art
first-principles theory matches experiment on this dataset. Per pair the SOTA gap is
g_i = |λ_sota − λ_exp| / λ_exp; averaged over all 21 train+validation pairs this gives
G_SOTA = 0.117 (derivation table in ../README.md).

Per case : d_i = |λ_pred − λ_exp| / λ_exp     (relative deviation from experiment)
Leaderboard: ratio R = mean(d_i) / G_SOTA      (R < 1 ⇒ better than published SOTA)
PASS     : mean(d_i) ≤ G_SOTA  AND  every d_i ≤ 3·G_SOTA (no catastrophic outlier,
           e.g. a forgotten SOC or wrong magnetic state).
"""
import argparse, csv, json, sys

G_SOTA = 0.117   # mean relative |λ_sota − λ_exp|/λ_exp over the 21 dataset pairs
CAP = 3.0 * G_SOTA


def rd(p):
    with open(p) as f:
        return {r["case_id"]: r for r in csv.DictReader(f)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred", required=True)
    ap.add_argument("--gold", required=True)
    ap.add_argument("--json", default="result.json")
    a = ap.parse_args()
    gold = rd(a.gold)
    pred = rd(a.pred)
    if set(pred) != set(gold):
        print(f"FAIL: ids {sorted(pred)} != gold {sorted(gold)}")
        json.dump({"pass": False, "error": "id mismatch"}, open(a.json, "w"))
        sys.exit(1)
    res, cost, devs, all_in = [], 0.0, [], True
    for cid, g in sorted(gold.items()):
        le = float(g["lambda_exp"])
        p = pred[cid]
        try:
            lp = float(p["lambda"])
        except Exception as e:
            print(f"FAIL {cid}: bad row {e}")
            json.dump({"pass": False, "error": f"bad row {cid}"}, open(a.json, "w"))
            sys.exit(1)
        d = abs(lp - le) / abs(le)
        ok = d <= CAP
        all_in = all_in and ok
        devs.append(d)
        try:
            cost += float(p.get("core_hours", "nan"))
        except Exception:
            pass
        res.append({"case_id": cid, "material": g.get("material", ""), "lambda_pred": lp,
                    "lambda_exp": le, "rel_dev": round(d, 4), "pass": ok})
        print(f"  {cid} {g.get('material',''):8s} λ {lp:6.3f} vs {le:5.2f}  "
              f"dev={d:6.1%} (cap {CAP:.1%}) -> {'PASS' if ok else 'FAIL'}")
    mean_d = sum(devs) / len(devs)
    ratio = mean_d / G_SOTA
    passed = all_in and mean_d <= G_SOTA
    print(f"\nmean rel dev: {mean_d:.1%}  vs SOTA gap G={G_SOTA:.1%}  ->  ratio {ratio:.3f} "
          f"({'beats' if ratio < 1 else 'behind'} published SOTA)")
    print(f"total cost: {cost:g} core-hours (reported)\nRESULT: {'PASS' if passed else 'FAIL'}")
    json.dump({"pass": passed, "mean_rel_dev": round(mean_d, 4), "sota_gap": G_SOTA,
               "ratio_to_sota": round(ratio, 4), "per_case_cap": CAP,
               "total_core_hours": cost, "cases": res}, open(a.json, "w"), indent=2)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
