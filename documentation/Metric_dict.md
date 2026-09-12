| metric_id                    | display_name                                                                           | notes                               |
| ---------------------------- | -------------------------------------------------------------------------------------- | ----------------------------------- |
| total_received               | Applications received                                                                  |                                     |
| total_resolved               | Applications resolved                                                                  |                                     |
| total_unresolved             | Unresolved applications                                                                |                                     |
| cost_filing                  | Cost of filing                                                                         |                                     |
| cost_filing_tenant           | Cost of filing for the tenant                                                          |                                     |
| budget_expenditures          | Budget expenditures                                                                    |                                     |
| salaries_wages               | Salaries and wages                                                                     |                                     |
| other_expenses               | Other direct operating expenses                                                        |                                     |
| benefits                     | Benefits (paid to employees)                                                           |                                     |
| revenue                      | Revenue                                                                                |                                     |
| adjudicators_FT              | Full time adjudicators                                                                 |                                     |
| adjudicators_PT              | Part time adjudicators                                                                 |                                     |
| staff                        | Staff (assuming administrative and customer service)                                   |                                     |
| adjudicators_FTE             | Full time equivalent number of adjudicators                                            |                                     |
| staff_FTE                    | Full time equivalent number of staff                                                   |                                     |
| region_central               | Central region (see map)                                                               |                                     |
| region_eastern               | Eastern region (see map)                                                               |                                     |
| region_northern              | Northern region                                                                        |                                     |
| region_southern              | Southern region                                                                        |                                     |
| region_southwestern          | Southwestern region                                                                    |                                     |
| region_torontoNorth          | Toronto North region                                                                   |                                     |
| region_torontoEast           | Toronto East region                                                                    |                                     |
| region_torontoSouth          | Toronto South region                                                                   |                                     |
| landlord_received            | Applications received from landlords                                                   |                                     |
| tenant_received              | Applications received from tenants                                                     |                                     |
| resolved_abandoned           | Ordered by hearing abandoned                                                           |                                     |
| resolved_mediation           | Mediated; ordered by hearing mediated                                                  |                                     |
| resolved_hearing             | Ordered by hearing contested or uncontested; ordered by review                         |                                     |
| resolved_wo_hearing          | Ordered ex parte; ordered by section 206 agreement                                     |                                     |
| review_submitted             | Case submitted for review                                                              |                                     |
| review_denied                | Case review denied                                                                     |                                     |
| review_sentHearing           | Review sent to a hearing                                                               |                                     |
| resolved_withdrawn           | Case resolved through withdrawal                                                       |                                     |
| resolved_other               | Discontinued; order voided; ordered amended; amendment denied                          |                                     |
| mediation_attempted          | Attempted mediation                                                                    |                                     |
| mediation_rate               | Portion of cases resolved through mediation                                            |                                     |
| resolved_withdrawn_mediation | Number of cases withdrawn due to mediation                                             |                                     |
| additional_staff             | Additional staff members                                                               |                                     |
| canonical_names_found        | Number of canonical adjudicator names found in report                                  | Check Methodology_notes for process |
| part_time_names_found        | Number of canonical adjudicator names followed by “(Part Time member)” or some variant | As above                            |
| cases                 | Number of applications/cases for a specific application type                            | Used in app_type_metrics.csv; scoped by app_code/applicant type |
| defaults              | Number of defaults for a specific application type                                     | Used in app_type_metrics.csv where reported |
| hearings              | Number of hearings for a specific application type                                    | Used in app_type_metrics.csv where reported |
| time_per_hearing      | Average time per hearing for a specific application type                              | Used in app_type_metrics.csv where reported |
| avg_days              | Average number of days                                                                | Used in Avg Days to First Hearing/service standard data |
| performance_standard  | Service standard threshold in business days                                          | Example: 25 business days for L1/L9; 30 for other applications |
| percent_in_standard   | Percentage of applications within the applicable service standard                     | Preserves provenance for “% within standard” values from original Tribunals Ontario Open Data files|
