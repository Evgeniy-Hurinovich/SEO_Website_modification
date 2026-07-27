# A2 Consulting — аудит a2c.by

Внутренний интерактивный отчёт по производительности, админке Битрикс и SEO-видимости сайта [a2c.by](https://a2c.by/).

## Локальный просмотр

```bash
cd anna-audit-report
python -m http.server 8765
```

Открыть: http://127.0.0.1:8765/

Или открыть файл `anna-audit-report/index.html` напрямую в браузере.

## Деплой на Vercel

1. Импортировать этот репозиторий на [vercel.com/new](https://vercel.com/new).
2. **Root Directory** → `anna-audit-report`
3. Framework Preset → **Other**
4. Build Command → оставить пустым
5. Output → оставить по умолчанию
6. Deploy

После пуша в `main` Vercel пересоберёт сайт автоматически.

## Данные отчёта

Все цифры в `anna-audit-report/index.html` в объектах `REPORT_DATA` и `SEO_DATA`. Секреты админки хранятся только локально в `.env` (не коммитятся).

## Важно

Отчёт не вносит изменений на боевой сайт a2c.by.
