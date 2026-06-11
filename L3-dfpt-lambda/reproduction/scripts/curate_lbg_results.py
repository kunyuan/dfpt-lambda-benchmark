#!/usr/bin/env python3
"""Curate raw LBG DFPT lambda rows into a benchmark-facing result table."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REPRO = ROOT / "L3-dfpt-lambda" / "reproduction"
JOBS = REPRO / "jobs"
RESULTS = REPRO / "results"
REFERENCE = ROOT / "data" / "lambda_reference.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def first_float(row: dict[str, str], key: str) -> float | None:
    try:
        value = row.get(key, "")
        if value == "":
            return None
        return float(value)
    except ValueError:
        return None


def fmt_pct(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:.2f}"


def collect_job_meta() -> dict[tuple[str, str, str], dict[str, str]]:
    meta: dict[tuple[str, str, str], dict[str, str]] = {}
    fallback: dict[tuple[str, str], dict[str, str]] = {}
    for path in sorted(JOBS.glob("lbg_jobs_*.csv")):
        for row in read_csv(path):
            case_id = row.get("case_id", "")
            qgrid = row.get("qgrid", "")
            job_id = row.get("job_id", "")
            if not case_id or not qgrid:
                continue
            selected = {
                "track": row.get("track", ""),
                "material": row.get("material", ""),
                "condition": row.get("condition", ""),
                "kgrid": row.get("kgrid", ""),
                "sku": row.get("sku", ""),
                "np": row.get("np", ""),
                "nk": row.get("nk", ""),
                "job_name": row.get("job_name", ""),
                "note": row.get("note", ""),
            }
            if job_id:
                meta[(case_id, qgrid, job_id)] = selected
            fallback[(case_id, qgrid)] = selected
    for key, value in fallback.items():
        meta.setdefault((key[0], key[1], ""), value)
    return meta


def collect_reference() -> dict[str, dict[str, str]]:
    return {row["case_id"]: row for row in read_csv(REFERENCE)}


def verdict(row: dict[str, str]) -> str:
    if row.get("status") != "Finished":
        return "failed_or_incomplete"
    lam = first_float(row, "lambda")
    if lam is None:
        return "finished_missing_lambda_artifact"
    lambda_err = first_float(row, "lambda_relerr_pct")
    omega_err = first_float(row, "omega_relerr_pct")
    top_q = first_float(row, "top_q_share_pct")
    if top_q is not None and top_q > 25:
        return "smoke_unconverged"
    lambda_close = lambda_err is not None and abs(lambda_err) <= 15
    omega_close = omega_err is None or abs(omega_err) <= 15
    if lambda_close and omega_close:
        return "reproduced"
    if lambda_close:
        return "lambda_close_omega_off"
    return "not_reproduced_yet"


def curate(raw_path: Path, out_csv: Path, out_md: Path) -> None:
    references = collect_reference()
    job_meta = collect_job_meta()
    rows: list[dict[str, str]] = []
    for raw in read_csv(raw_path):
        case_id = raw["case_id"]
        qgrid = raw["qgrid"]
        job_id = raw.get("job_id", "")
        meta = job_meta.get((case_id, qgrid, job_id), job_meta.get((case_id, qgrid, ""), {}))
        ref = references.get(case_id, {})
        row = {
            "case_id": case_id,
            "material_type": meta.get("track") or ref.get("material_type", ""),
            "material": meta.get("material") or ref.get("material", ""),
            "condition": meta.get("condition") or ref.get("condition", ""),
            "qgrid": qgrid,
            "kgrid": meta.get("kgrid", ""),
            "job_id": job_id,
            "status": raw.get("status", ""),
            "lambda_ref": raw.get("lambda_ref", ""),
            "lambda": raw.get("lambda", ""),
            "lambda_relerr_pct": raw.get("lambda_relerr_pct", ""),
            "omega_log_ref_K": raw.get("omega_log_ref_K", ""),
            "omega_log_K": raw.get("omega_log_K", ""),
            "omega_relerr_pct": raw.get("omega_relerr_pct", ""),
            "top_q_share_pct": raw.get("top_q_share_pct", ""),
            "sku": meta.get("sku", ""),
            "np": meta.get("np", ""),
            "nk": meta.get("nk", ""),
            "verdict": "",
            "diagnosis": raw.get("diagnosis", ""),
            "next_action": raw.get("next_action", ""),
        }
        row["verdict"] = verdict(row)
        rows.append(row)

    fieldnames = [
        "case_id", "material_type", "material", "condition", "qgrid", "kgrid",
        "job_id", "status", "lambda_ref", "lambda", "lambda_relerr_pct",
        "omega_log_ref_K", "omega_log_K", "omega_relerr_pct", "top_q_share_pct",
        "sku", "np", "nk", "verdict", "diagnosis", "next_action",
    ]
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    write_markdown_summary(rows, out_md)


def write_markdown_summary(rows: list[dict[str, str]], out_md: Path) -> None:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["material_type"] or "unknown"].append(row)

    lines = [
        "# LBG QE 7.1 Reproduction Status by Material Type",
        "",
        "Source table: `lbg_qe71_np8_sigma0025.csv`.",
        "",
        "Verdicts:",
        "",
        "- `reproduced`: lambda is within 15 percent of the paper reference, omega_log is within 15 percent when available, and top-q share is not above 25 percent.",
        "- `lambda_close_omega_off`: lambda is within 15 percent, but omega_log is outside the 15 percent gate.",
        "- `smoke_unconverged`: the run completed, but one q/mode carries more than 25 percent of lambda.",
        "- `finished_missing_lambda_artifact`: LBG marked the job finished, but the compact lambda artifact was not retrieved.",
        "- `not_reproduced_yet`: completed and parsed, but lambda is still outside the 15 percent gate.",
        "",
        "| material type | rows | parsed lambda | reproduced | lambda close only | smoke/unconverged | missing artifact | notes |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for material_type in sorted(grouped):
        group = grouped[material_type]
        parsed = sum(1 for row in group if row["lambda"])
        reproduced = sum(1 for row in group if row["verdict"] == "reproduced")
        close_only = sum(1 for row in group if row["verdict"] == "lambda_close_omega_off")
        smoke = sum(1 for row in group if row["verdict"] == "smoke_unconverged")
        missing = sum(1 for row in group if row["verdict"] == "finished_missing_lambda_artifact")
        notes = "; ".join(best_notes(group))
        lines.append(
            f"| {material_type} | {len(group)} | {parsed} | {reproduced} | "
            f"{close_only} | {smoke} | {missing} | {notes} |"
        )

    lines.extend(["", "## Per-Case Rows", ""])
    for material_type in sorted(grouped):
        lines.extend([
            f"### {material_type}",
            "",
            "| case | material | q | lambda | ref | lambda err % | omega_log K | omega err % | top-q % | verdict |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
        ])
        for row in grouped[material_type]:
            lines.append(
                f"| {row['case_id']} | {row['material']} | {row['qgrid']} | "
                f"{row['lambda']} | {row['lambda_ref']} | {row['lambda_relerr_pct']} | "
                f"{row['omega_log_K']} | {row['omega_relerr_pct']} | "
                f"{row['top_q_share_pct']} | {row['verdict']} |"
            )
        lines.append("")

    out_md.write_text("\n".join(lines) + "\n")


def best_notes(group: list[dict[str, str]]) -> list[str]:
    notes: list[str] = []
    for verdict_name in ("reproduced", "lambda_close_omega_off", "smoke_unconverged"):
        cases = [row["case_id"] for row in group if row["verdict"] == verdict_name]
        if cases:
            notes.append(f"{verdict_name}: {', '.join(sorted(set(cases)))}")
    return notes[:3]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--raw",
        default=str(RESULTS / "lbg_results_20260610_mpiifort_np8_batch1.raw.csv"),
    )
    parser.add_argument(
        "--out-csv",
        default=str(RESULTS / "lbg_qe71_np8_sigma0025.csv"),
    )
    parser.add_argument(
        "--out-md",
        default=str(RESULTS / "summary_by_material_type.md"),
    )
    args = parser.parse_args()
    curate(Path(args.raw), Path(args.out_csv), Path(args.out_md))
    print(f"wrote {args.out_csv}")
    print(f"wrote {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
