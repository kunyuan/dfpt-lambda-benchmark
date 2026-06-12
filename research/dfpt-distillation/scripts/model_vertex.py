#!/usr/bin/env python3
"""Model screened e-ph vertex — the analytic end (A4/A3) of the distillation ladder.

Computes, from an ONCV UPF file and the crystal's valence density:
  w(q)    : bare local-pseudopotential form factor (Ry), Coulomb tail explicit
  eps(q)  : 1 - (v_q + f_xc) chi0(q), chi0 = Lindhard(k_F, m_b)  [A4]
            (A3 hook: pass a tabulated real-band chi0 instead)
  g(q)    : w(q)/eps(q) — the model vertex to compare against dvscf matrix elements

Units: Rydberg atomic units (hbar = 2m_e = e^2/2 = 1; energies Ry, lengths bohr).
  v_q = 8*pi/q^2,  N(0) = k_F/(2*pi^2) per volume (both spins),  E = k^2.

Self-check (run as __main__): the screened acoustic limit g(q->0) must approach
-(2/3) E_F (compressibility sum rule); deviations beyond a few % indicate a parsing
or unit bug, not physics.

Status: A4 path implemented; A3 (real-band chi0) and A2 (G-resolved) are hooks.
Validate w(q) against published form factors (e.g. Na: Cohen-Heine tables) before
first production use.
"""
import argparse
import re
import numpy as np

RY_V_Q_PREF = 8.0 * np.pi  # v_q = 8*pi/q^2 in Ry-au


def parse_upf_local(upf_path):
    """Return (r, vloc_Ry, z_valence) from a UPF v2 file (SG15 ONCV layout)."""
    text = open(upf_path, errors="ignore").read()
    z = float(re.search(r'z_valence="\s*([0-9.Ee+-]+)"', text).group(1))

    def block(tag):
        m = re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", text, re.S)
        return np.fromstring(m.group(1), sep=" ")

    r = block("PP_R")
    vloc = block("PP_LOCAL")  # Ry, includes the -2*Z/r tail at large r
    n = min(len(r), len(vloc))
    return r[:n], vloc[:n], z


def form_factor(q, r, vloc, z, omega):
    """w(q) (Ry): short-range transform + analytic Coulomb tail, per cell volume omega."""
    dv = vloc + 2.0 * z / np.where(r > 1e-12, r, 1e-12)  # short-ranged remainder
    dv[r < 1e-12] = dv[np.argmax(r >= 1e-12)]
    qr = np.outer(q, r)
    j0 = np.where(qr > 1e-8, np.sin(qr) / np.where(qr > 1e-8, qr, 1), 1.0)
    short = (4.0 * np.pi / omega) * np.trapz(r**2 * dv * j0, r, axis=1)
    coul = -RY_V_Q_PREF * z / (omega * q**2)
    return short + coul


def lindhard_chi0(q, kf, mb=1.0):
    """Static Lindhard chi0(q) (Ry-au, both spins), band-mass rescaled by mb."""
    x = q / (2.0 * kf)
    with np.errstate(divide="ignore", invalid="ignore"):
        F = 0.5 + (1 - x**2) / (4 * x) * np.log(np.abs((1 + x) / (1 - x)))
    F = np.where(np.abs(x - 1) < 1e-10, 0.5, F)
    return -mb * (kf / (2 * np.pi**2)) * F


def eps_xc_pz(rs):
    """PZ81 epsilon_xc(rs) in Ry (exchange + correlation, unpolarized)."""
    ex = -0.9163305866 / rs
    if rs >= 1.0:
        ec = -0.2846 / (1 + 1.0529 * np.sqrt(rs) + 0.3334 * rs)  # 2*gamma in Ry
    else:
        ec = 2 * (0.0311 * np.log(rs) - 0.048 + 0.0020 * rs * np.log(rs) - 0.0116 * rs)
    return ex + ec


def fxc_alda(n):
    """ALDA kernel f_xc = d^2(n*eps_xc)/dn^2 (Ry*bohr^3), numerical second derivative."""
    def e_density(nn):
        rs = (3.0 / (4 * np.pi * nn)) ** (1.0 / 3.0)
        return nn * eps_xc_pz(rs)
    h = 1e-4 * n
    return (e_density(n + h) - 2 * e_density(n) + e_density(n - h)) / h**2


def model_vertex(q, upf_path, omega, n_valence_per_cell, mb=1.0, use_fxc=True,
                 chi0_table=None):
    """Return dict with w, chi0, eps, g on grid q. chi0_table=(q_t, chi0_t) → A3 path."""
    r, vloc, z = parse_upf_local(upf_path)
    n = n_valence_per_cell / omega
    kf = (3 * np.pi**2 * n) ** (1.0 / 3.0)
    w = form_factor(q, r, vloc, z, omega)
    if chi0_table is not None:
        chi0 = np.interp(q, chi0_table[0], chi0_table[1])  # A3: real-band chi0
    else:
        chi0 = lindhard_chi0(q, kf, mb)                    # A4: UEG mapping
    vq = RY_V_Q_PREF / q**2
    fxc = fxc_alda(n) if use_fxc else 0.0
    eps = 1.0 - (vq + fxc) * chi0
    return {"q": q, "w": w, "chi0": chi0, "eps": eps, "g": w / eps,
            "kf": kf, "ef": kf**2, "z": z, "fxc": fxc}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--upf", required=True)
    ap.add_argument("--omega", type=float, required=True, help="cell volume (bohr^3)")
    ap.add_argument("--nval", type=float, required=True, help="valence e- per cell")
    ap.add_argument("--mb", type=float, default=1.0)
    ap.add_argument("--out", default=None, help="write q,w,eps,g CSV")
    a = ap.parse_args()
    kf = (3 * np.pi**2 * a.nval / a.omega) ** (1.0 / 3.0)
    q = np.linspace(0.02 * kf, 2.5 * kf, 400)
    res = model_vertex(q, a.upf, a.omega, a.nval, a.mb)
    g0 = res["g"][0]
    target = -(2.0 / 3.0) * res["ef"]
    print(f"k_F = {res['kf']:.4f} 1/bohr   E_F = {res['ef']:.4f} Ry   "
          f"f_xc = {res['fxc']:.4f} Ry*bohr^3")
    print(f"acoustic-limit check: g(q->0) = {g0:.4f} Ry  vs  -(2/3)E_F = {target:.4f} Ry"
          f"   ({abs(g0/target-1):.1%} off)")
    print(f"g(2k_F) = {np.interp(2*res['kf'], q, res['g']):.4f} Ry")
    if a.out:
        np.savetxt(a.out, np.column_stack([q, res["w"], res["eps"], res["g"]]),
                   header="q_bohr^-1 w_Ry eps g_Ry", comments="")
        print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
