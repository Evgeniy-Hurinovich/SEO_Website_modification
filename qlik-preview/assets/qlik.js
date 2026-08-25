(function () {
  const D = window.A2SEO;
  const weeks = D.weeks;
  const labels = weeks.map((w) => w.label);
  const perfM = weeks.map((w) => w.mobile.perf);
  const lcpM = weeks.map((w) => w.mobile.lcp);
  const tbtM = weeks.map((w) => w.mobile.tbt);
  const fcpM = weeks.map((w) => (w.mobile.fcp != null ? w.mobile.fcp : null));
  const perfD = weeks.map((w) => (w.desktop && w.desktop.perf != null ? w.desktop.perf : null));
  const lcpD = weeks.map((w) => (w.desktop && w.desktop.lcp != null ? w.desktop.lcp : null));
  const tbtD = weeks.map((w) => (w.desktop && w.desktop.tbt != null ? w.desktop.tbt : null));
  const fcpD = weeks.map((w) => (w.desktop && w.desktop.fcp != null ? w.desktop.fcp : null));

  function lineChart(svg, series, opts) {
    const w = 640;
    const h = 210;
    const pad = { l: 42, r: 22, t: 22, b: 32 };
    const innerW = w - pad.l - pad.r;
    const innerH = h - pad.t - pad.b;
    const nums = series.flatMap((s) => s.values.filter((v) => v != null));
    const min = opts.yMin != null ? opts.yMin : 0;
    const max = opts.yMax != null ? opts.yMax : Math.max(...nums, opts.target || 0) * 1.08;
    const n = series[0].values.length;
    const x = (i) => pad.l + (n === 1 ? innerW / 2 : (i * innerW) / (n - 1));
    const y = (v) => pad.t + innerH - ((v - min) / (max - min)) * innerH;

    function segs(values) {
      const out = [];
      let cur = [];
      values.forEach((v, i) => {
        if (v == null) {
          if (cur.length) {
            out.push(cur);
            cur = [];
          }
        } else cur.push({ v, i });
      });
      if (cur.length) out.push(cur);
      return out;
    }

    let target = "";
    if (opts.target != null) {
      const ty = y(opts.target);
      target = `<line x1="${pad.l}" x2="${w - pad.r}" y1="${ty}" y2="${ty}" stroke="#1f7a45" stroke-dasharray="4 4" stroke-width="1.2"/>
        <text x="${w - pad.r}" y="${ty - 5}" text-anchor="end" fill="#1f7a45" font-size="11">${opts.targetLabel || ""}</text>`;
    }

    const axisLabels = opts.labels || labels;
    const dates = axisLabels
      .map((lb, i) => `<text x="${x(i)}" y="${h - 10}" text-anchor="middle" font-size="11" fill="#5a6a7e">${lb}</text>`)
      .join("");

    let body = "";
    series.forEach((s) => {
      const color = s.color;
      const dash = s.dash ? ` stroke-dasharray="${s.dash}"` : "";
      const sw = s.dash ? "2" : "2.4";
      segs(s.values).forEach((seg) => {
        const pts = seg.map((p) => `${x(p.i).toFixed(1)},${y(p.v).toFixed(1)}`).join(" ");
        if (!s.dash && seg.length > 1) {
          const area = `${x(seg[0].i).toFixed(1)},${y(min).toFixed(1)} ${pts} ${x(seg[seg.length - 1].i).toFixed(1)},${y(min).toFixed(1)}`;
          body += `<polygon points="${area}" fill="${color}" opacity="0.12"/>`;
        }
        if (seg.length > 1) {
          body += `<polyline points="${pts}" fill="none" stroke="${color}" stroke-width="${sw}" stroke-linejoin="round"${dash}/>`;
        }
      });
      s.values.forEach((v, i) => {
        if (v == null) return;
        const r = s.dash ? 5 : i === n - 1 ? 5 : 3.5;
        const ty = s.lblDy != null ? y(v) + s.lblDy : y(v) - 10;
        const tx = s.lblDx != null ? x(i) + s.lblDx : x(i);
        const anchor = s.lblDx ? "start" : "middle";
        body += `<circle cx="${x(i)}" cy="${y(v)}" r="${r}" fill="${s.dash ? "#fff" : color}" stroke="${color}" stroke-width="${s.dash ? 2 : 0}"/>
          <text x="${tx}" y="${ty}" text-anchor="${anchor}" font-size="11" fill="#1a2332" font-weight="700">${v}${opts.suffix || ""}</text>`;
      });
    });

    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    svg.innerHTML = `
      <rect x="0" y="0" width="${w}" height="${h}" fill="transparent"/>
      <polyline fill="none" stroke="#e2e8f0" points="${pad.l},${y(min)} ${w - pad.r},${y(min)}"/>
      ${target}
      ${body}
      ${dates}
    `;
  }

  const perfSvg = document.getElementById("chart-perf");
  const lcpSvg = document.getElementById("chart-lcp");
  if (perfSvg) {
    lineChart(
      perfSvg,
      [
        { values: perfM, color: "#2a5f8f" },
        { values: perfD, color: "#0c6e6b", dash: "6 4", lblDx: 8, lblDy: 4 },
      ],
      { yMax: 100, target: 85, targetLabel: "цель ≥85" }
    );
  }
  if (lcpSvg) {
    lineChart(
      lcpSvg,
      [
        { values: lcpM, color: "#c43c3c" },
        { values: lcpD, color: "#0c6e6b", dash: "6 4", lblDx: 8, lblDy: 4 },
      ],
      { target: 2.5, targetLabel: "цель ≤2.5 с" }
    );
  }
  const tbtSvg = document.getElementById("chart-tbt");
  if (tbtSvg) {
    lineChart(
      tbtSvg,
      [
        { values: tbtM, color: "#b8791d" },
        { values: tbtD, color: "#0c6e6b", dash: "6 4", lblDx: 8, lblDy: 4 },
      ],
      { target: 200, targetLabel: "цель ≤200" }
    );
  }
  const fcpSvg = document.getElementById("chart-fcp");
  if (fcpSvg) {
    lineChart(
      fcpSvg,
      [
        { values: fcpM, color: "#5b4db0" },
        { values: fcpD, color: "#0c6e6b", dash: "6 4", lblDx: 8, lblDy: 4 },
      ],
      { target: 1.8, targetLabel: "цель ≤1.8 с" }
    );
  }
  const siSvg = document.getElementById("chart-si");
  if (siSvg && D.siPageSpeed) {
    lineChart(siSvg, [{ values: D.siPageSpeed.values, color: "#0c6e6b" }], {
      labels: D.siPageSpeed.labels,
      target: D.siPageSpeed.target,
      targetLabel: "норма ≤3.4 с",
    });
  }

  function barGoals(svg, rows) {
    const w = 640;
    const rowH = 42;
    const h = 16 + rows.length * rowH;
    const pad = { l: 148, r: 56, t: 8, b: 8 };
    const innerW = w - pad.l - pad.r;
    const maxV = Math.max(...rows.map((r) => Math.max(r.now, r.target))) * 1.12;
    const x = (v) => pad.l + (v / maxV) * innerW;
    let body = "";
    rows.forEach((r, i) => {
      const y0 = pad.t + i * rowH;
      const nowW = Math.max(2, x(r.now) - pad.l);
      const tx = x(r.target);
      const unit = r.unit || "";
      body += `<text x="8" y="${y0 + 18}" font-size="12" fill="#5a6a7e">${r.title}</text>
        <rect x="${pad.l}" y="${y0 + 6}" width="${nowW}" height="16" rx="4" fill="#2a5f8f"/>
        <text x="${pad.l + nowW + 6}" y="${y0 + 18}" font-size="12" font-weight="700" fill="#1a2332">${r.now}${unit}</text>
        <line x1="${tx}" x2="${tx}" y1="${y0}" y2="${y0 + 28}" stroke="#1f7a45" stroke-width="2" stroke-dasharray="3 3"/>
        <text x="${tx + 4}" y="${y0 + 12}" font-size="10" fill="#1f7a45">${r.target}${unit}</text>`;
    });
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    svg.innerHTML = body;
  }
  const goalSvg = document.getElementById("chart-goals");
  if (goalSvg && D.goalBars) barGoals(goalSvg, D.goalBars);

  const vis = document.querySelector("[data-visibility-row]");
  if (vis && D.visibility) {
    vis.innerHTML = D.visibility
      .map((k) => {
        const unit = k.unit ? ` <small>${k.unit}</small>` : "";
        return `<article class="kpi ${k.tone || ""}">
          <span class="contour">${k.contour}</span>
          <h3>${k.title}</h3>
          <div class="val">${k.value}${unit}</div>
          <div class="delta">${k.delta || ""}</div>
          <div class="tgt">${k.target || ""}</div>
        </article>`;
      })
      .join("");
  }
  const visNote = document.querySelector("[data-vis-note]");
  if (visNote && D.visNote) visNote.textContent = D.visNote;
  const extra = document.querySelector("[data-extra-body]");
  if (extra && D.extra) {
    extra.innerHTML = D.extra
      .map((r) => {
        const [contour, title, value] = r;
        return `<article class="kpi">
          <span class="contour">${contour}</span>
          <h3>${title}</h3>
          <div class="val">${value}</div>
        </article>`;
      })
      .join("");
  }
  const tbody = document.querySelector("[data-raw-body]");
  if (tbody) {
    tbody.innerHTML = D.rows
      .map((r) => `<tr>${r.map((c) => `<td>${c === "" ? "—" : c}</td>`).join("")}<td>${D.url}</td></tr>`)
      .join("");
  }

  const track = document.querySelector(".track");
  const tabs = [...document.querySelectorAll("[data-sheet]")];
  const dots = [...document.querySelectorAll(".dots i")];
  let i = 0;

  function go(n) {
    i = n < 0 ? 1 : n > 1 ? 0 : n;
    track.dataset.i = String(i);
    tabs.forEach((t, idx) => t.setAttribute("aria-selected", idx === i ? "true" : "false"));
    dots.forEach((d, idx) => d.classList.toggle("on", idx === i));
    const live = document.getElementById("sheet-live");
    if (live) live.textContent = i === 0 ? "Лист 1 · KPI и тренд" : "Лист 2 · сырая таблица";
  }

  tabs.forEach((t) => t.addEventListener("click", () => go(Number(t.dataset.sheet))));
  document.querySelector("[data-prev]")?.addEventListener("click", () => go(i - 1));
  document.querySelector("[data-next]")?.addEventListener("click", () => go(i + 1));
  document.addEventListener("keydown", (e) => {
    if (e.key === "ArrowRight") go(i + 1);
    if (e.key === "ArrowLeft") go(i - 1);
  });

  let startX = 0;
  track?.addEventListener("pointerdown", (e) => {
    startX = e.clientX;
  });
  track?.addEventListener("pointerup", (e) => {
    const dx = e.clientX - startX;
    if (dx < -40) go(i + 1);
    if (dx > 40) go(i - 1);
  });

  go(0);
})();
