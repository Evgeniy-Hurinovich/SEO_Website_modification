# -*- coding: utf-8 -*-
"""
Weekly SEO/CWV monitor for a2c.by.

Writes metrics/history.jsonl and posts a digest to Bitrix24 (im.message.add)
or Telegram as a fallback.

Usage:
  python scripts/seo_weekly_monitor.py --dry-run --reuse-lh
  python scripts/seo_weekly_monitor.py --post-only --dry-run
  python scripts/seo_weekly_monitor.py --post-only
  python scripts/seo_weekly_monitor.py --bitrix-recent
  python scripts/seo_weekly_monitor.py --bitrix-ping
  python scripts/seo_weekly_monitor.py              # live + LH + history + post

Env (.env in repo root, not committed):
  BITRIX24_WEBHOOK_URL   https://PORTAL/rest/USER/CODE/   (or full …/im.message.add)
  BITRIX24_DIALOG_ID     chat123  |  sg123  |  USER_ID
  TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID   (fallback)
  GSC_CLICKS             optional weekly organic clicks
"""
from __future__ import annotations

import argparse
import json
import os
import re
import ssl
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "metrics" / "history.jsonl"
LH_TMP = ROOT / "_lh_tmp"
URLS = [
    "https://a2c.by/",
    "https://a2c.by/services/dwh/",
    "https://a2c.by/services/bi/",
    "https://a2c.by/contacts/",
]
CTX = ssl.create_default_context()
LH_VERSION = "12.2.1"


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip().strip("'").strip('"')
        if key and key not in os.environ:
            os.environ[key] = val


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "a2c-seo-monitor/1.0"})
    with urllib.request.urlopen(req, context=CTX, timeout=40) as r:
        return r.read().decode("utf-8", "replace")


def http_json(url: str, payload: dict, timeout: int = 30) -> dict:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=timeout) as r:
            raw = r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        try:
            data = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            raise RuntimeError(f"HTTP {e.code}: {raw[:400]}") from e
        err = data.get("error_description") or data.get("error") or raw[:400]
        raise RuntimeError(f"Bitrix REST error: {err}") from e
    try:
        data = json.loads(raw) if raw else {}
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Non-JSON response: {raw[:400]}") from e
    if isinstance(data, dict) and data.get("error"):
        err = data.get("error_description") or data.get("error")
        raise RuntimeError(f"Bitrix REST error: {err}")
    return data if isinstance(data, dict) else {"result": data}


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
                    "title": re.sub(r"\s+", " ", title_m.group(1)).strip()[:90] if title_m else None,
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
        sm = fetch("https://a2c.by/sitemap.xml")
        sitemap_ok = "<sitemapindex" in sm or "<urlset" in sm
    except Exception:
        pass
    ok_pages = [p for p in pages if p.get("ok")]
    return {
        "pages": pages,
        "canonical_ok": bool(ok_pages) and all(p.get("canonical") for p in ok_pages),
        "robots_ok": robots_ok,
        "sitemap_ok": sitemap_ok,
    }


def _metric_block(audits: dict, aid: str) -> tuple[str | None, float | None]:
    a = audits.get(aid) or {}
    display = a.get("displayValue")
    if isinstance(display, str):
        display = display.replace("\xa0", " ").strip()
    num = a.get("numericValue")
    try:
        num_f = float(num) if num is not None else None
    except (TypeError, ValueError):
        num_f = None
    return display, num_f


def parse_lighthouse_file(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    audits = data.get("audits") or {}
    cats = data.get("categories") or {}
    lcp_d, lcp_ms = _metric_block(audits, "largest-contentful-paint")
    tbt_d, tbt_ms = _metric_block(audits, "total-blocking-time")
    cls_d, cls_n = _metric_block(audits, "cumulative-layout-shift")
    fcp_d, fcp_ms = _metric_block(audits, "first-contentful-paint")
    return {
        "perf": round((cats.get("performance", {}).get("score") or 0) * 100),
        "seo": round((cats.get("seo", {}).get("score") or 0) * 100),
        "lcp": _fmt_sec(lcp_ms) or lcp_d,
        "lcp_ms": round(lcp_ms) if lcp_ms is not None else None,
        "tbt": _fmt_ms(tbt_ms) or tbt_d,
        "tbt_ms": round(tbt_ms) if tbt_ms is not None else None,
        "cls": cls_d if cls_d is not None else (f"{cls_n:.3f}" if cls_n is not None else None),
        "fcp": _fmt_sec(fcp_ms) or fcp_d,
        "fcp_ms": round(fcp_ms) if fcp_ms is not None else None,
        "lh_version": data.get("lighthouseVersion"),
        "fetch_time": data.get("fetchTime"),
    }


def _fmt_sec(ms: float | None) -> str | None:
    if ms is None:
        return None
    return f"{ms / 1000:.1f} с"


def _fmt_ms(ms: float | None) -> str | None:
    if ms is None:
        return None
    return f"{int(round(ms))} мс"


def _lh_candidates(form_factor: str) -> list[Path]:
    return [
        ROOT / "metrics" / f"_lh_{form_factor}_latest.json",
        ROOT / f"_lh_seo_{form_factor}.json",
        ROOT / f"_lh_{form_factor}.json",
    ]


def find_lh_json(form_factor: str) -> Path | None:
    for p in _lh_candidates(form_factor):
        if p.is_file() and p.stat().st_size > 200:
            return p
    return None


def run_lighthouse(form_factor: str) -> dict:
    out = ROOT / "metrics" / f"_lh_{form_factor}_latest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    LH_TMP.mkdir(parents=True, exist_ok=True)
    npx = "npx.cmd" if sys.platform == "win32" else "npx"
    cmd = [
        npx,
        "--yes",
        f"lighthouse@{LH_VERSION}",
        "https://a2c.by/",
        "--only-categories=performance,seo",
        f"--form-factor={form_factor}",
        "--output=json",
        f"--output-path={out}",
        "--chrome-flags=--headless --no-sandbox --disable-gpu",
        "--quiet",
    ]
    if form_factor == "desktop":
        cmd.append("--preset=desktop")
    env = os.environ.copy()
    env["TEMP"] = env["TMP"] = str(LH_TMP)
    err = None
    try:
        subprocess.run(cmd, check=True, cwd=str(ROOT), timeout=360, env=env)
    except Exception as e:
        err = str(e)
        # Windows EPERM on temp cleanup: JSON is often already written.
        if not (out.is_file() and out.stat().st_size > 200):
            return {"error": err}
    try:
        parsed = parse_lighthouse_file(out)
        if err:
            parsed["warning"] = err
        return parsed
    except Exception as e:
        return {"error": err or str(e)}


def load_history() -> list[dict]:
    if not HISTORY.exists():
        return []
    rows = []
    for ln in HISTORY.read_text(encoding="utf-8").splitlines():
        if ln.strip():
            rows.append(json.loads(ln))
    return rows


def append_history(row: dict) -> None:
    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    with HISTORY.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def date_ru(iso: str | None) -> str:
    if not iso:
        return "—"
    try:
        y, m, d = iso[:10].split("-")
        return f"{d}.{m}.{y}"
    except ValueError:
        return iso[:10]


def _dig(o, path):
    for k in path:
        if not isinstance(o, dict) or k not in o:
            return None
        o = o[k]
    return o


def delta_score(cur, prev, path: list[str]) -> str:
    a, b = _dig(cur, path), _dig(prev or {}, path)
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        return ""
    d = a - b
    if d == 0:
        return " (→0)"
    arrow = "▲" if d > 0 else "▼"
    return f" ({arrow}{d:+g})"


def delta_ms(cur, prev, path: list[str], kind: str) -> str:
    a, b = _dig(cur, path), _dig(prev or {}, path)
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        return ""
    d = a - b
    if abs(d) < 1:
        return " (→0)"
    arrow = "▲" if d > 0 else "▼"
    if kind == "s":
        return f" ({arrow}{d / 1000:+.1f} с)"
    return f" ({arrow}{d:+.0f} мс)"


def _canonical_line(live: dict) -> str:
    mark = "✓" if live.get("canonical_ok") else "✗"
    missing = []
    for p in live.get("pages") or []:
        if p.get("ok") and not p.get("canonical"):
            path = urllib.parse.urlparse(p.get("url") or "").path or "/"
            missing.append(path)
    extra = f" ({', '.join(missing)})" if missing else ""
    return f"canonical {mark}{extra}"


def format_digest(row: dict, prev: dict | None) -> str:
    m = row.get("mobile") or {}
    d = row.get("desktop") or {}
    live = row.get("live") or {}
    gsc = row.get("gsc") or {}
    field = row.get("field") or {}
    metrica = row.get("metrica") or {}

    gsc_clicks = gsc.get("clicks")
    gsc_line = (
        f"[GSC] клики за неделю: {gsc_clicks}{delta_score(row, prev, ['gsc', 'clicks'])}"
        if gsc_clicks is not None
        else "[GSC] клики за неделю: — (нет данных)"
    )
    field_line = (
        f"[field] CrUX LCP: {field.get('lcp')}"
        if field.get("lcp")
        else "[field] CrUX/PSI: — (лаг 2–4 нед., не в этом замере)"
    )
    org = metrica.get("organic_goals")
    biz_line = (
        f"[biz] Метрика, цели organic: {org}"
        if org is not None
        else "[biz] Метрика, цели organic: — (слот F3)"
    )

    m_err = m.get("error")
    d_err = d.get("error")
    mobile_line = (
        f"[lab] Speed mobile: ошибка LH — {m_err}"
        if m_err and m.get("perf") is None
        else (
            f"[lab] Speed mobile: Perf {m.get('perf')}{delta_score(row, prev, ['mobile', 'perf'])} · "
            f"LCP {m.get('lcp')}{delta_ms(row, prev, ['mobile', 'lcp_ms'], 's')} · "
            f"TBT {m.get('tbt')}{delta_ms(row, prev, ['mobile', 'tbt_ms'], 'ms')} · "
            f"SEO LH {m.get('seo')}"
        )
    )
    desktop_line = (
        f"[lab] Speed desktop: ошибка LH — {d_err}"
        if d_err and d.get("perf") is None
        else (
            f"[lab] Speed desktop: Perf {d.get('perf')}{delta_score(row, prev, ['desktop', 'perf'])} · "
            f"LCP {d.get('lcp')}{delta_ms(row, prev, ['desktop', 'lcp_ms'], 's')} · "
            f"TBT {d.get('tbt')}{delta_ms(row, prev, ['desktop', 'tbt_ms'], 'ms')}"
        )
    )

    lines = [
        f"a2c.by · weekly · {date_ru(row.get('date'))}",
        "",
        mobile_line,
        desktop_line,
        f"[live] {_canonical_line(live)} · "
        f"robots {'✓' if live.get('robots_ok') else '✗'} · "
        f"sitemap {'✓' if live.get('sitemap_ok') else '✗'}",
        "",
        gsc_line,
        field_line,
        biz_line,
        "",
        "▲▼ к прошлой неделе. lab — часы после деплоя; GSC — лаг 2–8 нед.; field — 2–4 нед.",
    ]
    return "\n".join(lines)


def redact_hook(url: str) -> str:
    return re.sub(r"(/rest/\d+/)[^/]+", r"\1***", url)


def bitrix_base() -> str:
    return (os.environ.get("BITRIX24_WEBHOOK_URL") or os.environ.get("WEBHOOK_URL") or "").strip()


def bitrix_method_url(method: str) -> str:
    base = bitrix_base().split("?")[0].rstrip("/")
    if not base:
        raise RuntimeError("BITRIX24_WEBHOOK_URL is empty")
    low = base.lower()
    suffix = method.lower()
    if low.endswith("/" + suffix) or low.endswith("/" + suffix + ".json"):
        return base if low.endswith(".json") else base + ".json"
    # URL already points at some other method — strip last segment if it looks like a REST method
    parts = base.split("/")
    if parts and "." in parts[-1] and not parts[-1].startswith("bitrix"):
        # e.g. .../CODE/im.message.add.json → replace method
        parts[-1] = f"{method}.json"
        return "/".join(parts)
    return f"{base}/{method}.json"


def post_bitrix24(text: str) -> str:
    dialog = (os.environ.get("BITRIX24_DIALOG_ID") or os.environ.get("BITRIX24_CHAT_ID") or "").strip()
    if not dialog:
        raise RuntimeError("BITRIX24_DIALOG_ID is empty (chat123 / sg123 / user id)")
    url = bitrix_method_url("im.message.add")
    data = http_json(
        url,
        {
            "DIALOG_ID": dialog,
            "MESSAGE": text,
            "SYSTEM": "N",
            "URL_PREVIEW": "N",
        },
    )
    msg_id = data.get("result")
    return f"im.message.add ok id={msg_id} via {redact_hook(url)} → {dialog}"


def post_telegram(text: str) -> str:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat = os.environ.get("TELEGRAM_CHAT_ID")
    if not (token and chat):
        raise RuntimeError("TELEGRAM_* not set")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    http_json(url, {"chat_id": chat, "text": text})
    return f"telegram ok chat={chat}"


def post_digest(text: str) -> str:
    if bitrix_base() and (
        os.environ.get("BITRIX24_DIALOG_ID") or os.environ.get("BITRIX24_CHAT_ID")
    ):
        return post_bitrix24(text)
    if os.environ.get("TELEGRAM_BOT_TOKEN") and os.environ.get("TELEGRAM_CHAT_ID"):
        return post_telegram(text)
    raise RuntimeError(
        "Нет канала доставки: задайте BITRIX24_WEBHOOK_URL + BITRIX24_DIALOG_ID "
        "(или TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID)"
    )


def bitrix_recent() -> None:
    url = bitrix_method_url("im.recent.list")
    data = http_json(url, {})
    items = data.get("result") or []
    if isinstance(items, dict):
        items = items.get("items") or items.get("recent") or []
    print(f"im.recent.list via {redact_hook(url)} · {len(items)} шт.")
    for it in items[:30]:
        if not isinstance(it, dict):
            continue
        chat = it.get("chat") or {}
        user = it.get("user") or {}
        dialog = it.get("id") or it.get("dialog_id") or chat.get("dialog_id")
        title = (
            chat.get("name")
            or user.get("name")
            or it.get("title")
            or ""
        )
        kind = it.get("type") or chat.get("type") or ""
        print(f"  DIALOG_ID={dialog}\t{kind}\t{title}")


def seed_baseline() -> int:
    """Write 11.08 + 20.08 lab rows if those dates are missing."""
    existing = { (r.get("date") or "")[:10] for r in load_history() }
    added = 0
    seed_rows = [
        {
            "date": "2026-08-11T12:00:00+00:00",
            "source": "manual-progress",
            "live": {"canonical_ok": False, "robots_ok": True, "sitemap_ok": True, "pages": []},
            "mobile": {
                "perf": 58,
                "seo": None,
                "lcp": "4.7 с",
                "lcp_ms": 4700,
                "tbt": "940 мс",
                "tbt_ms": 940,
                "cls": "0",
                "fcp": "2.3 с",
            },
            "desktop": None,
            "gsc": {"clicks": None},
            "field": {},
            "metrica": {},
        },
        {
            "date": "2026-08-20T11:06:00+00:00",
            "source": "lighthouse-12.2.1",
            "live": {
                "canonical_ok": False,
                "robots_ok": True,
                "sitemap_ok": True,
                "pages": [
                    {"url": u, "ok": True, "canonical": False} for u in URLS
                ],
            },
            "mobile": {
                "perf": 62,
                "seo": 100,
                "lcp": "5.7 с",
                "lcp_ms": 5745,
                "tbt": "550 мс",
                "tbt_ms": 550,
                "cls": "0",
                "fcp": "2.3 с",
                "lh_version": "12.2.1",
                "fetch_time": "2026-08-20T11:05:57.244Z",
            },
            "desktop": {
                "perf": 97,
                "seo": 100,
                "lcp": "1.1 с",
                "lcp_ms": 1055,
                "tbt": "70 мс",
                "tbt_ms": 66,
                "cls": "0.015",
                "fcp": "0.5 с",
                "lh_version": "12.2.1",
                "fetch_time": "2026-08-20T11:06:18.812Z",
            },
            "gsc": {"clicks": None},
            "field": {},
            "metrica": {},
        },
    ]
    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    for row in seed_rows:
        day = row["date"][:10]
        if day in existing:
            print(f"seed skip {day} (already in history)")
            continue
        append_history(row)
        existing.add(day)
        added += 1
        print(f"seed wrote {day}")
    return added


def apply_gsc_clicks(row: dict, clicks: int | None) -> None:
    if clicks is None:
        env_c = os.environ.get("GSC_CLICKS")
        if env_c and env_c.strip():
            try:
                clicks = int(env_c.strip())
            except ValueError:
                clicks = None
    if clicks is not None:
        row.setdefault("gsc", {})["clicks"] = clicks


def main() -> int:
    _configure_stdio()
    load_dotenv(ROOT / ".env")
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-lighthouse", action="store_true")
    ap.add_argument("--reuse-lh", action="store_true", help="Parse existing LH JSON, do not run Chrome")
    ap.add_argument("--dry-run", action="store_true", help="Print digest, do not write history or post")
    ap.add_argument("--post-only", action="store_true", help="Post last history row (no new probe/LH)")
    ap.add_argument("--no-post", action="store_true", help="Write history, skip webhook")
    ap.add_argument("--seed", action="store_true", help="Insert 11.08 + 20.08 baseline rows")
    ap.add_argument("--bitrix-recent", action="store_true", help="List recent Bitrix dialogs")
    ap.add_argument("--bitrix-ping", action="store_true", help="Send a short test message")
    ap.add_argument("--gsc-clicks", type=int, default=None)
    args = ap.parse_args()

    if args.seed:
        seed_baseline()
        if not (args.post_only or args.bitrix_ping or args.bitrix_recent):
            hist = load_history()
            if hist:
                prev = hist[-2] if len(hist) > 1 else None
                print(format_digest(hist[-1], prev))
            return 0

    if args.bitrix_recent:
        try:
            bitrix_recent()
        except Exception as e:
            print(f"bitrix-recent failed: {e}", file=sys.stderr)
            return 1
        return 0

    if args.bitrix_ping:
        text = (
            f"a2c.by · test · {datetime.now(timezone.utc).strftime('%d.%m.%Y %H:%M')} UTC\n"
            "[lab] SEO weekly monitor: канал Bitrix24 работает."
        )
        if args.dry_run:
            print(text)
            print("(dry-run, not posted)")
            return 0
        try:
            print(post_digest(text))
        except Exception as e:
            print(f"webhook failed: {e}", file=sys.stderr)
            return 1
        return 0

    if args.post_only:
        hist = load_history()
        if not hist:
            print("history.jsonl empty — run --seed first", file=sys.stderr)
            return 1
        row, prev = hist[-1], hist[-2] if len(hist) > 1 else None
        apply_gsc_clicks(row, args.gsc_clicks)
        digest = format_digest(row, prev)
        print(digest)
        if args.dry_run:
            print("\n(dry-run, not posted)")
            return 0
        try:
            print(post_digest(digest))
        except Exception as e:
            print(f"webhook failed: {e}", file=sys.stderr)
            return 1
        return 0

    hist = load_history()
    prev = hist[-1] if hist else None
    row = {
        "date": datetime.now(timezone.utc).isoformat(),
        "source": f"lighthouse-{LH_VERSION}",
        "live": probe_live(),
        "mobile": None,
        "desktop": None,
        "gsc": {"clicks": None},
        "field": {},
        "metrica": {},
    }
    apply_gsc_clicks(row, args.gsc_clicks)

    if not args.no_lighthouse:
        for form in ("mobile", "desktop"):
            if args.reuse_lh:
                found = find_lh_json(form)
                print(f"reuse LH {form}: {found or 'NOT FOUND'}")
                row[form] = parse_lighthouse_file(found) if found else {"error": "no LH json"}
            else:
                print(f"Lighthouse {form}...")
                row[form] = run_lighthouse(form)

    if not args.dry_run:
        append_history(row)

    digest = format_digest(row, prev)
    print(digest)
    if args.dry_run:
        print("\n(dry-run: history not written, not posted)")
        return 0
    if args.no_post:
        print("history written, post skipped (--no-post)")
        return 0
    try:
        print(post_digest(digest))
    except Exception as e:
        print(f"webhook failed: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
