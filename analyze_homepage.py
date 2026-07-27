# -*- coding: utf-8 -*-
import re
import sys
import ssl
import time
import statistics
import urllib.request
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")

html = open(r"D:\SEO_Website_modification\homepage.html", encoding="utf-8", errors="replace").read()
print("HTML bytes:", len(html.encode("utf-8")))
print("HTML chars:", len(html))

css = re.findall(r'<link[^>]+rel=["\']stylesheet["\'][^>]*>', html, re.I)
print("\n=== STYLESHEETS", len(css), "===")
for c in css:
    href = re.search(r'href=["\']([^"\']+)', c)
    media = re.search(r'media=["\']([^"\']+)', c)
    print("-", href.group(1) if href else c[:120], "| media=", media.group(1) if media else "all")

src_scripts = re.findall(r'<script([^>]*src=["\']([^"\']+)["\'][^>]*)>', html, re.I)
inline_scripts = re.findall(r"<script(?![^>]*src=)([^>]*)>(.*?)</script>", html, re.I | re.S)
print("\n=== SCRIPT TAGS ===")
print("external:", len(src_scripts))
print("inline:", len(inline_scripts))
blocking, defer, async_ = [], [], []
for attrs, src in src_scripts:
    a = attrs.lower()
    if "defer" in a:
        defer.append(src)
    elif "async" in a:
        async_.append(src)
    else:
        blocking.append(src)
print("render-blocking JS:", len(blocking))
for s in blocking:
    print("  BLOCK", s)
print("defer JS:", len(defer))
for s in defer:
    print("  defer", s)
print("async JS:", len(async_))
for s in async_:
    print("  async", s)
inline_size = sum(len(b) for a, b in inline_scripts)
print("inline JS total chars:", inline_size)

imgs = re.findall(r"<img[^>]+>", html, re.I)
print("\n=== IMAGES", len(imgs), "===")
lazy = sum(1 for img in imgs if re.search(r'loading=["\']lazy', img, re.I))
noalt = sum(1 for img in imgs if not re.search(r"alt=", img, re.I))
print("lazy:", lazy, "no alt:", noalt)
for img in imgs[:15]:
    src = re.search(r'(?:src|data-src)=["\']([^"\']+)', img, re.I)
    w = re.search(r'width=["\']?(\d+)', img, re.I)
    h = re.search(r'height=["\']?(\d+)', img, re.I)
    print(" ", (src.group(1) if src else "?")[:100], "w=", w.group(1) if w else "-", "h=", h.group(1) if h else "-")

hosts = Counter()
for m in re.findall(r"https?://([^/\"'\s]+)", html):
    hosts[m.lower()] += 1
print("\n=== EXTERNAL HOSTS ===")
for h, c in hosts.most_common(30):
    print(f"{c:4} {h}")

title = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
desc = re.search(r'name=["\']description["\'][^>]*content=["\']([^"\']*)', html, re.I)
if not desc:
    desc = re.search(r'content=["\']([^"\']*)["\'][^>]*name=["\']description', html, re.I)
canon = re.search(r'rel=["\']canonical["\'][^>]*href=["\']([^"\']+)', html, re.I)
print("\n=== SEO META ===")
print("title:", (title.group(1).strip() if title else None)[:160])
print("desc:", (desc.group(1)[:200] if desc else None))
print("canonical:", canon.group(1) if canon else None)
h1 = re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.I | re.S)
print("h1 count:", len(h1))
for h in h1[:5]:
    print(" H1:", re.sub(r"<[^>]+>", "", h).strip()[:120])

head = re.search(r"<head[^>]*>(.*?)</head>", html, re.I | re.S)
if head:
    h = head.group(1)
    print("\nHEAD size chars:", len(h))
    print("link in head:", len(re.findall(r"<link ", h, re.I)))
    print("script in head:", len(re.findall(r"<script ", h, re.I)))
    print("style in head:", len(re.findall(r"<style", h, re.I)))

# iframe / widgets
print("\nifames:", len(re.findall(r"<iframe", html, re.I)))
print("video:", len(re.findall(r"<video", html, re.I)))
print("swiper/slider mentions:", len(re.findall(r"swiper|owl-carousel|slick", html, re.I)))

# Measure assets
ctx = ssl.create_default_context()
urls = []
for m in re.findall(r'href=["\']([^"\']+\.css[^"\']*)', html, re.I):
    if m.startswith("//"):
        m = "https:" + m
    elif m.startswith("/"):
        m = "https://a2c.by" + m
    if m.startswith("http"):
        urls.append(("css", m))
for m in re.findall(r'src=["\']([^"\']+\.js[^"\']*)', html, re.I):
    if m.startswith("//"):
        m = "https:" + m
    elif m.startswith("/"):
        m = "https://a2c.by" + m
    if m.startswith("http"):
        urls.append(("js", m))

seen = set()
uniq = []
for t, u in urls:
    if u not in seen:
        seen.add(u)
        uniq.append((t, u))

print("\n=== ASSET SIZES", len(uniq), "===")
total = 0
rows = []
for t, u in uniq:
    try:
        req = urllib.request.Request(u, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=25, context=ctx) as r:
            cl = r.headers.get("Content-Length")
            ce = r.headers.get("Content-Encoding", "")
            cc = (r.headers.get("Cache-Control") or "")[:50]
            size = int(cl) if cl else -1
            if size > 0:
                total += size
            rows.append((size, t, ce, cc, u))
    except Exception as e:
        rows.append((-1, t, "", "", u[:90] + " ERR:" + str(e)[:50]))

rows.sort(reverse=True)
print("Sum Content-Length (when present):", total, "bytes =", round(total / 1024, 1), "KB")
for size, t, ce, cc, u in rows:
    kb = size / 1024 if size >= 0 else -1
    print(f"{kb:8.1f} KB  {t:3}  enc={ce:6}  cache={cc:30}  {u[:140]}")
