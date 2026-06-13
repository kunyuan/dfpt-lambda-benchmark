#!/usr/bin/env python3
"""A4u-v2: replace the sharp 2k_F cutoff with a Gaussian-smeared double-delta nesting.

v1 used a spherical-FS nesting factor 1/|Q| * theta(2k_F - |Q|): a hard cutoff that
(a) zeroes all |q+G| > 2k_F discontinuously and (b) diverges as |Q|->0. Both are
artifacts of zero smearing. DFPT's 'simple' el-ph uses a finite Gaussian width sigma;
the physically matched nesting is the static double-delta

    J(Q) = integral d3k delta_sigma(k^2 - kF^2) delta_sigma((k+Q)^2 - kF^2)

with delta_sigma a Gaussian of width sigma (energy units, eps_k = k^2 in Ry). This is
smooth across 2k_F (a tail beyond, rounded at), removing K's soft-mode node blowup and
Al's large-q drift WITHOUT a vertex change. Everything else is frozen A4u:

    lambda_qnu = C * sum_G |w(|q+G|)/eps(|q+G|)|^2 ((q+G).e_qnu)^2 J(|q+G|) / omega_qnu^2

J(Q) computed once on a grid by direct spherical k-integration, then interpolated.
NO new DFT. Tests whether the s-character class (Na/K/Al) unifies to ~10%; the
orbital class (P/S/V/Ta/Mo) is a separate structural gap and is NOT expected to close.
"""
import argparse, glob, re
import numpy as np


def smeared_nesting_table(kf, sigma, qmax, nq=200, nk=400, nmu=200):
    """J(Q) = int d3k G(k^2-kF^2) G((k+Q)^2-kF^2), G Gaussian width sigma (Ry)."""
    def G(x):
        return np.exp(-0.5 * (x / sigma) ** 2) / (sigma * np.sqrt(2 * np.pi))
    # k near the Fermi shell dominates; integrate k in [kf-5sigma_k, kf+5sigma_k]
    dk = 5 * sigma / (2 * kf)  # delta-eps -> delta-k ~ sigma/(2kf)
    kmin = max(1e-4, kf - 6 * dk - 0.05)
    kmax = kf + 6 * dk + 0.05
    kgrid = np.linspace(kmin, kmax, nk)
    mu = np.linspace(-1, 1, nmu)  # cos(angle between k and Q)
    Qs = np.linspace(1e-3, qmax, nq)
    J = np.zeros(nq)
    for iq, Q in enumerate(Qs):
        # vectorized over k, mu
        K, M = np.meshgrid(kgrid, mu, indexing='ij')
        e1 = K**2 - kf**2
        ekq = K**2 + Q**2 + 2 * K * Q * M
        e2 = ekq - kf**2
        integrand = G(e1) * G(e2) * K**2  # d3k = k^2 dk dOmega; phi integral = 2pi
        J[iq] = 2 * np.pi * np.trapz(np.trapz(integrand, mu, axis=1), kgrid)
    return Qs, J


def parse_dyn_first_q(path):
    t = open(path).read()
    m = re.search(r'q = \(\s*([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s*\)\s*\n\n\s*1\s+1\s*\n'
                  r'((?:\s*[-\d.Ee+]+.*\n){3})', t)
    q = np.array([float(m.group(i)) for i in (1, 2, 3)])
    D = np.zeros((3, 3), complex)
    for i, row in enumerate(m.group(4).strip().split('\n')):
        v = [float(x) for x in row.split()]
        for j in range(3):
            D[i, j] = v[2 * j] + 1j * v[2 * j + 1]
    return q, D


def parse_elph(path, sigma='0.025'):
    t = open(path).read()
    h = t.split('\n')[0].split()
    q = np.array([float(h[0]), float(h[1]), float(h[2])])
    blk = re.findall(rf'Gaussian Broadening:\s*{sigma} Ry.*?(?=Gaussian Broadening|\Z)', t, re.S)[0]
    return q, np.array([float(x) for x in re.findall(r'lambda\(\s*\d+\)=\s*([\d.Ee+-]+)', blk)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifacts", required=True)
    ap.add_argument("--model-csv", required=True)
    ap.add_argument("--alat", type=float, required=True)
    ap.add_argument("--kf", type=float, required=True)
    ap.add_argument("--mass", type=float, required=True)
    ap.add_argument("--lattice", required=True, choices=["bcc", "fcc", "sc"])
    ap.add_argument("--sigma-ry", type=float, default=0.025)
    a = ap.parse_args()

    tpa = 2 * np.pi / a.alat
    model = np.loadtxt(a.model_csv, skiprows=1)
    qm, gmod = model[:, 0], model[:, 3]

    def g2(Q):
        return np.interp(Q, qm, gmod, right=gmod[-1]) ** 2

    Gint = {
        "bcc": [[n + m, m + l, n + l] for n in range(-3, 4) for m in range(-3, 4) for l in range(-3, 4)],
        "fcc": [[-n + m + l, n - m + l, n + m - l] for n in range(-3, 4) for m in range(-3, 4) for l in range(-3, 4)],
        "sc": [[n, m, l] for n in range(-3, 4) for m in range(-3, 4) for l in range(-3, 4)],
    }[a.lattice]
    Gs = np.unique(np.array(Gint), axis=0)

    Qtab, Jtab = smeared_nesting_table(a.kf, a.sigma_ry, qmax=2 * a.kf + 1.0)

    def nest(Q):
        return np.interp(Q, Qtab, Jtab, right=Jtab[-1] * np.exp(-(Q - Qtab[-1])))

    data = []
    for f in sorted(glob.glob(f'{a.artifacts}/matdyn[0-9]*')):
        if '.elph.' in f:
            continue
        n = re.search(r'matdyn(\d+)$', f).group(1)
        if n == '0':
            continue
        q, D = parse_dyn_first_q(f)
        qe, lam = parse_elph(f'{a.artifacts}/matdyn{n}.elph.{n}')
        if np.linalg.norm(q) < 1e-8:
            continue
        w2, ev = np.linalg.eigh(D / a.mass)
        om = np.sqrt(np.abs(w2))
        lm = []
        for nu in range(3):
            s = 0.0
            for G in Gs:
                Q = (q + G) * tpa
                Qn = np.linalg.norm(Q)
                if Qn < 1e-9:
                    continue
                s += g2(Qn) * (Q @ np.real(ev[:, nu])) ** 2 * nest(Qn)
            lm.append(s / om[nu] ** 2)
        data.append((np.linalg.norm(q) * tpa / (2 * a.kf), lam, np.array(lm)))

    q0 = min(data, key=lambda d: d[0])
    iL = int(np.argmax(q0[1]))
    C = q0[1][iL] / q0[2][iL]
    print(f"A4u-v2 (smeared sigma={a.sigma_ry} Ry)  C@|q|/2kF={q0[0]:.3f}")
    print(f"{'|q|/2kF':>7s} {'lam_DFPT':>22s} {'lam_v2':>22s} {'ratio':>5s}")
    tD = tM = 0.0
    for x, lam, lm in sorted(data, key=lambda d: d[0]):
        lm = lm * C
        print(f"{x:7.3f} {str(np.round(lam,3)):>22s} {str(np.round(lm,3)):>22s} {lm.sum()/lam.sum():5.2f}")
        tD += lam.sum()
        tM += lm.sum()
    print(f"\nTOTAL: DFPT {tD:.3f}  v2 {tM:.3f}  ratio {tM/tD:.2f}")


if __name__ == "__main__":
    main()
