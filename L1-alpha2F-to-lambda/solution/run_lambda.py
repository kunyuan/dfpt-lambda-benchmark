#!/usr/bin/env python3
"""Oracle for L1: α²F(ω) → λ, ω_log.

A real submission is the agent's OWN run_lambda.py implementing the same moment
integrals. This reference reads each spectrum and integrates it.

Usage: run_lambda.py --params <cases.csv> --out <out.csv>
  cases.csv columns: case_id, spectrum_file
  each spectrum (in <dir-of-cases.csv>/spectra/<spectrum_file>): two columns
    "omega_meV  a2F"  (header line starts with '#')
  out.csv columns: case_id, lambda, omega_log_K
"""
import argparse, csv, math, os

MEV2K = 11.604519


def read_spectrum(path):
    ws, fs = [], []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            w, a = line.split()[:2]
            ws.append(float(w))
            fs.append(float(a))
    return ws, fs


def trapz(y, x):
    return sum((y[i] + y[i + 1]) * 0.5 * (x[i + 1] - x[i]) for i in range(len(x) - 1))


def moments(ws, fs):
    # λ = 2 ∫ α²F(ω)/ω dω ;  ω_log = exp[(2/λ) ∫ ln(ω) α²F(ω)/ω dω]   (ω in meV)
    glam = [2 * fs[i] / ws[i] for i in range(len(ws))]
    lam = trapz(glam, ws)
    glog = [2 * math.log(ws[i]) * fs[i] / ws[i] for i in range(len(ws))]
    wlog_meV = math.exp(trapz(glog, ws) / lam)
    return lam, wlog_meV * MEV2K  # ω_log in K


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--params", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    base = os.path.join(os.path.dirname(os.path.abspath(a.params)), "spectra")
    with open(a.params) as f:
        rows = list(csv.DictReader(f))
    with open(a.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["case_id", "lambda", "omega_log_K"])
        for r in rows:
            ws, fs = read_spectrum(os.path.join(base, r["spectrum_file"]))
            lam, wlogK = moments(ws, fs)
            w.writerow([r["case_id"], round(lam, 4), round(wlogK, 2)])


if __name__ == "__main__":
    main()
