# This script filters the LTB average days to first hearing data to only include 
# single application types (no combos), as an attempt to triage the multitude of
# app combinations found in the reports. It also builds out the full grid of `report_id`
# x `app_type` combinations, so that missing data can be clearly identified as 
# either `not_reported` (report submitted but no data) or `missing_report` 
# (no report submitted at all), based on the report_status field from 
# reporting_calendar.csv
# The output is l-type and t-type csv files ready for charting.
# L1 and L9 apps already have their own csv files (see output from 
# `L1_L9_filter_avgDaysFirstHearing.py`).
# 
# Written by ChatGPT 5.5 Thinking, with input and debugging by JMak22.
# ------------------------------------------------------------------


import pandas as pd
from pathlib import Path

INPUT = "LTBAvgDayFirstHearing_all_quarters.csv"
CALENDAR_INPUT = "reporting_calendar.csv"

OUTPUT_DIR = Path("data")
OUTPUT_DIR.mkdir(exist_ok=True)

L_OUTPUT = OUTPUT_DIR / "l_single_type_avg_days_chart.csv"
T_OUTPUT = OUTPUT_DIR / "t_single_type_avg_days_chart.csv"

df = pd.read_csv(INPUT)
calendar = pd.read_csv(CALENDAR_INPUT)

# Keep provincial average only
df = df[df["region_id"] == "province_average"].copy()

# Keep only single application types
df = df[~df["app_combo"].astype(str).str.contains("/", regex=False)].copy()

# Keep rows where app_combo and app_type match
# This avoids duplicated/expanded combo data
df = df[df["app_combo"] == df["app_type"]].copy()

# Exclude L1 and L9 because they already have their own prototype chart
df = df[~df["app_type"].isin(["L1", "L9"])].copy()

# Ensure numeric fields behave
df["avg_days"] = pd.to_numeric(df["avg_days"], errors="coerce")
df["performance_standard"] = pd.to_numeric(df["performance_standard"], errors="coerce")
df["percent_in_standard"] = pd.to_numeric(df["percent_in_standard"], errors="coerce")

# Keep only columns needed from source data
data_cols = [
    "report_id",
    "app_combo",
    "app_type",
    "avg_days",
    "performance_standard",
    "percent_in_standard",
]

df = df[data_cols].copy()

# Build complete report_id x app_type grid
app_types = sorted(df["app_type"].dropna().unique())

app_type_grid = pd.DataFrame({"app_type": app_types})

grid = (
    calendar.assign(key=1)
    .merge(app_type_grid.assign(key=1), on="key")
    .drop(columns="key")
)

# Merge real data onto complete grid
merged = grid.merge(
    df,
    on=["report_id", "app_type"],
    how="left"
)

# If app_combo is missing because no row existed, use app_type as the app_combo
merged["app_combo"] = merged["app_combo"].fillna(merged["app_type"])

# Assign data status
merged["data_status"] = "reported"

merged.loc[
    (merged["report_status"] == "missing_report") & (merged["avg_days"].isna()),
    "data_status"
] = "missing_report"

merged.loc[
    (merged["report_status"] == "reported") & (merged["avg_days"].isna()),
    "data_status"
] = "not_reported"

# Keep/reorder chart-ready columns
cols = [
    "report_id",
    "period_label",
    "period_order",
    "report_status",
    "app_combo",
    "app_type",
    "avg_days",
    "performance_standard",
    "percent_in_standard",
    "data_status",
]

merged = merged[cols].sort_values(["period_order", "app_type"])

# Split into L-type and T-type
l_type = merged[merged["app_type"].str.startswith("L", na=False)].copy()
t_type = merged[merged["app_type"].str.startswith("T", na=False)].copy()

l_type.to_csv(L_OUTPUT, index=False)
t_type.to_csv(T_OUTPUT, index=False)

print(f"Wrote {len(l_type)} L-type rows to {L_OUTPUT}")
print(f"Wrote {len(t_type)} T-type rows to {T_OUTPUT}")

print("\nData status counts:")
print(merged["data_status"].value_counts())