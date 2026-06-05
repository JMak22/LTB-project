# This script filters the LTBAvgDayFirstHearing_all_quarters.csv to keep 
# only L1 and L9 rows, adds a period_order column for sorting, and 
# a period_label column for readable labels. The output is saved to 
# L1_L9_avg_days_chart.csv, intended for visualization/graphing.
# 
# Written by ChatGPT 5.5 Thinking, with input and debugging by JMak22
# ----------------------------------------------------------

import pandas as pd
import re

INPUT = "LTBAvgDayFirstHearing_all_quarters.csv"
OUTPUT = "L1_L9_avg_days_chart.csv"

df = pd.read_csv(INPUT)

# Keep only provincial L1 and L9 rows
chart = df[
    (df["region_id"] == "province_average") &
    (df["app_combo"].isin(["L1", "L9"]))
].copy()

# Turn report_id into sortable period_order and readable labels
def period_order(report_id):
    # Example: 2016_2017_Q1
    m = re.match(r"(\d{4})_(\d{4})_Q(\d)", report_id)
    if m:
        start_year = int(m.group(1))
        q = int(m.group(3))
        return start_year + (q - 1) / 4

    # Example: 2015_2016_FY
    m = re.match(r"(\d{4})_(\d{4})_FY", report_id)
    if m:
        start_year = int(m.group(1))
        return start_year + 0.5

    return None

def period_label(report_id):
    m = re.match(r"(\d{4})_(\d{4})_Q(\d)", report_id)
    if m:
        return f"{m.group(1)}-{m.group(2)[-2:]} Q{m.group(3)}"

    m = re.match(r"(\d{4})_(\d{4})_FY", report_id)
    if m:
        return f"{m.group(1)}-{m.group(2)[-2:]} FY"

    return report_id

chart["period_order"] = chart["report_id"].apply(period_order)
chart["period_label"] = chart["report_id"].apply(period_label)

chart = chart[
    [
        "report_id",
        "period_label",
        "period_order",
        "app_combo",
        "app_type",
        "avg_days",
        "performance_standard",
        "percent_in_standard",
    ]
].sort_values(["period_order", "app_combo"])

chart.to_csv(OUTPUT, index=False)

print(f"Wrote {len(chart)} rows to {OUTPUT}")