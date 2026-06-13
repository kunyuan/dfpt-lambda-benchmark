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

## Iteration 2 (2026-06-13): the screening is fine — the *local scalar vertex* is the weak link

Refining the model exposed a sharper boundary than the s-vs-orbital split above. Two
fixes were tested against the s-character class:

- **Smeared double-delta nesting** (replace the sharp θ(2k_F−|Q|) cutoff with the
  Gaussian-broadened static nesting at the DFPT σ): barely moved the ratios (K 9.0→7.3,
  Al unchanged). The hard cutoff was *not* the dominant error.
- **Node diagnosis**: K's blowup (×7) sits in the **longitudinal** channel — the one the
  cancellation theorem protects — so it cannot be a screening failure. The cause is the
  bare *local* form factor w(|q|): K's node sits at Q/2k_F = 0.64, mid-range where the
  Umklapp channels sample it, while Na's node is pushed to 0.99 (the integration edge).
  Near the node the local-only w is unreliable — and K's low-lying empty 3d makes its
  pseudopotential genuinely nonlocal, so a local w is the wrong object there. K's
  transverse share is only 5% (it *is* free-electron), confirming this is a
  vertex-representation failure, not the orbital gap.

**Sharpened conclusion.** The UEG screening relation (the theorem) is robust for *every*
material tested — it is never the source of disagreement. What fails is the assumption
that the *bare* electron–phonon vertex is a local scalar form factor w(|q|). That
assumption holds only for the most free-electron metal (Na, node at 2k_F). It breaks
three ways: (i) node sensitivity where the pseudopotential is nonlocal (K — even though
K is free-electron); (ii) partial orbital/transverse coupling already at small q (Al,
45% small-q transverse); (iii) full orbital deformation potential (P, S, V, Ta, Mo,
~2/3 transverse). The minimal sufficient theory of λ is therefore **UEG-screened
*full* (nonlocal, orbital) vertex matrix elements** — the simplification rigorously
eliminates the self-consistent screening (the Sternheimer iteration), but *not* the
bare-vertex matrix-element evaluation, which carries the nonlocal/orbital structure that
is most of the DFPT cost. Next iteration: add the pseudopotential's nonlocal
Kleinman–Bylander projectors to the model vertex (NL knob) — the targeted fix for K and
the entry point to the orbital channel for the p/d materials.

## Iteration 3 (2026-06-13): the orbital channel splits by orbital type — d is cheap, p is not

Staying on the orbital anchors (P, V) — simple metals are settled and not revisited —
a model-free rigid-ion test resolves *how much theory the orbital 2/3 actually needs*.
In the Gaspari–Gyorffy (GG) on-site picture λ_qν ≈ η/(M ω_qν²) with a q-independent
matrix element η = N(0)⟨I²⟩, so **η = λ_qν·ω_qν² should be constant across q and modes**
if the coupling is an on-site rigid-ion matrix element.

- **V (3d): η clusters, and η_L ≈ η_T.** L-modes CV = 0.42, T-modes CV = 0.38, comparable
  magnitudes (~1×10⁻⁶ Ry²). The d-deformation potential is a genuine **isotropic on-site
  matrix element** — d orbitals couple to shear as strongly as to compression, so the
  transverse coupling is intrinsic and large. **Minimal orbital model for d-metals = a
  single GG number N(0)⟨I²⟩, q-independent — cheap.** This vindicates Gaspari–Gyorffy
  (1971) for transition metals as the correct minimal theory of the orbital channel.

- **P (3p): η_L ≫ η_T, and η_T scatters.** L-modes η = 3.6–11 (semi-clustered, CV 0.37);
  T-modes η = 0.08–8.5 (CV 1.22). The p-orbital transverse *vertex* is weak and
  q-dependent — **the 65% transverse λ-share of P is a soft-transverse-phonon effect
  (small ω_T amplifies a small η_T), not a large transverse coupling.** An on-site
  rigid-ion η is insufficient; the p-block transverse vertex is irreducibly q-resolved.

**Net.** "How much DFPT does the orbital 2/3 need?" splits by orbital character:
d-metals reduce to one on-site integral (GG) — DFPT's orbital matrix elements *are*
compressible there; p-metals do not — their transverse vertex is weak but q-structured
and needs the full evaluation. The minimal sufficient theory is therefore
material-class-dependent: UEG-screened scalar vertex (Na corner) → +GG on-site η
(d-metals) → full q-resolved vertex (p-metals, compounds). Each tier is a measured,
not assumed, reduction.
