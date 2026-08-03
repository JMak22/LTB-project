# LTB Project

This project aims to discover what can and cannot be known about LTB usage given currently available data and its structure.

To browse the database, go to [https://jmak22.github.io/LTB-project/](https://jmak22.github.io/LTB-project/)

## Authorship and Citation

This project was created and directed by **Jasna Maksimovic**. The work includes the collection, selection, normalization, validation, organization, and interpretation of longitudinal data from Ontario Landlord and Tenant Board and related tribunal reports.

AI tools assisted with drafting code and data-processing workflows. The project owner determined the research questions, selected the source material, directed and tested the transformations, evaluated the outputs, resolved inconsistencies, and made the final publication decisions.

When using or discussing this project, please cite:

> Jasna Maksimovic. *LTB Project: Ontario Landlord and Tenant Board Longitudinal Data*. 2026. https://github.com/JMak22/LTB-project

## Licensing and Source Attribution

Different parts of this repository are subject to different terms. See [LICENSE](LICENSE) for the full licensing notice.

Original software in `code/` is licensed under the MIT License. Original curated data structures, documentation, methodology, and visualizations are subject to the terms described in the repository licensing notice.

Underlying government reports, statistics, and public-sector information are not owned by the project creator.

Contains information licensed under the Open Government Licence – Ontario.


## Data Sources
- tribunalsontario.ca and its predecessors (via archive.org) -- source of Annual Reports and Open Data
- CanLII -- source of metadata on LTB cases (note that this is a portion of all cases submitted and heard at the LTB) -- nothing published yet, we may be limited in what we are allowed to share from this data set

## Ethical Considerations
This project uses publicly available information for research and civic analysis purposes. We will take care to comply with applicable Canadian privacy laws and to avoid publishing information or analyses that could cause harm to individuals or groups.

### To do:
- create institutional_changelog from Annual Report prose -- a way to communicate the institutional changes that have taken place in LTB as an organization since its inception

- figure out what can be gleaned AND ethically communicated from the CanLII data

- continue outreach to tenant unions, academics and other intersted parties

- include LTB Open Data in dashboard

- service design: investigate the viability of a Small Language Model to serve as a system/process navigator, helping the tenant understand where they're at in a LTB process and directing them towards tenant support organizations/community supports as soon as possible

### Ongoing:
- figuring out how to communicate gleanings from the Annual Reports in visual/interactive form
- integrating LTB Open Data into existing dashboard

### Tasks/cleanup finished:
- Operational metrics -- contains number of applications filed, resolved and unresolved for each report year. Some data is not available but can be calculated.
- Regional metrics -- contains number of applications filed, resolved and unresolved in each of the 8 regions for report years 1998-2014
- Financial metrics -- contains the cost of filing for the years when it was reported in the Annual Reports; budget, expenditures, salaries, other expenses and revenue for report years 2006-07, 2007-08 and 2009-10. Operating budgets were not reported in other Annual Reports, the data may be available elsewhere.
- Staffing metrics -- contains information about the number of adjudicators and, occasionally, other staff members. A public methodology summary explaining how staffing metrics were extracted and counted will be added.
- Reports -- list of report years -- this may need editing to include notes on relevant legislature changes over the years
- Application type dictionary - applic_type_dict 
- Application type metrics - applic_type_metrics 
- Resolution metrics - resolution_metrics
- validate extracted data
- Added full text of reports in markdown format -- searching, textual analysis and other fun, language-based stuff is now enabled. To the best of my knowledge, the markdown text represents the reports faithfully, there may be minor errors in formatting.
- created a .sqlite file of all CSVs, available via Datasette at the link above



## Limitations
1. ORHT/LTB Annual Reports represent aggregate data about the function of the bodies. The way the data is selected, structured and reported has changed over the years so the data cannot be considered complete.
2. OCR is not perfect, so documents may contain transcription errors, especially in charts, scanned images or tables. As a result, any kind of automated text analysis may contain errors.
3. Published tribunal data does not contain the full context of a dispute, outcome or settlement and certainly does not contain the lived experiences of any of the people or organizations involved in the dispute.
4. Care, wisdom and compassion should be applied to viewing and analyzing aggregate or longitudinal findings to prevent the unfair profiling, targeting, ranking, or stigmatizing of individuals, tenants, landlords, neighbourhoods, or communities. The world is unequal and unfair, housing is a basic human need and no one is perfect. May our work serve to ease stress and discomfort. 
