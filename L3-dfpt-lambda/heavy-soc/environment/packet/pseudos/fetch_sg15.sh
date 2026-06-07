#!/usr/bin/env bash
# Download SG15 ONCV norm-conserving PBE pseudopotentials (free).
set -e
B=http://www.quantum-simulation.org/potentials/sg15_oncv/upf
mkdir -p pseudo
for el in Al As B Ba Be C Ca Cd Co Cr Cu F Fe Ga Ge H Hf Hg In Ir La Li Lu Mg Mo N Na Nb Ni O Os P Pt Re Rh Ru S Sb Sc Si Sn Sr Ta Ti V Y Zn Zr; do
  for v in 1.2 1.1 1.0; do
    curl -fsSL "$B/${el}_ONCV_PBE-$v.upf" -o pseudo/${el}_ONCV_PBE-1.2.upf && head -c4 pseudo/${el}_ONCV_PBE-1.2.upf|grep -q UPF && { echo "$el v$v"; break; }; done
done
