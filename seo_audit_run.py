# -*- coding: utf-8 -*-
"""Full SEO visibility audit for a2c.by — public pages only."""
import json
import re
import ssl
import sys
import urllib.request
from collections import Counter
from html import unescape
from pathlib import Path
from urllib.parse import urljoin, urlparse

sys.stdout.reconfigure(encoding="utf-8")
OUT = Path(r"D:\SEO_Website_modification\seo_audit")
OUT.mkdir(exist_ok=True)
BASE = "https://a2c.by"
ctx = ssl.create_default_context()

URLS = [
    "/",
    "/services/",
    "/services/ai-rpa-ml/",
    "/services/ai-rpa-ml/ai-solutions/",
    "/services/bi/",
    "/services/bi/implementation-bi/",
    "/company/",
    "/company/reviews/",
    "/projects/",
    "/news/",
    "/contacts/",
]


def fetch(url, method="GET"):
    req = urllib.request.Request(
        url,
        method=method,
        headers={"User-Agent": "Mozilla/5.0 (compatible; A2SEOAudit/1.0)"},
    )
    with urllib.request.urlopen(req, timeout=45, context=ctx) as r:
        return r.geturl(), r.status, r.read(), dict(r.headers)


def strip(html):
    html = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.I | re.S)
    html = re.sub(r"<style[^>]*>.*?</style>", " ", html, flags=re.I | re.S)
    html = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", unescape(html)).strip()


def meta(html, name=None, prop=None):
    if name:
        m = re.search(
            rf'<meta[^>]+name=["\']{re.escape(name)}["\'][^>]+content=["\']([^"\']*)["\']',
            html,
            re.I,
        )
        if not m:
            m = re.search(
                rf'<meta[^>]+content=["\']([^"\']*)["\'][^>]+name=["\']{re.escape(name)}["\']',
                html,
                re.I,
            )
        return m.group(1).strip() if m else None
    if prop:
        m = re.search(
            rf'<meta[^>]+property=["\']{re.escape(prop)}["\'][^>]+content=["\']([^"\']*)["\']',
            html,
            re.I,
        )
        if not m:
            m = re.search(
                rf'<meta[^>]+content=["\']([^"\']*)["\'][^>]+property=["\']{re.escape(prop)}["\']',
                html,
                re.I,
            )
        return m.group(1).strip() if m else None


def analyze_page(path):
    url = urljoin(BASE, path)
    final, status, raw, headers = fetch(url)
    html = raw.decode("utf-8", "replace")
    title_m = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    title = re.sub(r"\s+", " ", title_m.group(1)).strip() if title_m else None
    h1s = [strip(x) for x in re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.I | re.S)]
    h2s = [strip(x) for x in re.findall(r"<h2[^>]*>(.*?)</h2>", html, re.I | re.S)]
    canonical = None
    cm = re.search(r'rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']', html, re.I)
    if not cm:
        cm = re.search(r'href=["\']([^"\']+)["\'][^>]*rel=["\']canonical["\']', html, re.I)
    if cm:
        canonical = cm.group(1)
    robots_meta = meta(html, name="robots")
    desc = meta(html, name="description")
    og_title = meta(html, prop="og:title")
    og_desc = meta(html, prop="og:description")
    og_url = meta(html, prop="og:url")
    tw = meta(html, name="twitter:card")
    imgs = re.findall(r"<img[^>]+>", html, re.I)
    noalt = sum(1 for i in imgs if not re.search(r'alt=', i, re.I) or re.search(r'alt=["\']\s*["\']', i))
    empty_alt = sum(1 for i in imgs if re.search(r'alt=["\']\s*["\']', i))
    # word count approx main
    text = strip(html)
    words = len(re.findall(r"[А-Яа-яA-Za-z0-9]{3,}", text))
    # internal links
    links = re.findall(r'href=["\']([^"\'#]+)', html, re.I)
    internal = []
    external = []
    for href in links:
        if href.startswith("mailto:") or href.startswith("tel:") or href.startswith("javascript:"):
            continue
        full = urljoin(final, href)
        host = urlparse(full).netloc.lower()
        if "a2c.by" in host or href.startswith("/"):
            internal.append(urlparse(full).path)
        else:
            external.append(host)
    # json-ld
    schemas = []
    for m in re.finditer(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html,
        re.I | re.S,
    ):
        try:
            data = json.loads(m.group(1))
            if isinstance(data, list):
                for d in data:
                    schemas.append(d.get("@type") if isinstance(d, dict) else str(type(d)))
            elif isinstance(data, dict):
                schemas.append(data.get("@type") or data.get("@graph") and "graph")
        except Exception:
            schemas.append("invalid-json-ld")
    # headings order issues
    return {
        "path": path,
        "final": final,
        "status": status,
        "bytes": len(raw),
        "title": title,
        "title_len": len(title or ""),
        "description": desc,
        "desc_len": len(desc or ""),
        "h1": h1s,
        "h1_count": len(h1s),
        "h2_sample": h2s[:8],
        "h2_count": len(h2s),
        "canonical": canonical,
        "robots_meta": robots_meta,
        "og_title": og_title,
        "og_desc": og_desc,
        "og_url": og_url,
        "twitter_card": tw,
        "img_count": len(imgs),
        "img_no_alt": noalt,
        "img_empty_alt": empty_alt,
        "word_approx": words,
        "internal_links": len(set(internal)),
        "internal_sample": sorted(set(internal))[:25],
        "external_hosts": sorted(set(external))[:15],
        "schemas": schemas,
        "x_robots": headers.get("X-Robots-Tag") or headers.get("x-robots-tag"),
        "cache_control": headers.get("Cache-Control") or headers.get("cache-control"),
    }


results = []
for p in URLS:
    try:
        r = analyze_page(p)
        results.append(r)
        print("OK", p, "title=", (r["title"] or "")[:70], "h1=", r["h1_count"], r["h1"][:1])
    except Exception as e:
        print("FAIL", p, e)
        results.append({"path": p, "error": str(e)})

# robots + sitemap
tech = {}
try:
    _, st, raw, _ = fetch(f"{BASE}/robots.txt")
    body = raw.decode("utf-8", "replace")
    tech["robots_status"] = st
    tech["robots_len"] = len(body.strip())
    tech["robots_body"] = body[:2000]
    tech["robots_has_sitemap"] = "sitemap:" in body.lower()
except Exception as e:
    tech["robots_error"] = str(e)

for sm in ["/sitemap.xml", "/sitemap_index.xml", "/sitemap.php"]:
    try:
        req = urllib.request.Request(f"{BASE}{sm}", method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
            tech[f"sitemap{sm}"] = r.status
    except Exception as e:
        code = getattr(getattr(e, "code", None), "__str__", lambda: None)()
        tech[f"sitemap{sm}"] = getattr(e, "code", str(e)[:80])

# duplicate titles
titles = [r.get("title") for r in results if r.get("title")]
tech["duplicate_titles"] = [t for t, c in Counter(titles).items() if c > 1]
descs = [r.get("description") for r in results if r.get("description")]
tech["duplicate_descriptions"] = [d for d, c in Counter(descs).items() if c > 1]
h1s = []
for r in results:
    for h in r.get("h1") or []:
        h1s.append(h)
tech["duplicate_h1"] = [h for h, c in Counter(h1s).items() if c > 1]

out = {"tech": tech, "pages": results}
(OUT / "seo_audit.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print("\nTECH", json.dumps(tech, ensure_ascii=False, indent=2)[:2000])
print("Saved", OUT / "seo_audit.json")
