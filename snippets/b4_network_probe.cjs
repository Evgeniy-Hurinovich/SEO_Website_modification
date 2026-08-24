/* Cold-load Network probe for B4 acceptance (puppeteer-core + system Chrome). */
const puppeteer = require("puppeteer-core");
const CHROME = process.env.CHROME || "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";

const TARGETS = /metrika\/tag\.js|mc\.yandex|loader_29|n8n_bot|gtag\/js|googletagmanager|google-analytics/i;

function classify(url) {
  if (/metrika\/tag\.js|mc\.yandex/i.test(url)) return "metrika";
  if (/loader_29|bitrix24\.by\/.*crm\/form/i.test(url)) return "b24form";
  if (/n8n_bot/i.test(url)) return "n8n";
  if (/gtag\/js|googletagmanager|google-analytics/i.test(url)) return "gtag";
  return "other";
}

(async () => {
  const browser = await puppeteer.launch({
    executablePath: CHROME,
    headless: true,
    args: ["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 390, height: 844, isMobile: true, hasTouch: true });
  const hits = [];
  const t0 = Date.now();
  page.on("request", (req) => {
    const url = req.url();
    if (TARGETS.test(url)) {
      hits.push({ ms: Date.now() - t0, type: classify(url), url: url.slice(0, 180) });
    }
  });
  await page.goto("https://a2c.by/", { waitUntil: "domcontentloaded", timeout: 60000 });
  const afterDom = Date.now() - t0;
  await new Promise((r) => setTimeout(r, 3000));
  const at3s = hits.map((h) => ({ ...h }));
  await new Promise((r) => setTimeout(r, 4500));
  const nav = await page.evaluate(() => {
    const t = performance.getEntriesByType("navigation")[0];
    const res = performance.getEntriesByType("resource")
      .filter((e) => /tag\.js|loader_29|n8n_bot|gtag|googletagmanager|mc\.yandex/i.test(e.name))
      .map((e) => ({ name: e.name.slice(0, 160), start: Math.round(e.startTime) }));
    return {
      loadEventEnd: t ? Math.round(t.loadEventEnd) : null,
      domContentLoaded: t ? Math.round(t.domContentLoadedEventEnd) : null,
      composite: document.documentElement.innerHTML.includes("start_frame_cache"),
      formBox: !!document.getElementById("bx24_form_inline_second"),
      formAttr: !!document.querySelector('[data-b24-form="inline/29/cjt1zt"]'),
      metrikaFlag: !!window._metrika_loaded,
      n8nFlag: !!window.n8nChatLoaded,
      canonical: !!document.querySelector('link[rel="canonical"]'),
      resources: res,
    };
  });
  console.log(JSON.stringify({ afterDom, hits, at3sCount: at3s.length, nav }, null, 2));
  await browser.close();
})().catch((e) => {
  console.error(String(e));
  process.exit(1);
});
