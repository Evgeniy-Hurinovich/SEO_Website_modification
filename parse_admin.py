# -*- coding: utf-8 -*-
import re
import sys
from pathlib import Path
from html import unescape

sys.stdout.reconfigure(encoding="utf-8")
OUT = Path(r"D:\SEO_Website_modification\admin_explore")


def load(name):
    return (OUT / name).read_text(encoding="utf-8", errors="replace")


def strip_tags(s):
    s = re.sub(r"<script[^>]*>.*?</script>", " ", s, flags=re.I | re.S)
    s = re.sub(r"<style[^>]*>.*?</style>", " ", s, flags=re.I | re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    s = unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def extract_table_rows(html, limit=80):
    """Pull visible text from adm-list / table rows."""
    rows = []
    for m in re.finditer(r"<tr[^>]*>(.*?)</tr>", html, re.I | re.S):
        t = strip_tags(m.group(1))
        if len(t) < 3:
            continue
        # skip pure chrome
        if t.startswith("Название") and len(t) < 40:
            continue
        rows.append(t[:300])
        if len(rows) >= limit:
            break
    return rows


def find_inputs(html, keys):
    found = {}
    for key in keys:
        # checkbox checked
        for m in re.finditer(
            rf'name=["\']({re.escape(key)}[^"\']*)["\'][^>]*>', html, re.I
        ):
            tag_start = html.rfind("<", 0, m.start())
            tag = html[tag_start : m.end() + 50]
            val = re.search(r'value=["\']([^"\']*)', tag, re.I)
            checked = "checked" in tag.lower()
            found[m.group(1)] = {"value": val.group(1) if val else "", "checked": checked, "tag": tag[:120]}
        # also input value=
        for m in re.finditer(
            rf'<input[^>]+name=["\']({re.escape(key)}[^"\']*)["\'][^>]*>', html, re.I
        ):
            tag = m.group(0)
            val = re.search(r'value=["\']([^"\']*)', tag, re.I)
            checked = "checked" in tag.lower()
            found[m.group(1)] = {"value": val.group(1) if val else "", "checked": checked}
        for m in re.finditer(
            rf'<textarea[^>]+name=["\']({re.escape(key)}[^"\']*)["\'][^>]*>(.*?)</textarea>',
            html,
            re.I | re.S,
        ):
            found[m.group(1)] = {"value": m.group(2)[:500], "checked": False}
        for m in re.finditer(
            rf'<select[^>]+name=["\']({re.escape(key)}[^"\']*)["\'][^>]*>(.*?)</select>',
            html,
            re.I | re.S,
        ):
            sel = re.search(r'<option[^>]+selected[^>]*>(.*?)</option>', m.group(2), re.I | re.S)
            if not sel:
                sel = re.search(r'<option[^>]+selected[^>]*value=["\']([^"\']*)', m.group(2), re.I)
                val = sel.group(1) if sel else strip_tags(m.group(2))[:80]
            else:
                val = strip_tags(sel.group(1))
            found[m.group(1)] = {"value": val, "checked": False}
    return found


print("=" * 70)
print("IBLOCK TYPES")
print("=" * 70)
html = load("05_iblock_types.html")
for r in extract_table_rows(html, 40):
    if "aspro" in r.lower() or "тип" in r.lower() or "ID" in r or len(r) > 20:
        if any(x in r.lower() for x in ["aspro", "контент", "каталог", "новост", "форм", "баннер", "услуг"]):
            print("-", r[:200])

print("\n" + "=" * 70)
print("IBLOCKS aspro_allcorp3_content")
print("=" * 70)
html = load("06_iblock_admin.html")
for r in extract_table_rows(html, 100):
    # look for id patterns
    if re.search(r"\b\d{1,3}\b", r) and len(r) > 15:
        if not any(x in r for x in ["Главное меню", "Настройки", "Рабочий стол"]):
            print("-", r[:220])

print("\n" + "=" * 70)
print("IBLOCK 38 list (Новости)")
print("=" * 70)
html = load("04_iblock38.html")
# sections / elements
for r in extract_table_rows(html, 60):
    if len(r) > 10 and not any(x in r for x in ["Главное меню", "Рабочий стол", "Настройки продукта"]):
        print("-", r[:220])

print("\n" + "=" * 70)
print("SITES")
print("=" * 70)
html = load("07_sites.html")
for r in extract_table_rows(html, 30):
    if "s1" in r.lower() or "a2c" in r.lower() or "сайт" in r.lower() or "http" in r.lower():
        print("-", r[:200])

print("\n" + "=" * 70)
print("TEMPLATES")
print("=" * 70)
html = load("08_templates.html")
for r in extract_table_rows(html, 40):
    if "aspro" in r.lower() or "шаблон" in r.lower() or "template" in r.lower() or "allcorp" in r.lower():
        print("-", r[:200])

print("\n" + "=" * 70)
print("COMPOSITE")
print("=" * 70)
html = load("10_composite.html")
# key settings text
for pat in [
    r"Композитный сайт[^<]{0,80}",
    r"композитн\w+[^.<]{0,100}",
    r'name=["\'][^"\']*COMPOSITE[^"\']*["\'][^>]*>',
]:
    pass
keys = find_inputs(html, ["composite", "COMPOSITE", "AUTO", "BANNER", "GROUP", "EXCLUDE", "FRAME"])
print("inputs sample:", list(keys.keys())[:30])
# Get visible status phrases
text = strip_tags(html)
for phrase in [
    "Композитный режим",
    "Включён",
    "Включен",
    "Выключен",
    "Выключён",
    "Автокомпозит",
    "Гостевой кэш",
    "HTML-кеш",
    "композит",
]:
    idx = text.lower().find(phrase.lower())
    if idx >= 0:
        print("CTX:", text[max(0, idx - 40) : idx + 120])

# radio/checkbox around composite
for m in re.finditer(r"(composite[^\"]*|COMPOSITE[^\"]*)", html, re.I):
    pass
checks = re.findall(r'<input[^>]+type=["\'](?:checkbox|radio)["\'][^>]*>', html, re.I)
print("checkbox/radio count", len(checks))
for c in checks[:40]:
    name = re.search(r'name=["\']([^"\']+)', c)
    val = re.search(r'value=["\']([^"\']*)', c)
    checked = "checked" in c.lower()
    if name and ("comp" in name.group(1).lower() or "auto" in name.group(1).lower() or checked):
        print(" ", name.group(1), "val=", val.group(1) if val else "", "checked=", checked)

print("\n" + "=" * 70)
print("CACHE")
print("=" * 70)
html = load("09_cache.html")
text = strip_tags(html)
for phrase in ["Управляемый кеш", "Автокеширование", "HTML-кеш", "кеширован", "очист"]:
    idx = text.lower().find(phrase.lower())
    if idx >= 0:
        print("CTX:", text[max(0, idx - 30) : idx + 100])

print("\n" + "=" * 70)
print("ROBOTS")
print("=" * 70)
html = load("13_seo_robots.html")
# textarea content
tas = re.findall(r"<textarea[^>]*>(.*?)</textarea>", html, re.I | re.S)
print("textareas:", len(tas))
for i, t in enumerate(tas[:3]):
    print(f"--- textarea {i} len={len(t)} ---")
    print(t[:800])

print("\n" + "=" * 70)
print("SITEMAP SEO")
print("=" * 70)
html = load("12_seo_sitemap.html")
text = strip_tags(html)
print(text[text.find("sitemap") - 50 if "sitemap" in text.lower() else 0 :][:500] if False else "")
for r in extract_table_rows(html, 40):
    if any(x in r.lower() for x in ["sitemap", "сайтмап", "xml", "генери", "расписан", "актив", "http"]):
        print("-", r[:200])
# also look for empty state
if "Нет" in text or "не создан" in text.lower() or "добавить" in text.lower():
    idx = text.lower().find("sitemap")
    print("around sitemap:", text[max(0, (idx or 0) - 20) : (idx or 0) + 200])
print("snippet:", text[2000:3500][:800])

print("\n" + "=" * 70)
print("FILEMAN /")
print("=" * 70)
html = load("16_fileman.html")
for r in extract_table_rows(html, 50):
    if any(
        x in r.lower()
        for x in [
            ".php",
            "services",
            "company",
            "project",
            "blog",
            "news",
            "index",
            "catalog",
            "upload",
            "include",
            "urlrewrite",
        ]
    ):
        print("-", r[:200])

print("\n" + "=" * 70)
print("PERFMON")
print("=" * 70)
html = load("11_perfmon.html")
text = strip_tags(html)
# find scores
for m in re.finditer(r"(Производительность|Конфигурация|Битрикс|Страница|PHP|БД|Масштабируемость)[^.]{0,80}", text):
    print("-", m.group(0)[:120])
nums = re.findall(r"(?:оценка|балл|mark)[^\d]{0,20}(\d+(?:[.,]\d+)?)", text, re.I)
print("nums near mark:", nums[:20])

print("\n" + "=" * 70)
print("ASPRO OPTIONS")
print("=" * 70)
html = load("17_aspro_options.html")
text = strip_tags(html)
print("title area:", text[:500])
# look for lazy, optimize, speed, compress, minify
for kw in ["lazy", "Lazy", "оптимиз", "скорост", "сжат", "миниф", "WebP", "webp", "композит", "кеш", "JS", "CSS", "отлож"]:
    idx = text.find(kw)
    if idx >= 0:
        print(f"KW {kw}:", text[max(0, idx - 30) : idx + 100])

print("\n" + "=" * 70)
print("MAIN SETTINGS snippets")
print("=" * 70)
html = load("15_settings.html")
text = strip_tags(html)
for kw in ["кеширован", "композит", "оптимиз", "сжат", "минификац", "MoveJS", "объединен", "Controll"]:
    idx = text.lower().find(kw.lower())
    if idx >= 0:
        print(f"KW {kw}:", text[max(0, idx - 40) : idx + 120])
