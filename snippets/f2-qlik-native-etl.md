# Qlik как ETL: SEO weekly без Python→CSV

Решение 26.08.2026 (Миша): приложение Qlik Sense **само** забирает источники (REST / JSON / HTML). Промежуточный Python→CSV больше не контур поставки.

Макет листов (спека UI, не источник данных):
https://seo-website-modification-3m77.vercel.app/qlik-preview/qlik

URL правды: `https://a2c.by/`  
Листы: KPI+тренд · сырая таблица  
Reload: пн 10:00  
История: QVD, не git.

---

## Что меняется

| Было | Стало |
|------|--------|
| Python мерит сайт → CSV → Folder Connection → Qlik рисует | Qlik load script = ETL + витрина |
| Git хранит код сборщика и снимок | Git хранит макет, ТЗ, `.qvs`. Боевые факты — в QVD на сервере |
| `QLIK_DROP_DIR` обязателен | Нужен только если выбран вариант lab «JSON-файл» (см. ниже) |

Python `scripts/seo_weekly_monitor.py` **не удаляем сразу**: он уже посчитал историю 27.07–24.08. Это сид в QVD (задача Q-0). Дальше его не ставим в Task Scheduler как поставщика для Qlik.

---

## Развилка lab (решить на шаге 1, иначе сломаем тренд)

Qlik **не запускает Chrome**. Lighthouse CLI 12.2.1 — это Node+браузер, 30–90 с, на финансовом report-сервере `EXECUTE` почти наверняка запрещён. Поэтому lab — один из двух вариантов:

### Вариант A — всё внутри Qlik (то, что предложил Миша)

REST: [PageSpeed Insights API v5](https://developers.google.com/speed/docs/insights/v5/get-started)  
`strategy=mobile|desktop`, `category=performance`.

Плюс: один движок, без файлов.  
Минус: это **лаборатория Google**, не наш Lighthouse 12.2.1. Уже было расхождение с замером Ани (TBT 30 vs наш 550 на 20.08). Ряд 27.07–24.08 **нельзя** клеить к PSI на одном графике.

Подпись карточки: **`psi`**, не `lab`. Историю LH оставить контуром `lab` (архив). Новый еженедельный ряд — `psi`.

### Вариант B — Qlik парсит JSON (рекомендация, если KPI остаётся LH 12.2.1)

Раз в неделю на **отдельной** машине (не Qlik-сервер):

```
npx --yes lighthouse@12.2.1 https://a2c.by/ --only-categories=performance,seo --form-factor=mobile --screenEmulation.mobile --output=json --output-path=\\qlik-share\seo\lh\YYYY-MM-DD_mobile.json
npx --yes lighthouse@12.2.1 https://a2c.by/ --only-categories=performance,seo --preset=desktop --output=json --output-path=\\qlik-share\seo\lh\YYYY-MM-DD_desktop.json
```

Qlik Folder Connection читает JSON, load script вынимает Perf/LCP/TBT. Это не «промежуточный CSV» — это сырой отчёт измерителя, как Миша и сказал: *можно распарсить файл json кликом*.

Каноникал / robots — REST GET HTML в том же скрипте Qlik (см. `.qvs`).

**Не делать:** гонять Lighthouse с самого Qlik-сервера через `EXECUTE`.

---

## Шаги реализации

### 0. Сид истории (Женя Г. + Федя, 0.5 дня)

Файл уже есть: `metrics/weekly_snapshot.csv` (длинная таблица).  
Один раз загрузить в `seo_fact.qvd`. Без этого понедельничный REST начнёт ряд с нуля и Ткачёнок потеряет 47→79.

Скрипт: `snippets/qlik/seo_weekly.qvs` секция `SEED`.

### 1. Допуски сервера (Миша / Ругарин, блокер)

Без ответа нельзя писать коннекторы:

1. Приложение SEO weekly на **этом** report-сервере — да/нет, стрим, кто видит.
2. Исходящий HTTPS с движка reload до:
   - `www.googleapis.com` (PSI + GSC)
   - `searchconsole.googleapis.com`
   - `api-metrika.yandex.net`
   - `api.webmaster.yandex.net`
   - `a2c.by` (HTML probe)
3. REST Connector / Web Connector — разрешён?
4. `EXECUTE` — нет (и не просим).
5. Папка под QVD + (если вариант B) под `lh\*.json`.
6. Кто владелец reload-задачи (сервисная УЗ, не личный логин).

Если исходящего интернета **нет** — вариант A мёртв. Остаётся B + ручной/API-шлюз во внутренней сети, либо REST через согласованный прокси.

### 2. Учётные записи API (Аня + Федя, 1–2 дня после шага 1)

| Источник | Что завести | Куда в Qlik |
|----------|-------------|-------------|
| PSI | Google Cloud API key, квота Pagespeed | REST `psi_mobile` / `psi_desktop` |
| GSC | Service account, свойство `sc-domain:a2c.by` или префикс URL | REST POST searchAnalytics + site inspect |
| Метрика | OAuth токен приложения, счётчик a2c.by, сегмент «Поисковый трафик», цели F3 | REST `stat/v1/data` |
| Вебмастер | OAuth, host-id a2c.by | REST summary / indexing-history |
| GA4 | только если нужен дубль отказов; иначе не в MVP | Data API |

Секреты — Data Connection / REST headers на сервере. Не в git, не в чат.

### 3. Модель данных (Федя)

Одна факт-таблица, та же схема, что была у CSV (Qlik сам развернёт широкую витрину):

| поле | смысл |
|------|--------|
| date | ISO недели / дня замера |
| contour | `lab` / `psi` / `gsc` / `webmaster` / `metrica` / `ga` / `live` / `field` |
| device | `mobile` / `desktop` / пусто |
| metric | `perf`, `lcp_ms`, `tbt_ms`, `clicks_week`, `avg_position`, … |
| value | число; пусто = слот |
| unit | `score` / `ms` / `s` / `count` / `rank` / `bool` / `pct` |
| source | `lighthouse-12.2.1` / `psi-v5` / `gsc-api` / `metrica-api` / `html-probe` / `seed-csv` |
| url | всегда `https://a2c.by/` для lab/psi |

Календарь: `WeekStart(date)` для ▲▼ к прошлой неделе.  
Не смешивать `lcp_ms` и `avg_position` на одной оси. Desktop — второе измерение, не замена mobile.

Накопление:

```
новый REST/JSON  →  CONCATENATE  seo_fact.qvd  →  STORE
```

Идемпотентность: ключ `date|contour|device|metric|url`. Перед concatenate — удалить ключи текущей даты (повторный reload в понедельник не двоит строки).

### 4. Load script (Федя)

Готовый каркас: `snippets/qlik/seo_weekly.qvs`.

Порядок в Data Load Editor:

1. SEED — только если QVD ещё нет  
2. EXTRACT — REST/JSON/HTML  
3. NORMALIZE — в длинную таблицу  
4. UPSERT → `STORE seo_fact INTO [lib://SEO/seo_fact.qvd] (qvd);`

Таймаут PSI: 60–120 с (Google сам гоняет Lighthouse). Reload-задача: не параллелить два PSI в одной секции без паузы — лимиты API.

### 5. Приложение (Федя, UI = макет)

Лист 1 как на макете:

- 5 KPI: Mobile Perf, LCP, TBT, клики GSC, конверсии organic  
- блок видимости: позиции, Метрика, индекс, слот Вебмастер  
- графики lab/psi mobile сплошная, desktop пунктир  
- факт vs цель года — отдельные бары, не ось LCP  

Лист 2: прямая таблица `seo_fact` (то, что было CSV).

Цвета: Perf/клики/цели — рост хорошо; LCP/TBT/отказы/позиция — рост плохо.

### 6. Расписание и приёмка

- Reload пн 10:00, владелец — сервисная УЗ.  
- Первый прогон: сид QVD + один живой PSI или один JSON LH.  
- Приёмка Ткачёнка: 5 карточек, ▲▼, подпись контура.  
- Не обещать живой GSC в тот же день: OAuth и верификация свойства обычно дольше, чем REST на PSI.

---

## Задачи (бэклог для разработчика)

### Миша / Ругарин

| ID | Задача | Готово, когда |
|----|--------|----------------|
| M-1 | ОК на приложение на report-сервере, стрим, список зрителей | есть место в хабе |
| M-2 | Исходящий HTTPS к Google / Яндекс / a2c.by | telnet/curl с движка reload или письменный «нет» |
| M-3 | REST Connector разрешён | коннектор создаётся без исключения политики |
| M-4 | Folder Connection: QVD; опционально `lh\` | путь `lib://SEO/` |
| M-5 | Сервисная УЗ + задача reload пн 10:00 | задача в QMC, не личный логин |

### Федя (Qlik)

| ID | Задача | Решение |
|----|--------|---------|
| Q-0 | Создать QVD из `metrics/weekly_snapshot.csv` | секция SEED в `.qvs` |
| Q-1 | Data connections: PSI, GSC, Метрика, Вебмастер, Web GET a2c.by | REST; ключи в коннекторе |
| Q-2 | Load script EXTRACT+NORMALIZE+UPSERT | `snippets/qlik/seo_weekly.qvs` |
| Q-3 | Лист 1 / лист 2 по макету | URL макета выше |
| Q-4 | Master items: KPI, Δ к предыдущей дате того же contour+metric+device | `Above()` / `set analysis` по `date` |
| Q-5 | Reload task + fail-mail на Федю/Женю Г. | QMC |
| Q-6 | Если M-2 = нет интернета | только Folder JSON (вариант B) + сид; API — через согласованный прокси |

### Аня (кабинеты)

| ID | Задача | Решение |
|----|--------|---------|
| A-1 | GSC: пустить service account на свойство a2c.by | IAM / пользователи свойства |
| A-2 | Метрика: токен, id счётчика, id целей F3, сегмент organic | отдать Феде в парольницу, не в git |
| A-3 | Вебмастер: host-id; найти «ошибки/исключения» (слот сейчас пустой) | если в API нет поля — плитка остаётся «—» |
| A-4 | Не подменять lab цифрами из UI PageSpeed | в приложение они не идут, кроме явного контура `psi` |

### Женя Г. (контракт KPI)

| ID | Задача | Решение |
|----|--------|---------|
| G-1 | Зафиксировать с Ткачёнком/Мишей: lab = LH 12.2.1 (вариант B) или psi-v5 (вариант A) | одна строка в шапке приложения |
| G-2 | Отдать CSV сид + макет | уже в git: `metrics/weekly_snapshot.csv`, `qlik-preview/` |
| G-3 | Если B: однострочный `.cmd`/Task Scheduler только `lighthouse --output json` на шару | без CSV, без Python |
| G-4 | Не смешивать ряды: `lab` 27.07–24.08 отдельно от нового `psi`, если выбран A | фильтр `contour` на графике |

### Разработчик сайта (не Qlik, но тот же KPI)

A4 canonical на P1 — иначе `live.canonical_ok` вечно 0. Это не задача Феди.

---

## Эндпоинты (вставить в REST Connector)

Подставить ключи только в Qlik. Ниже — контракт URL.

### PSI lab+field

```
GET https://www.googleapis.com/pagespeedonline/v5/runPagespeed
  ?url=https%3A%2F%2Fa2c.by%2F
  &strategy=mobile
  &category=performance
  &category=seo
  &key=***
```

JSON-пути:

- lab Perf: `lighthouseResult.categories.performance.score` × 100  
- lab LCP ms: `lighthouseResult.audits.largest-contentful-paint.numericValue`  
- lab TBT ms: `lighthouseResult.audits.total-blocking-time.numericValue`  
- lab FCP ms: `lighthouseResult.audits.first-contentful-paint.numericValue`  
- lab CLS: `lighthouseResult.audits.cumulative-layout-shift.numericValue`  
- field LCP: `loadingExperience.metrics.LARGEST_CONTENTFUL_PAINT_MS.percentile`  
- LH version Google: `lighthouseResult.lighthouseVersion` — писать в `source` как `psi-v5/{version}`

То же с `strategy=desktop`.

### GSC клики / позиция за прошлую полную неделю

```
POST https://www.googleapis.com/webmasters/v3/sites/https%3A%2F%2Fa2c.by%2F/searchAnalytics/query
Authorization: Bearer {token}
{
  "startDate": "2026-08-10",
  "endDate": "2026-08-16",
  "dimensions": [],
  "dataState": "final"
}
```

Ответ: `rows[0].clicks`, `impressions`, `ctr`, `position`.  
Индекс: `sites.list` / URL Inspection — во вторую очередь. Ошибки/исключения GSC (у нас факт 1060) — отчёт Coverage/Page indexing; в Search Analytics этого поля нет, нужна отдельная связь (Search Console API pageIndex или ручной слот, пока нет доступа).

### Метрика (неделя, organic)

```
GET https://api-metrika.yandex.net/stat/v1/data
  ?ids={COUNTER}
  &metrics=ym:s:visits,ym:s:users,ym:s:pageviews,ym:s:bounceRate,ym:s:avgVisitDurationSeconds,ym:s:pageDepth,ym:s:goalReaches<GOAL_ID>
  &filters=ym:s:trafficSourceName=='Переходы из поисковых систем'
  &date1=2026-08-10&date2=2026-08-16
```

Заголовок: `Authorization: OAuth {token}`.

### Вебмастер

```
GET https://api.webmaster.yandex.net/v4/user/{user-id}/hosts/{host-id}/summary
Authorization: OAuth {token}
```

Индексированные URL — `search-urls/in-search` или history. «Ошибки / исключения» — diagnostics; если метод не отдаёт одно число, плитка остаётся «—».

### Live probe (canonical / robots / sitemap)

REST GET `https://a2c.by/` (и 3 служебных URL) как текст. В Qlik:

- canonical: `Index(html, 'rel="canonical"')` или `rel='canonical'`  
- robots: GET `https://a2c.by/robots.txt` → есть `Sitemap:`  
- sitemap: GET `https://a2c.by/sitemap.xml` → HTTP 200 и `<urlset` / `<sitemapindex`

User-Agent задать в коннекторе (`a2c-seo-qlik/1.0`), иначе WAF.

### Lighthouse JSON (вариант B)

Файлы `lib://SEO/lh/*_mobile.json`:

- Perf: `categories.performance.score` × 100  
- LCP: `audits.largest-contentful-paint.numericValue`  
- TBT: `audits.total-blocking-time.numericValue`  
- version: `lighthouseVersion` — ждать `12.2.1`

---

## Что сознательно не делаем

- Python как обязательный слой до Qlik.  
- Личный GitHub как Data Connection.  
- `EXECUTE` Lighthouse на report-сервере.  
- Склейка PSI и LH 12.2.1 в один `contour=lab`.  
- LCP и позиции GSC на одной оси.  
- Desktop как «сайт быстрый» вместо mobile.  
- Реплика А2Групп в этом приложении.

---

## Первый ответ Феде в чат (можно копировать)

1. Макет: https://seo-website-modification-3m77.vercel.app/qlik-preview/qlik  
2. Сид: `metrics/weekly_snapshot.csv` → QVD один раз.  
3. Миша подтверждает исходящий HTTPS. Нет сети → только JSON на шаре.  
4. Load script: `snippets/qlik/seo_weekly.qvs`.  
5. Lab: либо PSI (`contour=psi`), либо JSON LH 12.2.1 (`contour=lab`). Не оба в одной линии.
