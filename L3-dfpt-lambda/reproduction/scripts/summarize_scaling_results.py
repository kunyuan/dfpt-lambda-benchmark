#!/usr/bin/env python3
"""Summarize generated QE scaling runs from lambda.dat files."""

from __future__ import annotations

import argparse
import csv
import math
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REPRO = ROOT / "L3-dfpt-lambda" / "reproduction"
INPUTS = REPRO / "inputs"
RESULTS = REPRO / "results"


def parse_lambda_dat(path: Path, sigma: float) -> dict[str, float] | None:
    if not path.exists():
        return None
    for line in path.read_text().splitlines():
        parts = line.split()
        if len(parts) >= 4:
            try:
                s = float(parts[0])
                lam = float(parts[1])
                omega = float(parts[2])
                share = float(parts[3])
            except ValueError:
                continue
            if math.isclose(s, sigma, abs_tol=1e-9):
                return {
                    "sigma_Ry": s,
                    "lambda": lam,
                    "omega_log_K": omega,
                    "top_q_share_pct": share,
                }
    return None


def q_from_dir(path: Path) -> int:
    m = re.fullmatch(r"q(\d+)", path.name)
    if not m:
        raise ValueError(f"cannot parse q-grid from {path}")
    return int(m.group(1))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", default=str(INPUTS / "scaling_runs"))
    parser.add_argument("--manifest", default=str(INPUTS / "selected_cases.csv"))
    parser.add_argument("--out", default=str(RESULTS / "scaling_summary.csv"))
    parser.add_argument("--sigma", type=float, default=0.025)
    args = parser.parse_args()

    manifest = {}
    with open(args.manifest, newline="") as f:
        for row in csv.DictReader(f):
            manifest[row["case_id"]] = row

    rows = []
    grouped = defaultdict(list)
    for qdir in sorted(Path(args.runs).glob("*/q*")):
        case_id = qdir.parent.name
        q = q_from_dir(qdir)
        parsed = parse_lambda_dat(qdir / "lambda.dat", args.sigma)
        meta = manifest.get(case_id, {})
        row = {
            "case_id": case_id,
            "tier": meta.get("tier", ""),
            "material": meta.get("material", ""),
            "condition": meta.get("condition", ""),
            "qgrid": q,
            "lambda_ref": meta.get("lambda_ref", ""),
            "omega_log_ref_K": meta.get("omega_log_ref_K", ""),
            "status": "missing" if parsed is None else "ok",
            "lambda": "",
            "lambda_relerr_pct": "",
            "omega_log_K": "",
            "omega_relerr_pct": "",
            "top_q_share_pct": "",
        }
        if parsed is not None:
            lam = parsed["lambda"]
            omega = parsed["omega_log_K"]
            row["lambda"] = f"{lam:.6g}"
            row["omega_log_K"] = f"{omega:.6g}"
            row["top_q_share_pct"] = f"{parsed['top_q_share_pct']:.3g}"
            try:
                ref = float(meta.get("lambda_ref", ""))
                row["lambda_relerr_pct"] = f"{100 * (lam - ref) / ref:.3g}"
            except ValueError:
                pass
            try:
                oref = float(meta.get("omega_log_ref_K", ""))
                row["omega_relerr_pct"] = f"{100 * (omega - oref) / oref:.3g}"
            except ValueError:
                pass
            grouped[case_id].append((q, lam, omega))
        rows.append(row)

    for case_id, vals in grouped.items():
        vals.sort()
        if len(vals) < 2:
            continue
        q_prev, lam_prev, omega_prev = vals[-2]
        q_last, lam_last, omega_last = vals[-1]
        for row in rows:
            if row["case_id"] == case_id and row["qgrid"] == q_last:
                row["delta_lambda_vs_prev_q_pct"] = f"{100 * (lam_last - lam_prev) / lam_prev:.3g}"
                if omega_prev:
                    row["delta_omega_vs_prev_q_pct"] = f"{100 * (omega_last - omega_prev) / omega_prev:.3g}"

    fieldnames = [
        "case_id", "tier", "material", "condition", "qgrid", "status",
        "lambda_ref", "lambda", "lambda_relerr_pct", "delta_lambda_vs_prev_q_pct",
        "omega_log_ref_K", "omega_log_K", "omega_relerr_pct", "delta_omega_vs_prev_q_pct",
        "top_q_share_pct",
    ]
    with open(args.out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
