# Canonical Datasets

## app_type_dictionary.csv
Dictionary of application types.
Columns: app_code,first_year,last_year,applicant_type,description,notes

## app_type_metrics.csv
Primary dataset for application type metrics by year.
Columns: report_id,app_code,description,metric_id,value,data_status

## financial_metrics.csv
Primary dataset for financial data, for the years where it was reported in Annual Reports. Additional data may be available in Tribunals Ontario Financial Reports.
Columns: report_id,metric_id,value,currency,notes

## operational_metrics.csv
Primary dataset for operational metrics (applications received, resolved and unresolved). Note that not all data values (ex. `total_resolved`) were reported in all years.
Columns: report_id,metric_id,value,unit,notes

## regional_metrics.csv
Primary dataset for operational metrics by region, for the years when these were reported by region. If I find a map of the regions, I'll include it in `/vis/` for clarity.
Columns: report_id,region_id,metric_id,value,unit,notes

## reports.csv
Distinguishes between `report_id` (ex. `1998_1999`) and `report_label` (ex. `1998-1999`)
Columns: report_id,report_label,start_period,end_period,report_period_notes

## resolution_metrics.csv
Primary dataset for the different resolution types (documented in `Metric_dict_mkdwn.md`), for the years when resolutions by type were published in Annual Reports (2013-2018).
Columns: report_id,metric_id,value,unit,notes

## staffing_metrics.csv
Primary dataset used to count number of adjudicators (full time and part time), derived in part from `member_counts_by_file.csv` and partly from numbers reported in Annual Reports.
Note that the number of Dispute Resolution Officers has not been reported so far.
Columns: report_id,metric_id,value,unit,notes

### member_counts_by_file.csv
Count of canonical names in each Annual Report that contained biographies of adjudicators. 
Columns: file,canonical_names_found,part_time_names_found,names_found

## landlord_vs_tenant_receipts.csv
Tracks percentage of applications received from landlord-type applications and tenant-type applications.
Columns: report_id,landlord_received,tenant_received,value_type,status

## /Avg_Days_First_Hearing/*.csv
## LTBAvgDayFirstHearing_all_quarters.csv
Tracks all applications filed with the LTB from FY 2015-16 until Q4 2025-26.
Columns: report_id,region_id,office_code,app_combo,app_type,avg_days,performance_standard,percent_in_standard,source_file

### L1_L9_avg_days_chart.csv
Average days to first hearing for L1 and L9 reports, 2015-2026.
Columns: report_id,period_label,period_order,app_combo,app_type,avg_days,performance_standard,percent_in_standard

### reporting_calendar.csv
List of expected reports, one per quarter from 2016-2026. Note that 2015-2016 was reported as a full fiscal year (FY) report.

### l_single_type_avg_days_chart.csv
Average days to first hearing for L-type applications that were filed as a single-type application.
Columns: report_id,period_label,period_order,report_status,app_combo,app_type,avg_days,performance_standard,percent_in_standard,data_status

### t_single_type_avg_days_chart.csv
Average days to first hearing for T-type applications that were filed as a single-type application.
Columns: report_id,period_label,period_order,report_status,app_combo,app_type,avg_days,performance_standard,percent_in_standard,data_status

### combo_application_summary.csv
Count of all the different application types that were filed together, together with a count of reporting periods in which they showed up and a frequency count of applications/period. Used as input to create a graph of commonly co-occurring applications in Gephi, [/vis/Co-occurring_app_types_2015_2026.png]
Columns: combo_family,app_combo,count,periods_present,count_per_period