# Data Dictionary

Source: `BI_Validation_Clean.csv` (8,000 synthetic operational records).
All data is fictional and intended for portfolio demonstration.

| Column | Suggested Power BI type | Meaning | Validation / interpretation |
|---|---|---|---|
| Record_ID | Text | Unique synthetic record key | Must be present and unique |
| Created_Date | Date/Time | Record creation timestamp | Required; drives reporting date |
| Resolved_Date | Date/Time | Resolution timestamp | Blank for unresolved or unreliable timestamps |
| Team | Text | Operational team | Team responsible for the record |
| Region | Text | Operating region | North, South, East, West or Central |
| Category | Text | Work category | Approved category or Unknown |
| Priority | Text | Priority band | P1, P2, P3 or P4 |
| Channel | Text | Intake channel | ServiceNow, JIRA, Email or Internal Queue |
| Complexity | Text | Work complexity | Low, Medium or High |
| Status | Text | Workflow status | Completed, Closed, Open, In Progress or Pending |
| Agent | Text | Synthetic assigned agent | Missing / invalid values are handled by cleaning rules |
| Root_Cause | Text | Classified cause | Synthetic issue classification |
| Items_Processed | Whole number | Number of items processed | Non-negative operational volume |
| Resolution_Minutes | Whole number | Minutes from creation to resolution | Blank when unresolved; derived from valid timestamps |
| SLA_Target_Minutes | Whole number | Target duration for the priority | P1 60; P2 240; P3 480; P4 960 |
| SLA_Status | Text | SLA outcome | Met, Breached, Pending or Unknown |
| QA_Score | Decimal | Quality score | 0–100; blank when not scored |
| QA_Result | Text | QA outcome | Pass (score >=85), Fail, or Not Scored |
| Rework_Flag | Whole number | Rework indicator | 1 when QA <80 or repeat record has QA <90; else 0 |
| CSAT | Decimal | Customer satisfaction score | 1–5; blank when unavailable |
| Repeat_Flag | Whole number | Repeat-contact indicator | 1 = repeat; 0 = not repeat |
| Escalated_Flag | Whole number | Escalation indicator | 1 = escalated; 0 = not escalated |
| Created_Month | Text | Creation month label | YYYY-MM derived from Created_Date |
| Week_Start | Date | Monday of creation week | Derived from Created_Date |
| Data_Quality_Flag | Text | Cleaning outcome classification | Valid, Corrected, Standardized or Nulled |

## KPI definitions and denominators

- **Completion rate:** records with Status Completed or Closed / all records.
- **SLA achievement:** Met / (Met + Breached). Pending and Unknown are excluded.
- **Average resolution time:** average Resolution_Minutes for nonblank resolved records.
- **Average CSAT:** average of nonblank CSAT scores.
- **Repeat rate:** records with Repeat_Flag = 1 / all records.
- **Escalation rate:** records with Escalated_Flag = 1 / all records.
- **QA pass rate:** Pass / (Pass + Fail). Not Scored is excluded.
- **Rework rate:** records with Rework_Flag = 1 / all records.
- **Valid data rate:** records with Data_Quality_Flag = Valid / all records.

The denominator is stated explicitly to avoid comparing percentages calculated on different populations.
