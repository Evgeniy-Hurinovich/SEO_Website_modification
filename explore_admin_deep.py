# -*- coding: utf-8 -*-
"""Deep dive: composite on/off, main CSS/JS opts, aspro pages, catalog/services."""
import re
import sys
import urllib.request
import urllib.parse
import http.cookiejar
import ssl
from pathlib import Path
from html import unescape

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"D:\SEO_Website_modification")
OUT = ROOT / "admin_explore"

env = {}
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    if not line.strip() or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    env[k.strip()] = v.strip()

BASE = "https://a2c.by"
ctx = ssl.create_default_context()
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(cj),
    urllib.request.HTTPSHandler(context=ctx),
)
opener.addheaders = [("User-Agent", "Mozilla/5.0")]


def fetch(url, data=None):
    if data is not None:
        body = urllib.parse.urlencode(data).encode()
        req = urllib.request.Request(url, data=body)
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
    else:
        req = urllib.request.Request(url)
    with opener.open(req, timeout=60) as r:
        return r.geturl(), r.read()


# login
_, raw = fetch(f"{BASE}/bitrix/admin/")
html = raw.decode("utf-8", "replace")
m = re.search(r'name=["\']sessid["\'][^>]*value=["\']([^"\']+)', html, re.I)
sessid = m.group(1) if m else ""
fetch(
    f"{BASE}/bitrix/admin/index.php?lang=ru",
    {
        "AUTH_FORM": "Y",
        "TYPE": "AUTH",
        "USER_LOGIN": env["BITRIX_LOGIN"],
        "USER_PASSWORD": env["BITRIX_PASSWORD"],
        "USER_REMEMBER": "Y",
        "Login": "Войти",
        "sessid": sessid,
    },
)

pages = {
    "20_composite_pages": f"{BASE}/bitrix/admin/composite_pages.php?lang=ru",
    "21_composite_log": f"{BASE}/bitrix/admin/composite.php?lang=ru&tabControl_active_tab=composite",
    "22_main_opt": f"{BASE}/bitrix/admin/settings.php?lang=ru&mid=main&mid_menu=1&tabControl_active_tab=edit5",
    "23_aspro_center": f"{BASE}/bitrix/admin/aspro.allcorp3_options.php?lang=ru&mid=aspro.allcorp3",
    "24_services_iblock": f"{BASE}/bitrix/admin/iblock_list_admin.php?IBLOCK_ID=42&type=aspro_allcorp3_content&lang=ru&find_section_section=0&SECTION_ID=0&apply_filter=Y",
    "25_catalog_iblocks": f"{BASE}/bitrix/admin/iblock_admin.php?lang=ru&type=aspro_allcorp3_catalog&admin=Y",
    "26_mainblocks": f"{BASE}/bitrix/admin/iblock_admin.php?lang=ru&type=aspro_allcorp3_mainblocks&admin=Y",
    "27_banners": f"{BASE}/bitrix/admin/iblock_admin.php?lang=ru&type=aspro_allcorp3_adv&admin=Y",
    "28_aspro_robots_gen": f"{BASE}/bitrix/admin/aspro.allcorp3_robots.php?lang=ru" if False else f"{BASE}/bitrix/admin/seo_robots.php?lang=ru",
    "29_site_checker": f"{BASE}/bitrix/admin/site_checker.php?lang=ru",
    "30_urlrewrite": f"{BASE}/bitrix/admin/urlrewrite_list.php?lang=ru",
    "31_yandex_metrika": f"{BASE}/bitrix/admin/settings.php?lang=ru&mid=yandex.metrika",
    "32_fileman_company": f"{BASE}/bitrix/admin/fileman_admin.php?lang=ru&path=%2Fcompany&site=s1",
    "33_fileman_services": f"{BASE}/bitrix/admin/fileman_admin.php?lang=ru&path=%2Fservices&site=s1",
    "34_perfmon_detail": f"{BASE}/bitrix/admin/perfmon_panel.php?lang=ru",
}

for name, url in pages.items():
    try:
        u, raw = fetch(url)
        (OUT / f"{name}.html").write_bytes(raw)
        title = re.search(r"<title[^>]*>(.*?)</title>", raw.decode("utf-8", "replace"), re.I | re.S)
        t = re.sub(r"\s+", " ", title.group(1)).strip() if title else "?"
        print(f"OK {name}: {t[:90]} ({len(raw)})")
    except Exception as e:
        print(f"FAIL {name}: {e}")


def strip_tags(s):
    s = re.sub(r"<script[^>]*>.*?</script>", " ", s, flags=re.I | re.S)
    s = re.sub(r"<style[^>]*>.*?</style>", " ", s, flags=re.I | re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", unescape(s)).strip()


def checkbox_state(html, name_substr):
    results = []
    for m in re.finditer(rf'<input[^>]+name=["\']([^"\']*{re.escape(name_substr)}[^"\']*)["\'][^>]*>', html, re.I):
        tag = m.group(0)
        n = m.group(1)
        checked = "checked" in tag.lower()
        typ = re.search(r'type=["\']([^"\']+)', tag, re.I)
        val = re.search(r'value=["\']([^"\']*)', tag, re.I)
        results.append((n, typ.group(1) if typ else "?", val.group(1) if val else "", checked))
    return results


# Analyze composite enable
html = (OUT / "10_composite.html").read_text(encoding="utf-8", errors="replace")
print("\n=== COMPOSITE STATE ===")
for n, typ, val, ch in checkbox_state(html, "composite"):
    if ch or "auto" in n.lower() or n in ("composite", "auto_composite"):
        print(f"  {n} type={typ} val={val} checked={ch}")
for n, typ, val, ch in checkbox_state(html, "auto"):
    print(f"  {n} type={typ} val={val} checked={ch}")
# look for enabled badge
text = strip_tags(html)
for kw in ["Включ", "выключ", "Активен", "не актив", "АвтоКомпозит", "работае"]:
    i = text.lower().find(kw.lower())
    if i >= 0:
        print(" ", text[max(0, i - 50) : i + 100])

# Main optimization tab
html = (OUT / "15_settings.html").read_text(encoding="utf-8", errors="replace")
print("\n=== MAIN MODULE OPT FLAGS ===")
for key in [
    "optimize_css_files",
    "optimize_js_files",
    "use_minified_css",
    "use_minified_js",
    "move_js_to_body",
    "compres_css_js_files",
    "compress_css_js_files",
    "control_js",
]:
    states = checkbox_state(html, key)
    for s in states:
        print(" ", s)
# broader search
for m in re.finditer(r'name=["\']([^"\']*(?:optim|minif|compress|move_js|css_files|js_files)[^"\']*)["\']', html, re.I):
    name = m.group(1)
    # find full input
    start = html.rfind("<input", 0, m.start())
    tag = html[start : m.end() + 80] if start >= 0 else ""
    checked = "checked" in tag.lower()
    print(f"  FOUND {name} checked={checked}")

# Services iblock 42
html = (OUT / "24_services_iblock.html").read_text(encoding="utf-8", errors="replace") if (OUT / "24_services_iblock.html").exists() else ""
print("\n=== SERVICES (IBLOCK 42) ===")
rows = re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.I | re.S)
for row in rows:
    t = strip_tags(row)
    if len(t) > 15 and not any(x in t for x in ["Рабочий стол", "Marketplace", "Административ"]):
        if re.search(r"\d{2,}", t):
            print("-", t[:180])

# Catalog
html = (OUT / "25_catalog_iblocks.html").read_text(encoding="utf-8", errors="replace") if (OUT / "25_catalog_iblocks.html").exists() else ""
print("\n=== CATALOG IBLOCKS ===")
for row in re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.I | re.S):
    t = strip_tags(row)
    if len(t) > 20 and re.search(r"\b\d{1,3}\b", t) and "Marketplace" not in t:
        if any(x in t for x in ["Продукт", "Тариф", "Комплект", "Обзор", "Мега", "Посадоч", "Всего"]):
            print("-", t[:200])

# Mainblocks
html = (OUT / "26_mainblocks.html").read_text(encoding="utf-8", errors="replace") if (OUT / "26_mainblocks.html").exists() else ""
print("\n=== MAINBLOCKS ===")
for row in re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.I | re.S):
    t = strip_tags(row)
    if len(t) > 15 and re.search(r"\d", t) and "Marketplace" not in t and "Рабочий стол" not in t:
        print("-", t[:200])

# Company / services folders
for fname, label in [("32_fileman_company.html", "COMPANY"), ("33_fileman_services.html", "SERVICES")]:
    p = OUT / fname
    if not p.exists():
        continue
    html = p.read_text(encoding="utf-8", errors="replace")
    print(f"\n=== FILEMAN {label} ===")
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.I | re.S):
        t = strip_tags(row)
        if ".php" in t.lower() or len(t.split()) <= 6 and len(t) > 2:
            if not any(x in t for x in ["Рабочий стол", "Marketplace", "Настройки продукта"]):
                print("-", t[:160])

# Site checker / errors
p = OUT / "29_site_checker.html"
if p.exists():
    html = p.read_text(encoding="utf-8", errors="replace")
    text = strip_tags(html)
    print("\n=== SITE CHECKER (snippet) ===")
    print(text[1500:3500][:1500])

# Metrika
p = OUT / "31_yandex_metrika.html"
if p.exists():
    html = p.read_text(encoding="utf-8", errors="replace")
    text = strip_tags(html)
    print("\n=== METRIKA ===")
    for kw in ["счётчик", "счетчик", "актив", "отлож", "async", "108757686", "включ"]:
        i = text.lower().find(kw.lower())
        if i >= 0:
            print(text[max(0, i - 40) : i + 100])

# Aspro options page
p = OUT / "23_aspro_center.html"
if p.exists():
    html = p.read_text(encoding="utf-8", errors="replace")
    text = strip_tags(html)
    print("\n=== ASPRO OPTIONS PAGE ===")
    print("len", len(html), "title area", text[:300])
    for kw in ["WebP", "Lazy", "lazy", "оптимиз", "скорост", "Google Page", "PageSpeed", "отлож", "критич"]:
        i = text.find(kw)
        if i >= 0:
            print(f"KW {kw}:", text[max(0, i - 40) : i + 120])

# Public site structure from homepage links
print("\n=== PUBLIC URL SAMPLE ===")
import urllib.request as u2
try:
    with opener.open(f"{BASE}/", timeout=30) as r:
        home = r.read().decode("utf-8", "replace")
    links = sorted(set(re.findall(r'href=["\'](https://a2c\.by)?(/[a-zA-Z0-9\-_/]+)["\']', home)))
    for href in links[:60]:
        path = href[1] if isinstance(href, tuple) else href
        print(path)
except Exception as e:
    print(e)
