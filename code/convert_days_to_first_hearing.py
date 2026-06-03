from pathlib import Path
import re
import pandas as pd


INPUT_FOLDER = Path("input_xlsx")
OUTPUT_CSV = Path("days_to_first_hearing_count.csv")


OFFICE_TO_REGION_ID = {
    "CE": "region_central",
    "EA": "region_eastern",
    "NO": "region_northern",
    "SO": "region_southern",
    "SW": "region_southwestern",
    "TE": "region_torontoEast",
    "TN": "region_torontoNorth",
    "TS": "region_torontoSouth",
    "Prov / Avg.": "province_average",
}


def clean_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def normalize_combo(value):
    return re.sub(r"\s+", "", clean_text(value))


def infer_report_id_from_filename(path):
    name = path.name

    # Prefer explicit quarter label, e.g. Q3 2021-2022 or Q3 2018-19
    q_match = re.search(r"Q([1-4])\s+(\d{4})-(\d{2,4})", name, re.IGNORECASE)
    if q_match:
        quarter = q_match.group(1)
        start_year = int(q_match.group(2))
        end_year_raw = q_match.group(3)

        if len(end_year_raw) == 2:
            end_year = int(str(start_year)[:2] + end_year_raw)
        else:
            end_year = int(end_year_raw)

        return f"{start_year}_{end_year}_q{quarter}"

    # Fall back to date range
    match = re.search(
        r"(\d{4})-(\d{1,2})-(\d{1,2})_(\d{4})-(\d{1,2})-(\d{1,2})",
        name
    )

    if not match:
        return path.stem

    start_year, start_month, _, end_year, end_month, _ = map(int, match.groups())

    fiscal_year = f"{start_year}_{start_year + 1}"

    if start_month == 4 and end_month == 3:
        return fiscal_year

    quarter_lookup = {
        (4, 6): "q1",
        (7, 9): "q2",
        (10, 12): "q3",
        (1, 3): "q4",
    }

    quarter = quarter_lookup.get((start_month, end_month))

    if quarter:
        return f"{fiscal_year}_{quarter}"

    return f"{start_year}_{end_year}"


def app_type_with_family(app_code, current_family):
    """
    Only A-codes need family suffix because L-codes and T-codes
    already encode their application family.
    """
    app_code = clean_text(app_code)

    if re.fullmatch(r"A\d+", app_code):
        if current_family == "L":
            return f"{app_code}_L"
        if current_family == "T":
            return f"{app_code}_T"

    return app_code


def find_office_columns(df):
    """
    Finds columns where office codes appear, then assumes:
    office col = avg_days
    following col = percent_in_standard
    """
    office_columns = {}

    for row_idx in range(min(10, len(df))):
        for col_idx, value in enumerate(df.iloc[row_idx]):
            text = clean_text(value)

            if text in OFFICE_TO_REGION_ID:
                office_columns[col_idx] = {
                    "office_code": text,
                    "region_id": OFFICE_TO_REGION_ID[text],
                    "avg_days_col": col_idx,
                    "percent_col": col_idx + 1,
                }

    return office_columns


def is_app_combo(value):
    text = normalize_combo(value)

    if not text:
        return False

    if "Avg" in text:
        return False

    return bool(re.fullmatch(r"[ALT]\d+(?:/[ALT]\d+)*", text))

def infer_performance_standard(app_combo, source_file):
    name = source_file.lower()

    if "l1" in name and "l9" in name:
        return 25

    app_parts = app_combo.split("/")

    if all(app in ["L1", "L9"] for app in app_parts):
        return 25

    return 30

def convert_workbook(path):
    df = pd.read_excel(path, sheet_name=0, header=None)
    print(df.head(15))

    report_id = infer_report_id_from_filename(path)
    office_columns = find_office_columns(df)

    rows = []
    current_family = None

    for _, row in df.iterrows():
        col_a = clean_text(row.iloc[0])
        col_a_norm = normalize_combo(col_a)

        if not col_a:
            continue

        if "Landlord" in col_a and "Apps" in col_a:
            current_family = "L"
            continue

        if "Tenant" in col_a and "Apps" in col_a:
            current_family = "T"
            continue

        if not is_app_combo(col_a):
            continue

        app_combo = col_a_norm
        app_parts = app_combo.split("/")

        for office_info in office_columns.values():
            avg_days = row.iloc[office_info["avg_days_col"]]
            percent_in_standard = row.iloc[office_info["percent_col"]]

            if pd.isna(avg_days) and pd.isna(percent_in_standard):
                continue

            performance_standard = infer_performance_standard(app_combo, path.name)
            
            for app in app_parts:
                rows.append({
                    "report_id": report_id,
                    "region_id": office_info["region_id"],
                    "office_code": office_info["office_code"],
                    "app_combo": app_combo,
                    "app_type": app_type_with_family(app, current_family),
                    "avg_days": avg_days,
                     "performance_standard": performance_standard,
                    "percent_in_standard": percent_in_standard,
                    "source_file": path.name,
                })

    return rows
   

def main():
    all_rows = []

    for path in sorted(INPUT_FOLDER.glob("*.xlsx")):
        rows = convert_workbook(path)
        print(f"{path.name}: {len(rows)} rows")
        all_rows.extend(rows)

    output = pd.DataFrame(all_rows)

    print(output["report_id"].value_counts().sort_index())
    print(output["app_type"].value_counts().sort_index())

    output.to_csv(OUTPUT_CSV, index=False)
    print(f"Wrote {len(output):,} rows to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()