# -*- coding: utf-8 -*-
"""
Weekly SEO/CWV monitor for a2c.by.

Writes metrics/history.jsonl and optionally posts a digest to a webhook
(Telegram Bot API or generic JSON webhook / Bitrix24).

Usage (Windows Task Scheduler / cron):
  python scripts/seo_weekly_monitor.py
  python scripts/seo_weekly_monitor.py --no-lighthouse   # only live HTML probe
  python scripts/seo_weekly_monitor.py --dry-run

Env:
  TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
  or WEBHOOK_URL (POST JSON {"text": "..."})
"""
from __future__ import annotations

import argparse
import json
import os
import re
import ssl
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "metrics" / "history.jsonl"
URLS = [
    "https://a2c.by/",
    "https://a2c.by/services/dwh/",
    "https://a2c.by/services/bi/",
    "https://a2c.by/contacts/",
]
CTX = ssl.create_default_context()


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "a2c-seo-monitor/1.0"})
    with urllib.request.urlopen(req, context=CTX, timeout=40) as r:
        return r.read().decode("utf-8", "replace")


def probe_live() -> dict:
    pages = []
    for u in URLS:
        try:
            html = fetch(u)
            title_m = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
            can = bool(re.search(r'rel=["\']canonical["\']', html, re.I))
            pages.append(
                {
                    "url": u,
                    "ok": True,
                    "title": re.sub(r"\s+", " ", title_m.group(1)).strip()[:90]
                    if title_m
                    else None,
                    "canonical": can,
                }
            )
        except Exception as e:
            pages.append({"url": u, "ok": False, "error": str(e)})
    robots_ok = False
    sitemap_ok = False
    try:
        robots_ok = "Sitemap:" in fetch("https://a2c.by/robots.txt")
    except Exception:
        pass
    try:
        sitemap_ok = "<sitemapindex" in fetch("https://a2c.by/sitemap.xml") or "<urlset" in fetch(
            "https://a2c.by/sitemap.xml"
        )
    except Exception:
        pass
    return {
        "pages": pages,
        "canonical_ok": all(p.get("canonical") for p in pages if p.get("ok")),
        "robots_ok": robots_ok,
        "sitemap_ok": sitemap_ok,
    }


def run_lighthouse(form_factor: str) -> dict | None:
    out = ROOT / "metrics" / f"_lh_{form_factor}_latest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "npx",
        "--yes",
        "lighthouse@12.2.1",
        "https://a2c.by/",
        f"--only-categories=performance,seo",
        f"--form-factor={form_factor}",
        "--output=json",
        f"--output-path={out}",
        "--chrome-flags=--headless --no-sandbox --disable-gpu",
        "--quiet",
    ]
    if form_factor == "desktop":
        cmd.append("--preset=desktop")
    try:
        subprocess.run(cmd, check=True, cwd=str(ROOT), timeout=300)
    except Exception as e:
        return {"error": str(e)}
    data = json.loads(out.read_text(encoding="utf-8"))
    audits = data.get("audits", {})
    cats = data.get("categories", {})

    def metric(aid: str) -> str | None:
        return audits.get(aid, {}).get("displayValue")

    return {
        "perf": round((cats.get("performance", {}).get("score") or 0) * 100),
        "seo": round((cats.get("seo", {}).get("score") or 0) * 100),
        "lcp": metric("largest-contentful-paint"),
        "tbt": metric("total-blocking-time"),
        "cls": metric("cumulative-layout-shift"),
        "fcp": metric("first-contentful-paint"),
    }


def load_prev() -> dict | None:
    if not HISTORY.exists():
        return None
    lines = [ln for ln in HISTORY.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if not lines:
        return None
    return json.loads(lines[-1])


def delta(cur, prev, key_path: list[str]) -> str:
    def dig(o, path):
        for k in path:
            if not isinstance(o, dict) or k not in o:
                return None
            o = o[k]
        return o

    a, b = dig(cur, key_path), dig(prev or {}, key_path)
    if a is None or b is None:
        return ""
    try:
        # numeric scores
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            d = a - b
            arrow = "↑" if d > 0 else ("↓" if d < 0 else "→")
            return f" ({arrow}{d:+g})"
    except Exception:
        pass
    return ""


def format_digest(row: dict, prev: dict | None) -> str:
    m = row.get("mobile") or {}
    d = row.get("desktop") or {}
    live = row.get("live") or {}
    lines = [
        f"a2c.by · weekly · {row['date'][:10]}",
        f"Speed mobile: Perf {m.get('perf')}{delta(row, prev, ['mobile','perf'])} · "
        f"LCP {m.get('lcp')} · TBT {m.get('tbt')} · SEO LH {m.get('seo')}",
        f"Speed desktop: Perf {d.get('perf')}{delta(row, prev, ['desktop','perf'])} · "
        f"LCP {d.get('lcp')} · TBT {d.get('tbt')}",
        f"SEO live: canonical {'✓' if live.get('canonical_ok') else '✗'} · "
        f"robots {'✓' if live.get('robots_ok') else '✗'} · "
        f"sitemap {'✓' if live.get('sitemap_ok') else '✗'}",
        "Note: lab metrics change after deploy; GSC positions lag 2–8 weeks.",
    ]
    return "\n".join(lines)


def post_webhook(text: str) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat = os.environ.get("TELEGRAM_CHAT_ID")
    if token and chat:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        body = json.dumps({"chat_id": chat, "text": text}).encode("utf-8")
        req = urllib.request.Request(
            url, data=body, headers={"Content-Type": "application/json"}, method="POST"
        )
        urllib.request.urlopen(req, context=CTX, timeout=30)
        return
    hook = os.environ.get("WEBHOOK_URL")
    if hook:
        body = json.dumps({"text": text}).encode("utf-8")
        req = urllib.request.Request(
            hook, data=body, headers={"Content-Type": "application/json"}, method="POST"
        )
        urllib.request.urlopen(req, context=CTX, timeout=30)
        return
    print("No TELEGRAM_* / WEBHOOK_URL set — skip notify", file=sys.stderr)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-lighthouse", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    prev = load_prev()
    row = {
        "date": datetime.now(timezone.utc).isoformat(),
        "live": probe_live(),
        "mobile": None,
        "desktop": None,
    }
    if not args.no_lighthouse:
        print("Lighthouse mobile...")
        row["mobile"] = run_lighthouse("mobile")
        print("Lighthouse desktop...")
        row["desktop"] = run_lighthouse("desktop")

    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    if not args.dry_run:
        with HISTORY.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    digest = format_digest(row, prev)
    print(digest)
    if not args.dry_run:
        try:
            post_webhook(digest)
        except Exception as e:
            print("webhook failed:", e, file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
