# -*- coding: utf-8 -*-
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
with open(r"D:\SEO_Website_modification\lighthouse-mobile.json", encoding="utf-8") as f:
    data = json.load(f)
audits = data["audits"]
print("=== ALL AUDITS WITH ISSUES ===")
for k, a in sorted(
    audits.items(),
    key=lambda x: (
        x[1].get("score") is None,
        x[1].get("score") if x[1].get("score") is not None else 99,
    ),
):
    score = a.get("score")
    if score is None or score < 1:
        print(
            score,
            "|",
            a.get("id"),
            "|",
            a.get("title"),
            "|",
            a.get("displayValue", ""),
        )
        details = a.get("details") or {}
        items = details.get("items") or []
        for it in items[:10]:
            url = it.get("url") or it.get("source") or it.get("label") or it.get("entity") or ""
            if isinstance(url, dict):
                url = str(url)[:100]
            wasted = (
                it.get("wastedBytes")
                or it.get("wastedMs")
                or it.get("transferSize")
                or it.get("mainThreadTime")
                or ""
            )
            print("   ", str(url)[:130], "wasted=", wasted)

# network requests summary
nr = audits.get("network-requests", {})
items = (nr.get("details") or {}).get("items") or []
print("\n=== NETWORK REQUESTS", len(items), "===")
total = 0
by_type = {}
for it in items:
    rt = it.get("resourceType") or "?"
    sz = it.get("transferSize") or 0
    total += sz
    by_type[rt] = by_type.get(rt, 0) + sz
print("total transfer", round(total / 1024, 1), "KB")
for rt, sz in sorted(by_type.items(), key=lambda x: -x[1]):
    print(rt, round(sz / 1024, 1), "KB")
print("\nTop transfer:")
for it in sorted(items, key=lambda x: -(x.get("transferSize") or 0))[:20]:
    print(
        round((it.get("transferSize") or 0) / 1024, 1),
        "KB",
        it.get("resourceType"),
        (it.get("url") or "")[:120],
    )
