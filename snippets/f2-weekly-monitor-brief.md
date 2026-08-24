# Еженедельный мониторинг a2c.by — для Евгения / Анны

**Цель:** 3–5 метрик с явной динамикой, без «каши» из 40 показателей.  
**Канал для Ткачёнка (решение встречи):** корпоративный **Qlik Sense**, не бот в чат.  
Сборщик в git остаётся: `metrics/history.jsonl` → CSV → папка Qlik. Чат Bitrix — запасной, не основной. План витрины: `snippets/f2-qlik-seo-dashboard-plan.md`.

## Что хочет руководитель (из разговора)

- Видеть **динамику**, а не разовый отчёт.
- Понять, **что меняется быстро** (скорость) vs **что через недели** (позиции).
- Узкий набор **3–5 главных** метрик, на которых завязана работа команды.

## Два контура (обязательно разделять в отчёте)

| Контур | Что меряем | Когда видно эффект |
|--------|------------|--------------------|
| **A. Скорость (lab)** | Lighthouse mobile/desktop | **Сразу** после деплоя (часы) |
| **B. Скорость (field)** | CrUX / PSI field / Метрика Web vitals | **2–4 недели** накопления |
| **C. Видимость** | GSC клики/показы, Вебмастер | **2–8 недель** после правок |
| **D. Бизнес** | Цели Метрики (organic) | weekly, тренд с 4-й недели |

Не обещать Евгению рост позиций «на следующей неделе» после технических правок — это специфика SEO, как он и услышал в разговоре.

## Рекомендуемые 5 KPI (карточка для Жени)

1. **Mobile LCP (lab)** — цель ≤2.5 с (сейчас ~5.7 с)  
2. **Mobile TBT (lab)** — цель ≤200 мс (сейчас ~550 мс)  
3. **Mobile Performance** — цель ≥85 (сейчас 62)  
4. **GSC: клики organic (неделя)** — тренд ↑ (без обещания скачка)  
5. **Метрика: целевые визиты из поиска** — цели F3 уже есть  

Опционально 6-й служебный: **canonical coverage** (да/нет на 5 URL) — P0 техдолг.

Desktop LCP/Perf — в той же таблице второй колонкой (сейчас отлично: Perf 97 / LCP 1.1 с), чтобы не путать «сайт быстрый на ПК» с «мобила в поиске».

## Автоматизация (схема)

```
[ cron / Task Scheduler раз в неделю ]
        ↓
  seo_weekly_monitor.py
        ↓
  ┌─────┴──────┐
  lab LH m/d   GSC API / ручной CSV   live HTML probe
        ↓
  metrics/history.jsonl
        ↓
  Bitrix24 REST  im.message.add
  DIALOG_ID=chatXXX  MESSAGE=дайджест
  (краткий дайджест + ▲▼ к прошлой неделе)
```

Контракт Bitrix24 (не `{"text":…}`):

```
POST {BITRIX24_WEBHOOK_URL}/im.message.add.json
Content-Type: application/json

{"DIALOG_ID":"chat123","MESSAGE":"...","URL_PREVIEW":"N"}
```

`DIALOG_ID`: `chat123` — групповой чат; `sg123` — чат проекта; число — личка.  
В URL чата: `/online/?IM_DIALOG=chat123`. Права входящего вебхука: **im**.

### Webhook-сообщение (пример текста)

```
a2c.by · weekly · 20.08.2026

[lab] Speed mobile: Perf 62 (▲+4) · LCP 5.7 с (▲+1.0 с) · TBT 550 мс (▼−393 мс) · SEO LH 100
[lab] Speed desktop: Perf 97 · LCP 1.1 с · TBT 70 мс
[live] canonical ✗ (/, /services/dwh/, /services/bi/, /contacts/) · robots ✓ · sitemap ✓

[GSC] клики за неделю: — (нет данных)
[field] CrUX/PSI: — (лаг 2–4 нед., не в этом замере)
[biz] Метрика, цели organic: — (слот F3)

▲▼ к прошлой неделе. lab — часы после деплоя; GSC — лаг 2–8 нед.; field — 2–4 нед.
```

### Переменные окружения (`.env`, не коммитить)

- `BITRIX24_WEBHOOK_URL` + `BITRIX24_DIALOG_ID` — основной канал
- `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` — запасной
- опционально `GSC_CLICKS` / позже GSC API

Скрипт: `scripts/seo_weekly_monitor.py`

```
python scripts/seo_weekly_monitor.py --seed --post-only --dry-run
python scripts/seo_weekly_monitor.py --post-only
python scripts/seo_weekly_monitor.py --bitrix-recent
python scripts/seo_weekly_monitor.py --dry-run --reuse-lh
```

### Task Scheduler (Windows, понедельник)

- Программа: `python` (полный путь, например `C:\Users\...\python.exe`)
- Аргументы: `D:\SEO_Website_modification\scripts\seo_weekly_monitor.py`
- Рабочая папка: `D:\SEO_Website_modification`
- Триггер: еженедельно, понедельник, 09:00
- Скрипт сам читает `.env`, ставит `TEMP` в `_lh_tmp` (обход EPERM Lighthouse на Windows) и печатает UTF-8 (▲▼)
- При сбое консоли: в свойствах задачи добавить `PYTHONIOENCODING=utf-8`

## Расписание для Анны

| День | Действие |
|------|----------|
| Пн | Скрипт / ручной LH mobile+desktop → чат Жене |
| Пн | F2: 5 строк GSC + Метрика organic в шаблон |
| После деплоя B4/A4 | Внеочередной lab в тот же день |

## Не смешивать в одном графике

Lab LCP и позиции в выдаче — разные оси времени. В чате всегда писать подпись: **lab** или **field** / **GSC**.
