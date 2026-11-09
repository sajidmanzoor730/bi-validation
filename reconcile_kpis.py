#!/usr/bin/env python3
"""Calculate KPI baselines and optionally reconcile a Power BI KPI export."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "BI_Validation_Clean.csv"
OUTPUT = ROOT / "outputs" / "python_kpi_baseline.csv"
TOLERANCE = 0.01


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def number(value: str) -> float | None:
    try:
        return float(value) if value.strip() else None
    except (ValueError, AttributeError):
        return None


def calculate(rows: list[dict[str, str]]) -> dict[str, float]:
    total = len(rows)
    if not total:
        raise ValueError("Clean dataset is empty")

    def count(predicate):
        return sum(1 for row in rows if predicate(row))

    def ratio(numerator: int, denominator: int) -> float:
        return numerator / denominator * 100 if denominator else 0.0

    completed = count(lambda r: r["Status"] in {"Completed", "Closed"})
    met = count(lambda r: r["SLA_Status"] == "Met")
    breached = count(lambda r: r["SLA_Status"] == "Breached")
    qa_pass = count(lambda r: r["QA_Result"] == "Pass")
    qa_fail = count(lambda r: r["QA_Result"] == "Fail")
    repeat = count(lambda r: r["Repeat_Flag"] == "1")
    escalated = count(lambda r: r["Escalated_Flag"] == "1")
    rework = count(lambda r: r["Rework_Flag"] == "1")
    valid = count(lambda r: r["Data_Quality_Flag"] == "Valid")

    resolution = [number(r["Resolution_Minutes"]) for r in rows]
    resolution = [v for v in resolution if v is not None]
    csat = [number(r["CSAT"]) for r in rows]
    csat = [v for v in csat if v is not None]

    return {
        "Total Records": float(total),
        "Completion Rate %": ratio(completed, total),
        "SLA Achievement %": ratio(met, met + breached),
        "Average Resolution Minutes": sum(resolution) / len(resolution) if resolution else 0.0,
        "Average CSAT": sum(csat) / len(csat) if csat else 0.0,
        "Repeat Rate %": ratio(repeat, total),
        "Escalation Rate %": ratio(escalated, total),
        "QA Pass Rate %": ratio(qa_pass, qa_pass + qa_fail),
        "Rework Rate %": ratio(rework, total),
        "Valid Data Rate %": ratio(valid, total),
    }


def write_baseline(metrics: dict[str, float], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Metric", "Python_Value"])
        writer.writeheader()
        for name, value in metrics.items():
            writer.writerow({"Metric": name, "Python_Value": f"{value:.4f}"})


def reconcile(metrics: dict[str, float], export_path: Path) -> list[dict[str, str]]:
    exported = {}
    for row in load_rows(export_path):
        if row.get("Metric"):
            exported[row["Metric"].strip()] = number(row.get("PowerBI_Value", ""))
    results = []
    for name, python_value in metrics.items():
        powerbi_value = exported.get(name)
        variance = None if powerbi_value is None else powerbi_value - python_value
        results.append({
            "Metric": name,
            "Python_Value": f"{python_value:.4f}",
            "PowerBI_Value": "" if powerbi_value is None else f"{powerbi_value:.4f}",
            "Variance": "" if variance is None else f"{variance:.4f}",
            "Status": "MISSING" if variance is None else ("PASS" if abs(variance) <= TOLERANCE else "FAIL"),
        })
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DATA)
    parser.add_argument("--powerbi-export", type=Path)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    metrics = calculate(load_rows(args.data))
    write_baseline(metrics, args.output)
    print(f"Python KPI baseline written to: {args.output}")
    for name, value in metrics.items():
        print(f"{name:<30} {value:.2f}")

    if args.powerbi_export:
        results = reconcile(metrics, args.powerbi_export)
        print("\nPower BI reconciliation (tolerance: +/- 0.01)")
        for row in results:
            print(f"{row['Status']:<7} {row['Metric']:<30} Python={row['Python_Value']} Power BI={row['PowerBI_Value']} Variance={row['Variance']}")
        failures = sum(row["Status"] != "PASS" for row in results)
        print(f"\n{len(results) - failures}/{len(results)} metrics passed")
        return 1 if failures else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
