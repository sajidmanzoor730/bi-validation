# 🔍 BI Validation & Monitoring

A complete Data Analytics and Power BI project focused on validating operational KPIs from raw source data through Python, SQL, and Power BI.

This project demonstrates how a Data Analyst can clean operational data, identify data-quality problems, build a reliable reporting model, calculate KPIs independently, and reconcile those results against Power BI.

---

## 📊 Dataset

The project uses a structured operational dataset covering **January–September 2026**.

### Dataset Files

| File | Purpose | Records |
|---|---|---:|
| `BI_Validation_Raw.csv` | Raw operational data containing intentional data-quality issues | 8,160 |
| `BI_Validation_Clean.csv` | Cleaned analytical dataset after validation and cleaning | 8,000 |
| `BI_Validation_Data_Quality_Issues.csv` | Documented data-quality issue types and cleaning actions | 24 issue types |
| `BI_Validation_Row_Issue_Log.csv` | Record-level findings for investigation and Power BI drilldown | 765 findings |
| `generate_bi_validation_data.py` | Reproducible Python data generator and validation script | — |

### Dataset Summary

- Raw rows: **8,160**
- Clean unique records: **8,000**
- Duplicate rows removed: **160**
- Reporting period: **January–September 2026**
- Documented issue types: **24**
- Record-level issue findings: **765**
- Fixed random seed for reproducibility

The raw dataset contains intentionally defective values so the same issues can be detected independently using Python, SQL, and Power BI.

The clean dataset is generated from the raw dataset using documented cleaning and validation rules.

---

## 🔄 Analytics Workflow

    Raw Operational Data
            ↓
    Data Quality Profiling
            ↓
    Python Cleaning & Validation
            ↓
    Clean Analytical Dataset
            ↓
    SQL KPI Validation
            ↓
    Power BI Data Model
            ↓
    DAX Measures
            ↓
    Power BI Dashboard
            ↓
    Source vs SQL vs Power BI Reconciliation
            ↓
    Investigation & Root-Cause Analysis

---

## 🧾 Main Fields

| Field | Description |
|---|---|
| `Record_ID` | Unique operational record identifier |
| `Created_Date` | Record creation date |
| `Resolved_Date` | Record resolution date |
| `Team` | Operational team responsible for the record |
| `Region` | Operating region |
| `Category` | Operational request category |
| `Priority` | P1–P4 priority level |
| `Channel` | Work-management or intake channel |
| `Complexity` | Low, Medium, or High |
| `Status` | Current operational status |
| `Agent` | Assigned operational owner |
| `Root_Cause` | Primary issue or root-cause classification |
| `Items_Processed` | Number of items handled |
| `Resolution_Minutes` | Time between creation and resolution |
| `SLA_Target_Minutes` | SLA target determined by priority |
| `SLA_Status` | Met, Breached, Pending, or Unknown |
| `QA_Score` | Quality-assessment score |
| `QA_Result` | QA assessment result |
| `Rework_Flag` | Indicates whether rework is required |
| `CSAT` | Customer satisfaction score |
| `Repeat_Flag` | Indicates repeat activity |
| `Escalated_Flag` | Indicates escalation |
| `Created_Month` | Reporting month |
| `Week_Start` | Monday of the created week |
| `Data_Quality_Flag` | Record-level data-quality classification |

---

## 🚨 Intentional Data-Quality Issues

The raw dataset contains realistic data-quality problems intentionally introduced so they can be detected, investigated, and corrected.

| Issue | Affected Rows |
|---|---:|
| Duplicate `Record_ID` | 160 |
| Missing Category | 75 |
| Invalid Category | 10 |
| Missing Agent | 55 |
| Missing CSAT | 45 |
| Negative Resolution Minutes | 12 |
| QA Score above 100 | 10 |
| Resolved Date before Created Date | 12 |
| Invalid Priority | 8 |
| Incorrect SLA Status | 18 |

### Additional Derived-Field Issues

Additional issue types cover inconsistent or missing derived fields:

- Missing or incorrect SLA target
- Missing or incorrect SLA status
- Missing or incorrect resolution minutes
- Incorrect QA result
- Incorrect rework flag
- Missing or incorrect created month
- Missing or incorrect week start
- Incorrect data-quality flag
- Other derived-field inconsistencies documented in the issue summary

The complete issue inventory is available in:

`BI_Validation_Data_Quality_Issues.csv`

The record-level findings are available in:

`BI_Validation_Row_Issue_Log.csv`

---

## 🧹 Data Cleaning

The clean dataset is generated from the raw dataset rather than copied from the original source.

### Cleaning Process

    Raw Dataset
         ↓
    Duplicate Detection
         ↓
    Missing-Value Checks
         ↓
    Invalid-Value Detection
         ↓
    Date Validation
         ↓
    Business Rule Validation
         ↓
    Derived Field Recalculation
         ↓
    Clean Analytical Dataset

### Cleaning Rules

1. Remove duplicate `Record_ID` values.
2. Standardize missing Category values to `Unknown`.
3. Standardize missing Agent values to `Unassigned`.
4. Keep missing CSAT values as `NULL`.
5. Set QA scores outside the 0–100 range to `NULL`.
6. Repair invalid Priority values using preserved SLA target information.
7. Set impossible `Resolved_Date` values to `NULL`.
8. Recalculate `Resolution_Minutes` from `Created_Date` and `Resolved_Date`.
9. Recalculate `SLA_Target_Minutes`.
10. Recalculate `SLA_Status`.
11. Recalculate `QA_Result`.
12. Recalculate `Rework_Flag`.
13. Recalculate `Created_Month`.
14. Recalculate `Week_Start`.
15. Recalculate `Data_Quality_Flag`.

The clean dataset keeps all **8,000 unique records**. Invalid values are corrected or converted to `NULL` rather than simply deleting affected records.

---

## ⚙️ Business Rules

### SLA Targets

| Priority | SLA Target |
|---|---:|
| P1 | 60 minutes |
| P2 | 240 minutes |
| P3 | 480 minutes |
| P4 | 960 minutes |

### SLA Logic

- **SLA Met:** `Resolution_Minutes <= SLA_Target_Minutes`
- **SLA Breached:** resolved record exceeds its SLA target
- **Pending:** unresolved record without a valid `Resolved_Date`
- **Unknown:** invalid or impossible resolution data prevents reliable SLA evaluation

### SLA Achievement

    SLA Achievement %
    =
    SLA Met Records
    /
    (SLA Met Records + SLA Breached Records)

`Pending` and `Unknown` records are excluded from the SLA denominator.

### Completion

A record is considered completed when:

    Status = Completed
    OR
    Status = Closed

### QA

A QA score of **85 or above** is considered a pass.

    QA Pass = QA_Score >= 85

### Rework

A record is flagged for rework when:

    QA_Score < 80

or:

    Repeat_Flag = 1
    AND
    QA_Score < 90

---

## 📈 Clean Dataset KPI Baseline

| KPI | Value |
|---|---:|
| Total Records | 8,000 |
| Completion Rate | 94.5% |
| SLA Met | 86.0% |
| SLA Breached | 14.0% |
| Average Resolution Time | 328 minutes |
| Average CSAT | 4.05 |
| Repeat Rate | 6.2% |
| Escalation Rate | 4.1% |
| QA Pass Rate | 87.8% |
| Rework Rate | 7.8% |
| Records Flagged Valid | 93.9% |

These values provide the initial reconciliation baseline for the reporting model.

---

## 🐍 Python Analysis

Python provides the data-generation, cleaning, profiling, and validation layer.

### Responsibilities

- Generate reproducible operational data
- Profile raw data
- Detect duplicate records
- Detect missing values
- Detect invalid values
- Validate dates
- Validate numerical ranges
- Apply cleaning rules
- Recalculate derived fields
- Generate issue logs
- Calculate KPI baselines
- Validate expected issue counts
- Reproduce the dataset consistently

### Main File

`generate_bi_validation_data.py`

The generator uses a fixed random seed so the dataset can be reproduced consistently.

---

## 🗄️ SQL Validation

SQL provides an independent analytical layer for validating results before they reach Power BI.

### SQL Analysis

The project validates:

- Total record count
- Unique record count
- Duplicate records
- Missing values
- Invalid values
- Data-quality issue counts
- SLA performance
- Completion rate
- Average resolution time
- CSAT
- QA performance
- Repeat rate
- Escalation rate
- Rework rate
- Team performance
- Regional performance
- Monthly trends
- Category performance
- Root-cause patterns
- Source-to-report reconciliation

### Example SQL

    SELECT
        SLA_Status,
        COUNT(*) AS Record_Count
    FROM BI_Validation_Clean
    GROUP BY SLA_Status
    ORDER BY Record_Count DESC;

### SLA Validation

    SELECT
        SLA_Status,
        COUNT(*) AS Records
    FROM BI_Validation_Clean
    WHERE SLA_Status IN ('Met', 'Breached')
    GROUP BY SLA_Status;

---

## 📊 Power BI

Power BI is the **primary reporting and visualization layer** of this project.

### Reporting Architecture

    BI_Validation_Raw.csv
              ↓
          Python ETL
              ↓
    BI_Validation_Clean.csv
              ↓
           SQL Layer
              ↓
        Power BI Model
              ↓
           DAX KPIs
              ↓
       Power BI Reports
              ↓
       KPI Reconciliation

---

## 🧩 Power BI Data Model

The model uses a central operational fact table with supporting dimensions.

    DimDate
         │
         │
    DimTeam ─────── FactOperations ─────── DimAgent
                         │
                         ├──────── DimCategory
                         │
                         ├──────── DimPriority
                         │
                         ├──────── DimRegion
                         │
                         └──────── DimChannel

### Fact Table

`FactOperations`

Contains operational records and measurable fields.

### Dimension Tables

- `DimDate`
- `DimTeam`
- `DimAgent`
- `DimCategory`
- `DimPriority`
- `DimRegion`
- `DimChannel`

Dimension tables are created from the cleaned dataset using distinct values or dedicated dimension/date-table logic.

Each agent belongs to one operational team.

---

## 📑 Power BI Report Pages

### 1. Executive Overview

High-level KPIs:

- Total Records
- Completion Rate
- SLA Achievement
- Average Resolution Time
- Average CSAT
- QA Pass Rate
- Repeat Rate
- Escalation Rate
- Rework Rate

Visuals:

- Monthly performance trend
- SLA performance
- Team comparison
- Workload distribution
- KPI summary

### 2. Operational Performance

Analysis by:

- Team
- Region
- Priority
- Category
- Channel
- Agent
- Month

Measures include:

- Resolution time
- SLA performance
- Workload
- Completion rate
- Items processed
- QA performance
- Rework

### 3. Data Quality

The data-quality page monitors:

- Duplicate records
- Missing values
- Invalid values
- Corrected records
- Standardized records
- Nulled values
- Valid records
- Data-quality rate

The row-level issue log supports drilldown into individual records.

### 4. KPI Validation

The validation page compares:

    Python
       ↓
    SQL
       ↓
    Power BI

Example reconciliation structure:

| KPI | Python | SQL | Power BI | Difference |
|---|---:|---:|---:|---:|
| Total Records | 8,000 | 8,000 | 8,000 | 0 |
| Completion Rate | 94.5% | 94.5% | 94.5% | 0 |
| SLA Achievement | 86.0% | 86.0% | 86.0% | 0 |
| Average Resolution | 328 | 328 | 328 | 0 |
| Average CSAT | 4.05 | 4.05 | 4.05 | 0 |

Final Power BI reconciliation values will be populated after the SQL and DAX validation layers are completed.

### 5. Investigation & Drilldown

The investigation page answers questions such as:

- Why did SLA performance change?
- Which team has the highest breach rate?
- Which categories create the most rework?
- Which records have unusually high resolution times?
- Where are data-quality issues concentrated?
- Which root causes drive escalations?
- Which records are affecting a KPI?

Drilldown flow:

    KPI
     ↓
    Team
     ↓
    Category
     ↓
    Record

---

## 🧮 DAX KPI Layer

Power BI measures use reusable DAX rather than hardcoded dashboard values.

### Total Records

    Total Records =
    COUNTROWS(FactOperations)

### Completed Records

    Completed Records =
    CALCULATE(
        [Total Records],
        FactOperations[Status] IN {"Completed", "Closed"}
    )

### Completion Rate

    Completion Rate =
    DIVIDE(
        [Completed Records],
        [Total Records]
    )

### SLA Met Records

    SLA Met Records =
    CALCULATE(
        [Total Records],
        FactOperations[SLA_Status] = "Met"
    )

### SLA Breached Records

    SLA Breached Records =
    CALCULATE(
        [Total Records],
        FactOperations[SLA_Status] = "Breached"
    )

### SLA Achievement

    SLA Achievement % =
    DIVIDE(
        [SLA Met Records],
        [SLA Met Records] + [SLA Breached Records]
    )

### Average Resolution Time

    Average Resolution Minutes =
    AVERAGE(
        FactOperations[Resolution_Minutes]
    )

### Average CSAT

    Average CSAT =
    AVERAGE(
        FactOperations[CSAT]
    )

Additional measures will cover:

- QA pass rate
- Rework rate
- Repeat rate
- Escalation rate
- Data-quality rate
- Items processed
- KPI variance
- Validation status

---

## 🔄 KPI Reconciliation

The project verifies that the same business definition produces the same result across analytical layers.

    Raw Source
        ↓
    Python
        ↓
    Clean Dataset
        ↓
    SQL
        ↓
    Power BI

For each major KPI:

    Python Result
          ↓
    SQL Result
          ↓
    Power BI Result
          ↓
    Difference Check

If results differ, the discrepancy is investigated rather than ignored.

---

## 🧪 Validation Framework

### Source Validation

Checks include:

- Row counts
- Unique IDs
- Required fields
- Data types
- Date ranges
- Valid categorical values

### Data Quality Validation

Checks include:

- Duplicate records
- Missing values
- Invalid categories
- Invalid priorities
- Invalid numerical values
- Impossible dates
- Derived-field inconsistencies

### KPI Validation

Checks include:

- KPI definitions
- Filter logic
- Denominators
- NULL handling
- Status handling
- Date logic

### Reconciliation

Results are compared across:

- Python
- SQL
- Power BI

### Investigation

When a KPI does not reconcile:

1. Identify the KPI difference.
2. Compare business definitions.
3. Compare filter logic.
4. Inspect source records.
5. Check transformation logic.
6. Check SQL calculations.
7. Check DAX calculations.
8. Identify the root cause.
9. Correct the logic.
10. Recalculate and revalidate.

---

## 🏷️ Data-Quality Classification

The clean dataset uses these classifications:

| Classification | Meaning |
|---|---|
| `Valid` | Record passes validation without changes |
| `Corrected` | Invalid information was repaired using a documented rule |
| `Standardized` | Missing or inconsistent categorical information was standardized |
| `Nulled` | An invalid value could not be safely repaired and was converted to NULL |

This allows Power BI to distinguish between records that were originally clean and records that required intervention.

---

## 📅 Time Analysis

The dataset covers:

    January 2026
          ↓
    September 2026

The Power BI model supports:

- Monthly trends
- Weekly trends
- Daily analysis
- Team trends
- Priority trends
- Category trends
- SLA trends
- Resolution-time trends

A dedicated `DimDate` table supports time-intelligence analysis.

---

## 📌 Key Analytical Questions

### Operational Performance

- How many records are processed?
- What is the completion rate?
- Which teams process the most work?
- Which categories have the highest workload?
- Which channels handle the most records?

### SLA

- What percentage of measurable records meet SLA?
- Which priorities have the highest breach rate?
- Which teams contribute most to SLA breaches?
- How does SLA performance change over time?

### Quality

- What is the QA pass rate?
- Where is rework concentrated?
- Which categories have lower QA scores?
- How does QA performance relate to repeat activity?

### Customer Experience

- What is the average CSAT?
- Which categories have lower CSAT?
- Are repeat records associated with lower CSAT?

### Data Quality

- How many records contain data-quality issues?
- Which issue types occur most often?
- Which teams or categories contain the most problematic records?
- How many values were corrected?
- How many values were standardized?
- How many values were converted to NULL?

### Validation

- Do Python, SQL, and Power BI produce the same KPI?
- If not, why?
- Which business rule caused the difference?
- Can the discrepancy be traced to individual records?

---

## 📁 Project Structure

    bi-validation/
    │
    ├── README.md
    │
    ├── data/
    │   ├── BI_Validation_Raw.csv
    │   ├── BI_Validation_Clean.csv
    │   ├── BI_Validation_Data_Quality_Issues.csv
    │   └── BI_Validation_Row_Issue_Log.csv
    │
    ├── python/
    │   └── generate_bi_validation_data.py
    │
    ├── sql/
    │   ├── 01_data_quality_checks.sql
    │   ├── 02_kpi_validation.sql
    │   └── 03_reconciliation.sql
    │
    ├── powerbi/
    │   └── BI_Validation_Dashboard.pbix
    │
    ├── documentation/
    │   ├── data_dictionary.md
    │   ├── validation_rules.md
    │   └── powerbi_model.md
    │
    └── screenshots/

---

## 🛠️ Technologies

- Power BI
- DAX
- Power Query
- SQL
- Python
- Pandas
- NumPy
- Excel
- GitHub

---

## 🎯 What This Project Demonstrates

This project demonstrates practical Data Analyst skills across the complete reporting lifecycle:

- Data cleaning
- Data profiling
- Data validation
- Exploratory analysis
- SQL analysis
- KPI development
- Power Query
- Power BI data modeling
- DAX
- Dashboard development
- Data-quality monitoring
- KPI reconciliation
- Root-cause analysis
- Operational reporting
- Drilldown analysis
- Documentation
- Reproducible analytics

The central idea is:

> **A dashboard is only useful when the numbers behind it can be trusted.**

This project demonstrates the process of making those numbers trustworthy.

---

## 👤 About

**Sajid Manzoor**

Data Analyst focused on:

- SQL
- Power BI
- Python
- Excel
- KPI Reporting
- Data Quality
- Operational Analytics

GitHub:

https://github.com/sajidmanzoor730

---

## 📌 Project Status

**Current stage:** Dataset and validation framework completed.

### Next Development Stages

1. Build SQL validation scripts
2. Create the Power BI data model
3. Build Power Query transformations
4. Create DAX KPI measures
5. Build the Power BI dashboard
6. Create the KPI reconciliation page
7. Add data-quality drilldowns
8. Validate Python vs SQL vs Power BI
9. Add final screenshots
10. Complete the portfolio case study
