#!/usr/bin/env python3
"""Oracle stand-in: emit cached literature first-principles λ (represents a correct off-sandbox run)."""
import argparse, csv, os
HERE = os.path.dirname(os.path.abspath(__file__)); CACHE = os.path.join(HERE, "precomputed.csv")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--params", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cached = {r["case_id"]: r for r in csv.DictReader(open(CACHE))}
    ids = [r["case_id"] for r in csv.DictReader(open(a.params))]
    with open(a.out, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["case_id", "lambda", "core_hours"])
        for cid in ids:
            c = cached[cid]; w.writerow([cid, c["lambda"], c.get("core_hours", "")])


if __name__ == "__main__":
    main()
