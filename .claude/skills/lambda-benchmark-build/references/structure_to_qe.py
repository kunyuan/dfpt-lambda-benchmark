#!/usr/bin/env python3
"""pymatgen Structure -> Quantum ESPRESSO pw.x input with a PROPER ibrav (never 0).

Why: ph.x SIGSEGVs on multi-atom cells written with ibrav=0. This emits ibrav + celldm
so phonon/el-ph runs are stable.

Covered safely: primitive Bravais (cubic-P, tetragonal-P, orthorhombic-P, hexagonal,
trigonal) and single-atom cubic F/I (elements). Centered MULTI-atom cells (F/I/C with
>1 site) print a WARNING — QE expects atoms in the PRIMITIVE basis there; verify the
coordinates (high-symmetry special positions are usually fine).

Usage:
    from structure_to_qe import qe_system_block
    text = qe_system_block(struct, species_pseudo={"Mg":"Mg.upf","B":"B.upf"},
                           masses={"Mg":24.305,"B":10.811}, ecutwfc=80)
"""
import math
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

ANG2BOHR = 1.8897259886

# (crystal_system, centering letter) -> ibrav
_IBRAV = {
    ("cubic", "P"): 1, ("cubic", "F"): 2, ("cubic", "I"): 3,
    ("hexagonal", "P"): 4, ("trigonal", "P"): 4, ("trigonal", "R"): 5,
    ("rhombohedral", "R"): 5,
    ("tetragonal", "P"): 6, ("tetragonal", "I"): 7,
    ("orthorhombic", "P"): 8, ("orthorhombic", "C"): 9,
    ("orthorhombic", "A"): 9, ("orthorhombic", "F"): 10, ("orthorhombic", "I"): 11,
    ("monoclinic", "P"): 12, ("monoclinic", "C"): 13,
    ("triclinic", "P"): 14,
}


def _centering(sg_symbol):
    return sg_symbol.strip()[0].upper()  # P/F/I/C/A/R


def qe_system_block(struct, species_pseudo, masses, ecutwfc=80.0, ecutrho=None,
                    degauss=0.02, nspin=1, smearing="methfessel-paxton"):
    sga = SpacegroupAnalyzer(struct)
    sys_name = sga.get_crystal_system()
    sg_sym = sga.get_space_group_symbol()
    cent = _centering(sg_sym)
    ibrav = _IBRAV.get((sys_name, cent))
    if ibrav is None:
        raise ValueError(f"no ibrav for {sys_name}/{cent} (sg {sg_sym}) — handle manually")

    # use conventional cell for lattice params; primitive for centered atoms
    conv = sga.get_conventional_standard_structure()
    a, b, c = conv.lattice.abc
    al, be, ga = conv.lattice.angles
    cell = conv if ibrav in (1, 4, 5, 6, 8, 12, 14) else sga.get_primitive_standard_structure()
    warn = ""
    if ibrav in (2, 3, 7, 9, 10, 11, 13) and len(cell) > 1:
        warn = f"# WARNING: centered lattice (ibrav={ibrav}), >1 atom — verify primitive-basis coords\n"

    celldm = {1: round(a * ANG2BOHR, 5)}
    if ibrav in (4, 6, 7):                      # need c/a
        celldm[3] = round(c / a, 5)
    elif ibrav in (8, 9, 10, 11):               # need b/a, c/a
        celldm[2] = round(b / a, 5); celldm[3] = round(c / a, 5)
    elif ibrav == 5:                            # rhombohedral: celldm(4)=cos(alpha)
        celldm[4] = round(math.cos(math.radians(al)), 5)
    elif ibrav in (12, 13):                     # monoclinic
        celldm[2] = round(b / a, 5); celldm[3] = round(c / a, 5)
        celldm[4] = round(math.cos(math.radians(ga)), 5)
    elif ibrav == 14:                           # triclinic
        celldm[2] = round(b / a, 5); celldm[3] = round(c / a, 5)
        celldm[4] = round(math.cos(math.radians(al)), 5)
        celldm[5] = round(math.cos(math.radians(be)), 5)
        celldm[6] = round(math.cos(math.radians(ga)), 5)

    els = sorted({str(s.symbol) for s in cell.species})
    cdm = ", ".join(f"celldm({k})={v}" for k, v in sorted(celldm.items()))
    if ecutrho is None:
        ecutrho = 4 * ecutwfc

    out = warn
    out += ("&control\n  calculation='scf', prefix='x', pseudo_dir='./pseudo', outdir='./out'\n/\n"
            f"&system\n  ibrav={ibrav}, {cdm}, nat={len(cell)}, ntyp={len(els)},\n"
            f"  ecutwfc={ecutwfc}, ecutrho={ecutrho},\n"
            f"  occupations='smearing', smearing='{smearing}', degauss={degauss}, nspin={nspin}\n/\n"
            "&electrons\n  conv_thr=1.0d-10, mixing_beta=0.7\n/\n"
            "ATOMIC_SPECIES\n")
    for e in els:
        out += f"  {e} {masses[e]} {species_pseudo[e]}\n"
    out += "ATOMIC_POSITIONS crystal\n"
    for site in cell:
        f = site.frac_coords
        out += f"  {site.specie.symbol} {f[0]:.6f} {f[1]:.6f} {f[2]:.6f}\n"
    # NB: append your own K_POINTS line; for el-ph use a dense grid (e.g. 24 24 24 0 0 0)
    return out


if __name__ == "__main__":
    import sys, warnings; warnings.filterwarnings("ignore")
    from pymatgen.core import Structure
    s = Structure.from_file(sys.argv[1])  # e.g. a .cif
    print(qe_system_block(s, {e: f"{e}.upf" for e in {x.symbol for x in s.species}},
                          {x.symbol: float(x.atomic_mass) for x in s.species}))
