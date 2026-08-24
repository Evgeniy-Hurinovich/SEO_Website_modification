# -*- coding: utf-8 -*-
from pathlib import Path

svg = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1320 980" role="img" aria-labelledby="archTitle archDesc">
  <title id="archTitle">Архитектура SEO weekly: от замера a2c.by до двух листов Qlik Sense</title>
  <desc id="archDesc">Понедельник 09:00 планировщик запускает Python. Скрипт мерит прод a2c.by через Lighthouse mobile и desktop, пишет CSV в папку. Qlik в 10:00 читает папку Folder Connection и обновляет два листа.</desc>
  <defs>
    <marker id="seq" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto">
      <path d="M0 1.5 L9 5 L0 8.5 Z" fill="#1a2332"/>
    </marker>
    <marker id="msg" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto">
      <path d="M0 1.5 L9 5 L0 8.5 Z" fill="#2a5f8f"/>
    </marker>
  </defs>
  <style>
    .pool { fill: #f4f7fa; stroke: #c5d0dc; stroke-width: 1.2; }
    .rail { fill: #1a2332; }
    .rt { fill: #e8eef4; font-size: 11px; font-weight: 700; letter-spacing: 0.4px; font-family: Segoe UI, Arial, sans-serif; }
    .task { fill: #fff; stroke: #0c6e6b; stroke-width: 1.6; }
    .opt { fill: #fff; stroke: #2a5f8f; stroke-width: 1.4; stroke-dasharray: 5 3; }
    .src { fill: #fff; stroke: #5a6a7e; stroke-width: 1.4; }
    .data { fill: #fff; stroke: #b8791d; stroke-width: 1.5; }
    .ql { fill: #fff; stroke: #1a2332; stroke-width: 1.6; }
    .evt { fill: #e6f4f3; stroke: #0c6e6b; stroke-width: 2; }
    .end { fill: #e8f6ee; stroke: #1f7a45; stroke-width: 2.4; }
    .t { font-family: Segoe UI, Arial, sans-serif; fill: #1a2332; }
    .a { font-size: 12.5px; font-weight: 700; }
    .b { font-size: 11px; fill: #5a6a7e; }
    .c { font-size: 10px; fill: #8b9aab; }
    .seq { fill: none; stroke: #1a2332; stroke-width: 1.7; marker-end: url(#seq); }
    .msg { fill: none; stroke: #2a5f8f; stroke-width: 1.5; stroke-dasharray: 6 4; marker-end: url(#msg); }
    .n { font-size: 10.5px; fill: #2a5f8f; font-style: italic; font-family: Segoe UI, Arial, sans-serif; }
  </style>

  <rect class="pool" x="16" y="16" width="1288" height="108" rx="14"/>
  <rect class="rail" x="16" y="16" width="48" height="108" rx="14"/>
  <rect class="rail" x="40" y="16" width="24" height="108"/>
  <text class="rt" transform="rotate(-90 40 70)" text-anchor="middle" x="40" y="74">1 · ПЛАНИРОВЩИК</text>
  <circle class="evt" cx="120" cy="70" r="26"/>
  <text class="t c" text-anchor="middle" x="120" y="67">timer</text>
  <text class="t a" text-anchor="middle" x="120" y="82">Пн 09:00</text>
  <path class="seq" d="M146 70 H188"/>
  <rect class="task" x="188" y="44" width="260" height="52" rx="10"/>
  <text class="t a" x="318" y="65" text-anchor="middle">Task Scheduler / cron</text>
  <text class="t b" x="318" y="82" text-anchor="middle">среда: Windows или CI</text>
  <path class="seq" d="M448 70 H490"/>
  <rect class="task" x="490" y="44" width="300" height="52" rx="10"/>
  <text class="t a" x="640" y="65" text-anchor="middle">старт процесса сбора</text>
  <text class="t b" x="640" y="82" text-anchor="middle">seo_weekly_monitor.py</text>
  <path class="seq" d="M640 96 V140"/>

  <rect class="pool" x="16" y="140" width="1288" height="224" rx="14"/>
  <rect class="rail" x="16" y="140" width="48" height="224" rx="14"/>
  <rect class="rail" x="40" y="140" width="24" height="224"/>
  <text class="rt" transform="rotate(-90 40 252)" text-anchor="middle" x="40" y="256">2 · СРЕДА СБОРА</text>
  <rect class="task" x="88" y="210" width="230" height="84" rx="10"/>
  <text class="t a" x="203" y="238" text-anchor="middle">Python-процесс</text>
  <text class="t b" x="203" y="256" text-anchor="middle">seo_weekly_monitor.py</text>
  <text class="t c" x="203" y="274" text-anchor="middle">машина / GitHub Actions</text>
  <path class="seq" d="M318 252 H360"/>
  <rect class="task" x="360" y="158" width="230" height="50" rx="10"/>
  <text class="t a" x="475" y="180" text-anchor="middle">Lighthouse mobile</text>
  <text class="t b" x="475" y="196" text-anchor="middle">lab · form-factor mobile</text>
  <rect class="task" x="360" y="218" width="230" height="50" rx="10"/>
  <text class="t a" x="475" y="240" text-anchor="middle">Lighthouse desktop</text>
  <text class="t b" x="475" y="256" text-anchor="middle">lab · вторая колонка</text>
  <rect class="task" x="360" y="278" width="230" height="50" rx="10"/>
  <text class="t a" x="475" y="300" text-anchor="middle">live HTML probe</text>
  <text class="t b" x="475" y="316" text-anchor="middle">canonical / robots / sitemap</text>
  <path class="seq" d="M590 183 H640 V252 H680"/>
  <path class="seq" d="M590 243 H680"/>
  <path class="seq" d="M590 303 H640 V252"/>
  <rect class="task" x="680" y="210" width="250" height="84" rx="10"/>
  <text class="t a" x="805" y="238" text-anchor="middle">сборка снимка недели</text>
  <text class="t b" x="805" y="256" text-anchor="middle">контур · метрика · значение</text>
  <text class="t c" x="805" y="274" text-anchor="middle">одна схема CSV</text>
  <rect class="opt" x="970" y="218" width="290" height="68" rx="10"/>
  <text class="t a" x="1115" y="244" text-anchor="middle">опционально: GSC / Метрика</text>
  <text class="t b" x="1115" y="262" text-anchor="middle">тот же CSV, contour = gsc | biz</text>
  <path class="seq" d="M805 294 V380"/>

  <rect class="pool" x="16" y="380" width="1288" height="134" rx="14"/>
  <rect class="rail" x="16" y="380" width="48" height="134" rx="14"/>
  <rect class="rail" x="40" y="380" width="24" height="134"/>
  <text class="rt" transform="rotate(-90 40 447)" text-anchor="middle" x="40" y="451">3 · ИСТОЧНИКИ</text>
  <rect class="src" x="88" y="408" width="260" height="78" rx="8"/>
  <text class="t a" x="218" y="438" text-anchor="middle">https://a2c.by/  ·  ПРОД</text>
  <text class="t b" x="218" y="456" text-anchor="middle">единственный URL для KPI lab</text>
  <text class="t c" x="218" y="472" text-anchor="middle">не стенд — иначе цифры врут</text>
  <rect class="src" x="390" y="408" width="230" height="78" rx="8"/>
  <text class="t a" x="505" y="438" text-anchor="middle">Google Search Console</text>
  <text class="t b" x="505" y="456" text-anchor="middle">клики / показы · лаг 2–8 нед.</text>
  <text class="t c" x="505" y="472" text-anchor="middle">API или ручной слот</text>
  <rect class="src" x="660" y="408" width="230" height="78" rx="8"/>
  <text class="t a" x="775" y="438" text-anchor="middle">Яндекс.Метрика</text>
  <text class="t b" x="775" y="456" text-anchor="middle">цели organic · F3</text>
  <text class="t c" x="775" y="472" text-anchor="middle">лаг weekly</text>
  <rect class="src" x="930" y="408" width="330" height="78" rx="8"/>
  <text class="t a" x="1095" y="438" text-anchor="middle">CrUX / PSI field — позже</text>
  <text class="t b" x="1095" y="456" text-anchor="middle">не смешивать с lab на одном графике</text>
  <text class="t c" x="1095" y="472" text-anchor="middle">лаг 2–4 недели</text>
  <path class="msg" d="M218 408 V318"/>
  <text class="n" x="226" y="338">данные (замер URL)</text>
  <path class="msg" d="M505 408 V350 H1115 V286"/>
  <path class="msg" d="M775 408 V358 H1115"/>

  <rect class="pool" x="16" y="530" width="1288" height="132" rx="14"/>
  <rect class="rail" x="16" y="530" width="48" height="132" rx="14"/>
  <rect class="rail" x="40" y="530" width="24" height="132"/>
  <text class="rt" transform="rotate(-90 40 596)" text-anchor="middle" x="40" y="600">4 · ХРАНИЛИЩЕ</text>
  <rect class="data" x="88" y="556" width="180" height="80" rx="8"/>
  <text class="t a" x="178" y="590" text-anchor="middle">history.jsonl</text>
  <text class="t b" x="178" y="608" text-anchor="middle">журнал рядом с кодом</text>
  <path class="seq" d="M268 596 H304"/>
  <rect class="data" x="304" y="556" width="200" height="80" rx="8"/>
  <text class="t a" x="404" y="590" text-anchor="middle">weekly_snapshot.csv</text>
  <text class="t b" x="404" y="608" text-anchor="middle">контракт для Qlik</text>
  <path class="seq" d="M504 596 H540"/>
  <rect class="data" x="540" y="556" width="360" height="80" rx="8"/>
  <text class="t a" x="720" y="586" text-anchor="middle">папка, которую видит Qlik</text>
  <text class="t b" x="720" y="604" text-anchor="middle">шара / Bitrix.Disk / drop</text>
  <text class="t c" x="720" y="620" text-anchor="middle">не личный GitHub как источник</text>
  <rect class="opt" x="940" y="560" width="320" height="72" rx="10"/>
  <text class="t a" x="1100" y="590" text-anchor="middle">код процесса — в git</text>
  <text class="t b" x="1100" y="608" text-anchor="middle">репозиторий ≠ витрина Qlik</text>
  <path class="seq" d="M720 636 V680"/>

  <rect class="pool" x="16" y="680" width="1288" height="220" rx="14"/>
  <rect class="rail" x="16" y="680" width="48" height="220" rx="14"/>
  <rect class="rail" x="40" y="680" width="24" height="220"/>
  <text class="rt" transform="rotate(-90 40 790)" text-anchor="middle" x="40" y="794">5 · QLIK SENSE</text>
  <circle class="evt" cx="120" cy="790" r="26"/>
  <text class="t c" text-anchor="middle" x="120" y="787">timer</text>
  <text class="t a" text-anchor="middle" x="120" y="802">Пн 10:00</text>
  <path class="seq" d="M146 790 H188"/>
  <rect class="ql" x="188" y="764" width="210" height="52" rx="10"/>
  <text class="t a" x="293" y="785" text-anchor="middle">Reload task</text>
  <text class="t b" x="293" y="802" text-anchor="middle">report-сервер, ОК Миши</text>
  <path class="seq" d="M398 790 H440"/>
  <rect class="ql" x="440" y="758" width="240" height="64" rx="10"/>
  <text class="t a" x="560" y="782" text-anchor="middle">Folder Connection</text>
  <text class="t b" x="560" y="800" text-anchor="middle">читает CSV, ничего не пишет</text>
  <path class="msg" d="M720 636 C720 710, 560 710, 560 758"/>
  <text class="n" x="580" y="728">поток данных</text>
  <path class="seq" d="M680 790 H722"/>
  <rect class="ql" x="722" y="712" width="230" height="56" rx="10"/>
  <text class="t a" x="837" y="736" text-anchor="middle">Лист 1 · 5 KPI + тренд</text>
  <text class="t b" x="837" y="752" text-anchor="middle">lab / GSC / field / biz</text>
  <rect class="ql" x="722" y="780" width="230" height="56" rx="10"/>
  <text class="t a" x="837" y="804" text-anchor="middle">Лист 2 · сырая таблица</text>
  <text class="t b" x="837" y="820" text-anchor="middle">длинный формат CSV</text>
  <path class="seq" d="M837 768 V780"/>
  <path class="seq" d="M952 808 H996"/>
  <circle class="end" cx="1028" cy="808" r="28"/>
  <circle class="end" cx="1028" cy="808" r="20" fill="none"/>
  <text class="t a" text-anchor="middle" x="1160" y="800">Ткачёнок / Руслан</text>
  <text class="t b" text-anchor="middle" x="1160" y="816">открывают приложение</text>
  <text class="t c" x="80" y="876">Среда Qlik: корпоративный report-сервер. Приложение не в личном кабинете.</text>

  <rect x="16" y="916" width="1288" height="48" rx="10" fill="#fff" stroke="#e2e8f0"/>
  <line class="seq" x1="40" y1="940" x2="100" y2="940"/>
  <text class="t b" x="108" y="944">последовательность процесса</text>
  <line class="msg" x1="380" y1="940" x2="440" y2="940"/>
  <text class="t b" x="448" y="944">поток данных / сообщение</text>
  <rect class="task" x="720" y="928" width="70" height="24" rx="6"/>
  <text class="t b" x="798" y="944">задача</text>
  <circle class="evt" cx="900" cy="940" r="10"/>
  <text class="t b" x="916" y="944">таймер</text>
  <rect class="data" x="1000" y="928" width="70" height="24" rx="4"/>
  <text class="t b" x="1078" y="944">файл данных</text>
  <rect class="opt" x="1188" y="928" width="22" height="24" rx="6"/>
  <text class="t b" x="1216" y="944">опция</text>
</svg>
"""

out = Path(__file__).resolve().parent / "architecture.svg"
out.write_text(svg, encoding="utf-8")
print("wrote", out, "chars", len(svg), "has cyr", "ПЛАНИРОВЩИК" in svg)
