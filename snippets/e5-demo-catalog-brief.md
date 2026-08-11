# E5 — чистка демо-каталога Aspro

Дата: 11.08.2026  
Цель: убрать шаблонный каталог из индекса и sitemap, не трогая коммерческие `/services/`.

## Аудит (до правок)

| Что | Статус |
|-----|--------|
| Публичный URL каталога | **https://a2c.by/product/** (не `/catalog/` — там 404) |
| Демо-текст Aspro | «инженерные услуги», «широкий ассортимент товаров» — шаблон |
| `/landings/` | Страница «Обзоры», список пуст, но тоже в sitemap |
| `meta robots` | **Нет** на `/product/` и `/landings/` → страницы индексируются |
| `sitemap-files.xml` | Включает **/product/** и **/landings/** |
| IB 75 «Каталог» | `INDEX_ELEMENT=N`, `INDEX_SECTION=N` — товары в sitemap iblock не попадают ✅ |
| IB 21 «Посадочные страницы» | ~37 демо-элементов (кондиционеры, водонагреватели…) — мусор в админке |
| Меню сайта | Ссылок на `/product/` на главной **нет** ✅ |

## План (3 шага, ~15 мин)

### Шаг 1 — noindex ✅ (11.08.2026)

**Фактически сделано (не SmartSEO — модуль не подходит для всего каталога):**

1. **robots.txt** — https://a2c.by/bitrix/admin/seo_robots.php?lang=ru  
   ```text
   Disallow: /product/
   Disallow: /landings/
   ```

2. **meta noindex в index.php** (в начало файла, до `IncludeComponent`):
   - https://a2c.by/bitrix/admin/fileman_file_edit.php?lang=ru&site=s1&path=%2Fproduct%2Findex.php
   - https://a2c.by/bitrix/admin/fileman_file_edit.php?lang=ru&site=s1&path=%2Flandings%2Findex.php  
   ```php
   <?$APPLICATION->SetPageProperty("robots", "noindex, follow");?>
   ```

### Шаг 2 — sitemap ✅ (11.08.2026)

1. https://a2c.by/bitrix/admin/seo_sitemap_edit.php?lang=ru&ID=1 → вкладка **Файлы** → снять галки с `/product` и `/landings`.  
2. https://a2c.by/bitrix/admin/seo_sitemap.php?lang=ru → **Запустить** (если зависло на 20% — сбросить `RUNNING=Y→N` в таблице `b_seo_sitemap_job`).  
3. Проверка: https://a2c.by/sitemap-files.xml — без `/product/` и `/landings/`.

### Шаг 3 — деактивировать демо-элементы ✅ (11.08.2026)

IB 21 «Посадочные страницы» (48 демо-элементов):  
https://a2c.by/bitrix/admin/iblock_list_admin.php?IBLOCK_ID=21&type=aspro_allcorp3_catalog&lang=ru

На проде все 48 элементов уже **неактивны** (`ACTIVE=N`). Если появятся новые — **Действия → Деактивировать**.

IB 75 «Каталог» — **не трогать**, там уже стоит запрет индексации элементов/разделов:  
https://a2c.by/bitrix/admin/iblock_edit.php?type=aspro_allcorp3_catalog&lang=ru&ID=75&admin=Y  
(поля «Индексировать элементы/разделы» = Нет).

## Проверка после правок

```text
/product/     → в HTML есть meta robots noindex
/landings/    → то же
sitemap-files → без product и landings
```

Публичные ссылки для ручной проверки:

- https://a2c.by/product/
- https://a2c.by/landings/
- https://a2c.by/sitemap-files.xml

## Не делаем

- Не удаляем папки `/product/` и `/landings/` с диска — Aspro может сломать обновления.  
- Не трогаем `/services/` и sitemap iblock 42.
