# A2 Consulting — аудит a2c.by

Внутренний интерактивный отчёт по производительности, админке Битрикс и SEO-видимости сайта [a2c.by](https://a2c.by/).

## Локальный просмотр

Откройте `index.html` в браузере или:

```bash
python -m http.server 8765
```

http://127.0.0.1:8765/

## Деплой на Vercel

1. Import репозитория на [vercel.com/new](https://vercel.com/new)
2. **Root Directory** — оставить **пустым** (сайт в корне репо)
3. Framework Preset → **Other**
4. Build Command → пусто
5. Output Directory → пусто
6. Deploy

После пуша в `main` Vercel обновит сайт автоматически.

## Структура

- `index.html` — отчёт (данные в `REPORT_DATA` и `SEO_DATA`)
- `favicon.*`, `og-preview.png` — иконка и превью ссылки
- `*.py` — скрипты аудита (локально)
- `.env.example` — шаблон секретов (настоящий `.env` не в git)

## Важно

Отчёт не меняет боевой сайт a2c.by. В meta стоит `noindex`.
