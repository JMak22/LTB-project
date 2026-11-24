# Average days to first hearing, by year: methodology (draft)

Draft written by Vinay for Jasna to edit. It covers the page `docs/wait-times.html`, the script `docs/assets/wait-times.js` (the year dropdown) and the file `docs/datasets/avg_days_first_hearing_by_year.csv`. All three are made by `code/build_wait_times.py`.

Status: built from `LTBAvgDayFirstHearing_all_quarters.csv`, up to Q4 2025 to 26 (January 1 to March 31, 2026). Q1 2026 to 27 is left out on purpose, see decision 1. Jasna confirmed fiscal years on November 24 and said she will write the text on the page herself, so the notes in this version are a placeholder. Two choices still need her yes, see "Open items".

## What the page shows

- A year dropdown at the top. The years are fiscal years (April to March), from 2015 to 16 to 2025 to 26, newest first. The newest year is selected when the page opens.
- For the chosen year, one bar for each of L1, L9 (landlord) and T1, T6 (tenant): the Ontario average number of days until a first hearing. The bars use the same scale for every year, so switching years shows real change.
- Under the chart, an "Inspect the data" section, in the same style as the home page. It lists every application type and combination for the chosen year, with the columns `year`, `application` and `provincial average wait time, days`. The page table has only these three columns (Jasna asked to leave out the quarterly averages column). The CSV file still has a fourth column with the quarterly averages used.
- Short notes on how to read the page, how each year is worked out, what is not shown, and the data problems.

## Where the numbers come from

- Tribunals Ontario Open Data, "average days to first hearing", one Excel file for L1 and L9 and one for other applications, every quarter.
- The project's conversion script turns the Excel files into `LTBAvgDayFirstHearing_all_quarters.csv`. The site's copy, `docs/datasets/avg_days_first_hearing.csv`, is identical to it (checked byte for byte on November 24, 2026).
- `code/build_wait_times.py` keeps the `province_average` rows up to the last period you give it, makes one number for each year and application, and writes the page, the data file and the dropdown script.

## Decisions

1. **Last period is Q4 2025 to 26.** Jasna decided on November 24 to skip Q1 2026 to 27, because Tribunals Ontario's published data is not consistent about the periods of the L1 and L9 file and the other applications file. I had already built a Q1 version, which is not used. The two Q1 files are also named "HearingOrder" on the Tribunals Ontario site, although the site lists them as first hearing.
2. **Year means fiscal year, April to March.** That is how the data is published (`report_id` such as 2025_2026_Q4). Jasna confirmed this on November 24 ("stick to FY"). The page says so next to the dropdown.
3. **A yearly number is the simple average of the quarterly averages.** The data has one average for each quarter and no number of applications, so the quarters cannot be weighted. The result can differ from the true average for the year. The page says this, and the Inspect the data table shows the quarterly values behind each number. 2015 to 16 has one full year figure, which is used as it is.
4. **Missing quarters are not filled in.** 2016 to 17 has Q1 to Q3 only and 2018 to 19 has Q2 to Q4 only. Some application types are missing in some quarters (for example T1 in 2022 to 23 has Q1 and Q3 only, and T6 has Q3 and Q4 only). The average uses the quarters that exist. A chart row that uses fewer quarters than the rest of the year says "Based on Q1 and Q3 only".
5. **A1, A2 and A4 appear twice.** They are in both the landlord and the tenant section of the Excel files, with different numbers. The converted CSV does not keep the section, but the A row's `app_type` ends in `_L` or `_T`, so the script uses that. They are listed as "A1 (landlord apps)" and "A1 (tenant apps)". The script stops with an error if one period, application and section ever has two different numbers.
6. **Combinations are listed once each.** A combination such as L1/L2 is one row in the data, but the converted CSV repeats it for each part. The script keeps one.
7. **Ontario average only.** Regional columns are ignored.
8. **No target lines and no pass or fail colours.** The Excel files say 25 business days for L1 and L9 and 30 for other applications. The Key Performance Indicators page says 50 calendar days for L1 and L9 and 55 for other applications, and it covers 2025 to 26 only. The data does not say which unit it uses, so the page does not compare the bars with any standard.
9. **Percent in standard is not used anywhere**, as Jasna asked. The column also mixes units (0.0044 in recent quarters, 40.85 in 2018 to 19 Q2).
10. **Rounding.** The chart shows whole days. The table and the data file show one decimal. Halves round up (84.5 becomes 85), and the rounding is done once, from the full value. For example T1 in 2025 to 26 is 132.73, which shows as 133 in the chart and 132.7 in the table. Do not round the one decimal value again: Python's `round()` turns 84.5 into 84, which would be wrong.
11. **Names of application types** are the wording in `app_type_dictionary.csv`, unchanged.
12. **Plain HTML and CSS in the site style, plus one small script file.** Without the script every year is shown one after the other. A link such as `wait-times.html#2022_2023` opens a given year. The script marks the parts of the page it makes with comments (`wait-times:style` and `wait-times:dashboard`). If `docs/wait-times.html` already exists, a new run replaces only those two parts, so text written by hand around them is kept.

## Problems found in the source data

- **Two standards.** See decision 8.
- **Units not stated.** I have not found whether the averages are calendar or business days.
- **`performance_standard` is set by our own script.** `infer_performance_standard` in `convert_avg_days_xslx_csv.py` assigns 25 or 30 from the file name. It is not read from the spreadsheet and never changes over time. The page does not use it.
- **Some quarters look like very small samples.** L9 in 2020 to 21 Q3 is 1.0 day, and T2/T5 in 2020 to 21 Q4 is 0.0 days. The files give no counts, so I cannot confirm this. These values are averaged into the year like any other (L9 in 2020 to 21 is 37.6 from 32.2, 59.0, 1.0 and 58.0). The note on the page warns about this, and the table shows every quarter.
- **The list of combinations changes a lot between quarters.** For example, 2022 to 23 Q2 has 4 rows for Ontario and 2019 to 20 Q2 has 66.
- **The downloader skips the Q1 2026 to 27 files.** `import_avg_days_hearing.py` and `import_avg_d_to_hearing_reports.py` only find files whose name contains "LTBAvgDayFirstHearing".
- **I could not see what Tribunals Ontario's period problem is.** I found no mismatch in the dates in the file names of the quarters up to Q4 2025 to 26, but I only checked the file names, not the sheets.

## Open items

- Jasna to confirm decision 3 (simple average of the quarters). She said the page looks great and asked to drop the "quarterly averages used" column from the table, which is done.
- Jasna writes the page text. Facts the text should keep: the yearly number is a simple average of the quarterly averages and is not weighted; some quarters and application types are missing; the days may be calendar or business days; the Excel files and the Key Performance Indicators page give different standards; the latest period is Q4 2025 to 26; scheduling varies, so people should check the Tribunals Ontario portal.
- Whether to show every application in the table, or only the ones other than L1, L9, T1 and T6. The table now includes all of them, so it also shows the numbers in the chart.
- Add a "Wait times" link to the navigation on the other pages (only the new page has it).
- Tell Tribunals Ontario about the problems above (Jasna is looking for a contact).

## Updating for a new quarter

1. Add the new quarter to `LTBAvgDayFirstHearing_all_quarters.csv` with the conversion script.
2. Run, from the repo root, with the new last report id (the chart, the table and the dropdown script are remade; text written by hand in the page stays):
   `python3 code/build_wait_times.py cleaned_data/Avg_Days_First_Hearing/LTBAvgDayFirstHearing_all_quarters.csv cleaned_data/app_type_dictionary.csv 2025_2026_Q4 docs`
   To make the whole page again from the template, delete `docs/wait-times.html` first.
3. Open `docs/wait-times.html`, pick a year, and check a few numbers against the data file.

## Checks done

- A separate script that does not use the build script recomputed every number from the raw CSV. All 44 chart numbers (4 applications, 11 years) match, all 748 table rows match, and every one of the 1,644 quarterly values in the raw data is used exactly once.
- The year dropdown, the links to a given year, the page without the script, and the page at desktop and phone width were tested in a real browser. There were no script errors and no sideways scrolling.

## Not checked

- I did not compare the converted CSV with the original Excel files. For Q4 2025 to 26, the four chart applications matched an earlier prototype.
- No screen reader was used. Only the page structure was read.
