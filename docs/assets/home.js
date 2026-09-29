(function () {
  "use strict";

  function parseCSV(text) {
    const lines = text.trim().split(/\r?\n/);
    const headers = lines.shift().split(",");
    return lines.map(function (line) {
      const cells = line.split(",");
      return Object.fromEntries(headers.map(function (header, index) {
        return [header, cells[index] || ""];
      }));
    });
  }

  function hasNumber(value) {
    return value !== "" && value !== null && value !== undefined && Number.isFinite(Number(value));
  }

  function yearLabel(value) {
    const parts = value.split("_");
    return parts[0] + "–" + parts[1].slice(-2);
  }

  function shortYear(value) {
    return value.split("_")[0];
  }

  function fullNumber(value) {
    return new Intl.NumberFormat("en-CA", { maximumFractionDigits: 0 }).format(Number(value));
  }

  function compactNumber(value) {
    return new Intl.NumberFormat("en-CA", { notation: "compact", maximumFractionDigits: 1 }).format(Number(value));
  }

  function percent(value) {
    return new Intl.NumberFormat("en-CA", { style: "percent", maximumFractionDigits: 1 }).format(Number(value));
  }

  function escapeHTML(value) {
    return String(value).replace(/[&<>"]/g, function (character) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[character];
    });
  }

  /*
   * ORIGINAL CHART RENDERER — UNCHANGED
   */
  function renderLineChart(target, rows, series, title, description) {
    if (!target) return;
    const width = 980;
    const height = 410;
    const margin = { top: 30, right: 26, bottom: 58, left: 72 };
    const chartWidth = width - margin.left - margin.right;
    const chartHeight = height - margin.top - margin.bottom;
    const values = rows.flatMap(function (row) {
      return series.filter(function (item) { return hasNumber(row[item.key]); })
        .map(function (item) { return Number(row[item.key]); });
    });
    const maximum = Math.max(1, ...values);
    const x = function (index) { return margin.left + index / Math.max(1, rows.length - 1) * chartWidth; };
    const y = function (value) { return margin.top + chartHeight - Number(value) / maximum * chartHeight; };

    const grid = [0, .25, .5, .75, 1].map(function (tick) {
      const value = maximum * tick;
      return '<g><line class="area-grid" x1="' + margin.left + '" x2="' + (width - margin.right) + '" y1="' + y(value) + '" y2="' + y(value) + '"></line>' +
        '<text class="area-axis" x="' + (margin.left - 12) + '" y="' + (y(value) + 4) + '" text-anchor="end">' + escapeHTML(compactNumber(value)) + '</text></g>';
    }).join("");

    const labels = rows.map(function (row, index) {
      if (index % 4 !== 0 && index !== rows.length - 1) return "";
      return '<text class="area-axis" x="' + x(index) + '" y="' + (height - 20) + '" text-anchor="middle">' + escapeHTML(shortYear(row.report_id)) + '</text>';
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
        current.push(x(index) + "," + y(row[item.key]));
      });
      if (current.length) segments.push(current.join(" "));

      const lines = segments.map(function (points) {
        return '<polyline points="' + points + '" fill="none" stroke="' + item.colour + '" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"></polyline>';
      }).join("");
      const points = rows.map(function (row, index) {
        if (!hasNumber(row[item.key])) return "";
        const label = item.label + ", " + yearLabel(row.report_id) + ": " + fullNumber(row[item.key]);
        return '<circle class="home-chart-point" cx="' +
                x(index) +
                '" cy="' +
                y(row[item.key]) +
                '" r="2.5" fill="' +
                item.colour +
                '" aria-hidden="true">' +
                '<title>' +
                escapeHTML(label) +
                '</title></circle>';
      }).join("");
      return "<g>" + lines + points + "</g>";
    }).join("");

    const legend = series.map(function (item) {
      return '<span><i style="background:' + item.colour + '"></i>' + escapeHTML(item.label) + '</span>';
    }).join("");

    target.innerHTML = '<div class="home-chart-scroll"><svg viewBox="0 0 ' + width + ' ' + height + '" role="img" aria-labelledby="' + target.id + '-title ' + target.id + '-desc"><title id="' + target.id + '-title">' + escapeHTML(title) + '</title><desc id="' + target.id + '-desc">' + escapeHTML(description) + '</desc>' + grid + plots + labels + '</svg></div><div class="area-legend" aria-label="Chart legend">' + legend + '</div>';
  }

  /*
   * PLUMBING CHANGE:
   * The deleted ltb_filing_summary_by_year.csv is no longer required.
   *
   * Landlord and tenant counts are reconstructed from
   * derived_application_family_share_by_year.csv using the same
   * longitudinal classification now used by Explore.
   *
   * A1–A4 remain outside the landlord/tenant buckets because those
   * families span an earlier combined reporting regime and a later
   * landlord/tenant split reporting regime.
   */
  function buildApplicationRows(operational, applicationFamilies, receipts) {
    const totals = new Map(
      operational
        .filter(function (row) { return row.metric_id === "total_received"; })
        .map(function (row) { return [row.report_id, row.value]; })
    );

    const statusMap = new Map(
      receipts.map(function (row) {
        return [row.report_id, row.status];
      })
    );

    const byYear = new Map();

    applicationFamilies.forEach(function (row) {
      if (!hasNumber(row.filings)) return;

      if (!byYear.has(row.report_id)) {
        byYear.set(row.report_id, {
          landlord_applications: 0,
          tenant_applications: 0
        });
      }

      const summary = byYear.get(row.report_id);

      const isAFamily = ["A1", "A2", "A3", "A4"].includes(
        row.application_family
      );

      if (!isAFamily && row.party_type === "landlord") {
        summary.landlord_applications += Number(row.filings);
      }

      if (!isAFamily && row.party_type === "tenant") {
        summary.tenant_applications += Number(row.filings);
      }
    });

    return Array.from(totals.keys()).sort().map(function (reportId) {
      const detail = byYear.get(reportId);

      return {
        report_id: reportId,
        total_applications: totals.get(reportId),
        landlord_applications: detail ? detail.landlord_applications : "",
        tenant_applications: detail ? detail.tenant_applications : "",
        share_status: statusMap.get(reportId) || "not available"
      };
    });
  }

  /*
   * ORIGINAL APPLICATION CHART — UNCHANGED
   */
  function renderApplicationChart(rows) {
    renderLineChart(document.getElementById("applications-volume-chart"), rows, [
      { key: "total_applications", label: "All applications", colour: "#173f37" },
      { key: "landlord_applications", label: "Landlord applications", colour: "#3c918f" },
      { key: "tenant_applications", label: "Tenant applications", colour: "#a76444" }
    ], "Total, landlord and tenant applications received over time", "A line chart of annual application volumes. Total applications begin in 1998–99. Detailed landlord and tenant counts begin in 1999–00. Landlord applications form the largest detailed series throughout.");

    const table = document.getElementById("applications-volume-table-body");
    if (table) {
      table.innerHTML = rows.map(function (row) {
        return '<tr><td>' + yearLabel(row.report_id) + '</td><td>' + fullNumber(row.total_applications) + '</td><td>' +
          (hasNumber(row.landlord_applications) ? fullNumber(row.landlord_applications) : 'Not available') + '</td><td>' +
          (hasNumber(row.tenant_applications) ? fullNumber(row.tenant_applications) : 'Not available') + '</td><td>' + escapeHTML(row.share_status) + '</td></tr>';
      }).join("");
    }
  }

  /*
   * ORIGINAL EVICTION CHART — UNCHANGED
   */
  function renderEvictionChart(rows) {
    renderLineChart(document.getElementById("eviction-volume-chart"), rows, [
      { key: "total_applications", label: "All applications", colour: "#173f37" },
      { key: "eviction_related_l1_l2_l4", label: "L1 + L2 + L4", colour: "#3c918f" }
    ], "Eviction-related L1, L2 and L4 applications compared with all applications", "A line chart comparing the calculated annual sum of L1, L2 and L4 case counts with all applications received from 1999–00 through 2024–25. The two series move closely together, while the calculated series remains below the total.");

    const table = document.getElementById("eviction-volume-table-body");
    if (table) {
      table.innerHTML = rows.map(function (row) {
        return '<tr><td>' + yearLabel(row.report_id) + '</td><td>' + fullNumber(row.l1_cases) + '</td><td>' + fullNumber(row.l2_cases) + '</td><td>' + fullNumber(row.l4_cases) + '</td><td>' + fullNumber(row.eviction_related_l1_l2_l4) + '</td><td>' + fullNumber(row.total_applications) + '</td><td>' + percent(row.share_of_total) + '</td></tr>';
      }).join("");
    }
  }

  /*
   * PLUMBING CHANGE:
   *   old: ltb_filing_summary_by_year.csv
   *   new: derived_application_family_share_by_year.csv
   *
   *   old: eviction_related_l1_l2_l4.csv
   *   new: derived_eviction_related_l1_l2_l4.csv
   */
  Promise.all([
    fetch("./datasets/operational_metrics.csv").then(function (response) {
      if (!response.ok) {
        throw new Error("operational_metrics.csv: HTTP " + response.status);
      }
      return response.text();
    }),

    fetch("./datasets/derived_application_family_share_by_year.csv").then(function (response) {
      if (!response.ok) {
        throw new Error("derived_application_family_share_by_year.csv: HTTP " + response.status);
      }
      return response.text();
    }),

    fetch("./datasets/landlord_vs_tenant_receipts.csv").then(function (response) {
      if (!response.ok) {
        throw new Error("landlord_vs_tenant_receipts.csv: HTTP " + response.status);
      }
      return response.text();
    }),

    fetch("./datasets/derived_eviction_related_l1_l2_l4.csv").then(function (response) {
      if (!response.ok) {
        throw new Error("derived_eviction_related_l1_l2_l4.csv: HTTP " + response.status);
      }
      return response.text();
    })
  ]).then(function (texts) {
    renderApplicationChart(
      buildApplicationRows(
        parseCSV(texts[0]),
        parseCSV(texts[1]),
        parseCSV(texts[2])
      )
    );

    renderEvictionChart(
      parseCSV(texts[3])
    );
  }).catch(function (error) {
    document.querySelectorAll(".home-line-chart").forEach(function (target) {
      target.innerHTML =
        '<p class="chart-error" role="alert">' +
        "The chart data could not be loaded. Check that the required CSV files are present in the datasets folder." +
        "</p>";
    });

    console.error(
      "LTB homepage chart data failed to load:",
      error
    );
  });
})();