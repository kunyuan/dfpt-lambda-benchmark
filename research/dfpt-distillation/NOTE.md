# When is DFPT overkill for λ? A transverse-coupling boundary map

**Companion note to** *Superconductivity in Electron Liquids: Precision Many-Body
Treatment of Coulomb Interaction* (Cai, Wang, Zhang, Zhang, Millis, Svistunov,
Prokof'ev, Chen; arXiv:2512.19382).

## Question

That paper proves, for the uniform electron gas (UEG), that the exact many-body
electron–phonon vertex collapses onto the Kohn–Sham screened form,

  z^e (v_q/ε_q) Γ₃^e  ≈  v_q / [1 − (v_q + f_xc) χ₀(q)],        (Eq. 33–35)

exact at q→0 by the compressibility sum rule and numerically accurate to |q| ≤ 2k_F
up to r_s = 5 (their Fig. 8). The vertex is then a scalar function of |q| alone. This
raises a practical question the present note answers empirically: **for which real
materials is the full DFPT machinery therefore unnecessary** — i.e. when does the
scalar UEG-screened vertex reproduce DFPT's λ, and when does it structurally fail?

## Method (ablation against DFPT)

We compute λ in full DFPT (Quantum ESPRESSO 7.1, `electron_phonon='simple'`, Allen
formula, σ = 0.025 Ry, q-grids 4³–6³, k = 24³ checked to 32³) as the reference (A0),
and compare against a frozen analytic vertex (A4u) built from the *same* pseudopotential
and the *same* DFPT phonons — only the vertex is swapped:

  λ_qν(A4u) = C Σ_G |w(|q+G|)/ε(|q+G|)|² ((q+G)·e_qν)² / (|q+G| ω_qν²),  |q+G| ≤ 2k_F

with w the bare local form factor, ε = 1 − (v+f_xc)χ₀ the UEG-screened dielectric
(Lindhard χ₀, PZ-ALDA f_xc — exactly Eq. 33), one global constant C, and the Umklapp
lattice sum mandatory (the G=0 scalar form is kinematically incomplete at every finite
q in a crystal). No fitted force fields, no per-material tuning.

The robust, model-free diagnostic is the **transverse share** of λ: the fraction
carried by phonon modes with e_qν ⟂ q, obtained by eigenvector projection of the DFPT
dynamical matrix. Longitudinal coupling (ion ∥ q) couples to density and is captured by
any scalar theory; transverse coupling (ion ⟂ q) couples only to the angular structure
of the Fermi-surface states and has **no scalar-UEG analog**.

## Result: the controlling axis is orbital character, not s/p/d block

| material | λ (DFPT) | ω_log (K) | FS character | transverse share | A4u vs DFPT |
|---|---:|---:|---|---:|---|
| Na (expt vol) | 0.32 | 113 | 3s, free-electron | **0.2 %** | **ratio ≈ 0.9** (10 %) |
| Al | 0.50 | 270 | 3s/p, free-electron | low | over ×1.6 (FS geometry) |
| P, 70 GPa | 0.70 | 440 | **3p** | **65 %** | under ×0.4 |
| S, 280 GPa | 0.59 | 549 | **3p** | **71 %** | — |
| V | 1.06 | 240 | **3d** | **63 %** | (orbital channel) |
| Mo | 0.56 | 262 | **4d** | **71 %** | — |
| Ta | 0.90 | 155 | **5d** | **63 %** | — |
| NbC | 0.84 | 310 | Nb-4d/C-2p covalent | acoustic-Kohn dominated | (needs q6) |

The transverse share separates the materials cleanly into **two classes that do not
follow the s/p/d periodic-table block**:

1. **s-character (free-electron) Fermi surfaces** — Na, Al. Transverse coupling is
   negligible (Na 0.2 %); λ is a density-response quantity. The UEG-screened scalar
   vertex reproduces DFPT to ~10 % (Na), the cancellation theorem holding on the lattice.
   The only residual is Fermi-surface *geometry* (Al's multivalent FS, carved at Bragg
   planes, is over-counted by the free sphere — a ~60 % effect localized in small-q
   transverse Umklapp, fixable with a real-FS nesting factor, not a vertex correction).

2. **orbital-character (p or d) Fermi surfaces** — P, S, V, Mo, Ta. Transverse coupling
   carries **~2/3 of λ at every q, including the smallest** (P 77 % at 0.15·2k_F, where
   Na shows 0.2 %). p and d states carry angular structure, so the deformation potential
   couples to shear; the scalar form factor w(|q|) misses this entirely and A4u
   under-counts P by 2.5×. Crucially this is *not* the sp-vs-d distinction: the
   high-pressure p-block elements P and S sit firmly with the transition metals.

## Implications

- **DFPT is overkill only for the free-electron corner.** For s-character metals
  (alkalis, simple sp) the UEG-screened analytic vertex — a seconds-scale calculation —
  reproduces DFPT, vindicating Eq. 33 as a lattice statement and confirming the 1970s
  screened-pseudopotential approach for exactly this class.

- **For orbital-character metals DFPT is minimal, not excessive.** The transverse/
  orbital channel that carries two-thirds of λ has no representation in any scalar
  (UEG, screened-pseudopotential) theory. A minimal sufficient theory there must carry
  an orbital/nonlocal vertex channel (e.g. a modernized Gaspari–Gyorffy d-phase-shift,
  or Bloch-projected matrix elements). This is a property of the band character at E_F,
  independent of electron correlation strength.

- **The field's important phonon superconductors are all orbital-character.**
  High-pressure hydrides, high-pressure p-block elements, transition-metal compounds —
  every workhorse system is in class 2. The scalar UEG simplification of Eq. 33, while
  rigorously correct, applies in practice only to the alkali/free-electron corner.

- This also dissolves the apparent paradox of V (strong on-site interaction, yet DFPT
  λ accurate): orbital character and correlation strength are independent axes. V is
  strongly orbital (so DFPT's full matrix elements are required — they supply 63 % of λ)
  but weakly correlated (so DFPT's single-particle framework suffices). The two are not
  the same thing.

## A methodological by-product (relevant to Table II)

The Na λ tension — point-contact experiment 0.10, this work's expt-volume LDA 0.32, the
paper's EPW-PBE 0.20 — resolves into a **pure volume effect**: at the LDA-relaxed volume
(13 % below experiment) our λ drops to 0.200, exactly matching the paper's EPW value.
k-mesh (k24→k32: 0.293→0.292) and vertex (theorem-protected) are eliminated. The
residual 0.20-vs-0.10 against experiment is genuine physics, not a calculation artifact —
relevant to the paper's Na quantum-critical prediction.

## Status / caveats

First-pass q-grids (q4 for several; NbC's acoustic Kohn anomaly needs q6, known from
prior validation). "Orbital character" here is read at the LDA/PBE level; correlation
(the V point) is a separate axis not probed here. A4u carries one global constant C and
a sharp 2k_F cutoff (a smeared double-delta refinement is queued, expected to remove the
monotone large-q drift and the soft-phonon node sensitivity seen in K). Pb's spin-orbit
(scalar λ=0.92 here; the Ward identity is spin-orbit-blind, so the cancellation is
predicted to survive — to be verified with a fully-relativistic pair). Full ledger and
per-q mode tables in `ledger.csv`; analysis in `scripts/a4u_vs_a0_na.py`.
