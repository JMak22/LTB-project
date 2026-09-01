/* LTB Wait Times — dependency-free static dashboard. */
(function () {
  "use strict";

  const MAX_SERIES = 5;
  const COLOURS = ["#173f37", "#d56735", "#477f9b", "#8a5c87", "#7b7927"];
  const charts = {
    first: { selected: new Set(), search: "", rows: [], periods: [], series: [] },
    order: { selected: new Set(), search: "", rows: [], periods: [], series: [] }
  };
  let dictionary = new Map();

  function element(id) {
    const value = document.getElementById(id);
    if (!value) throw new Error("A required page element is missing: " + id);
    return value;
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

  async function loadCSV(file, label) {
    const response = await fetch(new URL("./data/" + file, document.baseURI));
    if (!response.ok) throw new Error("Could not load " + label + " (HTTP " + response.status + ")");
    return parseCSV(await response.text());
  }

  function reportSlot(reportId) {
    const match = /^(\d{4})_(\d{4})_(Q[1-4]|FY)$/.exec(reportId || "");
    if (!match) return Number.MAX_SAFE_INTEGER;
    const year = Number(match[1]);
    if (match[3] === "FY") return year * 4;
    return year * 4 + Number(match[3].slice(1)) - 1;
  }

  function periodLabel(reportId) {
    const match = /^(\d{4})_(\d{4})_(Q[1-4]|FY)$/.exec(reportId || "");
    if (!match) return reportId;
    return match[1] + "–" + match[2].slice(-2) + " " + match[3];
  }

  function normaliseFirstHearing(rows) {
    const grouped = new Map();
    rows.forEach(function (row) {
      if (row.region_id !== "province_average") return;
      const key = [row.report_id, row.source_file, row.app_combo, row.avg_days,
        row.performance_standard, row.percent_in_standard].join("\u001f");
      if (!grouped.has(key)) {
        grouped.set(key, {
          report_id: row.report_id,
          period_label: periodLabel(row.report_id),
          app_combo: row.app_combo,
          avg_days: row.avg_days,
          source_file: row.source_file,
          app_types: []
        });
      }
      const record = grouped.get(key);
      if (!record.app_types.includes(row.app_type)) record.app_types.push(row.app_type);
    });

    return Array.from(grouped.values()).map(function (row) {
      row.series_id = row.app_types.join("/");
      delete row.app_types;
      return row;
    });
  }

  function codeForDictionary(code) {
    return code.replace("_L", "L").replace("_T", "T");
  }

  function seriesDescription(seriesId) {
    const descriptions = [];
    seriesId.split("/").forEach(function (code) {
      const record = dictionary.get(codeForDictionary(code));
      if (record && record.description && !descriptions.includes(record.description)) {
        descriptions.push(record.description);
      }
    });
    return descriptions.join(" + ");
  }

  function buildSeries(rows) {
    const records = new Map();
    rows.forEach(function (row) {
      if (!records.has(row.series_id)) {
        records.set(row.series_id, {
          id: row.series_id,
          appCombo: row.app_combo,
          description: seriesDescription(row.series_id),
          periods: new Set()
        });
      }
      records.get(row.series_id).periods.add(row.report_id);
    });
    return Array.from(records.values()).sort(function (left, right) {
      return left.id.localeCompare(right.id, undefined, { numeric: true });
    });
  }

  function buildPeriods(rows) {
    const periods = new Map();
    rows.forEach(function (row) {
      if (!periods.has(row.report_id)) {
        periods.set(row.report_id, {
          id: row.report_id,
          label: row.period_label || periodLabel(row.report_id),
          slot: reportSlot(row.report_id)
        });
      }
    });
    return Array.from(periods.values()).sort(function (left, right) {
      return left.slot - right.slot || left.id.localeCompare(right.id);
    });
  }

  function formatDays(value) {
    return new Intl.NumberFormat("en-CA", { maximumFractionDigits: 1 }).format(Number(value));
  }

  function niceMaximum(value) {
    if (value <= 10) return Math.ceil(value / 2) * 2;
    if (value <= 50) return Math.ceil(value / 5) * 5;
    if (value <= 200) return Math.ceil(value / 20) * 20;
    return Math.ceil(value / 100) * 100;
  }

  function optionMarkup(series, selected) {
    return '<label class="wait-option" data-search="' +
      escapeHTML((series.id + " " + series.appCombo + " " + series.description).toLowerCase()) + '">' +
      '<input type="checkbox" value="' + escapeHTML(series.id) + '"' + (selected ? " checked" : "") + '>' +
      '<span><strong>' + escapeHTML(series.id.replaceAll("_", " ")) + '</strong>' +
      '<small>' + escapeHTML(series.description || "Reported application grouping") + '</small></span></label>';
  }

  function renderOptions(kind) {
    const chart = charts[kind];
    const options = element(kind + "-options");
    options.innerHTML = chart.series.map(function (series) {
      return optionMarkup(series, chart.selected.has(series.id));
    }).join("");
    filterOptions(kind);
  }

  function filterOptions(kind) {
    const chart = charts[kind];
    const query = chart.search.trim().toLowerCase();
    let visible = 0;
    element(kind + "-options").querySelectorAll(".wait-option").forEach(function (option) {
      const matches = !query || option.dataset.search.includes(query);
      option.hidden = !matches;
      if (matches) visible += 1;
    });
    element(kind + "-option-status").textContent = visible + " of " + chart.series.length +
      " groupings shown · " + chart.selected.size + " selected";
  }

  function selectedRows(kind) {
    const chart = charts[kind];
    const values = new Map();
    chart.rows.forEach(function (row) {
      if (!chart.selected.has(row.series_id)) return;
      values.set(row.series_id + "\u001f" + row.report_id, row);
    });
    return values;
  }

  function renderChart(kind) {
    const chart = charts[kind];
    const target = element(kind + "-chart");
    const empty = element(kind + "-empty");
    const selected = chart.series.filter(function (series) { return chart.selected.has(series.id); });
    filterOptions(kind);

    if (!selected.length) {
      target.innerHTML = "";
      empty.hidden = false;
      return;
    }
    empty.hidden = true;

    const values = selectedRows(kind);
    const numericValues = Array.from(values.values()).map(function (row) { return Number(row.avg_days); })
      .filter(Number.isFinite);
    const maxValue = niceMaximum(Math.max(1, ...numericValues));
    const width = 1020;
    const height = 430;
    const left = 76;
    const right = 24;
    const top = 30;
    const bottom = 76;
    const plotWidth = width - left - right;
    const plotHeight = height - top - bottom;
    const minSlot = chart.periods[0].slot;
    const maxSlot = chart.periods[chart.periods.length - 1].slot;
    const slotRange = Math.max(1, maxSlot - minSlot);
    const x = function (slot) { return left + ((slot - minSlot) / slotRange) * plotWidth; };
    const y = function (value) { return top + plotHeight - (value / maxValue) * plotHeight; };

    const grid = [0, 0.25, 0.5, 0.75, 1].map(function (step) {
      const position = y(maxValue * step);
      return '<g><line x1="' + left + '" x2="' + (width - right) + '" y1="' + position +
        '" y2="' + position + '" class="grid-line"></line><text x="' + (left - 12) + '" y="' +
        (position + 4) + '" text-anchor="end" class="axis-label">' +
        escapeHTML(formatDays(maxValue * step)) + "</text></g>";
    }).join("");

    const labelEvery = Math.max(1, Math.ceil(chart.periods.length / 9));
    const xLabels = chart.periods.map(function (period, index) {
      if (index % labelEvery !== 0 && index !== chart.periods.length - 1) return "";
      return '<text x="' + x(period.slot) + '" y="' + (height - 38) +
        '" text-anchor="end" transform="rotate(-35 ' + x(period.slot) + " " + (height - 38) +
        ')" class="axis-label">' + escapeHTML(period.label) + "</text>";
    }).join("");

    const plots = selected.map(function (series, seriesIndex) {
      const colour = COLOURS[seriesIndex];
      const observations = chart.periods.map(function (period) {
        const row = values.get(series.id + "\u001f" + period.id);
        return row && Number.isFinite(Number(row.avg_days))
          ? { period: period, row: row, value: Number(row.avg_days) }
          : null;
      });
      const segments = [];
      let current = [];
      let previousSlot = null;
      observations.forEach(function (observation) {
        if (!observation || (previousSlot !== null && observation.period.slot - previousSlot > 1)) {
          if (current.length) segments.push(current);
          current = [];
          previousSlot = observation ? observation.period.slot : null;
          if (!observation) return;
        }
        current.push(x(observation.period.slot) + "," + y(observation.value));
        previousSlot = observation.period.slot;
      });
      if (current.length) segments.push(current);

      const lines = segments.map(function (points) {
        return '<polyline points="' + points.join(" ") + '" fill="none" stroke="' + colour +
          '" stroke-width="3.5" stroke-linejoin="round" stroke-linecap="round"></polyline>';
      }).join("");
      const points = observations.map(function (observation) {
        if (!observation) return "";
        const tooltip = series.id.replaceAll("_", " ") + ", " + observation.period.label + ": " +
          formatDays(observation.value) + " average days";
        return '<circle cx="' + x(observation.period.slot) + '" cy="' + y(observation.value) +
          '" r="4.5" fill="' + colour + '" class="chart-point" tabindex="0" role="img" aria-label="' +
          escapeHTML(tooltip) + '"><title>' + escapeHTML(tooltip) + "</title></circle>";
      }).join("");
      return "<g>" + lines + points + "</g>";
    }).join("");

    const legend = selected.map(function (series, index) {
      return '<span><i style="background:' + COLOURS[index] + '"></i>' +
        escapeHTML(series.id.replaceAll("_", " ")) + "</span>";
    }).join("");
    const chartLabel = (kind === "first" ? "Average days to first hearing" : "Average days from final hearing to order") +
      " for " + selected.map(function (series) { return series.id; }).join(", ");

    target.innerHTML = '<div class="chart-wrap"><svg class="line-chart wait-chart" viewBox="0 0 ' + width + " " + height +
      '" role="img" aria-label="' + escapeHTML(chartLabel) + '"><text x="18" y="' + (top + plotHeight / 2) +
      '" transform="rotate(-90 18 ' + (top + plotHeight / 2) + ')" text-anchor="middle" class="axis-title">Average days</text>' +
      grid + xLabels + plots + '</svg><div class="legend" aria-label="Chart legend">' + legend + "</div></div>";
  }

  function bindChart(kind) {
    element(kind + "-search").addEventListener("input", function (event) {
      charts[kind].search = event.target.value;
      filterOptions(kind);
    });
    element(kind + "-clear").addEventListener("click", function () {
      charts[kind].selected.clear();
      renderOptions(kind);
      renderChart(kind);
    });
    element(kind + "-options").addEventListener("change", function (event) {
      if (!event.target.matches('input[type="checkbox"]')) return;
      const id = event.target.value;
      if (event.target.checked && charts[kind].selected.size >= MAX_SERIES) {
        event.target.checked = false;
        element(kind + "-option-status").textContent = "Choose no more than five groupings at once.";
        return;
      }
      if (event.target.checked) charts[kind].selected.add(id);
      else charts[kind].selected.delete(id);
      renderChart(kind);
    });
  }

  function chooseDefaults(kind) {
    ["L1", "L9"].forEach(function (id) {
      if (charts[kind].series.some(function (series) { return series.id === id; })) charts[kind].selected.add(id);
    });
    if (!charts[kind].selected.size && charts[kind].series[0]) charts[kind].selected.add(charts[kind].series[0].id);
  }

  async function initialize() {
    const status = element("wait-status");
    try {
      const loaded = await Promise.all([
        loadCSV("avg_days_first_hearing.csv", "Average Days to First Hearing"),
        loadCSV("avg_days_hearing_to_order.csv", "Average Days from Hearing to Order"),
        loadCSV("app_type_dictionary.csv", "application type dictionary")
      ]);
      dictionary = new Map(loaded[2].map(function (row) { return [row.app_code, row]; }));
      charts.first.rows = normaliseFirstHearing(loaded[0]);
      charts.order.rows = loaded[1];

      ["first", "order"].forEach(function (kind) {
        charts[kind].series = buildSeries(charts[kind].rows);
        charts[kind].periods = buildPeriods(charts[kind].rows);
        chooseDefaults(kind);
        renderOptions(kind);
        renderChart(kind);
        bindChart(kind);
      });
      status.hidden = true;
    } catch (error) {
      status.hidden = false;
      status.classList.add("error");
      status.setAttribute("role", "alert");
      status.textContent = "The wait-time dashboard could not load its data. " + error.message +
        (window.location.protocol === "file:" ? " Open the folder through a local web server instead of opening the HTML file directly." : "");
      console.error("LTB Wait Times failed to initialize:", error);
    }
  }

  initialize();
})();
