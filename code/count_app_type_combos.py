# Count the different combinations of application types to determine which combos are most 
# frequent and identify filing patterns. 
#
# The output CSV was used to create a graph in Gephi to visualize the connections between
# the different application types. The graph is attached to the repo as a .png
# 
# Written by ChatGPT 5.5 Thinking, with input and debugging by JMak22.
# -------------------------------------------------------------

import pandas as pd

df = pd.read_csv("LTBAvgDayFirstHearing_all_quarters.csv")

def combo_family(combo):
    parts = str(combo).split("/")

    has_l = any(part.startswith("L") for part in parts)
    has_t = any(part.startswith("T") for part in parts)

    if has_l and has_t:
        return "Mixed"

    if has_l:
        return "Landlord"

    if has_t:
        return "Tenant"

    return "Other"

combo_df = df[
    df["app_combo"].astype(str).str.contains("/", regex=False)
].copy()

combo_df["combo_family"] = combo_df["app_combo"].apply(combo_family)

combo_counts = (
    combo_df
    .groupby(["combo_family","app_combo"])
    .size()
    .reset_index(name="count")
    .sort_values(
        ["combo_family", "count"],
        ascending=[True, False]
    )
)

combo_years = (
    combo_df.groupby("app_combo")["report_id"]
    .nunique()
    .reset_index(name="periods_present")
    .sort_values("periods_present", ascending=False)
)

combo_summary = combo_counts.merge(
    combo_years,
    on="app_combo",
    how="left"
)

combo_summary["count_per_period"] = (
    combo_summary["count"]
    / combo_summary["periods_present"]
)

combo_summary = combo_summary.sort_values(
    ["combo_family", "count"],
    ascending=[True, False]
)

print(combo_summary)

combo_summary.to_csv(
    "combo_application_summary.csv",
    index=False
)
