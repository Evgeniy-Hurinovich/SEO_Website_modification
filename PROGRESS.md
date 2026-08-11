# A2 Consulting SEO — статус работ

**Сайт:** https://a2c.by/  
**Платформа:** 1С-Битрикс 25.750 · Aspro Allcorp3 (шаблон **`aspro-allcorp3`**, дефис)  
**Пауза / обновлено:** 11 августа 2026 — фаза D (schema) закрыта: D1–D3  
**Отчёт (main):** D3 Review отмечен после live-проверки

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
| **B3** Hero → WebP ≤120 KB | ⏳ | Маркетинг. Не режим «Отдельная картинка» |
| **B4.1** Старый счётчик Метрики | ✅ | Живой `108757686` |
| **B4.2–B4.4** Отложить скрипты | ⏳ | Нужен **разработчик** (код) |
| **B5.1–B5.2** Perfmon + таблицы БД | ✅ | Конфиг ≈ 7.25; таблицы «оптимально» |
| **B5.3–B5.5** OPcache / MySQL / Redis | ⏳ | Тикет хостеру — маркетинг |
| **B5.6** Повторный Perfmon | ⏳ | После хостера |

---

## Фаза C — On-page

| Пункт | Статус | Примечание |
|-------|--------|------------|
| **C1–C4** | ✅ | H1, title/desc P1, контакты |
| **C5** width/height | ⏳ | После B3 |

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
| **E2** BI | ⏳ | После E1 |
| **E3** AI/RPA/ML | ⏳ | После E1 |
| **E4** Перелинковка | ⏳ | С E1–E3 |
| **E5** | ⏳ | По плану |

---

## Дальше (сейчас)

1. **E2** — посадочная BI (`/services/bi/`), по тому же шаблону.  
2. **C5** — после B3.  
3. Анна: **B3**, хостер **B5.3–B5.5**.  
4. Разработчик: **B4.2–B4.3**.

**Правило:** живой a2c.by не менять без явного «можно» / подтверждения шага.

---

## Отчёт / репозиторий

- Вкладки: `#visibility-plan`, `#exec-report`  
- `index.html` + `anna-audit-report/index.html`  
- Snippets: `snippets/d1-org-website.jsonld.html`, `snippets/d2-service.jsonld.php`  
- Локальные `_*.py` / dumps — не в git  
- Кеш после правок шаблона: https://a2c.by/bitrix/admin/cache.php?lang=ru  

### Полезные пути

- Шаблон: `/bitrix/templates/aspro-allcorp3/`  
- Footer: `page_blocks/footer_1.php`  
- Услуги: `components/bitrix/news/services/` (`section.php`, `detail.php`)  
- Service include: `/include/service_jsonld.php`  
