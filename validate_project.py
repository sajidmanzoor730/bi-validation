#!/usr/bin/env python3
"""Validate the BI Validation project's raw and curated CSV deliverables.

Run: python validate_project.py
Uses only the Python standard library; exits non-zero when a control fails.
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SLA_TARGETS = {"P1": 60, "P2": 240, "P3": 480, "P4": 960}
RESOLVED = {"Completed", "Closed"}
EXPECTED_RAW_ROWS = 8160
EXPECTED_CLEAN_ROWS = 8000
EXPECTED_DUPLICATES = 160


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def as_int(value: str) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def as_float(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_date(value: str) -> datetime | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass
    return None


def validate(root: Path = ROOT) -> tuple[list[str], dict[str, object]]:
    failures: list[str] = []
    checks = 0

    def check(condition: bool, message: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            failures.append(message)

    raw = read_csv(root / "BI_Validation_Raw.csv")
    clean = read_csv(root / "BI_Validation_Clean.csv")
    issue_summary = read_csv(root / "BI_Validation_Data_Quality_Issues.csv")
    issue_log = read_csv(root / "BI_Validation_Row_Issue_Log.csv")

    required = {
        "Record_ID", "Created_Date", "Resolved_Date", "Team", "Region",
        "Category", "Priority", "Channel", "Complexity", "Status", "Agent",
        "Items_Processed", "Resolution_Minutes", "SLA_Target_Minutes",
        "SLA_Status", "QA_Score", "QA_Result", "Rework_Flag", "CSAT",
        "Repeat_Flag", "Escalated_Flag", "Created_Month", "Week_Start",
        "Data_Quality_Flag",
    }
    check(bool(clean), "Clean dataset is empty")
    missing_columns = required.difference(clean[0].keys() if clean else set())
    check(not missing_columns, "Clean dataset is missing required columns: " + ", ".join(sorted(missing_columns)))
    check(len(raw) == EXPECTED_RAW_ROWS, f"Expected {EXPECTED_RAW_ROWS} raw rows; found {len(raw)}")
    if not clean or missing_columns:
        return failures, {
            "raw_rows": len(raw),
            "clean_rows": len(clean),
            "checks_run": checks,
            "checks_failed": len(failures),
        }
    check(len(clean) == EXPECTED_CLEAN_ROWS, f"Expected {EXPECTED_CLEAN_ROWS} clean rows; found {len(clean)}")

    raw_ids = [r.get("Record_ID", "") for r in raw]
    clean_ids = [r.get("Record_ID", "") for r in clean]
    raw_duplicate_rows = len(raw_ids) - len(set(raw_ids))
    check(raw_duplicate_rows == EXPECTED_DUPLICATES,
          f"Expected {EXPECTED_DUPLICATES} duplicate raw IDs; found {raw_duplicate_rows}")
    check(len(clean_ids) == len(set(clean_ids)), "Clean Record_ID values are not unique")
    check(all(clean_ids), "Clean dataset contains blank Record_ID values")

    allowed_priorities = set(SLA_TARGETS)
    allowed_statuses = {"Met", "Breached", "Pending", "Unknown"}
    allowed_dq = {"Valid", "Corrected", "Standardized", "Nulled"}
    bad_priority = bad_target = bad_sla = bad_dates = bad_resolution = 0
    bad_qa = bad_qa_result = bad_rework = bad_month = bad_week = 0
    blank_required = 0
    resolved_count = 0
    sla_eligible = sla_met = 0
    csat_values: list[float] = []

    for row in clean:
        priority = row["Priority"]
        target = as_int(row["SLA_Target_Minutes"])
        if priority not in allowed_priorities:
            bad_priority += 1
        elif target != SLA_TARGETS[priority]:
            bad_target += 1

        created = parse_date(row["Created_Date"])
        resolved = parse_date(row["Resolved_Date"])
        if created is None:
            bad_dates += 1
            continue
        expected_month = created.strftime("%Y-%m")
        expected_week = (created.date().toordinal() - created.weekday())
        from datetime import date, timedelta
        expected_week_text = (date.fromordinal(expected_week)).isoformat()
        if row["Created_Month"] != expected_month:
            bad_month += 1
        if row["Week_Start"] != expected_week_text:
            bad_week += 1

        minutes = as_int(row["Resolution_Minutes"])
        if resolved is not None:
            resolved_count += 1
            if resolved < created or minutes is None:
                bad_resolution += 1
            else:
                expected_minutes = round((resolved - created).total_seconds() / 60)
                if minutes != expected_minutes:
                    bad_resolution += 1
                if target is not None:
                    expected_sla = "Met" if expected_minutes <= target else "Breached"
                    if row["SLA_Status"] != expected_sla:
                        bad_sla += 1
                    sla_eligible += 1
                    sla_met += expected_sla == "Met"
        else:
            if minutes is not None:
                bad_resolution += 1
            expected_sla = "Unknown" if row["Status"] in RESOLVED else "Pending"
            if row["SLA_Status"] != expected_sla:
                bad_sla += 1

        qa = as_float(row["QA_Score"])
        if qa is not None and not 0 <= qa <= 100:
            bad_qa += 1
        expected_qa_result = "Not Scored" if qa is None else ("Pass" if qa >= 85 else "Fail")
        if row["QA_Result"] != expected_qa_result:
            bad_qa_result += 1

        repeat = as_int(row["Repeat_Flag"])
        expected_rework = int(qa is not None and (qa < 80 or (repeat == 1 and qa < 90)))
        if as_int(row["Rework_Flag"]) != expected_rework:
            bad_rework += 1

        csat = as_float(row["CSAT"])
        if csat is not None:
            if not 1 <= csat <= 5:
                blank_required += 1
            else:
                csat_values.append(csat)

        if row["SLA_Status"] not in allowed_statuses:
            bad_sla += 1
        if row["Data_Quality_Flag"] not in allowed_dq:
            blank_required += 1

    check(bad_priority == 0, f"{bad_priority} invalid priority values")
    check(bad_target == 0, f"{bad_target} SLA targets do not match priority rules")
    check(bad_sla == 0, f"{bad_sla} SLA statuses do not match dates and target rules")
    check(bad_dates == 0, f"{bad_dates} invalid or missing Created_Date values")
    check(bad_resolution == 0, f"{bad_resolution} resolution-time/date inconsistencies")
    check(bad_qa == 0, f"{bad_qa} QA scores outside 0-100")
    check(bad_qa_result == 0, f"{bad_qa_result} QA_Result values do not match QA_Score")
    check(bad_rework == 0, f"{bad_rework} Rework_Flag values do not match the documented rule")
    check(bad_month == 0, f"{bad_month} Created_Month values do not match Created_Date")
    check(bad_week == 0, f"{bad_week} Week_Start values are not Monday of the Created_Date week")
    check(blank_required == 0, f"{blank_required} invalid CSAT or Data_Quality_Flag values")

    summary_counts = {r["Issue_Type"]: as_int(r["Affected_Records"]) for r in issue_summary}
    log_counts = Counter(r["Issue_Type"] for r in issue_log)
    check(len(issue_summary) == 24, f"Expected 24 issue types; found {len(issue_summary)}")
    check(len(issue_log) == 765, f"Expected 765 row-level findings; found {len(issue_log)}")
    check(all(summary_counts.get(k) == v for k, v in log_counts.items()
              if k != "Duplicate_Record_ID"),
          "Issue summary counts do not agree with row-level issue log for overlapping issue types")
    check(summary_counts.get("Duplicate_Record_ID") == EXPECTED_DUPLICATES,
          "Duplicate issue count does not match raw duplicate count")

    metrics = {
        "raw_rows": len(raw),
        "clean_rows": len(clean),
        "duplicate_raw_rows": raw_duplicate_rows,
        "issue_types": len(issue_summary),
        "row_issue_findings": len(issue_log),
        "resolved_records": resolved_count,
        "sla_eligible_records": sla_eligible,
        "sla_achievement_pct": round(100 * sla_met / sla_eligible, 2) if sla_eligible else None,
        "average_csat": round(sum(csat_values) / len(csat_values), 2) if csat_values else None,
        "checks_run": checks,
        "checks_failed": len(failures),
    }
    return failures, metrics


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Project directory containing the CSV files")
    args = parser.parse_args()
    failures, metrics = validate(args.root)
    print("BI Validation project quality gate")
    print("=" * 36)
    for key, value in metrics.items():
        print(f"{key.replace('_', ' ').title():<28} {value}")
    print("\nResult:", "FAILED" if failures else "PASSED")
    for failure in failures:
        print(" -", failure)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
