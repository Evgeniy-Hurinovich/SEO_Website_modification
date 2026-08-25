# Макет: схема SEO + прототип Qlik

Внутренний сайт для показа руководству. Не боевой Qlik.

- `/` — блочная BPMN-схема (среды, процессы, потоки данных)
- `/qlik` — прототип двух листов

Цифры lab: Lighthouse 12.2.1, главная a2c.by, срез 24.08.2026 после B4.

## Локально

```
cd qlik-preview
npx --yes serve -l 4173 .
```

Открыть http://localhost:4173/

## GitHub + Vercel

Сайт лежит в папке `qlik-preview/` репозитория
`Evgeniy-Hurinovich/SEO_Website_modification`.

**На том же Vercel, что и SEO-отчёт** (корневой проект, без Root Directory):

- отчёт: `/`
- схема: `/qlik-preview/`
- макет Qlik: `/qlik-preview/qlik`

После push в `main` Vercel сам подхватит папку. В шапке отчёта есть ссылки «Схема» и «Макет Qlik».

Боевой URL:

- отчёт: https://seo-website-modification-3m77.vercel.app/#overview
- схема: https://seo-website-modification-3m77.vercel.app/qlik-preview/
- макет Qlik: https://seo-website-modification-3m77.vercel.app/qlik-preview/qlik

**Отдельный Vercel-проект** (другой URL): Root Directory = `qlik-preview`, Framework Other, без build. Тогда схема будет на `/` этого проекта; ссылка «Отчёт SEO» на `/` уже не ведёт на отчёт.

Сайт внутренний: `X-Robots-Tag: noindex`.
