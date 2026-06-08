#!/usr/bin/env python3
"""Extract total λ and ω_log from a Quantum ESPRESSO ph.x electron_phonon='simple' output.

  λ(σ)     = Σ_q (M_q/N) Σ_ν λ_qν              (N = Σ_q M_q ; M_q = star multiplicity)
  ω_log(σ) = exp[ Σ_q (M_q/N) Σ_ν λ_qν ln ω_qν / λ(σ) ]   (ω in K = cm⁻¹ × 1.43877)

evaluated across the el_ph_sigma scan; Γ acoustic modes (ω<5 cm⁻¹) are skipped.

Usage: extract_lambda.py <ph.out> [--sigma 0.025]
"""
import re, math, sys, argparse

CM2K = 1.43877


def extract(path):
    txt = open(path).read()
    blocks = re.split(r"Calculation of q =", txt)[1:]
    qdata = []
    for b in blocks:
        ms = re.search(r"Number of q in the star =\s*(\d+)", b)
        M = int(ms.group(1)) if ms else 1
        freqs = [float(x) for x in re.findall(
            r"freq \(\s*\d+\)\s*=\s*[-0-9.]+\s*\[THz\]\s*=\s*([-0-9.]+)\s*\[cm-1\]", b)]
        lam, s = [], -1
        for line in b.splitlines():
            if "Gaussian Broadening:" in line:
                s += 1
                lam.append([])
            m = re.search(r"lambda\(\s*\d+\)=\s*([0-9.]+)", line)
            if m and s >= 0:
                lam[s].append(float(m.group(1)))
        if lam and lam[0]:
            nm = len(lam[0])
            qdata.append((M, freqs[-nm:], lam))
    N = sum(q[0] for q in qdata)
    res = {}      # sigma_Ry -> (lambda, omega_log_K)
    domfrac = {}  # sigma_Ry -> max single-(q,ν) weighted contribution / λ_total
    nsig = max((len(q[2]) for q in qdata), default=0)
    for si in range(nsig):
        lt = ls = 0.0; mxc = 0.0
        for M, fr, lam in qdata:
            if si >= len(lam):
                continue
            w = M / N
            for nu in range(min(len(lam[si]), len(fr))):
                wq = abs(fr[nu])
                if wq < 5:                      # skip Γ acoustic
                    continue
                c = w * lam[si][nu]             # weighted contribution of this (q,ν)
                lt += c
                ls += c * math.log(wq * CM2K)
                mxc = max(mxc, c)
        res[round(0.005 * (si + 1), 3)] = (lt, math.exp(ls / lt) if lt > 0 else 0.0)
        domfrac[round(0.005 * (si + 1), 3)] = (mxc / lt) if lt > 0 else 0.0
    return res, N, len(qdata), domfrac


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("phout")
    ap.add_argument("--sigma", type=float, default=0.025, help="el_ph broadening (Ry) to report")
    a = ap.parse_args()
    res, N, nq, domfrac = extract(a.phout)
    print(f"# {a.phout}: {nq} irreducible q, N(grid)={N}")
    print(f"{'sigma_Ry':>9}{'lambda':>9}{'omega_log_K':>13}{'top_q_share':>13}")
    for s in sorted(res):
        lt, wl = res[s]
        mark = "  <-" if abs(s - a.sigma) < 1e-6 else ""
        print(f"{s:9.3f}{lt:9.3f}{wl:13.1f}{domfrac[s]*100:11.0f} %{mark}")
    if domfrac.get(round(a.sigma, 3), 0) > 0.25:
        print(f"# WARNING: a single (q,ν) carries {domfrac[round(a.sigma,3)]*100:.0f}% of λ "
              f"-> a phonon anomaly dominates this {'coarse ' if N <= 27 else ''}grid; λ is likely "
              f"NOT converged. Re-run on a denser q-grid and check λ stabilizes.")
