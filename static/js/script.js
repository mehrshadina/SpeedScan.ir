/* ============================================================
   PAGE SPEED DASHBOARD JS - COMPLETE FINAL VERSION
   Author: ChatGPT (custom optimized for your dashboard)
   ============================================================ */

/* ------------------------------------------------------------
   1) DOM Shortcuts
------------------------------------------------------------ */
const $ = (id) => document.getElementById(id);

/* ------------------------------------------------------------
   2) Color rules for CWV
------------------------------------------------------------ */
function scoreColorMetric(score, metricId) {
  if (score == null) return 'var(--muted)';

  switch (metricId) {
    case 'cumulative-layout-shift': // CLS
      if (score <= 0.1) return 'var(--success)';
      if (score <= 0.25) return 'var(--warning)';
      return 'var(--danger)';

    case 'total-blocking-time': // TBT
      if (score <= 200) return 'var(--success)';
      if (score <= 600) return 'var(--warning)';
      return 'var(--danger)';

    case 'first-contentful-paint': // FCP
    case 'largest-contentful-paint': // LCP
      if (score <= 1800) return 'var(--success)';
      if (score <= 3000) return 'var(--warning)';
      return 'var(--danger)';

    case 'speed-index':
      if (score <= 1800) return 'var(--success)';
      if (score <= 3000) return 'var(--warning)';
      return 'var(--danger)';

    default:
      if (score >= 90) return 'var(--success)';
      if (score >= 50) return 'var(--warning)';
      return 'var(--danger)';
  }
}

/* ------------------------------------------------------------
   3) Set Metric Helper
------------------------------------------------------------ */
function setMetric(id, displayValue, numericValue) {
  const el = $(id);
  const v = displayValue || numericValue || '—';
  el.innerText = v;

  if (numericValue != null) {
    el.style.color = scoreColorMetric(numericValue, id);
  } else {
    el.style.color = 'var(--muted)';
  }
}

/* ------------------------------------------------------------
   4) Render Environment Metadata (3×2 grid)
------------------------------------------------------------ */
function renderTestMeta(lhr) {
  const env = lhr?.environment || {};

  const meta = [
    {
      label: "Captured at",
      value: env.timestamp || "—",
      tip: "زمان دقیق ثبت گزارش"
    },
    {
      label: "Emulated Device",
      value: env.device || "Desktop",
      tip: "نوع دستگاهی که تست روی آن شبیه‌سازی شده است"
    },
    {
      label: "Lighthouse Version",
      value: env.lighthouseVersion || "—",
      tip: "نسخه Lighthouse استفاده‌شده"
    },
    {
      label: "Mode",
      value: env.mode || "Single page session",
      tip: "نوع اجرای تست"
    },
    {
      label: "Load Type",
      value: env.loadType || "Initial load",
      tip: "نوع بارگذاری اولیه"
    },
    {
      label: "Runtime",
      value: env.runtime || "HeadlessChromium",
      tip: "مرورگر یا موتور اجرایی"
    }
  ];

  let html = "";
  meta.forEach((m) => {
    html += `
      <div class="meta-item">
        <strong>${m.label}:</strong> ${m.value}
        <div class="tooltip">${m.tip}</div>
      </div>
    `;
  });

  $("testMeta").innerHTML = html;
}

/* ------------------------------------------------------------
   5) Render Filmstrip
------------------------------------------------------------ */
function renderFilmstrip(frames) {
  const container = $("filmstrip");
  container.innerHTML = "";

  if (!frames || !frames.length) {
    container.innerHTML = "<div class='muted'>No frames available</div>";
    return;
  }

  frames.forEach((f) => {
    const div = document.createElement("div");
    div.className = "thumb";
    div.style.backgroundImage = `url(${f.data})`;
    div.innerHTML = `<span>${(f.time / 1000).toFixed(1)}s</span>`;
    container.appendChild(div);
  });
}

/* ------------------------------------------------------------
   6) Render Categories
------------------------------------------------------------ */
function renderCategories(res) {
  const categories = res.lhr.categories;
  const audits = res.lhr.audits;

  const container = $("categories");
  container.innerHTML = "";

  Object.keys(categories).forEach((catKey) => {
    const c = categories[catKey];
    const percent = Math.round(c.score * 100);

    const catBox = document.createElement("div");
    catBox.className = "category-box";

    let items = "";
    (c.auditRefs || []).forEach((ref) => {
      const a = audits[ref.id];
      if (!a) return;

      const score = a.score === null ? "—" : Math.round(a.score * 100);
      const color =
        a.score === null
          ? "var(--muted)"
          : score >= 90
          ? "var(--success)"
          : score >= 50
          ? "var(--warning)"
          : "var(--danger)";

      items += `
        <div class="cat-item">
          <span>${a.title}</span>
          <span style="color:${color}">${score === "—" ? "—" : score + "%"}</span>
        </div>
      `;
    });

    catBox.innerHTML = `
      <h3>${c.title} <span class="cat-score">${percent}</span></h3>
      <div class="cat-list">${items}</div>
    `;

    container.appendChild(catBox);
  });
}

/* ------------------------------------------------------------
   7) Render Opportunities & Diagnostics
------------------------------------------------------------ */
function renderOppDiag(res) {
  const audits = res.lhr.audits;

  // Opportunities
  const oppHTML = Object.values(audits)
    .filter((a) => a.details?.type === "opportunity")
    .map(
      (a) => `
      <div class="opp-box">
        <div class="opp-title">${a.title}</div>
        <div class="opp-desc">${a.description || ""}</div>
        <div class="opp-savings">Savings: ${a.details.overallSavingsMs} ms</div>
      </div>`
    )
    .join("");

  $("opportunities").innerHTML = oppHTML || "<div class='muted'>No opportunities</div>";

  // Diagnostics
  const diagHTML = Object.values(audits)
    .filter((a) => a.details?.type === "diagnostic")
    .map(
      (a) => `
      <div class="diag-box">
        <div class="diag-title">${a.title}</div>
        <div class="diag-desc">${a.description || ""}</div>
      </div>`
    )
    .join("");

  $("diagnostics").innerHTML = diagHTML || "<div class='muted'>No diagnostics</div>";
}

/* ------------------------------------------------------------
   8) Render Core Web Vitals + Additional Metrics
------------------------------------------------------------ */
function renderCWV(audits) {
  setMetric("lcp", audits["largest-contentful-paint"]?.displayValue, audits["largest-contentful-paint"]?.numericValue);
  setMetric("fcp", audits["first-contentful-paint"]?.displayValue, audits["first-contentful-paint"]?.numericValue);
  setMetric("cls", audits["cumulative-layout-shift"]?.displayValue, audits["cumulative-layout-shift"]?.numericValue);

  setMetric("tbt", audits["total-blocking-time"]?.displayValue, audits["total-blocking-time"]?.numericValue);
  setMetric("speedIndex", audits["speed-index"]?.displayValue, audits["speed-index"]?.numericValue);
}

/* ------------------------------------------------------------
   9) Main Renderer
------------------------------------------------------------ */
function renderAll(res) {
  const lhr = res.lhr;

  renderTestMeta(lhr);
  renderCWV(lhr.audits);
  renderFilmstrip(res.filmstrip);
  renderOppDiag(res);
  renderCategories(res);
}

/* ------------------------------------------------------------
   10) Fetch API from Django
------------------------------------------------------------ */
async function loadReport() {
  try {
    const response = await fetch("/api/lighthouse/");
    const data = await response.json();
    renderAll(data);
  } catch (err) {
    console.error("Load error:", err);
  }
}

loadReport();
