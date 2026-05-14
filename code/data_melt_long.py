import pandas as pd

df = pd.read_csv("operational_raw_staging.csv")

long = df.melt(
    id_vars=["report_id", "notes"],
    value_vars=[
        "total_received",
        "total_resolved",
        "total_unresolved"
    ],
    var_name="metric_id",
    value_name="value"
)

long["unit"] = "applications"

long = long[
    ["report_id", "metric_id", "value", "unit", "notes"]
]

long.to_csv("operational_metrics.csv", index=False)
