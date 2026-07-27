# -*- coding: utf-8 -*-
"""Explore Bitrix admin — credentials from .env, never print secrets."""
import re
import sys
import json
from pathlib import Path
from urllib.parse import urljoin, urlparse, parse_qs
from html.parser import HTMLParser

import urllib.request
import urllib.parse
import http.cookiejar
import ssl

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(r"D:\SEO_Website_modification")
env = {}
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    env[k.strip()] = v.strip()

LOGIN = env["BITRIX_LOGIN"]
PASSWORD = env["BITRIX_PASSWORD"]
BASE = "https://a2c.by"
OUT = ROOT / "admin_explore"
OUT.mkdir(exist_ok=True)

ctx = ssl.create_default_context()
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(cj),
    urllib.request.HTTPSHandler(context=ctx),
)
opener.addheaders = [
    ("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"),
]


def fetch(url, data=None, method=None):
    if data is not None:
        body = urllib.parse.urlencode(data).encode("utf-8")
        req = urllib.request.Request(url, data=body, method=method or "POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
    else:
        req = urllib.request.Request(url, method=method or "GET")
    with opener.open(req, timeout=60) as r:
        raw = r.read()
        return r.geturl(), r.status, raw, dict(r.headers)


def save(name, content: bytes):
    path = OUT / name
    path.write_bytes(content)
    return path


# 1) GET login page
url, status, raw, headers = fetch(f"{BASE}/bitrix/admin/")
print("LOGIN PAGE", status, url, "bytes", len(raw))
save("01_login_page.html", raw)
html = raw.decode("utf-8", "replace")

# Extract sessid / form fields if present
sessid = None
m = re.search(r'name=["\']sessid["\'][^>]*value=["\']([^"\']+)', html, re.I)
if not m:
    m = re.search(r'bxSession\.sessid\s*=\s*[\'"]([^\'"]+)', html)
if not m:
    m = re.search(r'sessid[=:][\'"]?([a-f0-9]{32})', html, re.I)
if m:
    sessid = m.group(1)
    print("sessid found:", sessid[:8] + "...")
else:
    print("sessid: not on login page (ok)")

# 2) AUTH
auth_data = {
    "AUTH_FORM": "Y",
    "TYPE": "AUTH",
    "USER_LOGIN": LOGIN,
    "USER_PASSWORD": PASSWORD,
    "USER_REMEMBER": "Y",
    "Login": "Войти",
}
if sessid:
    auth_data["sessid"] = sessid

url, status, raw, headers = fetch(f"{BASE}/bitrix/admin/index.php?lang=ru", auth_data)
print("AUTH POST", status, "final", url, "bytes", len(raw))
save("02_after_auth.html", raw)
html = raw.decode("utf-8", "replace")

# Check success
ok = (
    "USER_LOGIN" not in html[:5000]
    and ("logout" in html.lower() or "bitrix_sessid" in html.lower() or "adm-header" in html.lower() or "menu-popup" in html.lower())
)
# Better checks
logged_in = (
    "Выход" in html
    or "Logout" in html
    or 'id="bx-panel"' in html
    or "adm-mainmenu" in html
    or "/bitrix/admin/?logout" in html
    or "bx-admin-login" not in html
)
# Fail if still login form
still_login = 'name="USER_PASSWORD"' in html or 'name="USER_LOGIN"' in html
print("still_login_form:", still_login)
print("title:", re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S))
title_m = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
print("title_text:", re.sub(r"\s+", " ", title_m.group(1)).strip() if title_m else None)

# Extract new sessid
m = re.search(r"['\"]bitrix_sessid['\"]\s*,\s*['\"]([a-f0-9]+)['\"]", html)
if not m:
    m = re.search(r'name=["\']sessid["\'][^>]*value=["\']([^"\']+)', html, re.I)
if not m:
    m = re.search(r"bxSession\.sessid\s*=\s*['\"]([^'\"]+)", html)
sessid2 = m.group(1) if m else None
print("post-auth sessid:", (sessid2[:8] + "...") if sessid2 else None)

# Save cookies summary (names only)
print("cookies:", [c.name for c in cj])

if still_login:
    print("AUTH FAILED")
    # look for error message
    for pat in [r"class=\"[^\"]*error[^\"]*\"[^>]*>(.*?)<", r"adm-login-message[^>]*>(.*?)<", r"Ошибка.*?<"]:
        em = re.search(pat, html, re.I | re.S)
        if em:
            print("err snippet:", re.sub(r"<[^>]+>", "", em.group(0))[:200])
    sys.exit(1)

print("AUTH OK")
(ROOT / "admin_explore" / "sessid.txt").write_text(sessid2 or "", encoding="utf-8")

# Pages to explore
pages = {
    "03_dashboard": f"{BASE}/bitrix/admin/index.php?lang=ru",
    "04_iblock38": f"{BASE}/bitrix/admin/iblock_list_admin.php?IBLOCK_ID=38&type=aspro_allcorp3_content&lang=ru&find_section_section=0&SECTION_ID=0&apply_filter=Y",
    "05_iblock_types": f"{BASE}/bitrix/admin/iblock_type_admin.php?lang=ru",
    "06_iblock_admin": f"{BASE}/bitrix/admin/iblock_admin.php?lang=ru&type=aspro_allcorp3_content&admin=Y",
    "07_sites": f"{BASE}/bitrix/admin/site_admin.php?lang=ru",
    "08_templates": f"{BASE}/bitrix/admin/template_admin.php?lang=ru",
    "09_cache": f"{BASE}/bitrix/admin/cache.php?lang=ru",
    "10_composite": f"{BASE}/bitrix/admin/composite.php?lang=ru",
    "11_perfmon": f"{BASE}/bitrix/admin/perfmon_panel.php?lang=ru",
    "12_seo_sitemap": f"{BASE}/bitrix/admin/seo_sitemap.php?lang=ru",
    "13_seo_robots": f"{BASE}/bitrix/admin/seo_robots.php?lang=ru",
    "14_modules": f"{BASE}/bitrix/admin/partner_modules.php?lang=ru",
    "15_settings": f"{BASE}/bitrix/admin/settings.php?lang=ru&mid=main",
    "16_fileman": f"{BASE}/bitrix/admin/fileman_admin.php?lang=ru&path=%2F&site=s1",
    "17_aspro_options": f"{BASE}/bitrix/admin/settings.php?lang=ru&mid=aspro.allcorp3",
    "18_menu_top": f"{BASE}/bitrix/admin/menu.php?lang=ru",
}

for name, page_url in pages.items():
    try:
        u, st, raw, _ = fetch(page_url)
        save(f"{name}.html", raw)
        title_m = re.search(r"<title[^>]*>(.*?)</title>", raw.decode("utf-8", "replace"), re.I | re.S)
        title = re.sub(r"\s+", " ", title_m.group(1)).strip() if title_m else "?"
        print(f"OK {st} {name}: {title[:80]} ({len(raw)} b) -> {u[:80]}")
    except Exception as e:
        print(f"FAIL {name}: {e}")

print("DONE")
