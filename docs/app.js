/*
 * Ontario LTB Data Explorer — dependency-free GitHub Pages edition.
 *
 * Keep CSV paths relative: this is what allows the same site to run at either
 * a repository root or a nested path such as /LTB-project/explorer/.
 */
(function () {
  "use strict";

  const DATASETS = [
    {
      id: "reports",
      label: "Annual report coverage",
      file: "reports.csv",
      description: "Authoritative annual-report inventory, reporting periods and historical notes, beginning in 1998–99."
    },
    {
      id: "operational",
      label: "Operational metrics",
      file: "operational_metrics.csv",
      description: "Reported annual applications received, resolved and unresolved, beginning in 1998–99."
    },
    {
      id: "filing_summary",
      label: "Filing summary by year",
      file: "ltb_filing_summary_by_year.csv",
      description: "Annual landlord, tenant, mixed and L1 filing totals and shares."
    },
    {
      id: "party_receipts",
      label: "Landlord and tenant receipts",
      file: "landlord_vs_tenant_receipts.csv",
      description: "Reported or calculated landlord and tenant shares, including the first report in 1998–99."
    },
    {
      id: "application_families",
      label: "Application families by year",
      file: "ltb_application_family_share_by_year.csv",
      description: "Filings and share of all cases by application family and party type."
    },
    {
      id: "application_change",
      label: "Application family change",
      file: "ltb_application_family_change_summary.csv",
      description: "Long-run change, peaks and total volume for each application family."
    },
    {
      id: "top_applications",
      label: "Top application families",
      file: "ltb_top_application_families.csv",
      description: "Ranked application families across the full reporting period."
    },
    {
      id: "staffing",
      label: "Staffing metrics",
      file: "staffing_metrics.csv",
      description: "Reported staffing and adjudicator measures by reporting year."
    },
    {
      id: "financial",
      label: "Financial metrics",
      file: "financial_metrics.csv",
      description: "Filing costs, expenditures and other reported financial measures."
    },
    {
      id: "l5_trends",
      label: "L5 filing trends",
      file: "ltb_l5_filings_trend_summary.csv",
      description: "L5 cases, hearings, defaults and year-over-year measures."
    }
  ];

  const COMPARISON_DATASETS = [
    {
      id: "app_type_metrics",
      label: "Application type metrics",
      file: "app_type_metrics.csv"
    },
    {
      id: "app_type_dictionary",
      label: "Application type dictionary",
      file: "app_type_dictionary.csv"
    }
  ];

  const PARTY_LABELS = {
    all: "All parties",
    landlord: "Landlord",
    tenant: "Tenant",
    mixed_other: "Mixed / Other"
  };

  const PAGE_SIZE = 12;

  const state = {
    data: {},
    allYears: [],
    startYear: "",
    endYear: "",
    party: "all",
    family: "L1",
    selectedApps: new Set(),
    appSearch: "",
    tableId: "filing_summary",
    tableSearch: "",
    tablePage: 0,
    currentTableRows: [],
    currentTableColumns: []
  };

  function element(id) {
    const result = document.getElementById(id);
    if (!result) throw new Error("A required page element is missing: " + id);
    return result;
  }

  function escapeHTML(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function parseCSV(text) {
    const matrix = [];
    let row = [];
    let value = "";
    let quoted = false;

    for (let index = 0; index < text.length; index += 1) {
      const character = text[index];
      const nextCharacter = text[index + 1];

      if (character === '"' && quoted && nextCharacter === '"') {
        value += '"';
        index += 1;
      } else if (character === '"') {
        quoted = !quoted;
      } else if (character === "," && !quoted) {
        row.push(value);
        value = "";
      } else if ((character === "\n" || character === "\r") && !quoted) {
        if (character === "\r" && nextCharacter === "\n") index += 1;
        row.push(value);
        if (row.some(function (cell) { return cell !== ""; })) matrix.push(row);
        row = [];
        value = "";
      } else {
        value += character;
      }
    }

    if (value || row.length) {
      row.push(value);
      matrix.push(row);
    }

    const headers = (matrix.shift() || []).map(function (header) {
      return header.replace(/^\uFEFF/, "").trim();
    });

    return matrix.map(function (cells) {
      return Object.fromEntries(headers.map(function (header, index) {
        return [header, cells[index] ?? ""];
      }));
    });
  }

  function yearLabel(value) {
    const parts = String(value || "").split("_");
    return parts[1] ? parts[0] + "–" + parts[1].slice(-2) : parts[0];
  }

  function shortYear(value) {
    const parts = String(value || "").split("_");
    return parts[1] ? parts[0].slice(-2) + "–" + parts[1].slice(-2) : parts[0];
  }

  function number(value) {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : 0;
  }

  function hasNumber(value) {
    return value !== undefined && value !== null && String(value).trim() !== "" && Number.isFinite(Number(value));
  }

  function compactNumber(value) {
    return new Intl.NumberFormat("en-CA", { notation: "compact", maximumFractionDigits: 1 }).format(value);
  }

  function fullNumber(value) {
    return new Intl.NumberFormat("en-CA", { maximumFractionDigits: 1 }).format(value);
  }

  function percent(value) {
    return new Intl.NumberFormat("en-CA", { style: "percent", maximumFractionDigits: 1 }).format(value);
  }

  function firstDetailedYear() {
    return (state.data.filing_summary && state.data.filing_summary[0] && state.data.filing_summary[0].report_id) || "1999_2000";
  }

  function selectedYearBounds() {
    const startIndex = Math.max(0, state.allYears.indexOf(state.startYear));
    const selectedEndIndex = state.allYears.indexOf(state.endYear);
    const endIndex = selectedEndIndex < 0 ? state.allYears.length - 1 : selectedEndIndex;
    return { startIndex: startIndex, endIndex: endIndex };
  }

  function yearInRange(year) {
    const index = state.allYears.indexOf(year);
    const bounds = selectedYearBounds();
    return index >= bounds.startIndex && index <= bounds.endIndex;
  }

  function filingRows() {
    const summaries = new Map((state.data.filing_summary || []).map(function (row) {
      return [row.report_id, row];
    }));

    const totals = new Map((state.data.operational || [])
      .filter(function (row) { return row.metric_id === "total_received"; })
      .map(function (row) { return [row.report_id, row.value]; }));

    const receipts = new Map((state.data.party_receipts || []).map(function (row) {
      return [row.report_id, row];
    }));

    return (state.data.reports || [])
      .filter(function (report) { return yearInRange(report.report_id); })
      .map(function (report) {
        const summary = summaries.get(report.report_id) || {};
        const partyReceipt = receipts.get(report.report_id) || {};
        return Object.assign({}, summary, {
          report_id: report.report_id,
          total_filings: totals.get(report.report_id) ?? summary.total_filings ?? "",
          landlord_share: summary.landlord_share ?? partyReceipt.landlord_received ?? "",
          tenant_share: summary.tenant_share ?? partyReceipt.tenant_received ?? ""
        });
      });
  }

  function availableFamilies() {
    const unique = new Map();
    for (const row of state.data.application_families || []) {
      if (state.party === "all" || row.party_type === state.party) {
        unique.set(row.application_family, row);
      }
    }

    return Array.from(unique.values()).sort(function (left, right) {
      return left.application_family.localeCompare(right.application_family, undefined, { numeric: true });
    });
  }

  function familyRows() {
    return (state.data.application_families || []).filter(function (row) {
      return row.application_family === state.family && yearInRange(row.report_id);
    });
  }

  function rankingRows() {
    return (state.data.application_change || [])
      .filter(function (row) { return state.party === "all" || row.party_type === state.party; })
      .slice()
      .sort(function (left, right) { return number(right.total_filings) - number(left.total_filings); })
      .slice(0, 6);
  }

  function dictionaryRows() {
    return (state.data.app_type_dictionary || []).slice().sort(function (left, right) {
      return left.app_code.localeCompare(right.app_code, undefined, { numeric: true });
    });
  }

  function selectedApplicationCodes() {
    return dictionaryRows()
      .map(function (row) { return row.app_code; })
      .filter(function (code) { return state.selectedApps.has(code); });
  }

  function applicationIsActive(row, reportId) {
    const startYear = Number(String(reportId).split("_")[0]);
    const firstYear = Number(row.first_year);
    const lastYear = row.last_year === "" ? null : Number(row.last_year);
    return Number.isFinite(startYear) && Number.isFinite(firstYear) &&
      startYear >= firstYear && (lastYear === null || startYear < lastYear);
  }

  function comparisonRows() {
    const selected = selectedApplicationCodes();
    const dictionary = new Map(dictionaryRows().map(function (row) { return [row.app_code, row]; }));
    const caseRows = new Map();

    (state.data.app_type_metrics || [])
      .filter(function (row) { return row.metric_id === "cases" && dictionary.has(row.app_code); })
      .forEach(function (row) {
        const key = row.report_id + "\u0000" + row.app_code;
        if (!caseRows.has(key)) caseRows.set(key, []);
        caseRows.get(key).push(row);
      });

    const totals = new Map((state.data.operational || [])
      .filter(function (row) { return row.metric_id === "total_received"; })
      .map(function (row) { return [row.report_id, row.value]; }));

    const availableYears = new Set((state.data.app_type_metrics || [])
      .filter(function (row) { return row.metric_id === "cases"; })
      .map(function (row) { return row.report_id; }));

    return state.allYears
      .filter(function (reportId) { return availableYears.has(reportId) && yearInRange(reportId); })
      .map(function (reportId) {
        const activeCodes = selected.filter(function (code) {
          return applicationIsActive(dictionary.get(code), reportId);
        });
        const missingCodes = [];
        let selectedTotal = 0;

        activeCodes.forEach(function (code) {
          const rows = caseRows.get(reportId + "\u0000" + code) || [];
          const row = rows.length === 1 ? rows[0] : null;
          if (!row || row.data_status !== "reported" || !hasNumber(row.value)) {
            missingCodes.push(code);
          } else {
            selectedTotal += number(row.value);
          }
        });

        const totalValue = totals.get(reportId);
        const comparableSelected = activeCodes.length && !missingCodes.length ? selectedTotal : "";
        const allApplications = hasNumber(totalValue) ? number(totalValue) : "";

        return {
          report_id: reportId,
          selected_applications: comparableSelected,
          all_applications: allApplications,
          share: hasNumber(comparableSelected) && hasNumber(allApplications) && number(allApplications) !== 0
            ? number(comparableSelected) / number(allApplications)
            : "",
          active_codes: activeCodes,
          missing_codes: missingCodes
        };
      });
  }

  function comparisonTooltip(row) {
    const selectedValue = hasNumber(row.selected_applications)
      ? fullNumber(number(row.selected_applications))
      : "Unavailable";
    const totalValue = hasNumber(row.all_applications)
      ? fullNumber(number(row.all_applications))
      : "Unavailable";
    const shareValue = hasNumber(row.share) ? percent(number(row.share)) : "Unavailable";
    return yearLabel(row.report_id) + "\nSelected applications: " + selectedValue +
      "\nAll applications: " + totalValue + "\nShare of all applications: " + shareValue;
  }

  function populateApplicationOptions() {
    element("application-options").innerHTML = dictionaryRows().map(function (row) {
      const id = "application-option-" + row.app_code;
      return '<div class="application-option" data-code="' + escapeHTML(row.app_code) + '" data-search="' +
        escapeHTML((row.app_code + " " + row.description).toLowerCase()) + '"><input id="' + escapeHTML(id) +
        '" type="checkbox" value="' + escapeHTML(row.app_code) + '"><label for="' + escapeHTML(id) +
        '"><strong>' + escapeHTML(row.app_code) + '</strong><span>' + escapeHTML(row.description) +
        "</span></label></div>";
    }).join("");
    filterApplicationOptions();
  }

  function filterApplicationOptions() {
    const query = state.appSearch.trim().toLowerCase();
    let shown = 0;
    document.querySelectorAll("#application-options .application-option").forEach(function (item) {
      const matches = !query || item.dataset.search.includes(query);
      item.hidden = !matches;
      if (matches) shown += 1;
    });
    renderApplicationSelectorState(shown);
  }

  function renderApplicationSelectorState(shownCount) {
    const options = Array.from(document.querySelectorAll("#application-options .application-option"));
    options.forEach(function (item) {
      const checkbox = item.querySelector('input[type="checkbox"]');
      checkbox.checked = state.selectedApps.has(item.dataset.code);
    });
    const shown = shownCount === undefined ? options.filter(function (item) { return !item.hidden; }).length : shownCount;
    element("application-option-status").textContent = shown + " of " + options.length + " application types shown; " +
      state.selectedApps.size + " selected.";
    element("select-filtered-apps").disabled = shown === 0;
    element("clear-selected-apps").disabled = state.selectedApps.size === 0;
  }

  function restoreApplicationSelectionFromURL() {
    const validCodes = new Set(dictionaryRows().map(function (row) { return row.app_code; }));
    const requested = new URL(window.location.href).searchParams.get("apps");
    if (!requested) return;
    requested.split(",").map(function (code) { return code.trim(); }).forEach(function (code) {
      if (validCodes.has(code)) state.selectedApps.add(code);
    });
  }

  function updateApplicationSelectionURL() {
    const url = new URL(window.location.href);
    const codes = selectedApplicationCodes();
    if (codes.length) url.searchParams.set("apps", codes.join(","));
    else url.searchParams.delete("apps");
    window.history.replaceState(null, "", url.pathname + url.search + url.hash);
  }

  function renderLineChart(target, rows, series, ariaLabel) {
    const width = 920;
    const height = 340;
    const left = 66;
    const right = 24;
    const top = 24;
    const bottom = 48;
    const chartWidth = width - left - right;
    const chartHeight = height - top - bottom;
    const values = rows.flatMap(function (row) {
      return series
        .filter(function (item) { return hasNumber(row[item.key]); })
        .map(function (item) { return number(row[item.key]); });
    });
    const maxValue = Math.max(1, ...values);
    const tickEvery = rows.length > 18 ? 5 : rows.length > 10 ? 3 : 1;

    function x(index) {
      return left + (index / Math.max(1, rows.length - 1)) * chartWidth;
    }

    function y(value) {
      return top + chartHeight - (value / maxValue) * chartHeight;
    }

    const grid = [0, 0.25, 0.5, 0.75, 1].map(function (step) {
      const position = y(maxValue * step);
      return '<g><line x1="' + left + '" x2="' + (width - right) + '" y1="' + position +
        '" y2="' + position + '" class="grid-line"></line><text x="' + (left - 12) +
        '" y="' + (position + 4) + '" text-anchor="end" class="axis-label">' +
        escapeHTML(compactNumber(maxValue * step)) + "</text></g>";
    }).join("");

    const xLabels = rows.map(function (row, index) {
      if (index % tickEvery !== 0 && index !== rows.length - 1) return "";
      return '<text x="' + x(index) + '" y="' + (height - 15) +
        '" text-anchor="middle" class="axis-label">' + escapeHTML(shortYear(row.report_id)) + "</text>";
    }).join("");

    const plots = series.map(function (item) {
      const segments = [];
      let current = [];

      rows.forEach(function (row, index) {
        if (!hasNumber(row[item.key])) {
          if (current.length) segments.push(current.join(" "));
          current = [];
          return;
        }

        current.push(x(index) + "," + y(number(row[item.key])));
      });

      if (current.length) segments.push(current.join(" "));

      const lines = segments.map(function (segment) {
        return '<polyline points="' + segment + '" fill="none" stroke="' + escapeHTML(item.colour) +
          '" stroke-width="3.5" stroke-linejoin="round" stroke-linecap="round"></polyline>';
      }).join("");

      const points = rows.map(function (row, index) {
        if (!hasNumber(row[item.key])) return "";
        const tooltip = item.tooltip
          ? item.tooltip(row)
          : item.label + ", " + yearLabel(row.report_id) + ": " + fullNumber(number(row[item.key]));
        return '<circle cx="' + x(index) + '" cy="' + y(number(row[item.key])) +
          '" r="4" fill="' + escapeHTML(item.colour) + '" class="chart-point" tabindex="0" role="img" aria-label="' +
          escapeHTML(tooltip) + '"><title>' +
          escapeHTML(tooltip) + "</title></circle>";
      }).join("");

      return "<g>" + lines + points + "</g>";
    }).join("");

    const legend = series.map(function (item) {
      return '<span><i style="background:' + escapeHTML(item.colour) + '"></i>' + escapeHTML(item.label) + "</span>";
    }).join("");

    target.innerHTML = '<div class="chart-wrap"><svg class="line-chart" viewBox="0 0 ' + width + " " + height +
      '" role="img" aria-label="' + escapeHTML(ariaLabel) + '">' + grid + xLabels + plots +
      '</svg><div class="legend" aria-label="Chart legend">' + legend + "</div></div>";
  }

  function renderRankingChart(target, rows) {
    const maximum = Math.max(1, ...rows.map(function (row) { return number(row.total_filings); }));
    const body = rows.map(function (row) {
      const width = Math.max(2, number(row.total_filings) / maximum * 100);
      return '<div class="rank-row"><div class="rank-label"><strong>' + escapeHTML(row.application_family) +
        "</strong><span>" + escapeHTML(row.description) + '</span></div><div class="rank-track"><span style="width:' +
        width + '%"></span></div><div class="rank-value">' + escapeHTML(compactNumber(number(row.total_filings))) + "</div></div>";
    }).join("");

    target.innerHTML = '<div class="ranking-chart" role="img" aria-label="Top application families by total filings">' +
      body + "</div>";
  }

  function populateYearFilters() {
    const bounds = selectedYearBounds();

    element("start-year").innerHTML = state.allYears.map(function (year, index) {
      return '<option value="' + escapeHTML(year) + '"' +
        (index > bounds.endIndex ? " disabled" : "") +
        (year === state.startYear ? " selected" : "") + ">" + escapeHTML(yearLabel(year)) + "</option>";
    }).join("");

    element("end-year").innerHTML = state.allYears.map(function (year, index) {
      return '<option value="' + escapeHTML(year) + '"' +
        (index < bounds.startIndex ? " disabled" : "") +
        (year === state.endYear ? " selected" : "") + ">" + escapeHTML(yearLabel(year)) + "</option>";
    }).join("");

    element("start-year").value = state.startYear;
    element("end-year").value = state.endYear;
  }

  function populateFamilyFilter() {
    const families = availableFamilies();
    if (families.length && !families.some(function (row) { return row.application_family === state.family; })) {
      state.family = families[0].application_family;
    }

    element("application-family").innerHTML = families.map(function (row) {
      return '<option value="' + escapeHTML(row.application_family) + '"' +
        (row.application_family === state.family ? " selected" : "") + ">" +
        escapeHTML(row.application_family + " · " + row.description) + "</option>";
    }).join("");

    element("application-family").value = state.family;
  }

  function renderCoverage() {
    const firstYear = state.allYears[0].split("_")[0];
    const lastYear = state.allYears[state.allYears.length - 1].split("_")[1];
    element("coverage-years").textContent = "Ontario · " + firstYear + "–" + lastYear;
    element("hero-title").textContent = state.allYears.length + " reporting years of tribunal activity, made explorable.";
    element("dataset-count").textContent = String(DATASETS.length);

    document.querySelectorAll(".first-detailed-year").forEach(function (item) {
      item.textContent = yearLabel(firstDetailedYear());
    });
  }

  function renderOverview(rows) {
    element("reporting-year-count").textContent = rows.length + (rows.length === 1 ? " reporting year" : " reporting years");

    renderLineChart(element("filing-chart"), rows, [
      { key: "total_filings", label: "All filings", colour: "#173f37" },
      { key: "landlord_filings", label: "Landlord", colour: "#d56735" },
      { key: "tenant_filings", label: "Tenant", colour: "#477f9b" }
    ], "Line chart of annual total, landlord and tenant filings");
  }

  function renderApplicationSection() {
    const rows = familyRows();
    const family = availableFamilies().find(function (row) { return row.application_family === state.family; });
    element("family-title").textContent = (rows[0] && rows[0].description) || (family && family.description) || state.family;
    element("ranking-party").textContent = PARTY_LABELS[state.party];

    document.querySelectorAll("#party-filter button").forEach(function (button) {
      const active = button.dataset.party === state.party;
      button.classList.toggle("active", active);
      button.setAttribute("aria-pressed", String(active));
    });

    if (rows.length) {
      renderLineChart(element("family-chart"), rows, [
        { key: "filings", label: state.family + " filings", colour: "#d56735" }
      ], "Line chart of " + state.family + " filings by year");
    } else {
      element("family-chart").innerHTML = '<p class="empty-state">Application-family breakdowns are unavailable for this reporting year. Detailed records begin in ' +
        escapeHTML(yearLabel(firstDetailedYear())) + ".</p>";
    }

    renderRankingChart(element("ranking-chart"), rankingRows());
  }

  function renderComparison() {
    const codes = selectedApplicationCodes();
    const empty = element("comparison-empty");
    const output = element("comparison-output");
    renderApplicationSelectorState();

    if (!codes.length) {
      element("comparison-codes").textContent = "No application types selected";
      element("comparison-chart").innerHTML = "";
      empty.innerHTML = "<strong>Choose at least one application type.</strong>" +
        "<span>The chart, annual percentages and period summary will appear here.</span>";
      empty.hidden = false;
      output.hidden = true;
      return;
    }

    const rows = comparisonRows();
    if (!rows.length) {
      const firstAvailable = state.allYears.find(function (reportId) {
        return (state.data.app_type_metrics || []).some(function (row) {
          return row.metric_id === "cases" && row.report_id === reportId;
        });
      });
      element("comparison-codes").textContent = codes.join(" + ");
      element("comparison-chart").innerHTML = "";
      empty.innerHTML = "<strong>No comparable application-type data in this year range.</strong>" +
        "<span>Change the reporting-period controls above to include " + escapeHTML(yearLabel(firstAvailable)) +
        " or later.</span>";
      empty.hidden = false;
      output.hidden = true;
      return;
    }

    const comparableRows = rows.filter(function (row) {
      return hasNumber(row.selected_applications) && hasNumber(row.all_applications);
    });
    const selectedAcrossPeriod = comparableRows.reduce(function (sum, row) {
      return sum + number(row.selected_applications);
    }, 0);
    const totalAcrossPeriod = comparableRows.reduce(function (sum, row) {
      return sum + number(row.all_applications);
    }, 0);
    const periodShare = totalAcrossPeriod ? selectedAcrossPeriod / totalAcrossPeriod : "";
    const excludedRows = rows.filter(function (row) {
      return !hasNumber(row.selected_applications) || !hasNumber(row.all_applications);
    });

    element("comparison-codes").textContent = codes.join(" + ");
    empty.hidden = true;
    output.hidden = false;

    renderLineChart(element("comparison-chart"), rows, [
      {
        key: "selected_applications",
        label: "Selected applications",
        colour: "#d56735",
        tooltip: comparisonTooltip
      },
      {
        key: "all_applications",
        label: "All LTB applications",
        colour: "#173f37",
        tooltip: comparisonTooltip
      }
    ], "Selected application types compared with all LTB applications by reporting year: " + codes.join(" plus "));

    element("comparison-summary").innerHTML = [
      ["Selected codes", codes.join(" + ")],
      ["Application types selected", fullNumber(codes.length)],
      ["Selected applications", comparableRows.length ? fullNumber(selectedAcrossPeriod) : "—"],
      ["All applications", comparableRows.length ? fullNumber(totalAcrossPeriod) : "—"],
      ["Share of all applications", hasNumber(periodShare) ? percent(number(periodShare)) : "—"]
    ].map(function (item) {
      return '<div><dt>' + escapeHTML(item[0]) + '</dt><dd>' + escapeHTML(item[1]) + "</dd></div>";
    }).join("");

    const missingNote = element("comparison-missing-note");
    if (excludedRows.length) {
      missingNote.hidden = false;
      missingNote.textContent = "The period summary uses " + comparableRows.length + " comparable reporting years. " +
        excludedRows.length + " displayed " + (excludedRows.length === 1 ? "year is" : "years are") +
        " excluded from the summary because a selected application type was not applicable or a required value was unavailable.";
    } else {
      missingNote.hidden = true;
      missingNote.textContent = "";
    }
  }

  function formatCell(column, value, row) {
    if (value === undefined || value === null || value === "") return "—";
    if (column === "report_id") return yearLabel(value);

    const numeric = Number(value);
    if (!Number.isFinite(numeric)) return String(value);
    if (/share|rate|pct/.test(column)) return percent(numeric);
    if (row.value_type === "percent" && /^(landlord|tenant)_received$/.test(column)) return percent(numeric);
    return fullNumber(numeric);
  }

  function filteredTableRows() {
    const query = state.tableSearch.trim().toLowerCase();
    return (state.data[state.tableId] || []).filter(function (row) {
      if (row.report_id && state.allYears.includes(row.report_id) && !yearInRange(row.report_id)) return false;
      if (row.party_type && state.party !== "all" && row.party_type !== state.party) return false;
      if (!query) return true;
      return Object.values(row).some(function (value) { return String(value).toLowerCase().includes(query); });
    });
  }

  function renderTable() {
    const dataset = DATASETS.find(function (item) { return item.id === state.tableId; }) || DATASETS[0];
    const rows = filteredTableRows();
    const originalFirstRow = (state.data[state.tableId] || [])[0] || {};
    const columns = Object.keys(rows[0] || originalFirstRow);
    const pageCount = Math.max(1, Math.ceil(rows.length / PAGE_SIZE));
    state.tablePage = Math.min(state.tablePage, pageCount - 1);
    const visibleRows = rows.slice(state.tablePage * PAGE_SIZE, state.tablePage * PAGE_SIZE + PAGE_SIZE);

    state.currentTableRows = rows;
    state.currentTableColumns = columns;

    element("dataset-description").textContent = dataset.description;
    element("matching-count").textContent = fullNumber(rows.length) + " matching " + (rows.length === 1 ? "row" : "rows");
    element("page-description").textContent = "Page " + (state.tablePage + 1) + " of " + pageCount;
    element("previous-page").disabled = state.tablePage === 0;
    element("next-page").disabled = state.tablePage >= pageCount - 1;
    element("download-csv").disabled = !rows.length;
    element("table-empty").hidden = Boolean(rows.length);

    element("table-head").innerHTML = "<tr>" + columns.map(function (column) {
      return '<th scope="col">' + escapeHTML(column.replaceAll("_", " ")) + "</th>";
    }).join("") + "</tr>";

    element("table-body").innerHTML = visibleRows.map(function (row) {
      return "<tr>" + columns.map(function (column) {
        return "<td>" + escapeHTML(formatCell(column, row[column], row)) + "</td>";
      }).join("") + "</tr>";
    }).join("");
  }

  function render() {
    if (!state.allYears.length) return;
    populateYearFilters();
    populateFamilyFilter();
    renderCoverage();
    renderOverview(filingRows());
    renderApplicationSection();
    renderComparison();
    renderTable();
  }

  function csvEscape(value) {
    const text = String(value ?? "");
    return /[",\n\r]/.test(text) ? '"' + text.replaceAll('"', '""') + '"' : text;
  }

  function downloadTable() {
    if (!state.currentTableRows.length) return;
    const columns = state.currentTableColumns;
    const body = [columns.join(",")].concat(state.currentTableRows.map(function (row) {
      return columns.map(function (column) { return csvEscape(row[column]); }).join(",");
    })).join("\n");

    const url = URL.createObjectURL(new Blob([body], { type: "text/csv;charset=utf-8" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = state.tableId + "-filtered.csv";
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  function bindEvents() {
    element("start-year").addEventListener("change", function (event) {
      state.startYear = event.target.value;
      state.tablePage = 0;
      render();
    });

    element("end-year").addEventListener("change", function (event) {
      state.endYear = event.target.value;
      state.tablePage = 0;
      render();
    });

    element("reset-filters").addEventListener("click", function () {
      state.startYear = state.allYears[0];
      state.endYear = state.allYears[state.allYears.length - 1];
      state.party = "all";
      state.tablePage = 0;
      render();
    });

    document.querySelectorAll("#party-filter button").forEach(function (button) {
      button.addEventListener("click", function () {
        state.party = button.dataset.party;
        state.tablePage = 0;
        render();
      });
    });

    element("application-family").addEventListener("change", function (event) {
      state.family = event.target.value;
      render();
    });

    element("application-search").addEventListener("input", function (event) {
      state.appSearch = event.target.value;
      filterApplicationOptions();
    });

    element("application-options").addEventListener("change", function (event) {
      if (!event.target.matches('input[type="checkbox"]')) return;
      if (event.target.checked) state.selectedApps.add(event.target.value);
      else state.selectedApps.delete(event.target.value);
      updateApplicationSelectionURL();
      renderComparison();
    });

    element("select-filtered-apps").addEventListener("click", function () {
      document.querySelectorAll("#application-options .application-option:not([hidden])").forEach(function (item) {
        state.selectedApps.add(item.dataset.code);
      });
      updateApplicationSelectionURL();
      renderComparison();
    });

    element("clear-selected-apps").addEventListener("click", function () {
      state.selectedApps.clear();
      updateApplicationSelectionURL();
      renderComparison();
    });

    element("dataset-select").addEventListener("change", function (event) {
      state.tableId = event.target.value;
      state.tablePage = 0;
      render();
    });

    element("table-search").addEventListener("input", function (event) {
      state.tableSearch = event.target.value;
      state.tablePage = 0;
      renderTable();
    });

    element("previous-page").addEventListener("click", function () {
      if (state.tablePage > 0) state.tablePage -= 1;
      renderTable();
    });

    element("next-page").addEventListener("click", function () {
      state.tablePage += 1;
      renderTable();
    });

    element("download-csv").addEventListener("click", downloadTable);
  }

  async function initialize() {
    const status = element("status-banner");

    try {
      const entries = await Promise.all(DATASETS.concat(COMPARISON_DATASETS).map(async function (dataset) {
        const url = new URL("./data/" + dataset.file, document.baseURI);
        const response = await fetch(url);
        if (!response.ok) throw new Error("Could not load " + dataset.label + " (HTTP " + response.status + ")");
        return [dataset.id, parseCSV(await response.text())];
      }));

      state.data = Object.fromEntries(entries);
      state.allYears = state.data.reports.map(function (row) { return row.report_id; });
      if (!state.allYears.length) throw new Error("The annual-report inventory does not contain any reporting periods.");

      state.startYear = state.allYears[0];
      state.endYear = state.allYears[state.allYears.length - 1];

      element("dataset-select").innerHTML = DATASETS.map(function (dataset) {
        return '<option value="' + escapeHTML(dataset.id) + '"' +
          (dataset.id === state.tableId ? " selected" : "") + ">" + escapeHTML(dataset.label) + "</option>";
      }).join("");
      element("dataset-select").value = state.tableId;

      restoreApplicationSelectionFromURL();
      populateApplicationOptions();
      bindEvents();
      render();
      status.hidden = true;
    } catch (error) {
      status.hidden = false;
      status.classList.add("error");
      status.setAttribute("role", "alert");
      status.textContent = "The explorer could not load its data. " + error.message +
        (window.location.protocol === "file:" ? " Open the folder through a local web server instead of opening index.html directly." : "");
      console.error("Ontario LTB Data Explorer failed to initialize:", error);
    }
  }

  initialize();
})();
