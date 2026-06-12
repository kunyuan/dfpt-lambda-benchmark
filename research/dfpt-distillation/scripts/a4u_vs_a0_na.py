#!/usr/bin/env python3
"""A4u vs A0 (frozen recipe — NO per-material tuning): mode-resolved vertex ablation with DFPT phonons held fixed.

A4u model: lambda_qnu = C * sum_G |w(|q+G|)/eps(|q+G|)|^2 ((q+G).e_nu)^2 / (|q+G| om_nu^2)
over Umklapp channels open on the Fermi sphere (|q+G| <= 2k_F); spherical double-delta
nesting ~ 1/|Q|; single constant C calibrated at the smallest-q longitudinal point
(q->0 anchored by the acoustic sum rule). Inputs: artifacts_distill/ from an A0 run
(matdynN dynamical matrices + matdynN.elph.N mode-resolved lambdas) and the model
vertex table from model_vertex.py.

Validated on Na LDA q6 (LBG 22867111): all 15 q x 3 modes reproduced, ratios
1.00-0.95 at |q| <= 0.5*2kF drifting to 0.81-0.87 at zone boundary; total 0.89.
"""
import argparse, glob, re
import numpy as np


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
    blk = re.findall(rf'Gaussian Broadening:\s*{sigma} Ry.*?(?=Gaussian Broadening|\Z)',
                     t, re.S)[0]
    lam = np.array([float(x) for x in re.findall(r'lambda\(\s*\d+\)=\s*([\d.Ee+-]+)', blk)])
    return q, lam


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifacts", required=True, help="artifacts_distill dir from A0 run")
    ap.add_argument("--model-csv", required=True, help="model_vertex.py output (q,w,eps,g)")
    ap.add_argument("--alat", type=float, required=True, help="bcc alat (bohr)")
    ap.add_argument("--kf", type=float, required=True, help="conduction k_F (1/bohr)")
    ap.add_argument("--mass", type=float, required=True, help="ion mass (Ry units, dyn header)")
    ap.add_argument("--sigma", default="0.025")
    ap.add_argument("--lattice", default="bcc", choices=["bcc", "fcc"])
    a = ap.parse_args()

    tpa = 2 * np.pi / a.alat
    model = np.loadtxt(a.model_csv, skiprows=1)
    qm, gmod = model[:, 0], model[:, 3]

    def g2(Q):
        return np.interp(Q, qm, gmod, right=gmod[-1]) ** 2

    # reciprocal lattice in 2pi/a units: bcc crystal -> fcc recip; fcc crystal -> bcc recip
    if a.lattice == "bcc":
        Gs = np.unique(np.array([[n + m, m + l, n + l] for n in range(-3, 4)
                                 for m in range(-3, 4) for l in range(-3, 4)]), axis=0)
    elif a.lattice == "fcc":
        Gs = np.unique(np.array([[-n + m + l, n - m + l, n + m - l] for n in range(-3, 4)
                                 for m in range(-3, 4) for l in range(-3, 4)]), axis=0)
    else:
        raise SystemExit(f"unsupported lattice {a.lattice}")

    data = []
    for f in sorted(glob.glob(f'{a.artifacts}/matdyn[0-9]*')):
        if '.elph.' in f:
            continue
        n = re.search(r'matdyn(\d+)$', f).group(1)
        if n == '0':
            continue
        q, D = parse_dyn_first_q(f)
        qe, lam = parse_elph(f'{a.artifacts}/matdyn{n}.elph.{n}', a.sigma)
        if np.linalg.norm(q) < 1e-8:
            continue
        w2, ev = np.linalg.eigh(D / a.mass)
        om = np.sqrt(np.abs(w2))
        lam_mod = []
        for nu in range(3):
            s = 0.0
            for G in Gs:
                Q = (q + G) * tpa
                Qn = np.linalg.norm(Q)
                if Qn < 1e-9 or Qn > 2 * a.kf:
                    continue
                s += g2(Qn) * (Q @ np.real(ev[:, nu])) ** 2 / Qn
            lam_mod.append(s / om[nu] ** 2)
        data.append((np.linalg.norm(q) * tpa / (2 * a.kf), lam, np.array(lam_mod)))

    q0 = min(data, key=lambda d: d[0])
    iL = int(np.argmax(q0[1]))
    C = q0[1][iL] / q0[2][iL]
    print(f"C calibrated at |q|/2kF={q0[0]:.3f} mode {iL}\n")
    print(f"{'|q|/2kF':>7s}  {'lam_DFPT':>26s}  {'lam_A4u':>26s}  {'ratio':>5s}")
    totD = totM = 0.0
    for x, lam, lm in sorted(data, key=lambda d: d[0]):
        lm = lm * C
        print(f"{x:7.3f}  {str(np.round(lam,3)):>26s}  {str(np.round(lm,3)):>26s}"
              f"  {lm.sum()/lam.sum():5.2f}")
        totD += lam.sum()
        totM += lm.sum()
    print(f"\nunweighted totals: DFPT {totD:.3f}  A4u {totM:.3f}  ratio {totM/totD:.2f}")


if __name__ == "__main__":
    main()
