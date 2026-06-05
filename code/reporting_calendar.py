# Script to create a reporting calendar based on the report IDs in the 
# LTBAvgDayFirstHearing_all_quarters.csv file. It generates 
# a complete list of expected report IDs, checks which reports 
# are present in the data and creates a calendar with the report status 
# (`reported` or `missing_report`)
# The resulting calendar is saved to reporting_calendar.csv. 
# It was needed to identify missing reports so that graphs/visualizations 
# would show appropriate gaps when there was no data/report and to differentiate
# between missing data and missing reports.
#
# Written by ChatGPT 5.5 Thinking, with input and debugging by JMak22
# ----------------------------------------------------------

import pandas as pd
import re

df = pd.read_csv("LTBAvgDayFirstHearing_all_quarters.csv")

# Get unique report IDs
reports = sorted(df["report_id"].dropna().unique())

# Extract all quarter-based reports
quarter_reports = []

for report in reports:
    m = re.match(r"(\d{4})_(\d{4})_Q(\d)", str(report))
    if m:
        quarter_reports.append(
            (
                int(m.group(1)),
                int(m.group(3)),
                report
            )
        )

# Determine range of years
start_year = min(y for y, q, r in quarter_reports)
end_year = max(y for y, q, r in quarter_reports)

expected = []

# Add FY report
expected.append("2015_2016_FY")

# Generate all expected quarters
for year in range(start_year, end_year + 1):
    for q in range(1, 5):
        expected.append(f"{year}_{year+1}_Q{q}")

existing = set(reports)

def period_label(report_id):
    m = re.match(r"(\d{4})_(\d{4})_Q(\d)", str(report_id))
    if m:
        return f"{m.group(1)}-{m.group(2)[-2:]} Q{m.group(3)}"

    m = re.match(r"(\d{4})_(\d{4})_FY", str(report_id))
    if m:
        return f"{m.group(1)}-{m.group(2)[-2:]} FY"

    return report_id


def period_order(report_id):
    m = re.match(r"(\d{4})_(\d{4})_Q(\d)", str(report_id))
    if m:
        return int(m.group(1)) + (int(m.group(3)) - 1) / 4

    m = re.match(r"(\d{4})_(\d{4})_FY", str(report_id))
    if m:
        # Put FY report before 2016-17 Q1
        return int(m.group(1)) - 0.5

    return None

calendar = pd.DataFrame({
    "report_id": expected
})

calendar["report_status"] = calendar["report_id"].isin(existing).map(
    {
        True: "reported",
        False: "missing_report"
    }
)

calendar["period_label"] = calendar["report_id"].apply(period_label)

calendar["period_order"] = calendar["report_id"].apply(period_order)

calendar = calendar[
    [
        "report_id",
        "period_label",
        "period_order",
        "report_status"
    ]
]

calendar.to_csv(
    "reporting_calendar.csv",
    index=False
)

print(calendar)