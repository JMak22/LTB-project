from pathlib import Path
import sqlite3
import pandas as pd
import shutil

REPO_ROOT = Path(__file__).resolve().parents[1]

CSV_DIR = REPO_ROOT / "cleaned_data"
MARKDOWN_DICT = CSV_DIR / "Metric_dict.md"
PUBLIC_MD_DICT = REPO_ROOT / "docs" / "Metric_dict.md"
OUTPUT_DB = REPO_ROOT / "docs" / "data" / "ltb_metrics.sqlite"

CSV_TABLES = {
    "reports.csv": "reports",
    "operational_metrics.csv": "operational_metrics",
    "financial_metrics.csv": "financial_metrics",
    "staffing_metrics.csv": "staffing_metrics",
    "regional_metrics.csv": "regional_metrics",
    "resolution_metrics.csv": "resolution_metrics",
    "app_type_metrics.csv": "app_type_metrics",
    "app_type_dictionary.csv": "app_type_dictionary",
    "member_counts_by_file.csv": "member_counts_by_file",
    "landlord_vs_tenant_receipts.csv": "landlord_vs_tenant_receipts"
}

def main():
    OUTPUT_DB.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(OUTPUT_DB) as conn:
        for csv_filename, table_name in CSV_TABLES.items():
            csv_path = CSV_DIR / csv_filename

            if not csv_path.exists():
                print(f"Skipping missing file: {csv_path}")
                continue

            print(f"Loading {csv_filename} -> {table_name}")
            df = pd.read_csv(csv_path)
            df.to_sql(table_name, conn, if_exists="replace", index=False)
        
        if MARKDOWN_DICT.exists():
           print("Loading markdown data dictionary")

           md_text = MARKDOWN_DICT.read_text(encoding="utf-8")

           md_df = pd.DataFrame([{
                "document_name": "metric_dictionary",
                "markdown_content": md_text
           }])

           md_df.to_sql(
                "documentation",
                conn,
                if_exists="replace",
                index=False
           )

    if MARKDOWN_DICT.exists():
       shutil.copy2(MARKDOWN_DICT, PUBLIC_MD_DICT)
       print(f"Copied markdown dictionary to: {PUBLIC_MD_DICT}")
    
    print(f"\nDone. Rebuilt database:")
    print(OUTPUT_DB)

if __name__ == "__main__":
    main()