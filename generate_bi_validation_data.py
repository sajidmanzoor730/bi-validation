#!/usr/bin/env python3
"""
BI Validation & Monitoring - synthetic data generator (fixed seed, fully reproducible)

Pipeline:  truth data -> inject realistic defects -> BI_Validation_Raw.csv
           raw CSV -> documented cleaning rules -> BI_Validation_Clean.csv
           independent detection on raw -> BI_Validation_Data_Quality_Issues.csv
All names/IDs are synthetic. No real companies, people, emails or phone numbers.

Usage: python generate_bi_validation_data.py [output_dir]
"""
import sys, os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, date

SEED = 20260606
OUT = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(SEED)

N = 8000
AS_OF = datetime(2026, 10, 6)
SLA = {"P1": 60, "P2": 240, "P3": 480, "P4": 960}
SLA_INV = {v: k for k, v in SLA.items()}
VALID_CATS = ["Data Review", "Account Processing", "Network Check", "Document Validation",
              "Quality Audit", "Service Request", "Exception Handling", "Record Update"]
RESOLVED_STATUSES = ["Completed", "Closed"]
QA_PASS = 85      # QA_Result = Pass if QA_Score >= 85
REWORK_QA = 80    # Rework if QA_Score < 80, or (Repeat_Flag = 1 and QA_Score < 90)

COLS = ["Record_ID", "Created_Date", "Resolved_Date", "Team", "Region", "Category", "Priority",
        "Channel", "Complexity", "Status", "Agent", "Root_Cause", "Items_Processed",
        "Resolution_Minutes", "SLA_Target_Minutes", "SLA_Status", "QA_Score", "QA_Result",
        "Rework_Flag", "CSAT", "Repeat_Flag", "Escalated_Flag", "Created_Month", "Week_Start",
        "Data_Quality_Flag"]

TEAM_SPEC = {  # weight, agent numbers, category mix, time factor
    "Operations": (30, range(1, 13), {"Account Processing": 35, "Exception Handling": 30, "Service Request": 25, "Record Update": 10}, 1.00),
    "Quality": (15, range(13, 19), {"Quality Audit": 55, "Data Review": 35, "Exception Handling": 10}, 0.95),
    "Network": (15, range(19, 25), {"Network Check": 65, "Service Request": 25, "Exception Handling": 10}, 1.05),
    "Customer Success": (22, range(25, 34), {"Service Request": 45, "Record Update": 25, "Account Processing": 20, "Exception Handling": 10}, 1.00),
    "Back Office": (18, range(34, 41), {"Document Validation": 40, "Record Update": 30, "Data Review": 30}, 1.10),
}
REGIONS = ["North", "South", "East", "West", "Central"]; REG_W = [24, 20, 22, 20, 14]
REG_F = {"North": 1.0, "South": 1.0, "East": 1.0, "West": 1.06, "Central": 0.97}
CHANNELS = ["ServiceNow", "JIRA", "Email", "Internal Queue"]; CH_W = [38, 22, 25, 15]
PRIOS = ["P1", "P2", "P3", "P4"]; PR_W = [6, 19, 45, 30]
CX = ["Low", "Medium", "High"]
CX_BY_P = {"P1": [.10, .40, .50], "P2": [.25, .45, .30], "P3": [.40, .45, .15], "P4": [.50, .40, .10]}
CX_MULT = {"Low": 0.70, "Medium": 1.00, "High": 1.35}
CX_ITEMS = {"Low": 0.8, "Medium": 1.0, "High": 1.4}
ITEMS_MEAN = {"Data Review": 24, "Account Processing": 9, "Network Check": 6, "Document Validation": 14,
              "Quality Audit": 18, "Service Request": 4, "Exception Handling": 5, "Record Update": 12}
MONTH_F = [1.00, 1.00, 1.02, 1.05, 1.12, 1.15, 1.05, 1.00, 0.98]  # Jan..Sep (May/Jun pressure)
ROOTS = ["Missing Information", "System Error", "Process Gap", "Incorrect Data", "Access Issue",
         "Network Issue", "Customer Request", "No Issue Found"]
ROOT_W = [.20, .14, .14, .18, .08, .06, .12, .08]


def pick(opts, w=None):
    opts = list(opts)
    p = None if w is None else np.array(w, float) / np.sum(w)
    return opts[int(rng.choice(len(opts), p=p))]


# ---------------------------------------------------------------- 1. truth data
days = pd.date_range("2026-01-01", "2026-09-30")
dw = np.array([(1.0 if d.weekday() < 5 else 0.12) * (1 + 0.025 * (d.month - 1)) for d in days])
dw /= dw.sum()
di = rng.choice(len(days), size=N, p=dw)
hw = np.array([1, 2, 3, 4, 4, 3, 3, 4, 4, 3, 2, 1, 1], float); hw /= hw.sum()
hh = rng.choice(np.arange(7, 20), size=N, p=hw)
mm = rng.integers(0, 60, N)
created = sorted(days[d].to_pydatetime() + timedelta(hours=int(h), minutes=int(m)) for d, h, m in zip(di, hh, mm))

agents = {}
for t, (_, nums, _, _) in TEAM_SPEC.items():
    names = [f"Agent_{n:03d}" for n in nums]
    wts = np.exp(rng.normal(0, 0.35, len(names)))
    agents[t] = (names, wts)
agent_time = {a: float(np.exp(rng.normal(0, 0.15))) for t in agents for a in agents[t][0]}
agent_qa = {a: float(rng.normal(0, 2.5)) for t in agents for a in agents[t][0]}

team_names = list(TEAM_SPEC)
truth = []
for i in range(N):
    c = created[i]
    team = pick(team_names, [TEAM_SPEC[t][0] for t in team_names])
    _, _, catmix, tf = TEAM_SPEC[team]
    cat = pick(catmix.keys(), list(catmix.values()))
    ag = pick(agents[team][0], agents[team][1])
    region = pick(REGIONS, REG_W)
    prio = pick(PRIOS, PR_W)
    cx = pick(CX, CX_BY_P[prio])
    ch = pick(CHANNELS, CH_W)
    rw = dict(zip(ROOTS, ROOT_W))
    if cat == "Network Check": rw["Network Issue"] = 0.45
    if cat == "Account Processing": rw["Access Issue"] = 0.15
    if cat in ("Data Review", "Record Update"): rw["Incorrect Data"] = 0.28
    root = pick(rw.keys(), list(rw.values()))
    target = SLA[prio]
    ratio = (0.5 * CX_MULT[cx] * (1.1 if prio == "P1" else 1.0) * agent_time[ag] * tf *
             MONTH_F[c.month - 1] * REG_F[region] * float(np.exp(rng.normal(0, 0.55))))
    minutes = int(max(5, round(target * ratio)))
    res_dt = c + timedelta(minutes=minutes)
    d_end = (date(2026, 9, 30) - c.date()).days
    p_unres = 0.04 + 0.5 * np.exp(-d_end / 5)
    unresolved = (rng.random() < p_unres) or (res_dt >= AS_OF)
    items = int(max(1, rng.poisson(ITEMS_MEAN[cat] * CX_ITEMS[cx])))
    rep = int(rng.random() < 0.045 + 0.035 * (root in ("Process Gap", "System Error")) + 0.02 * (cx == "High"))
    if unresolved:
        status = pick(["Open", "In Progress", "Pending"], [.30, .45, .25])
        breached = False
        esc = int(rng.random() < 0.02 + {"P1": .05, "P2": .03}.get(prio, 0) + 0.04 * (cx == "High"))
        row = dict(Resolved_Date=None, Resolution_Minutes=None, SLA_Status="Pending", QA_Score=None,
                   QA_Result="Not Scored", Rework_Flag=0, CSAT=None)
    else:
        status = pick(RESOLVED_STATUSES, [.60, .40])
        breached = minutes > target
        esc = int(rng.random() < 0.02 + {"P1": .05, "P2": .03}.get(prio, 0) + 0.04 * (cx == "High") + 0.03 * breached)
        if rng.random() < 0.06:
            qa = rng.uniform(55, 80)
        else:
            qa = rng.normal(93.5 + agent_qa[ag] - (2.5 if cx == "High" else 0) - (1.5 if breached else 0), 4.0)
        qa = round(float(min(100, max(50, qa))), 1)
        cs = 4.25 - 0.75 * breached - 0.6 * esc - 0.35 * rep + 0.03 * (qa - 92) + rng.normal(0, 0.55)
        cs = round(float(min(5, max(1, cs))), 1)
        rework = int(qa < REWORK_QA or (rep == 1 and qa < 90))
        row = dict(Resolved_Date=res_dt, Resolution_Minutes=minutes,
                   SLA_Status="Breached" if breached else "Met", QA_Score=qa,
                   QA_Result="Pass" if qa >= QA_PASS else "Fail", Rework_Flag=rework, CSAT=cs)
    ws = c.date() - timedelta(days=c.weekday())
    row.update(Record_ID=f"REC-{100001 + i}", Created_Date=c, Team=team, Region=region, Category=cat,
               Priority=prio, Channel=ch, Complexity=cx, Status=status, Agent=ag, Root_Cause=root,
               Items_Processed=items, SLA_Target_Minutes=target, Repeat_Flag=rep, Escalated_Flag=esc,
               Created_Month=c.strftime("%Y-%m"), Week_Start=ws, Data_Quality_Flag="Valid")
    truth.append(row)

# ---------------------------------------------------------------- 2. inject defects
R = [dict(r) for r in truth]
used, log = set(), []
res_idx = [i for i, r in enumerate(truth) if r["Status"] in RESOLVED_STATUSES]
all_idx = list(range(N))


def take(k, pool):
    cand = [i for i in pool if i not in used]
    ch = [int(x) for x in rng.choice(cand, size=k, replace=False)]
    used.update(ch)
    return ch


def note(i, issue, field):
    v = R[i][field]
    if isinstance(v, (datetime, date)): v = v.strftime("%Y-%m-%d %H:%M:%S") if isinstance(v, datetime) else v.isoformat()
    log.append((R[i]["Record_ID"], issue, field, "" if v is None else str(v)))


def inject(issue, field, k, pool, fn):
    for i in take(k, pool):
        R[i][field] = fn(i)
        note(i, issue, field)

INJ = {}
def count(issue, k): INJ[issue] = k

inject("Resolved_Before_Created", "Resolved_Date", 12, res_idx,
       lambda i: truth[i]["Created_Date"] - timedelta(minutes=int(rng.integers(30, 2880)))); count("Resolved_Before_Created", 12)
inject("Negative_Resolution_Minutes", "Resolution_Minutes", 12, res_idx, lambda i: -truth[i]["Resolution_Minutes"]); count("Negative_Resolution_Minutes", 12)
inject("QA_Score_Out_Of_Range", "QA_Score", 10, res_idx, lambda i: round(float(rng.uniform(101, 150)), 1)); count("QA_Score_Out_Of_Range", 10)
inject("Missing_CSAT", "CSAT", 45, res_idx, lambda i: None); count("Missing_CSAT", 45)
inject("Incorrect_SLA_Status", "SLA_Status", 18, res_idx, lambda i: "Breached" if truth[i]["SLA_Status"] == "Met" else "Met"); count("Incorrect_SLA_Status", 18)
inject("Missing_SLA_Status", "SLA_Status", 15, res_idx, lambda i: None); count("Missing_SLA_Status", 15)


def bad_res(i):
    t = truth[i]["Resolution_Minutes"]
    new = t + int(rng.choice([-1, 1])) * int(rng.integers(20, 400))
    return new if new > 0 else t + int(rng.integers(20, 400))
inject("Resolution_Minutes_Mismatch", "Resolution_Minutes", 25, res_idx, bad_res); count("Resolution_Minutes_Mismatch", 25)
inject("Missing_Resolution_Minutes", "Resolution_Minutes", 20, res_idx, lambda i: None); count("Missing_Resolution_Minutes", 20)
inject("Incorrect_QA_Result", "QA_Result", 20, res_idx, lambda i: "Fail" if truth[i]["QA_Result"] == "Pass" else "Pass"); count("Incorrect_QA_Result", 20)
inject("Missing_QA_Result", "QA_Result", 15, res_idx, lambda i: None); count("Missing_QA_Result", 15)

inject("Missing_Category", "Category", 75, all_idx, lambda i: None); count("Missing_Category", 75)
inject("Invalid_Category", "Category", 10, all_idx, lambda i: "Unknown_Category" if rng.random() < .7 else "Misc"); count("Invalid_Category", 10)
inject("Missing_Agent", "Agent", 55, all_idx, lambda i: None); count("Missing_Agent", 55)
inject("Invalid_Priority", "Priority", 8, all_idx, lambda i: "P5" if rng.random() < .75 else "P0"); count("Invalid_Priority", 8)
inject("Missing_SLA_Target", "SLA_Target_Minutes", 20, all_idx, lambda i: None); count("Missing_SLA_Target", 20)
inject("Incorrect_SLA_Target", "SLA_Target_Minutes", 15, all_idx, lambda i: int(rng.choice([30, 120, 300, 720, 1440]))); count("Incorrect_SLA_Target", 15)
inject("Missing_Created_Month", "Created_Month", 25, all_idx, lambda i: None); count("Missing_Created_Month", 25)


def bad_month(i):
    m0 = truth[i]["Created_Date"].month
    return f"2026-{int(rng.choice([m for m in range(1, 10) if m != m0])):02d}"
inject("Incorrect_Created_Month", "Created_Month", 15, all_idx, bad_month); count("Incorrect_Created_Month", 15)
inject("Missing_Week_Start", "Week_Start", 25, all_idx, lambda i: None); count("Missing_Week_Start", 25)


def bad_week(i):
    ws, cd = truth[i]["Week_Start"], truth[i]["Created_Date"].date()
    if cd != ws and rng.random() < .5: return cd
    return ws + timedelta(days=int(rng.choice([-7, 7])))
inject("Incorrect_Week_Start", "Week_Start", 15, all_idx, bad_week); count("Incorrect_Week_Start", 15)
inject("Incorrect_Rework_Flag", "Rework_Flag", 20, res_idx, lambda i: 1 - truth[i]["Rework_Flag"]); count("Incorrect_Rework_Flag", 20)
inject("Missing_Rework_Flag", "Rework_Flag", 10, all_idx, lambda i: None); count("Missing_Rework_Flag", 10)

# source-system Data_Quality_Flag: catches only some issues, and is blank on other rows
for i in rng.choice(sorted(used), size=60, replace=False):
    R[int(i)]["Data_Quality_Flag"] = "Review"
blank_idx = [int(x) for x in rng.choice([i for i in all_idx if R[i]["Data_Quality_Flag"] != "Review"], 120, replace=False)]
for i in blank_idx:
    R[i]["Data_Quality_Flag"] = None
    note(i, "Missing_Data_Quality_Flag", "Data_Quality_Flag")
count("Missing_Data_Quality_Flag", 120)
untouched = [i for i in all_idx if i not in used and R[i]["Data_Quality_Flag"] == "Valid"]
dup_src = [int(x) for x in rng.choice(untouched, 160, replace=False)]
for i in dup_src:
    log.append((R[i]["Record_ID"], "Duplicate_Record_ID", "Record_ID", R[i]["Record_ID"]))
count("Duplicate_Record_ID", 160)

# duplicates are re-ingested later in the file (exact copies)
keyed = [(float(i), R[i]) for i in all_idx] + [(i + float(rng.uniform(5, 1200)), dict(R[i])) for i in dup_src]
keyed.sort(key=lambda x: x[0])
raw_rows = [r for _, r in keyed]


def fmt_dt(v):
    if v is None: return None
    return v.strftime("%Y-%m-%d %H:%M:%S") if isinstance(v, datetime) else v.strftime("%Y-%m-%d")

raw = pd.DataFrame([{c: (fmt_dt(r[c]) if c in ("Created_Date", "Resolved_Date", "Week_Start") else r[c]) for c in COLS}
                    for r in raw_rows], columns=COLS)
for c in ["Items_Processed", "Resolution_Minutes", "SLA_Target_Minutes", "Rework_Flag", "Repeat_Flag", "Escalated_Flag"]:
    raw[c] = raw[c].astype("Int64")
raw.to_csv(os.path.join(OUT, "BI_Validation_Raw.csv"), index=False)

# ---------------------------------------------------------------- 3. cleaning pipeline (raw -> clean)
r0 = pd.read_csv(os.path.join(OUT, "BI_Validation_Raw.csv"), dtype=str, keep_default_na=False)
df = r0.drop_duplicates("Record_ID", keep="first").copy()                       # rule 1
cat_ok = df.Category.isin(VALID_CATS)
agent_blank = df.Agent.str.strip() == ""
prio_ok = df.Priority.isin(PRIOS)
tgt_raw = pd.to_numeric(df.SLA_Target_Minutes, errors="coerce")
prio_c = df.Priority.where(prio_ok, tgt_raw.map(SLA_INV)).fillna("P3")            # rule 5: infer from original SLA target
tgt_c = prio_c.map(SLA).astype(int)                                              # rule 8
cr = pd.to_datetime(df.Created_Date)
rs = pd.to_datetime(df.Resolved_Date.replace("", np.nan))
impossible = rs < cr
rs_c = rs.mask(impossible)                                                       # rule 6
res_c = ((rs_c - cr).dt.total_seconds() / 60).round().astype("Int64")            # rule 7
resolved_status = df.Status.isin(RESOLVED_STATUSES)
sla_c = np.where(res_c.isna(), np.where(resolved_status, "Unknown", "Pending"),
                 np.where(res_c.fillna(0) <= tgt_c, "Met", "Breached"))           # rule 9
qa_raw = pd.to_numeric(df.QA_Score, errors="coerce")
qa_bad = qa_raw.notna() & ~qa_raw.between(0, 100)
qa_c = qa_raw.mask(~qa_raw.between(0, 100))                                      # rule 4
qar_c = np.where(qa_c.isna(), "Not Scored", np.where(qa_c >= QA_PASS, "Pass", "Fail"))   # rule 10
rep = pd.to_numeric(df.Repeat_Flag)
rew_c = ((qa_c < REWORK_QA) | ((rep == 1) & (qa_c < 90))).astype(int)            # rule 11
mon_c = cr.dt.strftime("%Y-%m")                                                  # rule 12
wk_c = (cr.dt.normalize() - pd.to_timedelta(cr.dt.weekday, unit="D")).dt.strftime("%Y-%m-%d")  # rule 13
csat = pd.to_numeric(df.CSAT, errors="coerce")
csat_c = csat.where(csat.between(1, 5))                                          # rule 3 (kept NULL, not imputed)

nulled = qa_bad | impossible | (resolved_status & csat.isna())
neq = lambda a, b: ~((a == b) | (a.isna() & b.isna()))
corrected = (~prio_ok | neq(tgt_raw, tgt_c) | neq(pd.to_numeric(df.Resolution_Minutes, errors="coerce"), res_c.astype(float))
             | (df.SLA_Status != sla_c) | (df.QA_Result != qar_c)
             | neq(pd.to_numeric(df.Rework_Flag, errors="coerce"), rew_c.astype(float))
             | (df.Created_Month != mon_c) | (df.Week_Start != wk_c))
standardized = ~cat_ok | agent_blank
dq = np.select([nulled, corrected, standardized], ["Nulled", "Corrected", "Standardized"], "Valid")  # rule 14

clean = pd.DataFrame({
    "Record_ID": df.Record_ID, "Created_Date": df.Created_Date,
    "Resolved_Date": rs_c.dt.strftime("%Y-%m-%d %H:%M:%S"),
    "Team": df.Team, "Region": df.Region, "Category": df.Category.where(cat_ok, "Unknown"),
    "Priority": prio_c, "Channel": df.Channel, "Complexity": df.Complexity, "Status": df.Status,
    "Agent": df.Agent.where(~agent_blank, "Unassigned"), "Root_Cause": df.Root_Cause,
    "Items_Processed": pd.to_numeric(df.Items_Processed).astype("Int64"),
    "Resolution_Minutes": res_c, "SLA_Target_Minutes": tgt_c.astype("Int64"), "SLA_Status": sla_c,
    "QA_Score": qa_c, "QA_Result": qar_c, "Rework_Flag": rew_c.astype("Int64"), "CSAT": csat_c,
    "Repeat_Flag": rep.astype("Int64"), "Escalated_Flag": pd.to_numeric(df.Escalated_Flag).astype("Int64"),
    "Created_Month": mon_c, "Week_Start": wk_c, "Data_Quality_Flag": dq})[COLS]
clean = clean.sort_values("Record_ID").reset_index(drop=True)
clean.to_csv(os.path.join(OUT, "BI_Validation_Clean.csv"), index=False)

# ---------------------------------------------------------------- 4. independent detection on RAW -> issue summary
raw_s = r0
rs_all = pd.to_datetime(raw_s.Resolved_Date.replace("", np.nan)); cr_all = pd.to_datetime(raw_s.Created_Date)
valid_dates = rs_all.notna() & (rs_all >= cr_all)
tg = pd.to_numeric(raw_s.SLA_Target_Minutes, errors="coerce")
pr_ok = raw_s.Priority.isin(PRIOS)
pr_c = raw_s.Priority.where(pr_ok, tg.map(SLA_INV))
tg_exp = pr_c.map(SLA)
calc_min = ((rs_all - cr_all).dt.total_seconds() / 60).round()
rmin = pd.to_numeric(raw_s.Resolution_Minutes, errors="coerce")
qa = pd.to_numeric(raw_s.QA_Score, errors="coerce"); qa_in = qa.between(0, 100)
exp_status = np.where(calc_min <= tg_exp, "Met", "Breached")
rework_exp = ((qa < REWORK_QA) | ((pd.to_numeric(raw_s.Repeat_Flag) == 1) & (qa < 90))).astype(int)
rw = pd.to_numeric(raw_s.Rework_Flag, errors="coerce")
resolved_s = raw_s.Status.isin(RESOLVED_STATUSES)
wk_exp = (cr_all.dt.normalize() - pd.to_timedelta(cr_all.dt.weekday, unit="D")).dt.strftime("%Y-%m-%d")

DETECT = [  # issue, field, rule, cleaning action, mask
    ("Duplicate_Record_ID", "Record_ID", "Record_ID appears more than once (rows after the first)", "Keep first occurrence, drop the rest", raw_s.duplicated("Record_ID")),
    ("Missing_Category", "Category", "Category is blank", "Set to 'Unknown'", raw_s.Category.str.strip() == ""),
    ("Invalid_Category", "Category", "Category not in the 8 approved values", "Set to 'Unknown'", (raw_s.Category.str.strip() != "") & ~raw_s.Category.isin(VALID_CATS)),
    ("Missing_Agent", "Agent", "Agent is blank", "Set to 'Unassigned'", raw_s.Agent.str.strip() == ""),
    ("Missing_CSAT", "CSAT", "Completed/Closed record with blank CSAT", "Leave NULL (no imputation, excluded from AVG)", resolved_s & (raw_s.CSAT == "")),
    ("Negative_Resolution_Minutes", "Resolution_Minutes", "Resolution_Minutes < 0", "Recalculate from Created/Resolved dates", rmin < 0),
    ("QA_Score_Out_Of_Range", "QA_Score", "QA_Score outside 0-100", "Set to NULL; QA_Result = 'Not Scored'", qa.notna() & ~qa_in),
    ("Resolved_Before_Created", "Resolved_Date", "Resolved_Date earlier than Created_Date", "Set Resolved_Date and Resolution_Minutes to NULL; SLA_Status = 'Unknown'", rs_all < cr_all),
    ("Invalid_Priority", "Priority", "Priority not in P1-P4", "Infer from original SLA_Target_Minutes (60/240/480/960)", ~pr_ok),
    ("Incorrect_SLA_Status", "SLA_Status", "SLA_Status contradicts dates vs SLA target", "Recalculate (Met if minutes <= target)", valid_dates & (raw_s.SLA_Status != "") & (raw_s.SLA_Status != exp_status)),
    ("Missing_SLA_Status", "SLA_Status", "SLA_Status is blank", "Recalculate", raw_s.SLA_Status == ""),
    ("Missing_SLA_Target", "SLA_Target_Minutes", "SLA_Target_Minutes is blank", "Recalculate from Priority", tg.isna()),
    ("Incorrect_SLA_Target", "SLA_Target_Minutes", "SLA_Target_Minutes does not match Priority", "Recalculate from Priority", pr_ok & tg.notna() & (tg != tg_exp)),
    ("Resolution_Minutes_Mismatch", "Resolution_Minutes", "Resolution_Minutes <> minutes between Created and Resolved", "Recalculate from dates", valid_dates & (rmin >= 0) & (rmin != calc_min)),
    ("Missing_Resolution_Minutes", "Resolution_Minutes", "Resolved record with dates but blank minutes", "Recalculate from dates", valid_dates & rmin.isna()),
    ("Incorrect_QA_Result", "QA_Result", "QA_Result contradicts QA_Score (Pass if >= 85)", "Recalculate", qa_in & (raw_s.QA_Result != "") & (raw_s.QA_Result != np.where(qa >= QA_PASS, "Pass", "Fail"))),
    ("Missing_QA_Result", "QA_Result", "QA_Result is blank", "Recalculate", raw_s.QA_Result == ""),
    ("Incorrect_Rework_Flag", "Rework_Flag", "Rework_Flag contradicts rule (QA<80, or Repeat and QA<90)", "Recalculate", qa_in & rw.notna() & (rw != rework_exp)),
    ("Missing_Rework_Flag", "Rework_Flag", "Rework_Flag is blank", "Recalculate", rw.isna()),
    ("Missing_Created_Month", "Created_Month", "Created_Month is blank", "Recalculate (YYYY-MM)", raw_s.Created_Month == ""),
    ("Incorrect_Created_Month", "Created_Month", "Created_Month <> month of Created_Date", "Recalculate", (raw_s.Created_Month != "") & (raw_s.Created_Month != cr_all.dt.strftime("%Y-%m"))),
    ("Missing_Week_Start", "Week_Start", "Week_Start is blank", "Recalculate (Monday of week)", raw_s.Week_Start == ""),
    ("Incorrect_Week_Start", "Week_Start", "Week_Start is not the Monday of Created_Date's week", "Recalculate", (raw_s.Week_Start != "") & (raw_s.Week_Start != wk_exp)),
    ("Missing_Data_Quality_Flag", "Data_Quality_Flag", "Data_Quality_Flag is blank", "Recalculate (Valid/Corrected/Standardized/Nulled)", raw_s.Data_Quality_Flag == ""),
]
summ = []
for k, (issue, field, rule, action, m) in enumerate(DETECT, 1):
    n = int(m.sum())
    assert n == INJ[issue], f"{issue}: detected {n} vs injected {INJ[issue]}"
    summ.append({"Issue_ID": f"DQ{k:02d}", "Issue_Type": issue, "Affected_Field": field, "Detection_Rule": rule,
                 "Cleaning_Action": action, "Affected_Records": n,
                 "Pct_Of_Raw_Rows": round(100 * n / len(raw_s), 2)})
pd.DataFrame(summ).to_csv(os.path.join(OUT, "BI_Validation_Data_Quality_Issues.csv"), index=False)
pd.DataFrame(log, columns=["Record_ID", "Issue_Type", "Affected_Field", "Raw_Value"]).to_csv(
    os.path.join(OUT, "BI_Validation_Row_Issue_Log.csv"), index=False)

# ---------------------------------------------------------------- 5. self-checks
assert len(raw) == 8160 and clean.Record_ID.is_unique and len(clean) == 8000
flagged = set(clean.loc[clean.Data_Quality_Flag != "Valid", "Record_ID"])
issue_ids = {r for r, t, _, _ in log if t not in ("Duplicate_Record_ID", "Missing_Data_Quality_Flag")}
assert flagged == issue_ids, (len(flagged), len(issue_ids))
print("rows raw/clean:", len(raw), len(clean))
print(clean.Data_Quality_Flag.value_counts().to_dict())
done = clean.Status.isin(RESOLVED_STATUSES)
ev = clean[clean.SLA_Status.isin(["Met", "Breached"])]
print(f"Completion {done.mean():.1%} | SLA met {(ev.SLA_Status=='Met').mean():.1%} | breach {(ev.SLA_Status=='Breached').mean():.1%}"
      f" | avg res {clean.Resolution_Minutes.mean():.0f} min | CSAT {clean.CSAT.mean():.2f} | repeat {clean.Repeat_Flag.mean():.1%}"
      f" | esc {clean.Escalated_Flag.mean():.1%} | QA pass {(clean.QA_Result=='Pass').sum()/(clean.QA_Result!='Not Scored').sum():.1%}"
      f" | rework {clean.Rework_Flag.mean():.1%} | DQ valid {(clean.Data_Quality_Flag=='Valid').mean():.1%}")
