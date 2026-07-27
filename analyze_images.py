# -*- coding: utf-8 -*-
import re, ssl, sys, urllib.request
sys.stdout.reconfigure(encoding="utf-8")
html = open(r"D:\SEO_Website_modification\homepage.html", encoding="utf-8", errors="replace").read()
ctx = ssl.create_default_context()

srcs = re.findall(r'data-src=(["\'])(.*?)\1', html, re.I)
srcs = [m[1] for m in srcs]
srcs += re.findall(r'src=(["\'])(/upload/.*?)\1', html, re.I)
srcs = [m[1] if isinstance(m, tuple) else m for m in srcs]
# fix tuples from second findall
clean = []
for s in srcs:
    if isinstance(s, tuple):
        s = s[-1] if s[-1].startswith("/") else s[1]
    clean.append(s)
srcs = clean

seen = set()
imgs = []
for s in srcs:
    if s.startswith("data:"):
        continue
    if s.startswith("//"):
        s = "https:" + s
    elif s.startswith("/"):
        s = "https://a2c.by" + s
    if not s.startswith("http"):
        continue
    if s in seen:
        continue
    seen.add(s)
    imgs.append(s)

print("Unique images:", len(imgs))
rows = []
total = 0
for u in imgs:
    try:
        req = urllib.request.Request(u, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
            cl = r.headers.get("Content-Length")
            ct = r.headers.get("Content-Type", "")
            size = int(cl) if cl else -1
            if size > 0:
                total += size
            rows.append((size, ct, u))
    except Exception as e:
        rows.append((-1, str(e)[:40], u[:100]))
rows.sort(reverse=True)
print("Total:", round(total / 1024 / 1024, 2), "MB")
for size, ct, u in rows[:30]:
    print(f"{size/1024:8.1f} KB  {ct[:28]:28}  {u[:130]}")

print("\n=== GZIP TRANSFER SIZES ===")
assets = [
    "https://a2c.by/bitrix/cache/css/s1/aspro-allcorp3/template_2fc29da55f642450718e4ec86fac1ecf/template_2fc29da55f642450718e4ec86fac1ecf_v1.css?1784123939829142",
    "https://a2c.by/bitrix/cache/js/s1/aspro-allcorp3/template_b7a50725e04e6a8fa86d39748ed55546/template_b7a50725e04e6a8fa86d39748ed55546_v1.js?1782808685727045",
    "https://a2c.by/bitrix/js/main/core/core.min.js?1770884153229643",
    "https://a2c.by/bitrix/cache/js/s1/aspro-allcorp3/kernel_main/kernel_main_v1.js?1774852966159756",
    "https://a2c.by/bitrix/js/main/jquery/jquery-3.6.0.min.js",
    "https://a2c.by/bitrix/js/ui/design-tokens/dist/ui.design-tokens.min.css?177088415423463",
    "https://a2c.by/bitrix/panel/main/popup.min.css?177088415820774",
]
for u in assets:
    req = urllib.request.Request(
        u, headers={"User-Agent": "Mozilla/5.0", "Accept-Encoding": "gzip, deflate, br"}
    )
    with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
        data = r.read()
        name = u.split("/")[-1][:60]
        print(f"{len(data)/1024:7.1f} KB transferred  enc={r.headers.get('Content-Encoding')}  {name}")

# hero / background images from CSS-like inline
bgs = re.findall(r"(?:background(?:-image)?\s*:\s*url\(|data-bg=[\"']|data-src=[\"'])([^\"')]+)", html, re.I)
print("\nbg candidates:", len(set(bgs)))
