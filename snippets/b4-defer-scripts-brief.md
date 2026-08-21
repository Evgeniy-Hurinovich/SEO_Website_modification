# ТЗ разработчику — B4.2–B4.4 (отложить сторонние скрипты)

> **Статус 21.08.2026:** B4.2 и B4.3 — **СДЕЛАНО**.  
> Дальнейшие задачи разработчика: `snippets/dev-control-tz-mobile-seo.md` (A4 + приёмка + isolation/Redis).

**Сайт:** https://a2c.by/  
**Шаблон:** `/bitrix/templates/aspro-allcorp3/`  
**Дата:** 11.08.2026 (обновлено 21.08)  

## Baseline (lab)

Мобильная главная `https://a2c.by/` (Lighthouse 12.2.1):

| Метрика | 11.08 | **20.08** | Цель после B4 |
|---------|-------|-----------|----------------|
| Performance | 58 | **62** | ≥65–70 |
| LCP | 4.7 с | **5.7 с** (шум lab) | ≤3.5–4.0 с (итог ≤2.5 с с B5) |
| TBT | **940 мс** | **550 мс** | ≤400–500 мс (итог ≤200) |
| TTI | 10.2 с | **7.6 с** | ≤6 с |
| CLS | 0 | **0** | держать ≤0.1 |
| Desktop Perf | — | **97** | держать ≥90 |

Ориентир для приёмки B4: сравнивать с **20.08** (TBT 550 / Perf 62). Исторический baseline defer-задачи — **11.08 TBT 940 мс**.

## Цель

Снизить **TBT / INP** и конкуренцию с LCP на first load: Метрика, CRM-форма B24 и (опционально) чат не должны грузиться синхронно в критическом пути.

## Что уже сделано (не ломать)

- Счётчик Метрики один: **108757686** (старый 107023549 убран из модуля)  
- Hero баннеры → WebP ≤120 KB (B3)  
- АвтоКомпозит включён; JS в конец + сжатые копии (B1–B2)  
- `custom.css` — aspect-ratio для CLS (C5)

## Где искать на сервере (важно)

### `invis-counter.php` — **не место правки B4.2**

| | |
|---|---|
| **Путь** | `/include/invis-counter.php` (корень сайта) |
| **Админка** | Контент → Структура сайта → Файлы и папки → `include` |
| **Статус** | Файл **пустой** — через него Метрика **не подключена** |
| **Для B4.2** | **Не править.** Не вписывать сюда счётчик (будет дубль с кодом в шаблоне) |

Рабочий счётчик **108757686** — отдельный inline `<script>` перед `</body>` + stub `/bitrix/js/yandex.metrika/script.js`.

**Как найти место правки B4.2** (SSH или файловый менеджер):

```bash
grep -r "108757686\|ym(" /home/bitrix/www/bitrix/templates/aspro-allcorp3/
```

Обычно: `footer.php`, `footer_1.php`, `page_blocks/footer_*.php` или include в шаблоне.

Модуль «Яндекс.Метрика» в админке (`/bitrix/admin/settings.php?mid=yandex.metrika`) — поле счётчика **оставить пустым** (B4.1 уже сделано).

---

### `loader_29.js` — **не локальный файл на диске**

| | |
|---|---|
| **URL** | `https://cdn-ru.bitrix24.by/b14332120/crm/form/loader_29.js` |
| **На сервере** | Файла `loader_29.js` **нет** — только inline-код, который его подгружает |
| **Маркеры в HTML** | `#bx24_form_inline_second`, `data-b24-form="inline/29/cjt1zt"`, кеш-блок `FrontPageForm` |

**Как найти место правки B4.3:**

```bash
grep -r "bx24_form_inline_second\|loader_29\|cjt1zt\|FrontPageForm" /home/bitrix/www/
```

Типичные места: `/index.php` (главная), `/include/mainpage/`, шаблон `/bitrix/templates/aspro-allcorp3/` (компоненты, `page_blocks/`).

Пример того, что сейчас в HTML главной (нужно отложить):

```html
<div id="bx24_form_inline_second"></div>
<script data-b24-form="inline/29/cjt1zt" data-skip-moving="true">
(function(w,d,u){var s=d.createElement('script');s.async=true;s.src=u+'?'+(Date.now()/180000|0);
var h=d.getElementsByTagName('script')[0];h.parentNode.insertBefore(s,h);})
(window,document,'https://cdn-ru.bitrix24.by/b14332120/crm/form/loader_29.js');
</script>
```

---

## B4.2 — отложить Яндекс.Метрику

**Где править:** inline-вставка `ym(108757686, 'init', …)` + `tag.js` в шаблоне (см. grep выше). **Не** `invis-counter.php`, **не** модуль Метрики в админке.

**Требование:**

1. Не грузить `mc.yandex.ru/metrika/tag.js` до первого из событий:
   - `scroll` / `click` / `touchstart` / `keydown`, **или**
   - timeout **3–5 с** после `load`
2. Для бота Метрики / согласий — допустима немедленная загрузка (если нужно для учёта)
3. После отложенной загрузки — тот же `ym(108757686, 'init', {…})` с текущими опциями (webvisor, clickmap, ecommerce)
4. **Не включать** снова номер счётчика в модуле Битрикс «Яндекс.Метрика» (будет дубль)

**Проверка:** в Network при cold load первые ~3 с нет `tag.js`; после скролла/таймера — визиты идут в 108757686; цели F3 («Заказать звонок» и др.) продолжают срабатывать.

## B4.3 — отложить CRM-форму Bitrix24 на главной

**Где править:** PHP/HTML-файл на сервере, из которого выводится inline loader (см. grep выше). Сам `loader_29.js` лежит на CDN Bitrix24, не в репозитории сайта.

Маркеры блока на главной:

- `data-b24-form="inline/29/cjt1zt"`
- `https://cdn-ru.bitrix24.by/b14332120/crm/form/loader_29.js`
- контейнер `#bx24_form_inline_second` / dynamic `FrontPageForm`

**Требование:**

1. Не подключать `loader_29.js` в initial HTML (убрать `data-skip-moving` sync insert)  
2. Загружать loader по:
   - попаданию блока формы во viewport (IntersectionObserver), **или**
   - клику «Получить консультацию» / скроллу до формы, **или**
   - timeout после `load` (например 4–6 с)
3. Форма после загрузки должна открываться/отображаться как сейчас  
4. Не ломать композитный кеш Aspro (dynamic block FrontPageForm)

**Проверка:** cold load главной — нет `loader_29.js` в первых запросах; TBT ниже baseline; форма работает.

## B4.4 — опционально: чат n8n

**Где:** `/n8n_bot/` + вставка в шаблоне (если виджет на first load).

Отложить по той же схеме (interaction / timeout). Если чата на first paint нет — пропустить.

## Не делать

- Не удалять аналитику и CRM  
- Не откатывать B3 WebP / Композит  
- Не править модуль Метрики «включить счётчик» без согласования

## Сдача

1. Diff / список изменённых файлов  
2. Скрин Network cold load (без tag.js / loader_29 early)  
3. Подтверждение: цели Метрики + отправка формы B24 OK  

Ориентир эффекта: **TBT** с **550 мс** (lab 20.08; было 940 на 11.08) вниз к ≤400 мс, лучше ≤200 мс. Повторный Lighthouse mobile на `/` после деплоя.
