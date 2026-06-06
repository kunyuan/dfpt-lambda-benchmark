#!/usr/bin/env python3
"""Score L1 predictions: λ and ω_log within relative tolerance of the gold.

Usage: score.py --pred <out.csv> --gold <gold.csv> [--json <result.json>]
Both CSVs: case_id, lambda, omega_log_K. PASS iff every case has
|λ−λ_gold|/λ_gold ≤ TOL and |ω_log−ω_log_gold|/ω_log_gold ≤ TOL, exactly one
prediction per gold id. Exit 0 iff PASS.
"""
import argparse, csv, json, sys

TOL = 0.02  # deterministic moment integrals; tight (catches units / missing factor-of-2 / wrong formula)


def read(path):
    with open(path) as f:
        return {r["case_id"]: r for r in csv.DictReader(f)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred", required=True)
    ap.add_argument("--gold", required=True)
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    gold, pred = read(a.gold), read(a.pred)

    if set(pred) != set(gold):
        print(f"FAIL: prediction ids {sorted(pred)} != gold ids {sorted(gold)}")
        if a.json:
            json.dump({"pass": False, "error": "id mismatch"}, open(a.json, "w"))
        sys.exit(1)

    ok, results = True, []
    for cid, g in sorted(gold.items()):
        lg, wg = float(g["lambda"]), float(g["omega_log_K"])
        p = pred[cid]
        try:
            lp, wp = float(p["lambda"]), float(p["omega_log_K"])
        except (ValueError, KeyError) as e:
            print(f"FAIL {cid}: bad prediction row ({e})")
            if a.json:
                json.dump({"pass": False, "error": f"bad row {cid}"}, open(a.json, "w"))
            sys.exit(1)
        dl, dw = abs(lp - lg) / abs(lg), abs(wp - wg) / abs(wg)
        passed = dl <= TOL and dw <= TOL
        ok = ok and passed
        results.append({"case_id": cid, "lambda_err": round(dl, 4),
                        "omega_log_err": round(dw, 4), "pass": passed})
        print(f"  {cid}: λ {lp} vs {lg} ({dl:+.2%})  ω_log {wp} vs {wg} ({dw:+.2%})  "
              f"-> {'PASS' if passed else 'FAIL'}")

    print("RESULT:", "PASS" if ok else "FAIL")
    if a.json:
        json.dump({"pass": ok, "tolerance": TOL, "cases": results}, open(a.json, "w"), indent=2)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
