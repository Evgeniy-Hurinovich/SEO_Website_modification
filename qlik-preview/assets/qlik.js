(function () {
  const D = window.A2SEO;
  const weeks = D.weeks;
  const labels = weeks.map((w) => w.label);
  const perf = weeks.map((w) => w.mobile.perf);
  const lcp = weeks.map((w) => w.mobile.lcp);
  const tbt = weeks.map((w) => w.mobile.tbt);

  function lineChart(svg, values, opts) {
    const w = 640;
    const h = 210;
    const pad = { l: 42, r: 18, t: 16, b: 32 };
    const innerW = w - pad.l - pad.r;
    const innerH = h - pad.t - pad.b;
    const min = opts.yMin != null ? opts.yMin : 0;
    const max = opts.yMax != null ? opts.yMax : Math.max(...values, opts.target || 0) * 1.08;
    const x = (i) => pad.l + (values.length === 1 ? innerW / 2 : (i * innerW) / (values.length - 1));
    const y = (v) => pad.t + innerH - ((v - min) / (max - min)) * innerH;
    const pts = values.map((v, i) => `${x(i).toFixed(1)},${y(v).toFixed(1)}`).join(" ");
    const area = `${pad.l},${y(min).toFixed(1)} ${pts} ${x(values.length - 1).toFixed(1)},${y(min).toFixed(1)}`;
    const color = opts.color || "#0c6e6b";
    let target = "";
    if (opts.target != null) {
      const ty = y(opts.target);
      target = `<line x1="${pad.l}" x2="${w - pad.r}" y1="${ty}" y2="${ty}" stroke="#1f7a45" stroke-dasharray="4 4" stroke-width="1.2"/>
        <text x="${w - pad.r}" y="${ty - 5}" text-anchor="end" fill="#1f7a45" font-size="11">${opts.targetLabel || ""}</text>`;
    }
    const dots = values
      .map((v, i) => {
        const last = i === values.length - 1;
        return `<circle cx="${x(i)}" cy="${y(v)}" r="${last ? 5 : 3.5}" fill="${color}"/>
          <text x="${x(i)}" y="${y(v) - 10}" text-anchor="middle" font-size="11" fill="#1a2332" font-weight="700">${v}${opts.suffix || ""}</text>
          <text x="${x(i)}" y="${h - 10}" text-anchor="middle" font-size="11" fill="#5a6a7e">${labels[i]}</text>`;
      })
      .join("");
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    svg.innerHTML = `
      <rect x="0" y="0" width="${w}" height="${h}" fill="transparent"/>
      <polyline fill="none" stroke="#e2e8f0" points="${pad.l},${y(min)} ${w - pad.r},${y(min)}"/>
      <polygon points="${area}" fill="${color}" opacity="0.12"/>
      <polyline points="${pts}" fill="none" stroke="${color}" stroke-width="2.4" stroke-linejoin="round"/>
      ${target}
      ${dots}
    `;
  }

  const perfSvg = document.getElementById("chart-perf");
  const lcpSvg = document.getElementById("chart-lcp");
  if (perfSvg) {
    lineChart(perfSvg, perf, { yMax: 100, target: 85, targetLabel: "цель ≥85", color: "#2a5f8f" });
  }
  if (lcpSvg) {
    lineChart(lcpSvg, lcp, { target: 2.5, targetLabel: "цель ≤2.5 с", color: "#c43c3c", suffix: "" });
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
