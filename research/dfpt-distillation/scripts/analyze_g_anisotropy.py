#!/usr/bin/env python3
"""A1 knob: k/band-anisotropy statistics of the DFPT e-ph matrix elements.

Input: EPW `prtgkk` dumps (|g(k,q,nu)| on explicit k,q grids, meV) from an A0 run.
For each (q, nu): FS-average gbar(q,nu) over k with Fermi-window weights, plus the
relative spread. Then recompute lambda with g -> gbar (same omega_q,nu — vertex knob
only) and report delta_lambda vs A0.

STATUS: stub — the prtgkk dump format must be pinned against a real epw.out from the
first Na A0 run before this is filled in. Self-check: on Na the spread should be ~0
(theorem zone).
"""
raise SystemExit("stub: pin EPW prtgkk format on the first Na A0 artifacts first")
