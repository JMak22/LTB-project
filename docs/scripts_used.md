## Scripts Used

### convert_ltb_report_to_md.py
Purpose:
Convert OCR annual report PDFs into markdown text files, used as an initial conversion method which was later found to have left the OCR data oddly configured (paragraphs in tables, for example) with textual loss. It was decided that another attempt will be made, using ChatGPT Model 5.5-Thinking to perform the conversion using a combination of vision processing and Python script processing.

Input:
- ocr_pdfs/*.pdf

Output:
- intermediate .md reports, superseded by later version contained in `md_reports/*.md`

### extract_names.py, dedupe_names.py, count_members.py
Purpose:
Extract adjudicator names from reports that contained biographies so that the number of adjudicators can be counted for that report year.

Input:
- *.txt files created from `raw_pdfs`, biography portions for some years, only names for other years

Output:
- intermediate extracted name CSVs
- fields likely included `source_file`, `cleaned_name`, `metadata` (ex. "Part-time member")

Followed by:
1. Creation of `canonical_names.csv` including variants (ex. "Jim" vs "James", etc)

-> Final canonical adjudicator counts in `member_counts_by_file.csv`

### data_melt_long.py
Purpose:
Converting wide form data into long form data.

### import_avg_days_hearing.py
Purpose:
Imports the .xlsx files from Tribunals Ontario Open Data

~~### convert_days_to_first_hearing.py~~
(surpassed)

### convert_avg_days_xlsx_csv.py
Purpose: 
Convert imported Excel files to CSV long form

Input:
Downloaded .xlsx files

Output:
~~`days_to_first_hearing_count.csv` -- can be found in `cleaned_data/*.csv`~~
/Avg_Days_First_Hearing/*.csv

### L1_L9_filter_avgDaysFirstHearing.py
Purpose: Filter out L1 and L9 applications from input file.

Input:
LTBAvgDayFirstHearing_all_quarters.csv

Output:
L1_L9_avg_days_chart.csv

### reporting_calendar.py
Purpose: Create list of expected reporting periods in all downloaded files to help identify gaps and classify data as either `missing_report` or `no_data_reported` or whatever I actually named that in [data_flow.md]

Input:
LTBAvgDayFirstHearing_all_quarters.csv

Output:
reporting_calendar.csv

### filter_AvgDaysHearing_app_type_singles.py
Purpose: Further separate the applications of a single type (sorting out the mess of app types in the reports so that graphing/vis is not a nightmare)

Input:
LTBAvgDayFirstHearing_all_quarters.csv

Output:
l_single_type_avg_days_chart.csv
t_single_type_avg_days_chart.csv

### count_app_type_combos.py
Purpose: count and sort the remaining applications that were filed as combinations of different types, counting most frequently occurring combinations. 

Input:
LTBAvgDayFirstHearing_all_quarters.csv

Output:
combo_application_summary.csv