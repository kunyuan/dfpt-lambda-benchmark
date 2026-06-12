# DFPT distillation: a knob-by-knob price list for λ

**Question.** Which elements of the DFPT machinery are necessary for the electron-phonon
coupling λ, per material class — and which can be removed at measured, negligible cost?

**Anchor.** Cai et al., arXiv:2512.19382 prove (UEG, VDiagMC) that the exact many-body
e-ph vertex collapses onto the Kohn-Sham screened form:
z^e (v_q/ε_q) Γ₃^e ≈ v_q / (1 − (v_q + f_xc) χ₀(q)) — exact at q→0 (Ward identity /
compressibility sum rule; ALDA f_xc is exact for the UEG compressibility), numerically
valid for |q| ≤ 2k_F up to r_s = 5 (their Fig. 8), with m*/m ≈ 1 protecting the DOS slot.
DFPT's information content beyond this analytic skeleton is therefore an enumerable list
of lattice effects. This project prices each one by **top-down ablation**: start from a
converged DFPT calculation and switch off one element at a time. Top-down (not
bottom-up reconstruction) so every Δλ has a unique attribution — same code, same
pseudopotential, same grids, one knob per step.

## The ablation ladder

| knob | what is switched off | replaced by | prices |
|---|---|---|---|
| **A0** | — (full DFPT, reference) | — | — |
| **A1** | k/band dependence of g | FS-average ḡ(q,ν) | matrix-element anisotropy / orbital selectivity |
| **A2** | self-consistent local fields | one-shot diagonal screening δV_ion(q+G)/ε(q+G) | off-diagonal ε_GG′ |
| **A3** | G-shell anisotropy of ε | scalar ε(\|q\|) = 1 − (v+f_xc)χ₀(\|q\|), χ₀ from real bands (sum over states, no SCF of the response) | reciprocal-lattice structure of screening |
| **A4** | real-band χ₀ | Lindhard(k_F, m_b) — the UEG mapping of the μ* protocol | FS geometry in screening (nesting, true 2k_F Kohn structure) |

Endpoint A4 = Eq. (33) of the paper. **A0→A4 lossless for a material = the lattice
version of the cancellation theorem holds there.**

Orthogonal knobs, priced independently:

- **P** (phonon slot): DFPT ω_qν, e_qν → second-order perturbation lattice dynamics from
  the SAME w(q)/ε(q) (Ewald + band-structure energy). No MLIP anywhere — fitted force
  fields would entangle attribution and smuggle DFT back in.
- **F** (xc kernel): ALDA f_xc → 0 (pure RPA). Prices the kernel.
- **NL** (pseudopotential nonlocality): full separable projectors → local part only.
  Must be priced separately from A1, else d-metal attribution is confounded.

Ablation algebra: report the telescoping budget λ(A0)→λ(A1)→…→λ(A4) per material plus
P/F/NL one-off deltas. The result is a **materials × knobs price matrix**; the minimal
sufficient theory per class = A0 minus all knobs measured free, with *measured* (not
assumed) error.

## Materials and phases (= L4 train set, shared HPC artifacts)

| phase | materials | role |
|---|---|---|
| 1 | Na (then K) | theorem zone: expect A0→A4 lossless at the few-% level → validates the whole pipeline |
| 2 | Al, Sn, Pb(±SOC) | multivalent sp: Umklapp enters; Pb probes whether SOC disturbs the cancellation (Ward identity is spin-orbit-blind — verify) |
| 3 | V, Ta, Mo (+NL knob) | d at E_F: expected bleed order A1/NL first, then A2 — the bleed order is itself the d-physics result |
| 4 | Nb3Sn, V3Si, NbC, NbN, MgB2 | compounds: optical modes, covalent σ-bond coupling (MgB2 expected A1 ceiling) |
| 5 | synthesis | price matrix, per-class minimal estimators, failure-mode anatomy |

## Implementation: mostly post-processing of artifacts we already produce

The L4-train LBG campaign (QE 7.1 + ph.x) generates per run: `dvscf` (self-consistent
δV_KS per q), phonon ω/eigenvectors, and (with EPW, `prtgkk`) g(k,q,ν) on explicit
grids. The ladder is then:

- **A1**: statistics over EPW g-dumps — FS-average vs spread; λ recomputed with ḡ.
- **A2–A4**: generate the bare perturbation δV_ion analytically from the pseudopotential,
  screen with the model ε of each rung (`scripts/model_vertex.py`), compare matrix
  elements against dvscf, recompute λ.
- **P**: `scripts/screened_phonons.py` (Ewald + χ-weighted band-structure energy) vs ph.x.

Protocol deltas vs the standard qe-eph-lambda recipe are in `protocol.md` (LDA pseudos
for the distillation track — the theorem anchors ALDA f_xc; artifact retention list;
1-atom cells keep dvscf small). Run ledger: `ledger.csv`. Material/knob plan:
`manifest.csv`.

## Expected deliverable

A standalone methods paper — "the minimal sufficient theory of λ": (i) numerical
validity map of the lattice cancellation theorem across material classes; (ii) a
λ estimator 10⁴–10⁶× cheaper than DFPT with DFPT-grade accuracy in its validated
domain (sp + multivalent metals), usable for high-throughput screening; (iii) anatomy
of where and *in which order* the simplifications fail in d/covalent systems — i.e.,
what a lattice generalization of the theorem must add. Companion to arXiv:2512.19382:
that paper proves why DFPT is right; this one measures which parts of it are needed.

## Known tensions to resolve on the way

- Na: EPW λ = 0.2 (arXiv:2512.19382 Table II) vs 1970s screened-pseudopotential 0.13–0.15
  vs point-contact experiment 0.10±0.03. Factor-2 spread on the *easiest* material —
  either a small-λ convergence/smearing artifact in DFPT or an underestimated Umklapp
  contribution. Phase 1 must settle this as its first output.
- PBE vs LDA kernel: L4-train uses PBE (benchmark protocol); the distillation track runs
  LDA. Na is cheap — run both, price the kernel difference alongside the F knob.

## Phase-1 result (2026-06-13, Na): the ladder redesigned by data

First A0↔analytic comparison (Na, LDA, q6, mode-resolved λ_qν from elph files,
DFPT phonons held fixed = vertex-only ablation):

1. **G=0 scalar model is invalid at any finite q** — not approximately, structurally:
   bcc-monovalent 2k_F (0.961/bohr) exceeds half the shortest G (1.096/bohr), so
   Umklapp channels are kinematically open on the Fermi sphere at every grid q.
   Transverse modes couple *only* via Umklapp; measured T-share goes 0.2% (high-sym q,
   where min|q+G| lands on the form-factor node) → 67% (mixed q, min|q+G| in the
   form-factor's strong mid-range). The lattice sum over G is mandatory at every rung.
2. **A4u (UEG screening + Umklapp lattice sum + spherical-FS nesting), one constant
   calibrated at the smallest-q L point, reproduces all 15 q × 3 mode λ_qν**:
   ratios 1.00–0.95 for |q| ≤ 0.5·2k_F, drifting smoothly to 0.81–0.87 at the zone
   boundary; unweighted total ratio 0.89. The lattice cancellation theorem holds for
   Na at the ~10% level; the residual is monotone in q with the right sign for the
   sharp θ(2k_F−|q+G|) cutoff vs the smeared double-delta (next refinement).
3. Corollary for the Na λ tension (exp 0.10 / 1970s 0.13 / EPW-PBE 0.2 / ours 0.32):
   the vertex is theorem-protected — remaining suspects are the *phonon/volume* slot
   (LDA at experimental volume → soft phonons → 1/ω² inflation) and k-resolution of
   the double-delta (k32/k40 jobs in flight).

Analysis: `scripts/a4u_vs_a0_na.py` on the 22867111 artifacts.

## Phase-1b (Na relax + Al): the anti-overfit test bites, as designed

- Na LDA equilibrium: a0 = 7.736 bohr (4.09 Å) vs expt 4.29 Å (−13% volume).
  Relaxed-volume q6 in flight (22867472) — the volume verdict for the λ tension.
- **Al fails the frozen A4u recipe in a localized, interpretable way**: total ratio
  1.62, but large-q mode ratios ≈ 0.9–1.1 (screened vertex magnitude still correct)
  while small-q transverse Umklapp channels overshoot ×2–7. Mechanism: Al's
  2k_F (1.85/bohr) ≫ shortest G (1.42/bohr), so small-q Umklapp scattering crosses
  Bragg planes — exactly where the real Al FS is gapped (2nd/3rd-zone carving); the
  free-sphere phase space overcounts those channels. **First non-trivial price-list
  entry: the spherical-FS approximation costs ~10% (monovalent Na) vs ~60%
  (multivalent Al), concentrated in transverse Umklapp.** Next rung: real-FS
  double-delta nesting (A3-geometry), not a vertex fix.
