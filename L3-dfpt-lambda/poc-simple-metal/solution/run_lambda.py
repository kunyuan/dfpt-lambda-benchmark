#!/usr/bin/env python3
"""Oracle (stand-in) for the L3 λ task.

A REAL solver reads each structure in --params, runs DFPT (SCF → phonons →
electron-phonon on a dense k double-delta) for the stated condition, and reports
the computed λ, ω_log, and the core-hours it spent.

Running DFPT is not possible inside the cheap verifier sandbox, so this oracle
emits a *cached* reference result (`precomputed.csv`, sitting beside this script) —
i.e. it stands in for "having correctly run the DFPT pipeline". It exists to prove
the task plumbing + verifier, not to compute anything. Replace it with an actual
DFPT driver (Quantum ESPRESSO pw.x/ph.x + a λ extraction) for a live run.
"""
import argparse, csv, os

HERE = os.path.dirname(os.path.abspath(__file__))
_CACHE = os.path.join(HERE, "precomputed.csv")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--params", required=True)  # cases.csv (case_id, structure_file, condition, mu_star)
    ap.add_argument("--out", required=True)      # out.csv (case_id, lambda, omega_log_K, core_hours)
    a = ap.parse_args()

    cached = {r["case_id"]: r for r in csv.DictReader(open(_CACHE))}
    with open(a.params) as f:
        ids = [r["case_id"] for r in csv.DictReader(f)]

    with open(a.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["case_id", "lambda", "omega_log_K", "core_hours"])
        for cid in ids:
            c = cached[cid]
            w.writerow([cid, c["lambda"], c["omega_log_K"], c["core_hours"]])


if __name__ == "__main__":
    main()
