# BI Validation & Monitoring - Data Package

Seed: 20260606 | Period: 2026-01-01 to 2026-09-30 (as-of 2026-10-06) | All data synthetic.

## Files
| File | Rows | Purpose |
|---|---|---|
| BI_Validation_Raw.csv | 8,160 | Source extract with injected defects |
| BI_Validation_Clean.csv | 8,000 | Cleaned, one row per Record_ID |
| BI_Validation_Data_Quality_Issues.csv | 24 | Issue type, rule, action, affected count |
| BI_Validation_Row_Issue_Log.csv | 765 | Record-level issues (for drilldown) |
| generate_bi_validation_data.py | - | Reproduces everything |

## Business rules
- SLA targets: P1=60, P2=240, P3=480, P4=960 min. Met if Resolution_Minutes <= target.
- Resolution_Minutes = minutes between Created_Date and Resolved_Date.
- Completion = Status in (Completed, Closed). Unresolved rows: SLA_Status = Pending.
- QA_Result: Pass if QA_Score >= 85, else Fail; no score = "Not Scored".
- Rework_Flag = 1 if QA_Score < 80, or (Repeat_Flag = 1 and QA_Score < 90).
- Week_Start = Monday of Created_Date week; Created_Month = YYYY-MM.

## Cleaning rules (applied in order)
1. Drop duplicate Record_ID (keep first).
2. Blank/invalid Category -> "Unknown"; blank Agent -> "Unassigned".
3. CSAT: left NULL when missing (no imputation); out-of-range -> NULL.
4. QA_Score outside 0-100 -> NULL (QA_Result "Not Scored").
5. Invalid Priority (P5/P0) -> inferred from the original SLA_Target_Minutes.
6. Resolved_Date < Created_Date -> Resolved_Date NULL.
7. Resolution_Minutes recalculated from dates (NULL if no valid Resolved_Date).
8. SLA_Target_Minutes recalculated from Priority.
9. SLA_Status recalculated (Met / Breached / Pending / Unknown if closed with no valid date).
10-13. QA_Result, Rework_Flag, Created_Month, Week_Start recalculated.
14. Data_Quality_Flag (precedence): Nulled > Corrected > Standardized > Valid.

Raw Data_Quality_Flag is the unreliable source flag (Valid / Review / blank).
