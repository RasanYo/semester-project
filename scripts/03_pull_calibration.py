"""Pull ONE event's coverage, and measure what a full pull would cost.

    .venv/bin/python scripts/03_pull_calibration.py [event_id]

Volume cannot be known before pulling: `estimateResults` is confirmed useless
(it reported 1 for a query that returned 1,953) and `content` is a mandatory
column, so there is no cheap metadata-only counting query. The only honest way
to size the remaining events is to compile one, read `actualResults`, and
extrapolate by window length.

This submits exactly one real query. The archive lands in data/corpus/, which
is gitignored -- the corpus is a cache, the manifest is the fact.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import date

import pandas as pd

from mediapos import config as cfg
from mediapos import queries as q
from mediapos.manifest import sha256_file

CORPUS_DIR = cfg.REPO_ROOT / "data" / "corpus"
RECEIPT = cfg.DATA_OUT / "pull_receipts.json"


def main(event_id: str = "A-631", resume_id: str | None = None) -> int:
    """`resume_id` attaches to a query already submitted, instead of paying for
    a second compile of the same window."""
    events = pd.read_csv(cfg.DATA_OUT / "events.csv").set_index("event_id")
    qrows = pd.read_csv(cfg.DATA_OUT / "queries.csv").set_index("event_id")
    if event_id not in qrows.index:
        print(f"no query for {event_id}")
        return 1
    ev, qrow = events.loc[event_id], qrows.loc[event_id]

    print("=" * 78)
    print(f"CALIBRATION PULL -- {event_id}")
    print("=" * 78)
    print(f"  {ev['date']}  {ev['label_de']}")
    span = (date.fromisoformat(qrow["date_to"])
            - date.fromisoformat(qrow["date_from"])).days
    print(f"  window {qrow['date_from']} -> {qrow['date_to']}  ({span} days)")
    print(f"  {qrow['n_sources']} sources, languages {qrow['languages']}")

    yaml_text = (cfg.REPO_ROOT / qrow["yaml_path"]).read_text(encoding="utf-8")
    ok, message = q.validate(yaml_text, name=f"{qrow['query_name']}-precheck")
    print(f"\n[1/4] validate  {'PASS' if ok else 'FAIL'}: {message[:80]}")
    if not ok:
        return 1

    if resume_id:
        query_id = resume_id
        print(f"[2/4] resume    attaching to query {query_id} (no new submit)")
    else:
        print("[2/4] submit    one real query (this one compiles)")
        query_id = q.submit(
            yaml_text,
            name=qrow["query_name"],
            comment=f"mediapos calibration pull for {event_id}",
        )
        print(f"        id {query_id}")

    print("[3/4] wait      polling with backoff; queue waits of ~50 min have "
          "been seen")
    row = q.wait_for(query_id)
    actual = row.get("actualResults")
    print(f"        finished: actualResults={actual}  "
          f"estimateResults={row.get('estimateResults')} (ignore this)")
    print(f"        addedOn={row.get('addedOn')} startedOn={row.get('startedOn')} "
          f"finishedOn={row.get('finishedOn')}")

    if not row.get("downloadUrl"):
        print("        no downloadUrl -- nothing to fetch")
        return 1

    dest = CORPUS_DIR / f"{event_id}.tsv.xz"
    print(f"[4/4] download  -> {dest.relative_to(cfg.REPO_ROOT)}")
    q.download(row["downloadUrl"], dest)
    compressed = dest.stat().st_size

    # Measure rather than assume: the compression ratio decides disk planning.
    languages, media, uncompressed, n = Counter(), Counter(), 0, 0
    for article in q.read_articles(dest):
        n += 1
        languages[article.get("language")] += 1
        media[article.get("medium_code")] += 1
        uncompressed += len(article.get("content") or "")

    print("\n" + "-" * 78)
    print(f"  articles            {n:,}  (API said {actual})")
    print(f"  compressed          {compressed:,} B  "
          f"({compressed / max(n, 1):,.0f} B/article)")
    print(f"  content chars       {uncompressed:,}  "
          f"(~{uncompressed / max(compressed, 1):.1f}x compression on text alone)")
    print(f"  by language         {dict(languages)}")
    print(f"  outlets present     {len(media)} of {qrow['n_sources']} requested")
    print("\n  top outlets:")
    for code, count in media.most_common(10):
        print(f"    {code:<8} {count:>6,}")
    absent = sorted(set(q.SOURCES) - set(media))
    if absent:
        print(f"  outlets with 0 articles: {absent}")

    days = (date.fromisoformat(qrow["date_to"])
            - date.fromisoformat(qrow["date_from"])).days
    per_day = n / max(days, 1)
    total_days = sum(
        (date.fromisoformat(r["date_to"]) - date.fromisoformat(r["date_from"])).days
        for _, r in pd.read_csv(cfg.DATA_OUT / "queries.csv").iterrows()
    )
    print("\n  EXTRAPOLATION (linear in window days, the only basis we have)")
    print(f"    this window        {days} days, {per_day:,.0f} articles/day")
    print(f"    all 20 events      {total_days} days -> ~{per_day * total_days:,.0f} "
          f"articles")
    mb = per_day * total_days * compressed / max(n, 1) / 1e6
    print(f"    compressed         ~{mb:,.0f} MB")
    print("-" * 78)

    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    receipts = json.loads(RECEIPT.read_text()) if RECEIPT.exists() else {}
    receipts[event_id] = {
        "query_id": query_id,
        "query_name": qrow["query_name"],
        "window": [qrow["date_from"], qrow["date_to"]],
        "n_sources": int(qrow["n_sources"]),
        "actual_results": actual,
        "articles_read": n,
        "compressed_bytes": compressed,
        "sha256": sha256_file(dest),
        "added_on": row.get("addedOn"),
        "finished_on": row.get("finishedOn"),
        "by_language": dict(languages),
        "by_medium": dict(media),
        "local_path": str(dest.relative_to(cfg.REPO_ROOT)),
    }
    RECEIPT.write_text(json.dumps(receipts, indent=2, ensure_ascii=False) + "\n")
    print(f"\n  receipt -> {RECEIPT.relative_to(cfg.REPO_ROOT)} "
          f"(the archive itself stays out of git)")
    return 0


if __name__ == "__main__":
    raise SystemExit(
        main(
            sys.argv[1] if len(sys.argv) > 1 else "A-631",
            sys.argv[2] if len(sys.argv) > 2 else None,
        )
    )
