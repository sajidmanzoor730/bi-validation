-- BI Validation: independent SQL quality checks (SQLite-compatible).
-- Load BI_Validation_Clean.csv as a table named BI_Validation_Clean.
-- Each query should return zero rows/count for a clean result unless noted.

-- 1. Duplicate business keys (expected: zero).
SELECT Record_ID, COUNT(*) AS occurrences
FROM BI_Validation_Clean
GROUP BY Record_ID
HAVING COUNT(*) > 1;

-- 2. Invalid priority-to-SLA mapping (expected: zero).
SELECT Record_ID, Priority, SLA_Target_Minutes
FROM BI_Validation_Clean
WHERE (Priority = 'P1' AND SLA_Target_Minutes <> 60)
   OR (Priority = 'P2' AND SLA_Target_Minutes <> 240)
   OR (Priority = 'P3' AND SLA_Target_Minutes <> 480)
   OR (Priority = 'P4' AND SLA_Target_Minutes <> 960)
   OR Priority NOT IN ('P1', 'P2', 'P3', 'P4');

-- 3. Resolved date earlier than created date (expected: zero).
SELECT Record_ID, Created_Date, Resolved_Date
FROM BI_Validation_Clean
WHERE Resolved_Date <> ''
  AND datetime(Resolved_Date) < datetime(Created_Date);

-- 4. Resolution minutes do not reconcile to timestamps (expected: zero).
SELECT Record_ID, Resolution_Minutes,
       ROUND((julianday(Resolved_Date) - julianday(Created_Date)) * 1440) AS Expected_Minutes
FROM BI_Validation_Clean
WHERE Resolved_Date <> ''
  AND CAST(Resolution_Minutes AS INTEGER) <>
      ROUND((julianday(Resolved_Date) - julianday(Created_Date)) * 1440);

-- 5. SLA status does not reconcile to resolution time and target (expected: zero).
SELECT Record_ID, SLA_Status, Resolution_Minutes, SLA_Target_Minutes
FROM BI_Validation_Clean
WHERE Resolved_Date <> ''
  AND SLA_Status <> CASE
      WHEN CAST(Resolution_Minutes AS INTEGER) <= CAST(SLA_Target_Minutes AS INTEGER)
      THEN 'Met' ELSE 'Breached' END;

-- 6. Invalid QA values or result labels (expected: zero).
SELECT Record_ID, QA_Score, QA_Result
FROM BI_Validation_Clean
WHERE (QA_Score <> '' AND
       (CAST(QA_Score AS REAL) < 0 OR CAST(QA_Score AS REAL) > 100))
   OR QA_Result <> CASE
       WHEN QA_Score = '' THEN 'Not Scored'
       WHEN CAST(QA_Score AS REAL) >= 85 THEN 'Pass'
       ELSE 'Fail' END;

-- 7. KPI baseline for independent reconciliation.
SELECT
  COUNT(*) AS total_records,
  ROUND(100.0 * SUM(CASE WHEN Status IN ('Completed','Closed') THEN 1 ELSE 0 END) / COUNT(*), 2) AS completion_pct,
  ROUND(100.0 * SUM(CASE WHEN SLA_Status = 'Met' THEN 1 ELSE 0 END) /
    NULLIF(SUM(CASE WHEN SLA_Status IN ('Met','Breached') THEN 1 ELSE 0 END), 0), 2) AS sla_achievement_pct,
  ROUND(AVG(CASE WHEN CSAT <> '' THEN CAST(CSAT AS REAL) END), 2) AS average_csat,
  ROUND(100.0 * SUM(CASE WHEN QA_Result = 'Pass' THEN 1 ELSE 0 END) /
    NULLIF(SUM(CASE WHEN QA_Result IN ('Pass','Fail') THEN 1 ELSE 0 END), 0), 2) AS qa_pass_pct
FROM BI_Validation_Clean;
