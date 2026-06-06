#!/usr/bin/env python3
"""Score L3 λ predictions: accuracy (λ, ω_log within tolerance) + cost (core-hours).

Usage: score.py --pred <out.csv> --gold <ref.csv>
out.csv columns:  case_id, lambda, omega_log_K, core_hours
ref.csv columns:  case_id, lambda_ref, omega_log_K_ref
PASS iff every case has |λ−λ_ref|/λ_ref ≤ TOL and |ω_log−ω_log_ref|/ω_log_ref ≤ TOL,
exactly one prediction per gold id. Total core-hours is reported (cost axis), not gated.
"""
import argparse, csv, json, sys

TOL = 0.15  # matches the computed-vs-experimental λ spread (median ~9%)


def read(path, key):
    with open(path) as f:
        return {r[key]: r for r in csv.DictReader(f)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred", required=True)
    ap.add_argument("--gold", required=True)
    a = ap.parse_args()
    gold = read(a.gold, "case_id")
    pred = read(a.pred, "case_id")

    results, ok, total_cost = [], True, 0.0
    # shape guard: exactly the gold ids, one each
    if set(pred) != set(gold):
        print(f"FAIL: prediction ids {sorted(pred)} != gold ids {sorted(gold)}")
        sys.exit(1)

    for cid, g in sorted(gold.items()):
        lr, wr = float(g["lambda_ref"]), float(g["omega_log_K_ref"])
        p = pred[cid]
        try:
            lp, wp = float(p["lambda"]), float(p["omega_log_K"])
            ch = float(p.get("core_hours", "nan"))
        except (ValueError, KeyError) as e:
            print(f"FAIL {cid}: bad prediction row ({e})")
            sys.exit(1)
        dl, dw = abs(lp - lr) / abs(lr), abs(wp - wr) / abs(wr)
        passed = dl <= TOL and dw <= TOL
        ok = ok and passed
        if ch == ch:  # not nan
            total_cost += ch
        results.append({"case_id": cid, "lambda_err": round(dl, 3),
                        "omega_log_err": round(dw, 3), "core_hours": ch, "pass": passed})
        print(f"  {cid}: λ {lp} vs {lr} ({dl:+.1%})  ω_log {wp} vs {wr} ({dw:+.1%})  "
              f"{ch:g} core-h  -> {'PASS' if passed else 'FAIL'}")

    print(f"\ntotal cost: {total_cost:g} core-hours  (cost axis — reported, not gated)")
    print("RESULT:", "PASS" if ok else "FAIL")
    json.dump({"pass": ok, "tolerance": TOL, "total_core_hours": total_cost, "cases": results},
              open("result.json", "w"), indent=2)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
