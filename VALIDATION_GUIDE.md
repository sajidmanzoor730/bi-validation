# BI Validation — Running the Quality Gate

This guide explains how to reproduce the validation checks in this repository.

## Quick start

Requires Python 3.10 or newer. The validator uses only the Python standard library.

```bash
python validate_project.py
python -m unittest discover -s tests -v
```

The validator exits with status code `1` when a quality gate fails, which makes it suitable for a CI job or a pre-refresh check. It checks the published raw and clean row counts, duplicate business keys, issue inventory, row-level issue log, date logic, resolution-time calculations, SLA rules, QA rules, and derived calendar fields.

## Independent SQL review

Load `BI_Validation_Clean.csv` into SQLite as `BI_Validation_Clean`, then run the statements in `sql/validation_checks.sql`. The first six queries are exception queries and should return no rows. The final query produces an independent KPI baseline.

## What is implemented vs. planned

Implemented in this repository:
- Reproducible synthetic raw and clean datasets.
- Data-quality issue summary and row-level investigation log.
- Python quality gate and regression tests.
- SQLite-compatible SQL exception checks and KPI baseline query.

Still planned:
- A packaged Power BI `.pbix` model and report.
- DAX measures executed and reconciled against the Python/SQL baseline.
- Automated scheduled refresh monitoring and alert delivery.

The datasets are synthetic and intended for portfolio demonstration. They do not represent real customers, employees, or production systems.
