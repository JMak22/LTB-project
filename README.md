# LTB Project

This project aims to discover what can and cannot be known about LTB usage given currently available data and its structure.

## Data Sources
- tribunalsontario.ca and its predecessors (via archive.org) -- source of Annual Reports
- CanLII -- source of metadata on LTB cases (note that this is a portion of all cases submitted and heard at the LTB)

## Ethical Considerations
This project uses publicly available information for research and civic analysis purposes. We will take care to comply with applicable Canadian privacy laws and to avoid publishing information or analyses that could cause harm to individuals or groups.

## Current Workflow
- downloaded metadata via CanLII API
- downloaded ORHT/LTB Annual Reports
- OCRs of Annual Reports
- created one documents for Annual reports from 1998 to fiscal 2024-2025
- currently engaged in cleaning up CanLII metadata and operational data from Annual Reports

### Ongoing:
- updating Metric_dict_mkdwn as new metric_ids are identified

### Data clean up finished:
- Operational metrics -- contains number of applications filed, resolved and unresolved for each report year. Some data is not available but can be calculated
- Regional metrics -- contains number of applications filed, resolved and unresolved in each of the 8 regions for report years 1998-2014
- Financial metrics -- contains the cost of filing for the years when it was reported in the Annual Reports; as well as budget, expenditures, salaries, other expenses and revenue for report years 2006-07, 2007-08 and 2009-10. Operating budgets were not reported in other Annual Reports, the data may be available elsewhere.
- Staffing metrics -- contains information about the number of adjudicators and, occasionally, other staff members. See [[Methodology_notes]] for how staffing metrics were extracted and counted for the years where adjudicator biographies were included in the reports (1998-2010)
- Reports -- list of report years -- this may need editing to include notes on relevant legislature changes over the years

### To do:
- create applic_type_dict which will contain application type codes and explanations of each type
- create applic_type_metrics from Annual Report data
- create resolution_metrics from Annual Report data
- create institutional_changelog from Annual Report data
- validate extracted data

- compare metadata available from CanLII with data available from Annual Reports
- decide if additional housing data should be collected from other sources (ex. Statistics Canada, CMHC, etc.)
 
- decide on first story to tell from data
  - create visualisations that best illustrate the story

- share findings and conclusions with interested parties

## Limitations
1. ORHT/LTB Annual Reports represent aggregate data about the function of the bodies. The way the data is selected, structured and reported has changed over the years so the data cannot be considered complete.
2. OCR is not perfect, so documents may contain transcription errors, especially in charts, scanned images or tables. As a result, any kind of automated text analysis may contain errors.
3. Published tribunal data does not contain the full context of a dispute, outcome or settlement and certainly does not contain the lived experiences of any of the people or organizations involved in the dispute.
4. Care, wisdom and compassion should be applied to viewing and analyzing aggregate or longitudinal findings to prevent the unfair profiling, targeting, ranking, or stigmatizing of individuals, tenants, landlords, neighbourhoods, or communities. The world is unequal and unfair, housing is a basic human need and no one is perfect. May our work serve to ease stress and discomfort. 
