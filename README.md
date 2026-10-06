# BI Validation & Monitoring

A practical validation framework for checking whether operational KPIs remain accurate and consistent from source data through SQL analysis and dashboard reporting.

## Overview

This project documents a structured BI validation workflow for operational reporting.

The framework focuses on:

- Source-to-report reconciliation
- Data-quality checks
- KPI validation
- Dashboard consistency
- Refresh review
- Investigation and escalation workflows

The goal is to make sure reported metrics can be traced back to the underlying data and that reporting issues can be identified before they affect decision-making.

## Validation Workflow

**Source Data → Data Quality Checks → SQL Analysis → KPI Validation → Dashboard Reconciliation → Refresh Review → Investigation**

## Source-to-Report Reconciliation

Key reporting metrics should be compared between the source data, analytical layer, and dashboard.

### Ticket Volume

Validate that:

- Source row counts are understood
- Duplicate records are identified
- Clean record counts match the analytical dataset
- Dashboard totals reconcile with the validated dataset

### SLA Performance

Validate:

- Total resolved records
- SLA-compliant records
- SLA-breached records
- SLA achievement percentage

The dashboard calculation should use the same business definition as the underlying SQL analysis.

### Resolution & CSAT

Check that:

- Resolution metrics use valid resolved records
- Resolution times are calculated consistently
- CSAT calculations use valid survey responses
- Dashboard values reconcile with analytical results

### Repeat & Escalation

Review:

- Repeat-ticket counts
- Escalation counts
- Repeat-ticket rate
- Escalation rate

These metrics should be validated against the underlying ticket-level records.

## Data-Quality Gates

Before reporting KPIs, perform basic data-quality checks.

### Duplicate Detection

Check for duplicate identifiers such as `Ticket_ID`.

Example SQL:

\`\`\`sql
SELECT
    Ticket_ID,
    COUNT(*) AS record_count
FROM Tickets
GROUP BY Ticket_ID
HAVING COUNT(*) > 1;
\`\`\`

### Missing Values

Review important fields such as:

- `Ticket_ID`
- `Created_Date`
- `Category`
- `Priority`
- `Agent`
- `Status`
- `Resolution_Timestamp`

### Invalid Values

Check for:

- Negative resolution times
- Invalid timestamps
- Unknown categories
- Missing identifiers
- Unexpected status values
- Invalid SLA calculations

## KPI Validation

Each KPI should have a defined calculation and validation rule.

| KPI | Validation |
|---|---|
| Ticket Volume | Reconcile dashboard count with cleaned dataset |
| SLA Achievement | Compare calculated SLA result with dashboard KPI |
| Average Resolution Time | Validate calculation against resolved records |
| CSAT | Reconcile dashboard average with valid survey responses |
| Repeat Rate | Validate repeat-ticket classification |
| Escalation Rate | Reconcile escalation flags with ticket records |

## Dashboard Reconciliation

After the analytical layer is validated, compare the results with the dashboard.

Review:

- KPI cards
- Trend charts
- Category breakdowns
- Priority analysis
- Team performance
- Filters and slicers
- Date ranges

A dashboard value should be traceable to a defined calculation and underlying dataset.

## Refresh Review

After a dataset refresh, review:

1. Refresh completion status
2. Row counts
3. Duplicate counts
4. Missing-value checks
5. KPI totals
6. Dashboard filters
7. Unexpected changes in trends

Large changes should be investigated rather than automatically accepted.

## Investigation Workflow

When a KPI does not reconcile:

1. Identify the discrepancy
2. Check dashboard filters
3. Review the KPI definition
4. Check the SQL calculation
5. Inspect source records
6. Check data-quality issues
7. Document the root cause
8. Correct and revalidate

This creates a repeatable investigation process instead of relying on manual trial and error.

## Validation Principles

### Traceability

Every important KPI should be traceable to its source data and calculation.

### Consistency

The same business definition should be used across SQL, Python, Power BI, and reporting outputs.

### Reconciliation

Dashboard values should be compared against independently calculated results.

### Documentation

Validation rules, assumptions, and identified issues should be documented.

### Repeatability

Checks should be structured so they can be repeated after future data updates.

## Scope

This project demonstrates a practical BI validation framework using operational analytics workflows.

It does not represent a live enterprise monitoring environment and does not include:

- Production Power BI gateways
- Enterprise data warehouses
- Automated production alerts
- Enterprise scheduled refresh infrastructure
- Confidential business data

## What This Project Demonstrates

- BI validation
- Data-quality analysis
- KPI reconciliation
- SQL validation
- Dashboard quality checks
- Root-cause investigation
- Reporting controls
- Data documentation
- Operational analytics

## Analyst Relevance

BI validation is an important part of Data Analyst work because accurate reporting depends on more than building dashboards.

This workflow demonstrates how to:

- Validate source data
- Check analytical calculations
- Reconcile dashboard results
- Investigate unexpected KPI changes
- Document data-quality issues
- Build repeatable reporting controls

## Tools & Technologies

- SQL
- Python
- Pandas
- Power BI
- Excel
- GitHub

## Author

**Sajid Manzoor**

Data Analyst | SQL | Power BI | Python | Excel

GitHub: `sajidmanzoor730`
