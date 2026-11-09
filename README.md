# BI Validation & Monitoring

![BI validation](https://github.com/sajidmanzoor730/bi-validation/actions/workflows/validate.yml/badge.svg)

A reproducible data-quality and KPI-validation project built around a synthetic operational dataset. The goal is simple: **make sure the numbers used in operational reporting are consistent with the underlying records and business rules.**

This repository demonstrates data profiling, controlled defect injection, cleaning, issue logging, independent validation, and KPI reconciliation using Python and SQL.

> **Data note:** All records are synthetic and generated for this portfolio project. They do not represent real customers, employees, or production systems.

## Project overview

The generator creates an intentionally imperfect raw dataset, applies documented cleaning rules, and publishes a curated dataset plus issue logs.

| Deliverable | Description |
|---|---|
| `BI_Validation_Raw.csv` | Synthetic source data with intentional quality defects (8,160 rows) |
| `BI_Validation_Clean.csv` | Curated dataset after cleaning (8,000 unique records) |
| `BI_Validation_Data_Quality_Issues.csv` | Summary of 24 issue types and cleaning actions |
| `BI_Validation_Row_Issue_Log.csv` | 765 record-level issue findings for investigation |
| `generate_bi_validation_data.py` | Reproducible data generator, defect injection, cleaning and issue logging |
| `validate_project.py` | Independent standard-library quality gate for the published files |
| `tests/test_validation.py` | Regression tests for key project controls |
| `sql/validation_checks.sql` | SQLite-compatible exception queries and KPI baseline |
| `reconcile_kpis.py` | Python KPI baseline and optional Power BI export comparison |
| `powerbi/BI_Validation_Measures.dax` | DAX measures and Calendar table definition |
| `DATA_DICTIONARY.md` | Field definitions, types and KPI denominators |
| `POWER_BI_DASHBOARD_GUIDE.md` | Report page plan, setup steps and reconciliation workflow |

## Quick start

Python 3.10 or newer is recommended.

```bash
# Re-run the generator (requires pandas and NumPy)
python -m pip install -r requirements.txt
python generate_bi_validation_data.py

# Run the independent quality gate (standard library only)
python validate_project.py

# Run regression tests
python -m unittest discover -s tests -v
```

The validator exits with a non-zero status when a control fails, making it suitable for a pre-report-refresh check or CI workflow.

## Validation controls

The independent Python quality gate checks:

- Raw and curated row counts, duplicate raw IDs and unique curated IDs.
- Presence of required columns and valid identifiers.
- Priority-to-SLA-target mapping (P1 = 60, P2 = 240, P3 = 480, P4 = 960 minutes).
- Resolution dates and calculated resolution minutes.
- SLA status against resolution time and target.
- QA score range and QA result classification.
- Rework flag against the documented rule.
- Created month and Monday week-start derivations.
- Data-quality classifications and issue-summary / row-log consistency.

The SQL examples provide a separate way to inspect duplicate keys, SLA target mapping, date logic, resolution minutes, SLA status and QA rules. Load `BI_Validation_Clean.csv` into SQLite under the table name `BI_Validation_Clean`, then run `sql/validation_checks.sql`. The exception queries should return no rows; the final query returns a KPI baseline for comparison.

## Business rules

### SLA targets

| Priority | Target |
|---|---:|
| P1 | 60 minutes |
| P2 | 240 minutes |
| P3 | 480 minutes |
| P4 | 960 minutes |

- **Met:** resolution time is less than or equal to the target.
- **Breached:** resolution time exceeds the target.
- **Pending:** record is unresolved.
- **Unknown:** a resolved record has no reliable resolution timestamp.
- SLA achievement = Met / (Met + Breached). Pending and Unknown are excluded.

### Other rules

- Completed records have status `Completed` or `Closed`.
- QA pass requires a score of at least 85.
- Rework is flagged when QA is below 80, or when a repeat record has QA below 90.
- CSAT is retained only when it is between 1 and 5; missing values are not imputed.
- Invalid values that cannot be safely inferred are left blank / NULL rather than fabricated.

## Data-quality scenario

The raw dataset includes duplicate IDs, missing and invalid categories, missing agents and CSAT, impossible dates, negative or mismatched resolution times, invalid QA scores, incorrect SLA fields, and inconsistent derived fields.

The cleaning process keeps the 8,000 unique records and applies explicit rules to correct, standardize, or null invalid values. The issue summary describes issue types; the row-level log supports record investigation. A row can have more than one issue finding, so issue findings are not the same as distinct affected records.

## KPI baseline

The original project baseline documents the following values from the curated synthetic dataset. Recalculate them with Python or SQL when regenerating the data:

| KPI | Baseline |
|---|---:|
| Total records | 8,000 |
| Completion rate | 94.5% |
| SLA achievement | 86.0% |
| Average resolution time | 328 minutes |
| Average CSAT | 4.05 |
| Repeat rate | 6.2% |
| Escalation rate | 4.1% |
| QA pass rate | 87.8% |
| Rework rate | 7.8% |
| Records flagged Valid | 93.9% |

## Current implementation status

**Implemented in this repository**
- Reproducible synthetic raw and clean datasets.
- Defect injection, cleaning rules, issue summary and row-level issue log.
- Independent Python validation script and regression tests.
- SQLite-compatible SQL exception checks and KPI baseline query.
- Power BI DAX measure definitions, data dictionary and dashboard build guide.
- Python KPI baseline export and optional comparison against a Power BI CSV export.
- CI execution of the Python KPI baseline and regression tests.

**Not yet implemented / not claimed**
- A published Power BI `.pbix` report and completed semantic model.
- Actual DAX measures executed and reconciled against Python and SQL.
- Scheduled production refresh monitoring, gateway integration or alert delivery.

The architecture and report-page ideas in this project are a design direction, not a claim that a live enterprise BI service has been deployed.

## Power BI next step

Follow `POWER_BI_DASHBOARD_GUIDE.md` to build the report in Power BI Desktop. Copy measures from `powerbi/BI_Validation_Measures.dax`. Export the report's KPI values as a CSV with `Metric,PowerBI_Value` columns, then run `python reconcile_kpis.py --powerbi-export path/to/powerbi_kpis.csv`. A successful comparison is required before claiming cross-tool reconciliation.

## Skills demonstrated

Python · Pandas · NumPy · SQL · Data Cleaning · Data Profiling · Data Quality · KPI Definitions · SLA Analysis · Reconciliation · Root-Cause Investigation · Reproducible Analytics · GitHub

---

**Sajid Manzoor**  
[GitHub profile](https://github.com/sajidmanzoor730)
