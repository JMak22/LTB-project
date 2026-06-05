raw_pdfs
├── manual extraction path
│   ├── LTB Rough Annual report data.ods
│   ├── LTB_data_organised.ods
│   ├── annual_report_biography_extracts.zip
│   └── cleaned_data/*.csv
│
└── OCR / markdown verification path
    ├── ocr_pdfs
    └── md_reports


## Manual extraction workflow

-> LTB Rough Annual report data.ods 
- working notes
- initial data capture

-> LTB_data_organised.ods 
- intermediate stage
- normalization, organization

-> annual_report_biography_extracts.zip
- text of reports containing biographies or just adjudicator names for some years
- used to extract names and derive a canonical list of adjudicator names, later used to derive counts

-> cleaned_data/*.csv
- published structured datasets

## OCR/text verification workflow

see above

Purpose:
- searchability
- reproducibility
- verification of manually extracted data
- support for future automated information extraction

## Average Days to First Hearing Excel sheets + related

Imported Excel from Tribunals Ontario Open Data site with `import_avg_days_hearing.py`
Converted Excel -> CSV with `convert_avg_days_xlsx_csv.py`
    Output: /Avg_Days_First_Hearing/*.csv

Using `LTBAvgDayFirstHearing_all_quarters.csv` as input:
- `L1_L9_filter_avgDaysFirstHearing.py` --> L1_L9_avg_days_chart.csv
- `reporting_calendar.py` --> reporting_calendar.csv
- `filter_AvgDaysHearing_app_type_singles.py` ---> l_single_type_avg_days_chart.csv
                                              └──> t_single_type_avg_days_chart.csv
- `count_app_type_combos.py` --> combo_application_summary.csv --> Gephi graph (Co-occurring_app_types_2015_2026.png) --> combo_app_type_gephi_export.csv (contains additional statistics on the graph, done by Gephi)
