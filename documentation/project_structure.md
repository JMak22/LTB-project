# Project Structure

## raw_pdfs/
Original downloaded annual reports.

## ocr_pdfs/
OCR-processed versions of original reports.

## md_reports/
Markdown text extracted from OCR PDFs.

## cleaned_data/
Structured datasets derived from report extraction and cleaning as well as from Tribunals Ontario Open Data.

## code/
Python scripts and processing utilities.

## methodology/
Methodological notes and extraction decisions.

## docs/
Project website docs and HTML pages

## documentation/
List of canonical datasets, how which species of file was obtained (starting with raw_pdfs/ and going from there), metric dictionary and a list of scripts used and their purposes

## md_reports/
Markdown version of the annual reports

## ~~working_data/~~
These spreadsheets are intermediate working and normalization documents used during manual extraction of annual report metrics.

They contain:
- exploratory extraction
- manual categorization
- normalization decisions
- incomplete or superseded values
- working annotations

They should not be treated as canonical final datasets.

### ~~annual_report_biography_extracts.zip
This archive contains portions of reports that contained adjudicator biographies. It was OCR generated, so it may contain transcription errors, gaps between characters etc. It was used to derive adjudicator counts via creating a list of canonical names and counting those names.

## ~~notes/
Working notes and exploratory material.