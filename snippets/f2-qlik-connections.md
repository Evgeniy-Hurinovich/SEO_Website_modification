# SEO weekly — подключения и слоты

Для разработчика Qlik. Макет: https://seo-website-modification-3m77.vercel.app/qlik-preview/qlik  
ТЗ ETL: [f2-qlik-native-etl.md](./f2-qlik-native-etl.md) · load script: [qlik/seo_weekly.qvs](./qlik/seo_weekly.qvs)

**Факт макета:** lab считался Lighthouse CLI 12.2.1 по URL сайта. Видимость 10–16.08 — ручной съём из кабинетов (лист «SEO динамика»), **не** Search Console API и не Метрика API. Ниже — куда ходить, чтобы те же плитки заполнять из Qlik.

URL правды: `https://a2c.by/`  
Не клеить PSI и LH 12.2.1 в один `contour=lab`.

---

## Слоты (плитка есть, значения нет)

В макете и в сырой таблице пустое `value` = слот. Не выдумывать число. В Qlik: `—`, контур и metric оставить.

| Плитка / metric | Контур | Почему пусто | Чем закрыть |
|-----------------|--------|--------------|-------------|
| Клики organic / нед. · `clicks_week` | `gsc` | кабинет GSC в поток не подключали | Search Analytics API, полная прошлая неделя, `dataState=final` |
| Ошибки / исключения Вебмастер | `webmaster` | в кабинете не нашли одно число | Webmaster API diagnostics/summary; если поля нет — слот остаётся |
| CrUX LCP · `crux_lcp` | `field` | field 2–4 нед., в weekly lab не входил | PSI `loadingExperience` или CrUX API |
| Desktop lab 24.08 | `lab` | 24.08 снимали только mobile | повторный LH/PSI `strategy=desktop` |

Есть число в макете, но **нет в** [weekly_snapshot.csv](../metrics/weekly_snapshot.csv) (сид QVD сейчас только lab+live):

позиции Google/Яндекс, Метрика, GA, индекс GSC 271 / Вебмастер 165, ошибки GSC 1060, Speed Index, конверсии ~2. Их Qlik забирает коннекторами ниже, не из CSV.

---

## Адреса сайта (live probe, не API)

REST GET, User-Agent задать в коннекторе (`a2c-seo-qlik/1.0`).

| URL | Зачем |
|-----|--------|
| https://a2c.by/ | lab URL; `rel=canonical` в HTML |
| https://a2c.by/services/dwh/ | canonical P1 |
| https://a2c.by/services/bi/ | canonical P1 |
| https://a2c.by/contacts/ | canonical P1 |
| https://a2c.by/robots.txt | есть `Sitemap:` → `robots_ok` |
| https://a2c.by/sitemap.xml | HTTP 200 и `<urlset` / `<sitemapindex` → `sitemap_ok` |

metric: `canonical_ok` / `robots_ok` / `sitemap_ok`, contour `live`, value `0` или `1`.

---

## Коннекторы Qlik

Секреты только в Data Connection. Не в git.

### 1. Lab скорость — два взаимоисключающих варианта

**A. PageSpeed Insights API** (всё внутри Qlik) → contour **`psi`**

```
GET https://www.googleapis.com/pagespeedonline/v5/runPagespeed
  ?url=https%3A%2F%2Fa2c.by%2F
  &strategy=mobile
  &category=performance
  &category=seo
  &key=***
```

То же с `strategy=desktop`. Таймаут коннектора ≥ 120 с.

JSON:

| metric | путь |
|--------|------|
| `perf` | `lighthouseResult.categories.performance.score` × 100 |
| `lcp_ms` | `lighthouseResult.audits.largest-contentful-paint.numericValue` |
| `tbt_ms` | `lighthouseResult.audits.total-blocking-time.numericValue` |
| `fcp_ms` | `lighthouseResult.audits.first-contentful-paint.numericValue` |
| `cls` | `lighthouseResult.audits.cumulative-layout-shift.numericValue` |
| `speed_index_s` | `lighthouseResult.audits.speed-index.numericValue` / 1000 |
| `crux_lcp` (field) | `loadingExperience.metrics.LARGEST_CONTENTFUL_PAINT_MS.percentile` |
| `source` | `psi-v5/` + `lighthouseResult.lighthouseVersion` |

Доки: https://developers.google.com/speed/docs/insights/v5/get-started  
UI контроля: https://pagespeed.web.dev/analysis?url=https%3A%2F%2Fa2c.by%2F&form_factor=mobile

Ряд макета 27.07–24.08 (47→79) — **не PSI**, это LH 12.2.1. На графике фильтр `contour=lab` для архива, новые точки — `psi`.

**B. Lighthouse JSON 12.2.1** (шара, не report-сервер) → contour **`lab`**

`npx lighthouse@12.2.1 https://a2c.by/ --output=json` → `lib://SEO/lh/YYYY-MM-DD_mobile.json`.  
`EXECUTE` на Qlik-сервере не использовать.

### 2. Google Search Console

Кабинет: https://search.google.com/search-console  
Свойство: URL-prefix `https://a2c.by/` или `sc-domain:a2c.by` (уточнить у Ани).

**Клики, показы, CTR, средняя позиция** (`clicks_week`, `avg_position` — в макете 10,1 за 10–16.08):

```
POST https://www.googleapis.com/webmasters/v3/sites/https%3A%2F%2Fa2c.by%2F/searchAnalytics/query
Authorization: Bearer {token}
{
  "startDate": "<пн прошлой недели>",
  "endDate": "<вс прошлой недели>",
  "dimensions": [],
  "dataState": "final"
}
```

Доки: https://developers.google.com/webmaster-tools/v1/searchanalytics/query

**Индекс 271 и ошибки/исключения 1060** — не Search Analytics. Page indexing / Coverage, отдельный коннектор или слот, пока нет доступа.

### 3. Яндекс Метрика

Кабинет: https://metrika.yandex.ru/  
Счётчик на сайте (сверить с Аней перед боем): **108757686**  
Сегмент: поисковый трафик. Цели F3 — id от Ани.

```
GET https://api-metrika.yandex.net/stat/v1/data
  ?ids={COUNTER}
  &date1=<пн>&date2=<вс>
  &metrics=ym:s:visits,ym:s:users,ym:s:pageviews,ym:s:bounceRate,ym:s:avgVisitDurationSeconds,ym:s:pageDepth,ym:s:goalReaches<GOAL_ID>
  &filters=ym:s:trafficSourceName=='Переходы из поисковых систем'
Authorization: OAuth {token}
```

| Макет | metric |
|-------|--------|
| Просмотры 417 | `views` |
| Посетители 157 | `visitors` |
| Отказы 22,29% / моб. 26,92% | `bounce_pct` (+ `device=mobile`) |
| Время 3 мин 39 с | `time_on_site_s` = 219 |
| Глубина 2,66 | `depth` |
| Конверсии ~2 / мес | `organic_conv_month` (цели F3) |

Доки: https://yandex.ru/dev/metrika/doc/api2/api_v1/intro.html

### 4. Яндекс Вебмастер

Кабинет: https://webmaster.yandex.ru/

```
GET https://api.webmaster.yandex.net/v4/user/{user-id}/hosts/{host-id}/summary
Authorization: OAuth {token}
```

| Макет | metric |
|-------|--------|
| Страниц в индексе 165 | `indexed_pages` |
| Ошибки / исключения | слот, пока API не отдаст одно число |
| Средняя позиция Яндекс 7,5 | уточнить кабинет у Ани; в Search Analytics Яндекса нет 1-в-1 как у GSC |

Доки: https://yandex.ru/dev/webmaster/doc/dg/concepts/about.html

### 5. Google Analytics 4

Кабинет: https://analytics.google.com/  
На сайте gtag: **G-SC3E8P9T2E** (property id — у Ани).

```
POST https://analyticsdata.googleapis.com/v1beta/properties/{PROPERTY_ID}:runReport
```

Макет 10–16.08: посетители 142, отказы 38,10%, отказы моб. 46,51%.

Доки: https://developers.google.com/analytics/devguides/reporting/data/v1

### 6. CrUX (field), если закрывать слот `crux_lcp`

```
POST https://chromeuxreport.googleapis.com/v1/records:queryRecord
{ "origin": "https://a2c.by", "formFactor": "PHONE" }
```

Либо поле `loadingExperience` в ответе PSI. Не мешать с lab LCP на одной оси.

Доки: https://developer.chrome.com/docs/crux/api

---

## Кабинеты, откуда сняли макет (не Data Connection)

Лист «SEO динамика» (неделя 10–16.08 и цели года):  
https://docs.google.com/spreadsheets/d/1q4J5n2Ujr6pvQ-8FIK9BFzZqlQcBgjtAaZGMJcj7psA/edit?gid=1343572353  

Не использовать таблицу как боевой источник Qlik. Только сверка. GitHub тоже не Data Connection.

---

## Сид, который уже можно залить

Длинная таблица lab+live (27.07–24.08):  
https://github.com/Evgeniy-Hurinovich/SEO_Website_modification/blob/main/metrics/weekly_snapshot.csv  
[raw](https://raw.githubusercontent.com/Evgeniy-Hurinovich/SEO_Website_modification/main/metrics/weekly_snapshot.csv)

Цифры видимости — в [qlik-preview/assets/data.js](../qlik-preview/assets/data.js) (`visibility`, `extra`, `rows` с датой `2026-08-16`).

---

## Исходящий HTTPS с движка reload (Миша)

- `www.googleapis.com` — PSI + GSC
- `searchconsole.googleapis.com` / `www.googleapis.com/webmasters` — GSC
- `analyticsdata.googleapis.com` — GA4
- `chromeuxreport.googleapis.com` — CrUX
- `api-metrika.yandex.net` — Метрика
- `api.webmaster.yandex.net` — Вебмастер
- `a2c.by` — HTML / robots / sitemap

Нет исходящего интернета → только Folder JSON (вариант B) + сид CSV. API не заведутся.
