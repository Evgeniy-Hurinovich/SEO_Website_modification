# A2 Consulting SEO — статус работ

**Сайт:** https://a2c.by/  
**Платформа:** 1С-Битрикс 25.750 · Aspro Allcorp3 (шаблон **`aspro-allcorp3`**, дефис)  
**Пауза / обновлено:** 20 августа 2026 — повторный lab SEO+CWV (mobile/desktop); OPcache включён хостером  
**Отчёт (main):** цифры CWV — тренд 27.07 → 11.08 → 20.08 (Lighthouse 12.2.1)

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
| **A4** canonical | ✅ | IB 42/41/38 + новости |

---

## Фаза B — Скорость

| Пункт | Статус | Примечание |
|-------|--------|------------|
| **B1** АвтоКомпозит | ✅ | Включён |
| **B2** JS в конец + сжатые CSS/JS | ✅ | Включено в main |
| **B3** Hero → WebP ≤120 KB | ✅ | 11.08.2026: 4 слайда IB 23 → WebP (105/100/57/43 KB); H1 на месте |
| **B4.1** Старый счётчик Метрики | ✅ | Живой `108757686` |
| **B4.2–B4.3** Отложить Метрику + CRM | ✅ | Сделано 21.08.2026 (разработчик) |
| **B4.4** n8n чат | ✅ | Сделано 21.08.2026 (разработчик) |
| **B5.1–B5.2** Perfmon + таблицы БД | ✅ | Конфиг ≈ 7.25; таблицы «оптимально» |
| **B5.3** OPcache | ✅ | Включён (`enable=1`, 128 MB). Лимит `max_accelerated_files=10000` хостер **не меняет** (вирт. хостинг, 24.08) — закрыто как ограничение тарифа |
| **B5.4** MySQL READ-COMMITTED | ⏳ | Глобально нельзя → разработчик (`SET SESSION`) |
| **B5.5** Redis | ⏳ | PHP-модули есть; нужен host:port + переключение кеша Битрикс |
| **B5.6** Повторный Perfmon | ⏳ | После Redis / SESSION isolation (лимит OPcache-файлов не поднимем) |

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
| **F2** Еженедельный дашборд | ⏳ | Встреча: витрина = **Qlik**, не чат. Сборщик `seo_weekly_monitor.py` + `metrics/history.jsonl` остаётся. План: `snippets/f2-qlik-seo-dashboard-plan.md`. Блокер: папка данных + ОК Миши на report-сервер |
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

| Метрика | 27.07→11.08 | 11.08→20.08 | Итог за месяц |
|---------|-------------|-------------|----------------|
| Perf | +11 | +4 | **47→62** ↑ |
| LCP | −1.7 с | +1.0 с (шум lab) | всё ещё ≫ 2.5 с |
| TBT | ≈0 | −390 мс | **900→550** ↑ лучше |
| TTI | хуже | −2.6 с | **9.3→7.6** ↑ |

### Desktop `/` (20.08, впервые)

| Perf | LCP | FCP | TBT | CLS | SEO |
|------|-----|-----|-----|-----|-----|
| **97** | **1.1 с** | 0.5 с | 70 мс | 0.015 | **100** |

### Прочее

| URL | Дата | Perf | LCP | TBT |
|-----|------|------|-----|-----|
| `/services/dwh/` | 11.08 | 58 | 7.5 с | 660 мс |

**Чтение тренда:** среднесрочно рост после B1–B3; за неделю lab шумит по LCP, но Perf/TBT/TTI лучше. До цели (Perf ≥85, LCP ≤2.5 с) нужен **B4**. Live: **нет rel=canonical**. OPcache включён (лимит файлов ещё низкий).

Отчёт обновлён: `index.html`, `anna-audit-report/index.html`.

---

## Дальше (сейчас)

1. Разработчик: **A4 canonical** — контрольное ТЗ `snippets/dev-control-tz-mobile-seo.md` (**B4.2–B4.3 ✅** 21.08).  
2. Приёмка B4: скрины Network + цели Метрики + форма B24.  
3. Хостер: Redis host:port (лимит `max_accelerated_files` на вирт. хостинге **не поднимают** — 24.08).  
4. Разработчик: MySQL `SET SESSION` + Redis в кеше Битрикс (когда дадут порт).  
5. **Контрольный lab mobile** после приёмки B4 / A4 vs 20.08.  
6. **F2** — Bitrix24 webhook + DIALOG_ID → тестовый пост → Task Scheduler (Пн).

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
