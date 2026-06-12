#!/usr/bin/env python3
"""Score L4 λ predictions against EXPERIMENTAL gold with per-case uncertainty.

Per case: z = (λ_pred − λ_exp) / σ_eff, σ_eff = max(σ_exp, REL_FLOOR·λ_exp).
Credit  : score_i = exp(−z²/2)  (1.0 exact, 0.61 at 1σ, 0.14 at 2σ).
PASS    : every case |z| ≤ ZMAX  AND  mean(score) ≥ MEAN_MIN.

Rationale: experimental λ values carry heterogeneous error bars (tunneling ~3–6%,
specific-heat γ ~8%, point-contact ~30% on tiny λ); a single relative tolerance
would be unfair at both ends, so the gate is uncertainty-normalized.
"""
import argparse, csv, json, math, sys

REL_FLOOR = 0.05   # σ floor as fraction of λ_exp (even gold-standard routes spread ~5%)
ZMAX = 2.0         # per-case gate: within 2 effective sigma
MEAN_MIN = 0.50    # fleet gate: mean Gaussian credit


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
    res, cost, scores, all_in = [], 0.0, [], True
    for cid, g in sorted(gold.items()):
        le, se = float(g["lambda_exp"]), float(g["sigma_exp"])
        s_eff = max(se, REL_FLOOR * abs(le))
        p = pred[cid]
        try:
            lp = float(p["lambda"])
        except Exception as e:
            print(f"FAIL {cid}: bad row {e}")
            json.dump({"pass": False, "error": f"bad row {cid}"}, open(a.json, "w"))
            sys.exit(1)
        z = (lp - le) / s_eff
        sc = math.exp(-0.5 * z * z)
        ok = abs(z) <= ZMAX
        all_in = all_in and ok
        scores.append(sc)
        try:
            cost += float(p.get("core_hours", "nan"))
        except Exception:
            pass
        res.append({"case_id": cid, "material": g.get("material", ""), "lambda_pred": lp,
                    "lambda_exp": le, "sigma_eff": round(s_eff, 4), "z": round(z, 2),
                    "score": round(sc, 3), "pass": ok})
        print(f"  {cid} {g.get('material',''):8s} λ {lp:6.3f} vs {le:5.2f}±{s_eff:.2f}  "
              f"z={z:+5.2f}  credit={sc:.3f} -> {'PASS' if ok else 'FAIL'}")
    mean_sc = sum(scores) / len(scores)
    passed = all_in and mean_sc >= MEAN_MIN
    print(f"\nmean credit: {mean_sc:.3f} (gate {MEAN_MIN})  all |z|<={ZMAX}: {all_in}")
    print(f"total cost: {cost:g} core-hours (reported)\nRESULT: {'PASS' if passed else 'FAIL'}")
    json.dump({"pass": passed, "mean_score": round(mean_sc, 4), "zmax": ZMAX,
               "mean_min": MEAN_MIN, "rel_floor": REL_FLOOR,
               "total_core_hours": cost, "cases": res}, open(a.json, "w"), indent=2)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
