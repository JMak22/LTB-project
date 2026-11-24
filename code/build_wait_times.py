"""Build the LTB wait times page: Ontario average days to a first hearing, by year.

Reads the project's combined CSV (LTBAvgDayFirstHearing_all_quarters.csv), keeps the
province average rows up to a chosen last period, and writes:

  wait-times.html                              the page (one view per year)
  datasets/avg_days_first_hearing_by_year.csv  the numbers behind the page

If wait-times.html already exists, only the two marked parts (the styles and the dashboard card) are replaced, so text written by hand around them is kept.
Delete the page first to make it all again from the template.
The page needs assets/wait-times.js to switch years. Without JavaScript every year is
shown one after the other.

Usage:
  python3 -I build_wait_times.py <all_quarters_csv> <dictionary_csv> <last_report_id> <out_dir>

Example:
  python3 -I build_wait_times.py LTBAvgDayFirstHearing_all_quarters.csv \
      app_type_dictionary.csv 2025_2026_Q4 docs

How a yearly number is made: the data has one average per quarter and no counts of
applications, so a year is the simple average of the quarterly averages that exist for
that application. It is not weighted. 2015 to 16 is one full year figure.
"""
import csv
import html
import math
import re
import sys
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ALL_QUARTERS, DICTIONARY, LAST_REPORT_ID, OUT_DIR = sys.argv[1:5]

# The four application types in the chart. Landlord side first, then tenant side.
SHOWN = [("L1", "Landlord"), ("L9", "Landlord"), ("T1", "Tenant"), ("T6", "Tenant")]
COLOURS = {"Landlord": "#477f9b", "Tenant": "#d56735"}
OPEN_DATA_URL = "https://tribunalsontario.ca/en/about/open-data/#panel8"
KPI_URL = "https://tribunalsontario.ca/en/about/key-performance-indicators/ltb-key-performance-indicators"
MONTH_NAMES = {4: "April", 3: "March"}


def half_up(x, places="1"):
    """Round halves up (84.5 -> 85). Python round() would give 84.
    Always pass the full precision value, never one that was already rounded."""
    return Decimal(repr(float(x))).quantize(Decimal(places), rounding=ROUND_HALF_UP)


def whole_days(x):
    return int(half_up(x, "1"))


def one_decimal(x):
    return f"{half_up(x, '0.1'):.1f}"


def year_id(report_id):
    return "_".join(report_id.split("_")[:2])  # 2025_2026_Q4 -> 2025_2026


def quarter_of(report_id):
    return report_id.split("_")[2]  # Q1..Q4 or FY


def year_label(yid):
    start, end = yid.split("_")
    return f"{start} to {end[2:]}"  # 2025_2026 -> 2025 to 26


def join_words(items):
    items = list(items)
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " and " + items[-1]


def quarters_phrase(quarters):
    quarters = list(quarters)
    if quarters == ["Q1", "Q2", "Q3", "Q4"]:
        return "Q1 to Q4"
    return join_words(quarters)


def natural_key(combo):
    parts = [(p[0], int(p[1:])) for p in combo.split("/")]
    return (len(parts) > 1, parts)


# ---- read -----------------------------------------------------------------
names = {}
with open(DICTIONARY, newline="", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        names[row["app_code"]] = row["description"]

raw = []
with open(ALL_QUARTERS, newline="", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        if r["region_id"] == "province_average" and r["report_id"] <= LAST_REPORT_ID:
            raw.append(r)

# ---- one value for each period, application and section --------------------
# A1, A2 and A4 appear in both the landlord and the tenant section of the Excel
# files, with different numbers. The converted CSV does not keep the section, but the
# A row's app_type ends in _L or _T, so that is used. Every other application code
# already tells the section (L or T).
cell = {}
for r in raw:
    combo, app_type = r["app_combo"], r["app_type"]
    if any(p.startswith("A") for p in combo.split("/")):
        if not app_type.startswith("A"):
            continue  # the A row carries the section
        family = app_type[-1]
        if family not in ("L", "T"):
            raise SystemExit(f"Unexpected A type {app_type} in {r['report_id']}")
    else:
        family = None
    key = (r["report_id"], combo, family)
    value = float(r["avg_days"])
    if key in cell and cell[key] != value:
        raise SystemExit(f"Two different values for {key}: {cell[key]} and {value}")
    cell[key] = value

# ---- one number for each year and application ------------------------------
quarter_values = defaultdict(lambda: defaultdict(list))  # year -> (combo, family) -> [(quarter, value)]
for (report_id, combo, family), value in cell.items():
    quarter_values[year_id(report_id)][(combo, family)].append((quarter_of(report_id), value))

years = sorted(quarter_values, reverse=True)  # newest first
records = {}  # year -> list of dicts
year_quarters = {}
for yid in years:
    all_q = set()
    recs = []
    for (combo, family), qv in quarter_values[yid].items():
        qv.sort(key=lambda x: x[0])
        exact = math.fsum(v for _, v in qv) / len(qv)
        all_q.update(q for q, _ in qv)
        if qv[0][0] == "FY":
            detail = "Full year figure"
        else:
            detail = ", ".join(f"{q} {one_decimal(v)}" for q, v in qv)
        suffix = {"L": " (landlord apps)", "T": " (tenant apps)", None: ""}[family]
        if "/" in combo:
            name = None
        elif family:
            name = names.get(combo + family)
        else:
            name = names.get(combo)
        recs.append({
            "year_id": yid, "year": year_label(yid), "combo": combo, "family": family,
            "label": combo + suffix, "name": name, "exact": exact,
            "quarters": [q for q, _ in qv], "detail": detail,
        })
    recs.sort(key=lambda x: (natural_key(x["combo"]), x["family"] or ""))
    records[yid] = recs
    year_quarters[yid] = sorted(all_q)

# ---- write the dataset ------------------------------------------------------
out = Path(OUT_DIR)
(out / "datasets").mkdir(parents=True, exist_ok=True)
with open(out / "datasets" / "avg_days_first_hearing_by_year.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["year", "application", "provincial_average_wait_time_days", "quarters_in_the_average"])
    for yid in years:
        for r in records[yid]:
            w.writerow([r["year"], r["label"], one_decimal(r["exact"]), r["detail"]])

# ---- page -------------------------------------------------------------------
e = html.escape
chart_max = max(r["exact"] for yid in years for r in records[yid] if (r["combo"], r["family"]) in [(c, None) for c, _ in SHOWN])
SCALE_MAX = int(math.ceil(chart_max / 100.0) * 100)
TICKS = list(range(0, SCALE_MAX + 1, 100))
axis = "".join(f'<span style="left:{t / SCALE_MAX * 100:.1f}%">{t}</span>' for t in TICKS)


def period_text(yid, quarters):
    start, end = (int(x) for x in yid.split("_"))
    if quarters == ["FY"]:
        return f"April {start} to March {end}"
    first = {"Q1": "April", "Q2": "July", "Q3": "October", "Q4": "January"}[quarters[0]]
    first_year = end if quarters[0] == "Q4" else start
    last = {"Q1": "June", "Q2": "September", "Q3": "December", "Q4": "March"}[quarters[-1]]
    last_year = end if quarters[-1] == "Q4" else start
    return f"{first} {first_year} to {last} {last_year}"


def chart_panel(yid):
    by_key = {(r["combo"], r["family"]): r for r in records[yid]}
    yq = year_quarters[yid]
    rows_html = []
    for group in ("Landlord", "Tenant"):
        rows_html.append(f'<tr class="wt-group"><th colspan="3" scope="colgroup">{group} applications</th></tr>')
        for code, g in SHOWN:
            if g != group:
                continue
            rec = by_key.get((code, None))
            title = e(names.get(code, ""))
            if rec is None:
                rows_html.append(
                    f'<tr><th scope="row"><span class="wt-code">{code}</span><span class="wt-name">{title}</span>'
                    '<span class="wt-name">No figure was published for this year.</span></th>'
                    '<td class="wt-chart" aria-hidden="true"><div class="wt-track"></div></td>'
                    '<td class="wt-num">No data</td></tr>'
                )
                continue
            note = ""
            if rec["quarters"] != yq:
                note = f'<span class="wt-name">Based on {quarters_phrase(rec["quarters"])} only.</span>'
            bar = rec["exact"] / SCALE_MAX * 100
            rows_html.append(
                f'<tr><th scope="row"><span class="wt-code">{code}</span><span class="wt-name">{title}</span>{note}</th>'
                '<td class="wt-chart" aria-hidden="true"><div class="wt-track">'
                f'<div class="wt-bar" style="width:{bar:.1f}%;background:{COLOURS[group]}"></div></div></td>'
                f'<td class="wt-num">{whole_days(rec["exact"])}</td></tr>'
            )
    label = year_label(yid)
    if yq == ["FY"]:
        how = f"Tribunals Ontario published one figure for the full year {label}, so each number is that figure."
    else:
        how = (f"Each number is the simple average of the quarterly averages published for {label} "
               f"({quarters_phrase(yq)}). It is not weighted by the number of applications.")
    return f"""
        <div class="wt-panel" data-year="{yid}">
          <h3 class="wt-year-heading">{label}</h3>
          <p class="wt-sub">Ontario average, {period_text(yid, yq)}. One bar for each single application type.</p>
          <table class="wt-table">
            <caption class="sr-only">Bar chart showing the average number of days until first hearing for L1, L9, T1 and T6 applications, {label}</caption>
            <thead>
              <tr>
                <th scope="col">Application</th>
                <th scope="col"><span class="sr-only">Bar chart of average days</span></th>
                <th scope="col" class="wt-num">Average days</th>
              </tr>
            </thead>
            <tbody>
{chr(10).join(rows_html)}
            </tbody>
            <tfoot aria-hidden="true">
              <tr class="wt-axis-row"><th></th><td class="wt-chart"><div class="wt-axis">{axis}</div></td><td></td></tr>
            </tfoot>
          </table>
          <p class="wt-how">{how}</p>
        </div>"""


def data_table(yid):
    label = year_label(yid)
    body = []
    for r in records[yid]:
        name = f'<span class="wt-name">{e(r["name"])}</span>' if r["name"] else ""
        body.append(
            f'<tr><td class="wt-year" data-label="Year">{label}</td><th scope="row"><span class="wt-code">{e(r["label"])}</span>{name}</th>'
            f'<td class="wt-num" data-label="Provincial average wait time, days">{one_decimal(r["exact"])}</td>'
            f'</tr>'
        )
    return f"""
          <div class="wt-data-wrap" data-year="{yid}">
            <table class="wt-data">
              <caption class="sr-only">Provincial average wait time in days for every application type and combination, {label}</caption>
              <thead><tr><th scope="col">Year</th><th scope="col">Application</th><th scope="col" class="wt-num">Provincial average wait time, days</th></tr></thead>
              <tbody>
{chr(10).join(body)}
              </tbody>
            </table>
          </div>"""


options = "".join(f'<option value="{yid}">{year_label(yid)}</option>' for yid in years)
panels = "".join(chart_panel(yid) for yid in years)
tables = "".join(data_table(yid) for yid in years)
counts = "".join(
    f'<p class="wt-data-count" data-year="{yid}">{len(records[yid])} applications and combinations for {year_label(yid)}. Scroll inside the table to see them all.</p>'
    for yid in years
)
latest_label = year_label(years[0])
oldest_label = year_label(years[-1])
last_q = LAST_REPORT_ID.split("_")[2]
last_year_label = year_label(year_id(LAST_REPORT_ID))
LAST_PERIOD = {"Q1": "April 1 to June 30", "Q2": "July 1 to September 30", "Q3": "October 1 to December 31", "Q4": "January 1 to March 31"}[last_q]
last_cal_year = int(LAST_REPORT_ID.split("_")[1]) if last_q == "Q4" else int(LAST_REPORT_ID.split("_")[0])

PAGE = f"""<!doctype html>
<html lang="en-CA">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Average days to a first hearing at the Ontario Landlord and Tenant Board, by year, for L1, L9, T1 and T6 applications.">
  <meta name="color-scheme" content="dark light">
  <title>Wait times — LTB Project</title>
  <link rel="icon" href="./assets/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="./assets/site.css">
  <link rel="stylesheet" href="./assets/mvp.css">
  <script src="./assets/site.js" defer></script>
  <script src="./assets/wait-times.js" defer></script>
  <script src="./assets/analytics-consent.js" defer></script>
  <!-- wait-times:style:start (made by code/build_wait_times.py, do not edit by hand) -->
  <style>
    [data-year][hidden] {{ display: none !important; }}
    .wt-hero {{ padding-top: 78px; padding-bottom: 28px; }}
    .wt-hero h1 {{ max-width: 900px; margin: 0 0 24px; font-size: clamp(40px, 5.4vw, 70px); }}
    .wt-lead {{ max-width: 760px; color: #d9dedb; font-family: Georgia, "Times New Roman", serif; font-size: clamp(18px, 1.7vw, 23px); line-height: 1.55; }}
    .wt-card {{ margin-top: 28px; padding: 28px 32px 24px; }}
    .wt-card h2 {{ margin: 0 0 18px; font-family: Georgia, serif; font-size: 26px; font-weight: 500; letter-spacing: 0; color: var(--ink); }}
    .wt-controls {{ display: flex; flex-wrap: wrap; align-items: center; gap: 8px 14px; margin: 0 0 24px; }}
    .wt-controls[hidden] {{ display: none; }}
    .wt-controls label {{ font-weight: 700; color: var(--ink); }}
    .wt-controls select {{ min-width: 150px; }}
    .wt-hint {{ color: #4d5a54; font-size: 13px; }}
    .wt-panel + .wt-panel {{ margin-top: 40px; }}
    .wt-year-heading {{ margin: 0 0 4px; font-family: Georgia, serif; font-size: 22px; font-weight: 500; color: var(--ink); }}
    .wt-sub {{ margin: 0 0 14px; color: #4d5a54; font-size: 14px; }}
    .wt-how {{ margin: 14px 0 0; max-width: 720px; color: #3f4c46; font-size: 13px; line-height: 1.5; }}
    .wt-table, .wt-data {{ width: 100%; border-collapse: collapse; color: var(--ink); font-size: 15px; }}
    .wt-table caption, .wt-data caption {{ text-align: left; }}
    .wt-table th, .wt-table td, .wt-data th, .wt-data td {{ position: static; max-width: none; padding: 12px 10px; text-align: left; vertical-align: middle; border-top: 1px solid #d4d0c5; border-bottom: 0; background: transparent; color: var(--ink); font-size: 15px; letter-spacing: 0; text-transform: none; white-space: normal; line-height: 1.4; }}
    .wt-table thead th, .wt-data thead th {{ border-top: 0; color: #4d5a54; font-size: 12px; font-weight: 700; letter-spacing: .04em; text-transform: uppercase; }}
    .wt-table .wt-group th {{ padding-top: 22px; border-top: 2px solid var(--ink); font-family: Georgia, serif; font-size: 19px; font-weight: 700; }}
    .wt-table tbody tr:first-child th {{ border-top: 0; }}
    .wt-code {{ display: block; font-weight: 800; font-size: 16px; }}
    .wt-name {{ display: block; margin-top: 2px; color: #4d5a54; font-size: 13px; font-weight: 400; line-height: 1.4; }}
    .wt-chart {{ width: 46%; }}
    .wt-track {{ position: relative; height: 26px; background-image: linear-gradient(to right, #d4d0c5 1px, transparent 1px); background-size: {100 / (SCALE_MAX / 100):.4f}% 100%; }}
    .wt-track::after {{ content: ""; position: absolute; top: 0; right: 0; bottom: 0; width: 1px; background: #d4d0c5; }}
    .wt-bar {{ height: 100%; }}
    .wt-num {{ width: 92px; text-align: right; font-variant-numeric: tabular-nums; font-size: 18px; font-weight: 700; }}
    .wt-table th.wt-num, .wt-table td.wt-num {{ width: 132px; padding-left: 42px; }}
    .wt-table thead .wt-num, .wt-data thead .wt-num {{ font-size: 12px; font-weight: 700; }}
    .wt-axis-row th, .wt-axis-row td {{ padding-top: 4px; padding-bottom: 0; border-top: 0; }}
    .wt-axis {{ position: relative; height: 20px; color: #4d5a54; font-size: 12px; }}
    .wt-axis span {{ position: absolute; transform: translateX(-50%); }}
    .wt-axis span:first-child {{ transform: none; }}
    .wt-axis-title {{ margin: 2px 0 0; color: #4d5a54; font-size: 12px; }}
    .wt-legend {{ display: flex; flex-wrap: wrap; gap: 8px 26px; margin: 18px 0 0; color: #3f4c46; font-size: 13px; }}
    .wt-legend span {{ display: inline-flex; align-items: center; gap: 8px; }}
    .wt-swatch {{ display: inline-block; width: 16px; height: 12px; }}
    .wt-data-count {{ margin: 0 0 8px; color: #3f4c46; font-size: 13px; font-weight: 700; }}
    .wt-data-note {{ margin: 8px 0 12px; max-width: 720px; color: #3f4c46; font-size: 13px; line-height: 1.5; }}
    .evidence-details .wt-scroll {{ max-height: 480px; overflow: auto; }}
    .wt-data {{ min-width: 560px; font-size: 14px; }}
    .wt-data th, .wt-data td {{ padding: 8px 12px; font-size: 14px; }}
    .wt-data thead th {{ position: sticky; top: 0; z-index: 1; background: var(--artifact); border-bottom: 1px solid #d4d0c5; }}
    .wt-data .wt-code {{ font-size: 14px; }}
    .wt-data .wt-year {{ white-space: nowrap; }}
    .wt-data .wt-num {{ width: auto; font-size: 14px; font-weight: 700; }}
    .wt-notes {{ padding-top: 44px; padding-bottom: 20px; }}
    .wt-notes h2 {{ max-width: none; margin: 38px 0 10px; font-size: 28px; }}
    .wt-notes h2:first-child {{ margin-top: 0; }}
    .wt-notes p {{ max-width: 760px; color: #d9dedb; }}
    .wt-notes a {{ color: var(--accent); }}
    @media (max-width: 760px) {{
      .wt-card {{ padding: 20px 16px; }}
      .wt-table thead {{ position: absolute; left: -9999px; }}
      .wt-table, .wt-table tbody, .wt-table tr, .wt-table th, .wt-table td {{ display: block; }}
      .wt-table tr {{ position: relative; padding: 10px 0; border-top: 1px solid #d4d0c5; }}
      .wt-table th, .wt-table td {{ border: 0; padding: 4px 0; }}
      .wt-table .wt-group {{ padding: 0; border-top: 2px solid var(--ink); }}
      .wt-chart {{ width: auto; }}
      .wt-table th.wt-num, .wt-table td.wt-num {{ width: auto; padding-left: 0; }}
      .wt-table .wt-num {{ width: auto; text-align: left; font-size: 16px; }}
      .wt-table .wt-num::before {{ content: "Average days: "; font-weight: 400; font-size: 14px; }}
      .wt-table tfoot {{ display: none; }}
      .evidence-details .wt-scroll {{ max-height: 520px; }}
      .wt-data {{ min-width: 0; }}
      .wt-data thead {{ position: absolute; left: -9999px; }}
      .wt-data, .wt-data tbody, .wt-data tr, .wt-data th, .wt-data td {{ display: block; }}
      .wt-data tr {{ display: flex; flex-direction: column; padding: 10px 12px; border-top: 1px solid #d4d0c5; }}
      .wt-data tr:first-child {{ border-top: 0; }}
      .wt-data th, .wt-data td {{ border: 0; padding: 2px 0; font-size: 14px; }}
      .wt-data th[scope="row"] {{ order: -1; }}
      .wt-data td::before {{ content: attr(data-label) ": "; color: #4d5a54; font-weight: 400; }}
      .wt-data .wt-num {{ text-align: left; width: auto; }}
      .wt-data .wt-year {{ white-space: normal; }}
    }}
  </style>
  <!-- wait-times:style:end -->
</head>
<body>
  <a class="skip-link" href="#main">Skip to main content</a>
  <header class="site-header">
    <div class="header-inner">
      <a class="wordmark" href="./" aria-label="LTB Project home"><span>LTB</span> Project</a>
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="primary-nav"><span aria-hidden="true">☰</span><span class="sr-only">Open navigation</span></button>
      <nav id="primary-nav" class="primary-nav" aria-label="Primary navigation">
        <a href="./">Home</a>
        <a href="./explore.html">Explore</a>
        <a href="./analysis.html">Analysis</a>
        <a href="./wait-times.html" aria-current="page">Wait times</a>
        <a href="./data.html">Data</a>
        <a href="./about.html">About</a>
      </nav>
    </div>
  </header>

  <main id="main">
    <section class="wt-hero page-shell" aria-labelledby="wt-title">
      <p class="eyebrow">ORHT / LTB · Wait times</p>
      <h1 id="wt-title">How long until a first hearing?</h1>
      <p class="wt-lead">Choose a year to see the Ontario average number of days until a first hearing, for four common application types. Your own wait may be shorter or longer.</p>
    </section>

    <!-- wait-times:dashboard:start (made by code/build_wait_times.py, do not edit by hand) -->
    <section class="page-shell" aria-labelledby="wt-chart-title">
      <div class="artifact-card wt-card">
        <h2 id="wt-chart-title">Average days to first hearing</h2>
        <div class="wt-controls" id="wt-controls" hidden>
          <label for="wt-year">Year</label>
          <select id="wt-year">{options}</select>
          <span class="wt-hint">Fiscal years, April to March</span>
        </div>
        <p id="wt-status" class="sr-only" role="status" aria-live="polite"></p>
{panels}
        <p class="wt-axis-title">Days, same scale for every year.</p>
        <div class="wt-legend">
          <span><i class="wt-swatch" style="background:{COLOURS['Landlord']}"></i>Landlord applications</span>
          <span><i class="wt-swatch" style="background:{COLOURS['Tenant']}"></i>Tenant applications</span>
        </div>
        <details class="evidence-details">
          <summary>Inspect the data</summary>
          <p class="wt-data-note">Every application type and combination Tribunals Ontario reported for the year, with the Ontario average. A1, A2 and A4 appear in both the landlord and the tenant section of the Tribunals Ontario files, with different numbers, so they are listed once for each.</p>
{counts}
          <div class="table-scroll wt-scroll">
{tables}
          </div>
          <p class="source-line">Sources: <a href="./datasets/avg_days_first_hearing.csv">avg_days_first_hearing.csv</a> (every quarter) and <a href="./datasets/avg_days_first_hearing_by_year.csv">avg_days_first_hearing_by_year.csv</a> (the numbers on this page).</p>
        </details>
      </div>
    </section>
    <!-- wait-times:dashboard:end -->

    <section class="wt-notes page-shell" aria-label="How to read this page">
      <h2>How to read this</h2>
      <p>Each bar is the average number of days until a first hearing, across Ontario, as published by Tribunals Ontario. An average is not a promise. Scheduling varies, so check the Tribunals Ontario portal for your own file.</p>

      <h2>How each year is worked out</h2>
      <p>Tribunals Ontario publishes these averages one quarter at a time and does not publish how many applications are behind them. For each year, this page takes the simple average of the quarterly averages that were published. It is not weighted by the number of applications, so it can differ from the true average for the year. Some quarters are missing for some application types, and some quarterly values look very low or very high, so one quarter can move a year a lot. The downloadable CSV lists the quarterly averages behind every number. For {oldest_label}, only a full year figure was published.</p>

      <h2>What is not shown</h2>
      <p>Many people file more than one type of application at the same time. Tribunals Ontario reports those combinations on their own, so the bars show only single type L1, L9, T1 and T6 applications. Other types and combinations are in the Inspect the data table. Regional averages are not shown. The share of hearings held within a standard is not shown, because the published figures for it are not consistent.</p>

      <h2>A note on the data</h2>
      <p>The Tribunals Ontario files do not say whether the days are calendar days or business days. The Excel files state a standard of 25 business days for L1 and L9 and 30 business days for other applications. The Tribunals Ontario <a href="{KPI_URL}">Key Performance Indicators page</a> lists 50 calendar days for L1 and L9 and 55 calendar days for other applications. These do not match, so this page does not compare the averages with any standard. The latest period on this page is {last_q} {last_year_label} ({LAST_PERIOD}, {last_cal_year}), the most recent data we could confirm.</p>

      <h2>Sources</h2>
      <p>Tribunals Ontario Open Data, <a href="{OPEN_DATA_URL}">average days to first hearing</a>, quarterly files from {oldest_label} to {last_q} {last_year_label}. The numbers on this page are in the <a href="./datasets/avg_days_first_hearing_by_year.csv">data file</a>.</p>
    </section>
  </main>

  <footer><p>© 2026 Jasna Maksimovic | This is a Civic Tech Toronto project</p><span class="footer-attribution">Contains information licensed under the Open Government Licence – Ontario</span></footer>
</body>
</html>
"""

def region(text, name):
    return re.search(rf"<!-- wait-times:{name}:start.*?<!-- wait-times:{name}:end -->", text, re.S)


target = out / "wait-times.html"
new_page, mode = PAGE, "wrote the full page"
if target.exists():
    old_page = target.read_text(encoding="utf-8")
    if all(region(old_page, n) and region(PAGE, n) for n in ("style", "dashboard")):
        new_page = old_page
        for n in ("style", "dashboard"):
            m = region(new_page, n)
            new_page = new_page[:m.start()] + region(PAGE, n).group(0) + new_page[m.end():]
        mode = "page already existed: replaced only the chart, the table and their styles, text you wrote is untouched"
target.write_text(new_page, encoding="utf-8")
print(mode)

js = """(function () {
  "use strict";
  var select = document.getElementById("wt-year");
  var controls = document.getElementById("wt-controls");
  var status = document.getElementById("wt-status");
  if (!select || !controls) { return; }
  var items = document.querySelectorAll("[data-year]");

  function show(id, announce) {
    var found = false;
    for (var i = 0; i < select.options.length; i++) {
      if (select.options[i].value === id) { found = true; }
    }
    if (!found) { id = select.options[0].value; }
    for (var j = 0; j < items.length; j++) {
      items[j].hidden = items[j].getAttribute("data-year") !== id;
    }
    select.value = id;
    if (announce) {
      status.textContent = "Showing " + select.options[select.selectedIndex].text;
      try { history.replaceState(null, "", "#" + id); } catch (err) { /* ignore */ }
    }
  }

  controls.hidden = false;
  select.addEventListener("change", function () { show(select.value, true); });
  show(window.location.hash.replace("#", ""), false);
})();
"""
(out / "assets").mkdir(parents=True, exist_ok=True)
(out / "assets" / "wait-times.js").write_text(js, encoding="utf-8")

print("years:", ", ".join(year_label(y) for y in years))
print("applications per year:", {year_label(y): len(records[y]) for y in years})
print("chart scale max:", SCALE_MAX, "| last period:", LAST_REPORT_ID)
