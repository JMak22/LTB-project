from pathlib import Path
import re
import pandas as pd


# ------------------------------------------------------------
# Folder setup
# ------------------------------------------------------------

INPUT_FOLDER = Path("input_xlsx")
OUTPUT_FOLDER = Path("output_csv")
OUTPUT_FOLDER.mkdir(exist_ok=True)


# ------------------------------------------------------------
# Region mapping
# ------------------------------------------------------------

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


OUTPUT_COLUMNS = [
    "report_id",
    "region_id",
    "office_code",
    "app_combo",
    "app_type",
    "avg_days",
    "performance_standard",
    "percent_in_standard",
    "source_file",
]


# ------------------------------------------------------------
# Basic cleaning helpers
# ------------------------------------------------------------

def clean_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def normalize_combo(value):
    return re.sub(r"\s+", "", clean_text(value))


def clean_numeric(value):
    """
    Keeps numeric values clean while tolerating cells like:
    35%
    31.8 days
    blank
    """
    if pd.isna(value):
        return pd.NA

    text = str(value).strip()

    if not text:
        return pd.NA

    text = (
        text.replace(",", "")
            .replace("%", "")
            .replace("days", "")
            .replace("day", "")
            .strip()
    )

    match = re.search(r"-?\d+(?:\.\d+)?", text)

    if not match:
        return pd.NA

    number = float(match.group())

    if number.is_integer():
        return int(number)

    return number


# ------------------------------------------------------------
# Filename/report parsing
# ------------------------------------------------------------

def infer_report_info_from_filename(path):
    """
    Returns report_id and standardized output filename.

    Standard output filename:
        YYYY_YYYY_Qn_LTBAvgDayFirstHearing.csv

    Example:
        2025_2026_Q2_LTBAvgDayFirstHearing.csv
    """

    name = path.name.replace("%20", " ")

    # Prefer explicit quarter label:
    # Q3 2021-2022
    # Q3 2021-22
    q_match = re.search(r"Q([1-4])\s+(\d{4})-(\d{2,4})", name, re.IGNORECASE)
    
    if q_match:
        quarter_num = q_match.group(1)
        start_year = int(q_match.group(2))
        end_year_raw = q_match.group(3)

        if len(end_year_raw) == 2:
            end_year = int(str(start_year)[:2] + end_year_raw)
        else:
            end_year = int(end_year_raw)

        report_id = f"{start_year}_{end_year}_Q{quarter_num}"
        output_filename = f"{start_year}_{end_year}_Q{quarter_num}_LTBAvgDayFirstHearing.csv"

        return {
            "report_id": report_id,
            "output_filename": output_filename,
            "quarter": f"Q{quarter_num}",
            "fiscal_start": start_year,
            "fiscal_end": end_year,
        }

    # Handle full fiscal-year files marked with FY.
    # Example:
    # 2015-04-01_2016-3-31 ... _FY.xlsx
    if re.search(r"[_\s-]FY\b", name, re.IGNORECASE):
        date_match = re.search(
            r"(\d{4})-(\d{1,2})-(\d{1,2})_(\d{4})-(\d{1,2})-(\d{1,2})",
            name,
        )

        if not date_match:
            raise ValueError(f"Could not infer fiscal year from FY filename: {path.name}")

        start_year, start_month, _, end_year, end_month, _ = map(int, date_match.groups())

        # Expected full fiscal year: April 1 to March 31.
        if start_month != 4 or end_month != 3:
            raise ValueError(f"FY file does not appear to cover Apr-Mar: {path.name}")

        report_id = f"{start_year}_{end_year}_FY"
        output_filename = f"{start_year}_{end_year}_FY_LTBAvgDayFirstHearing.csv"

        return {
            "report_id": report_id,
            "output_filename": output_filename,
            "quarter": "FY",
            "fiscal_start": start_year,
            "fiscal_end": end_year,
        }

    # Fall back to date range:
    # 2025-10-01_2025-12-31
    date_match = re.search(
        r"(\d{4})-(\d{1,2})-(\d{1,2})_(\d{4})-(\d{1,2})-(\d{1,2})",
        name,
    )

    if not date_match:
        raise ValueError(f"Could not infer report year/quarter from filename: {path.name}")

    start_year, start_month, _, end_year, end_month, _ = map(int, date_match.groups())

    quarter_lookup = {
        (4, 6): "Q1",
        (7, 9): "Q2",
        (10, 12): "Q3",
        (1, 3): "Q4",
    }

    quarter = quarter_lookup.get((start_month, end_month))

    if not quarter:
        raise ValueError(f"Could not infer quarter from filename date range: {path.name}")

    # Fiscal year runs April-March.
    if start_month in [1, 2, 3]:
        fiscal_start = start_year - 1
        fiscal_end = start_year
    else:
        fiscal_start = start_year
        fiscal_end = start_year + 1

    report_id = f"{fiscal_start}_{fiscal_end}_{quarter}"
    output_filename = f"{fiscal_start}_{fiscal_end}_{quarter}_LTBAvgDayFirstHearing.csv"

    return {
        "report_id": report_id,
        "output_filename": output_filename,
        "quarter": quarter,
        "fiscal_start": fiscal_start,
        "fiscal_end": fiscal_end,
    }


# ------------------------------------------------------------
# Workbook structure detection
# ------------------------------------------------------------

def find_office_columns(df):
    """
    Finds office-code columns in the first few rows.

    In these workbooks:
        office column = avg_days
        next column = percent_in_standard
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

    if not office_columns:
        raise ValueError("Could not find office columns such as CE, EA, NO, SO, SW, TE, TN, TS, Prov / Avg.")

    return office_columns


def is_app_combo(value):
    """
    Identifies application-code combo rows, e.g.
        L1
        L1/L9
        T2
        A1
        A1/A2
    """

    text = normalize_combo(value)

    if not text:
        return False

    if "Avg" in text:
        return False

    return bool(re.fullmatch(r"[ALT]\d+(?:/[ALT]\d+)*", text))


def app_type_with_family(app_code, current_family):
    """
    A-codes can appear under landlord or tenant sections.
    So A1 under landlord becomes A1_L.
    A1 under tenant becomes A1_T.

    L-codes and T-codes already identify their family.
    """

    app_code = clean_text(app_code)

    if re.fullmatch(r"A\d+", app_code):
        if current_family == "L":
            return f"{app_code}_L"
        if current_family == "T":
            return f"{app_code}_T"

    return app_code


def infer_performance_standard(app_combo, source_file):
    """
    L1/L9 reports use 25 business days.
    Other-applications reports use 30 business days.

    This also catches app_combo directly, in case filename detection is imperfect.
    """

    name = source_file.lower()

    if "l1" in name and "l9" in name:
        return 25

    app_parts = app_combo.split("/")

    if all(app in ["L1", "L9"] for app in app_parts):
        return 25

    return 30


# ------------------------------------------------------------
# Workbook conversion
# ------------------------------------------------------------

def convert_workbook(path):
    """
    Converts one workbook into standardized rows.
    """

    df = pd.read_excel(path, sheet_name=0, header=None, engine="openpyxl")

    report_info = infer_report_info_from_filename(path)
    office_columns = find_office_columns(df)

    rows = []
    current_family = None

    for _, row in df.iterrows():
        col_a = clean_text(row.iloc[0])

        if not col_a:
            continue

        # Track whether we are in landlord or tenant section.
        if "Landlord" in col_a and "Apps" in col_a:
            current_family = "L"
            continue

        if "Tenant" in col_a and "Apps" in col_a:
            current_family = "T"
            continue

        if not is_app_combo(col_a):
            continue

        app_combo = normalize_combo(col_a)
        app_parts = app_combo.split("/")

        for office_info in office_columns.values():
            avg_days_raw = row.iloc[office_info["avg_days_col"]]
            percent_raw = row.iloc[office_info["percent_col"]]

            avg_days = clean_numeric(avg_days_raw)
            percent_in_standard = clean_numeric(percent_raw)

            if pd.isna(avg_days) and pd.isna(percent_in_standard):
                continue

            performance_standard = infer_performance_standard(app_combo, path.name)

            for app in app_parts:
                rows.append({
                    "report_id": report_info["report_id"],
                    "region_id": office_info["region_id"],
                    "office_code": office_info["office_code"],
                    "app_combo": app_combo,
                    "app_type": app_type_with_family(app, current_family),
                    "avg_days": avg_days,
                    "performance_standard": performance_standard,
                    "percent_in_standard": percent_in_standard,
                    "source_file": path.name,
                })

    return report_info, rows


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main():
    if not INPUT_FOLDER.exists():
        raise FileNotFoundError(f"Input folder not found: {INPUT_FOLDER}")

    xlsx_files = sorted(INPUT_FOLDER.glob("*.xlsx"))

    if not xlsx_files:
        raise FileNotFoundError(f"No .xlsx files found in: {INPUT_FOLDER}")

    grouped_rows = {}
    errors = []

    for path in xlsx_files:
        print(f"Processing: {path.name}")

        try:
            report_info, rows = convert_workbook(path)

            if not rows:
                raise ValueError("No usable rows extracted.")

            output_filename = report_info["output_filename"]

            grouped_rows.setdefault(output_filename, [])
            grouped_rows[output_filename].extend(rows)

            print(f"  Extracted {len(rows)} rows -> {output_filename}")

        except Exception as e:
            print(f"  ERROR: {e}")
            errors.append({
                "source_file": path.name,
                "error": str(e),
            })

    # Write one combined CSV per fiscal year + quarter.
    for output_filename, rows in grouped_rows.items():
        output = pd.DataFrame(rows)

        output = output[OUTPUT_COLUMNS]

        output = output.sort_values(
            by=[
                "report_id",
                "region_id",
                "office_code",
                "app_combo",
                "app_type",
            ],
            na_position="last",
        )

        output_path = OUTPUT_FOLDER / output_filename
        output.to_csv(output_path, index=False, encoding="utf-8-sig")

        print(f"Wrote {len(output):,} rows to {output_path}")

    # Also write one master file for trend analysis.
    if grouped_rows:
        master_rows = []

        for rows in grouped_rows.values():
            master_rows.extend(rows)

        master = pd.DataFrame(master_rows)
        master = master[OUTPUT_COLUMNS]

        master = master.sort_values(
            by=[
                "report_id",
                "region_id",
                "office_code",
                "app_combo",
                "app_type",
            ],
            na_position="last",
        )

        master_path = OUTPUT_FOLDER / "LTBAvgDayFirstHearing_all_quarters.csv"
        master.to_csv(master_path, index=False, encoding="utf-8-sig")

        print(f"Wrote master file: {len(master):,} rows to {master_path}")

    # Write errors, if any.
    if errors:
        errors_df = pd.DataFrame(errors)
        errors_path = OUTPUT_FOLDER / "conversion_errors.csv"
        errors_df.to_csv(errors_path, index=False, encoding="utf-8-sig")

        print(f"Some files had errors. See: {errors_path}")

    print("Done.")


if __name__ == "__main__":
    main()