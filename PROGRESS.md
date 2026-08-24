# A2 Consulting SEO — статус работ

**Сайт:** https://a2c.by/  
**Платформа:** 1С-Битрикс 25.750 · Aspro Allcorp3 (шаблон **`aspro-allcorp3`**, дефис)  
**Пауза / обновлено:** 24 августа 2026 — Network-приёмка B4 + контрольный lab LH 12.2.1  
**Отчёт (main):** цифры CWV — тренд 27.07 → 11.08 → 20.08 → **24.08 после B4** (Lighthouse 12.2.1)

---

## Сегодня (10.08.2026) — сделано

1. **Отчёт руководству** — вкладка `#exec-report` в стиле canvas (chips, метрики, таблицы A–C, карточки итога).  
2. **C5** — в плане видимости примечание: отложено (CLS 0.001; width/height после B3).  
3. **D1** ✅ Organization + WebSite JSON-LD  
   - Файл: `/bitrix/templates/aspro-allcorp3/page_blocks/footer_1.php`  
   - Вставка: после `</footer>` (не через footer_custom — в Aspro пункта custom не было)  
   - Запасная копия: `footer_custom.php` (сайт её не читает)  
   - Черновик в репо: `snippets/d1-org-website.jsonld.html`  
4. **D2** ✅ Service JSON-LD на услугах  
   - Логика: `/include/service_jsonld.php`  
   - Подключение (в конце, в `<?php ... ?>`):  
     - `.../components/bitrix/news/services/section.php`  
     - `.../components/bitrix/news/services/detail.php`  
   - Черновик: `snippets/d2-service.jsonld.php`  
   - Проверено: P1 + вложенные; главная/контакты — только D1  
5. **D3** ✅ Review JSON-LD на `/company/reviews/`  
   - Логика: `/include/reviews_jsonld.php`  
   - Подключение: `.../news.list/review-list-inner/template.php` (перед `endif` ITEMS)  
   - Черновик: `snippets/d3-reviews.jsonld.php`  
   - Проверено 11.08: 16 Review + AggregateRating 5/5; не утекает на главную/услуги  

**Важно при правках PHP в админке:** выключить автоперевод браузера; править «как PHP», не визуальным редактором.

---

## Фаза A — Индексация и обход ✅

| Пункт | Статус | Результат |
|-------|--------|-----------|
| **A1** robots.txt | ✅ | Публично заполнен; `Sitemap: https://a2c.by/sitemap.xml` |
| **A2** sitemap.xml | ✅ | 200, sitemapindex, 8 дочерних карт |
| **A3** GSC + Вебмастер | ✅ | GSC: sitemap «Успешно». Яндекс: в очереди (маркетинг) |
| **A4** canonical | ⏳ P0 | Live HTML 11.08 и 20.08 — нет rel=canonical (есть og:url). IB «готово» ≠ прод |

---

## Фаза B — Скорость

| Пункт | Статус | Примечание |
|-------|--------|------------|
| **B1** АвтоКомпозит | ✅ | Включён |
| **B2** JS в конец + сжатые CSS/JS | ✅ | Включено в main |
| **B3** Hero → WebP ≤120 KB | ✅ | 11.08.2026: 4 слайда IB 23 → WebP (105/100/57/43 KB); H1 на месте |
| **B4.1** Старый счётчик Метрики | ✅ | Живой `108757686` |
| **B4.2–B4.3** Отложить Метрику + CRM | ✅ | Код 21.08. **Network-приёмка 24.08:** `tag.js` и `loader_29` не в первые 3 с (load+3 / load+5). Форма открывается. F3 кабинет не переснимали |
| **B4.4** n8n чат | ✅ | Код 21.08, origin `a28c633`. **Приёмка 24.08:** `n8n_bot` не в первые 3 с (load+3) |
| **B5.1–B5.2** Perfmon + таблицы БД | ✅ | Конфиг ≈ 7.25; таблицы «оптимально» |
| **B5.3** OPcache | ✅ | Включён (`enable=1`, 128 MB). Лимит `max_accelerated_files=10000` хостер **не меняет** (вирт. хостинг, 24.08) — закрыто как ограничение тарифа |
| **B5.4** MySQL READ-COMMITTED | ⏳ | Глобально нельзя → разработчик (`SET SESSION`) |
| **B5.5** Redis | ⏳ | PHP-модули есть; нужен host:port + переключение кеша Битрикс |
| **B5.6** Повторный Perfmon | ⏳ | После Redis / SESSION isolation (лимит OPcache-файлов не поднимем) |

### Network-приёмка B4 (24.08)

Cold load `/`, без скролла (puppeteer-core + Chrome, `snippets/b4_network_probe.cjs`):

- **0–3 с от navigation start:** нет `tag.js`, нет `loader_29`, нет `n8n`.
- **gtag** `G-SC3E8P9T2E` ~4.5 с (не B4).
- **Метрика** `tag.js?id=108757686` ~8.8 с ≈ `loadEventEnd` + 3 с.
- **n8n** CSS/JS ~8.8 с; **loader_29.js** ~10.8 с ≈ load+5 с.
- Композит: `start_frame_cache` есть. Canonical: нет.
- Форма «Получить консультацию»: поля Имя / Телефон / Компания / Отправить, `window.b24form === true`. Лид не отправляли. Хит Метрики `B24_FORM_29_VIEW`. Кабинет F3 не переснимали. `invis-counter.php` не трогали.

---

## Фаза C — On-page

| Пункт | Статус | Примечание |
|-------|--------|------------|
| **C1–C4** | ✅ | H1, title/desc P1, контакты |
| **C5** width/height | ✅ | 11.08.2026: `custom.css` — aspect-ratio logo/brands/hero (desktop). Проверено live |

---

## Фаза D — Schema

| Пункт | Статус | Примечание |
|-------|--------|------------|
| **D1** Organization + WebSite | ✅ | `footer_1.php` |
| **D2** Service | ✅ | `/include/service_jsonld.php` |
| **D3** Review на `/company/reviews/` | ✅ | `/include/reviews_jsonld.php` + `review-list-inner/template.php`; 16 Review + AggregateRating, 11.08.2026 |

---

## Фаза E — Контент

| Пункт | Статус | Примечание |
|-------|--------|------------|
| **E1** DWH посадочная | ✅ | Описание раздела обновлено 11.08.2026 (FAQ/H2/H3/CTA); UF_TOP_SEO опционально позже |
| **E2** BI посадочная | ✅ | Описание раздела обновлено 11.08.2026 (FAQ/H2/H3/CTA) |
| **E3** AI/RPA/ML посадочная | ✅ | Описание раздела обновлено 11.08.2026 (FAQ/H2/H3/CTA) |
| **E4** Перелинковка кейсы ↔ услуги | ✅ | 3 услуги + 9 проектов, проверено 11.08.2026 |
| **E5** Демо-каталог | ✅ | robots + noindex в index.php, sitemap без /product/ и /landings/, IB 21 (48 шт.) деактивированы |

---

## Фаза F — Замер видимости

| Пункт | Статус | Примечание |
|-------|--------|------------|
| **F1** Доступы GSC + Вебмастер | ✅ | 11.08.2026: GSC владелец + sitemap «Успешно»; Яндекс sitemap OK (все дочерние) |
| **F2** Еженедельный дашборд | ⏳ | Два контура: сборщик `seo_weekly_monitor.py` + `metrics/history.jsonl`; витрина = **Qlik** (`snippets/f2-qlik-seo-dashboard-plan.md`). Webhook в чат B24 — отдельный трек. Блокер Qlik: папка данных + ОК Миши |
| **F3** Цели Метрики (organic) | ✅ | 11.08.2026: цели «Заказать звонок», «Клик по телефону», «Контакты»; сегмент «Поисковый трафик»; тест callback — 1 целевой визит |

---

## Замеры скорости — тренд

Источник: **Lighthouse 12.2.1** lab (локально). PSI API — 429 в моменты замеров.

### Mobile `/`

| Дата | Perf | LCP | FCP | TTI | TBT | CLS | SEO LH |
|------|------|-----|-----|-----|-----|-----|--------|
| **27.07** (старт) | **47** | **6.4 с** | 3.9 с | 9.3 с | 900 мс | 0.001 | — |
| **11.08** (после B1–B3) | **58** | **4.7 с** | 2.3 с | 10.2 с | 940 мс | 0 | — |
| **20.08** (повтор) | **62** | **5.7 с** | 2.3 с | 7.6 с | **550 мс** | 0 | **100** |
| **24.08** (после B4) | **79** | **3.7 с** | 2.4 с | 7.1 с | **330 мс** | 0.004 | **100** |

| Метрика | 27.07→11.08 | 11.08→20.08 | 20.08→24.08 | Итог |
|---------|-------------|-------------|-------------|------|
| Perf | +11 | +4 | **+17** | **47→79** ↑ |
| LCP | −1.7 с | +1.0 с (шум lab) | **−2.0 с** | **6.4→3.7** ↑ |
| TBT | ≈0 | −390 мс | **−220 мс** | **900→330** ↑ |
| TTI | хуже | −2.6 с | −0.5 с | **9.3→7.1** · этап ≤6 с не закрыт |

### Desktop `/` (20.08, не переснимали 24.08)

| Perf | LCP | FCP | TBT | CLS | SEO |
|------|-----|-----|-----|-----|-----|
| **97** | **1.1 с** | 0.5 с | 70 мс | 0.015 | **100** |

### Прочее

| URL | Дата | Perf | LCP | TBT |
|-----|------|------|-----|-----|
| `/services/dwh/` | 11.08 | 58 | 7.5 с | 660 мс |
| `/services/dwh/` | **24.08** | **63** | **7.2 с** | **410 мс** |

**Чтение тренда:** цель этапа на главной **закрыта** (Perf ≥70–75, LCP ≤3.5–4.0 с, TBT ≤350–400 мс). **Не закрыты:** TTI ≤6 с (7.1), норма «верх» (≥85 / ≤2.5 / ≤200), DWH LCP 7.2 с. Desktop 97 — держать. Live: **нет rel=canonical**. Gtag `G-SC3E8P9T2E` грузится сразу (не B4).

Отчёт обновлён 24.08: `index.html`, `anna-audit-report/index.html`. B4.4 в origin (`a28c633`). Lab JSON: `metrics/_lh_home_mobile_20260824.json`, `metrics/_lh_dwh_mobile_20260824.json` (gitignored).

---

## Целевые KPI этапа

| Метрика | Сейчас (lab 24.08) | Цель этапа | Норма «верх» |
|---------|--------------------|------------|--------------|
| Mobile Perf | **79** | ≥70–75 ✅ | ≥85 |
| Mobile LCP | **3.7 с** | ≤3.5–4.0 с ✅ | ≤2.5 с |
| Mobile TBT | **330 мс** | ≤350–400 мс ✅ | ≤200 мс |
| Mobile TTI | **7.1 с** | ≤6 с ✗ | ≤3.8 с |
| Mobile CLS / SEO LH | 0.004 / 100 | держать | ≤0.1 / 100 |
| Desktop Perf / LCP / TBT | 97 / 1.1 с / 70 мс (20.08) | держать ≥90 | ≥90 / ≤2.5 с / ≤200 мс |
| DWH mobile Perf / LCP | 63 / 7.2 с | дожим | ≤2.5 с LCP |
| rel=canonical | нет в HTML | на всех публичных URL | 100% |
| Позиции / GSC | ~9–10 | weekly тренд кликов | лаг 2–8 нед. |

Lab ≠ field ≠ GSC.

---

## Дальше (сейчас)

1. Разработчик: **A4 canonical** (P0) — ТЗ: `snippets/dev-control-tz-mobile-seo.md`.  
2. Разработчик: **B5.4** `SET SESSION transaction_isolation='READ-COMMITTED'`.  
3. Хостер: Redis host:port → кеш Битрикс (**B5.5**); затем **B5.6** Perfmon. Files-лимит не трогаем.  
4. Дожим: TTI ≤6 с (gtag `G-SC3E8P9T2E` сразу); отдельно LCP `/services/dwh/`.  
5. **F2**: сборщик уже есть; витрина Qlik — не чат B24.  
6. Анна: при желании подтвердить цели F3 в кабинете Метрики (форму 24.08 открывали, лид не слали).

**Правило:** живой a2c.by не менять без явного «можно» / подтверждения шага.

**Правило:** живой a2c.by не менять без явного «можно» / подтверждения шага.

---

## Отчёт / репозиторий

- Вкладки: `#visibility-plan`, `#exec-report`, `#seo-eval` (SEO-оценка)  
- `index.html` + `anna-audit-report/index.html`  
- Snippets: `snippets/d1-org-website.jsonld.html`, `snippets/d2-service.jsonld.php`  
- Локальные `_*.py` / dumps — не в git  
- Кеш после правок шаблона: https://a2c.by/bitrix/admin/cache.php?lang=ru  

### Полезные пути

- Шаблон: `/bitrix/templates/aspro-allcorp3/`  
- Footer: `page_blocks/footer_1.php`  
- Услуги: `components/bitrix/news/services/` (`section.php`, `detail.php`)  
- Service include: `/include/service_jsonld.php`  
