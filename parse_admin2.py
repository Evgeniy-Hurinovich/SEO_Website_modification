# -*- coding: utf-8 -*-
import re, sys
from pathlib import Path
from html import unescape
sys.stdout.reconfigure(encoding="utf-8")
OUT = Path(r"D:\SEO_Website_modification\admin_explore")

def strip_tags(s):
    s = re.sub(r"<script[^>]*>.*?</script>", " ", s, flags=re.I|re.S)
    s = re.sub(r"<style[^>]*>.*?</style>", " ", s, flags=re.I|re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", unescape(s)).strip()

# Composite pages - how many cached?
html = (OUT/"20_composite_pages.html").read_text(encoding="utf-8", errors="replace")
text = strip_tags(html)
print("=== COMPOSITE PAGES ===")
for kw in ["Всего", "страниц", "нет запис", "композит", "кеш", "0 /"]:
    i = text.lower().find(kw.lower())
    if i>=0: print(text[max(0,i-30):i+120])
# count rows that look like URLs
urls = re.findall(r"https?://a2c\.by/[^\s\"'<]+", html)
print("a2c urls in page:", len(set(urls)))
print("sample:", list(set(urls))[:10])

# Aspro center - LazyLoad checkbox
html = (OUT/"23_aspro_center.html").read_text(encoding="utf-8", errors="replace")
print("\n=== ASPRO LAZY / OPT ===")
for m in re.finditer(r'.{0,80}LazyLoad.{0,200}', html, re.I):
    chunk = m.group(0)
    print("RAW:", re.sub(r"\s+"," ", chunk)[:280])
# find USE_LAZY_LOAD or similar
for m in re.finditer(r'name=["\']([^"\']*(?:LAZY|WEBP|OPTIM|SPEED|PAGE)[^"\']*)["\'][^>]*>', html, re.I):
    tag_start = html.rfind("<", 0, m.start())
    tag = html[tag_start:m.end()+40]
    print(m.group(1), "checked=" + str("checked" in tag.lower()), tag[:150])

# Banners / huge banners
html = (OUT/"27_banners.html").read_text(encoding="utf-8", errors="replace")
print("\n=== BANNERS IBLOCKS ===")
for row in re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.I|re.S):
    t = strip_tags(row)
    if len(t)>20 and re.search(r"\d{1,3}", t) and "Marketplace" not in t and "Рабочий стол" not in t:
        if any(x in t for x in ["Баннер", "Больш", "Маркет", "Реклам", "Всего", "позиц"]):
            print("-", t[:200])

# Perfmon recommendations text
html = (OUT/"11_perfmon.html").read_text(encoding="utf-8", errors="replace")
text = strip_tags(html)
print("\n=== PERFMON DETAILS ===")
# Find recommendation table-ish
idx = text.find("Производительность:")
print(text[idx:idx+2500] if idx>=0 else text[3000:5500])

# Services sections deeper - subsections
html = (OUT/"24_services_iblock.html").read_text(encoding="utf-8", errors="replace")
print("\n=== SERVICE SECTIONS/ELEMENTS clearer ===")
# Look for adm-list-table-cell content
cells = re.findall(r'class="adm-list-table-cell[^"]*"[^>]*>(.*?)</td>', html, re.I|re.S)
# too many - try links to iblock_element
links = re.findall(r'iblock_element_edit\.php\?[^"\']+["\'][^>]*>([^<]+)', html, re.I)
print("elements:", links[:30])
seclinks = re.findall(r'iblock_list_admin\.php\?[^"\']+SECTION_ID=(\d+)[^"\']*["\'][^>]*>([^<]+)', html, re.I)
print("sections:", seclinks[:40])

# Check if /services/ path exists on disk listing - we saw only index files, services are SEF from iblock
print("\nNote: /services/ is SEF from IBLOCK 42, not physical folders per service")
