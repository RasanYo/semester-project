"""Pull the coverage window of every event in the repertoire.

    .venv/bin/python scripts/04_pull_all.py [--dry-run]

Archives are keyed by WINDOW, not by event. Two ballot objects voted on the
same day share one window and therefore one set of articles -- downloading it
twice would not just waste 97 MB, it would misrepresent the same articles as
two independent observations.

Resumable: a window whose archive is already on disk with a matching receipt is
skipped, not resubmitted. Interrupt it and rerun; it picks up where it stopped.

The archives land in data/corpus/, which is gitignored. What gets versioned is
the receipt: query id, window, article count, sha256, and the per-outlet and
per-language breakdown. The corpus is a cache; the manifest is the fact.
"""

from __future__ import annotations

import json
import sys
import time
from collections import Counter, defaultdict

import pandas as pd

from mediapos import config as cfg
from mediapos import queries as q
from mediapos.manifest import sha256_file

CORPUS_DIR = cfg.REPO_ROOT / "data" / "corpus"
RECEIPTS = cfg.DATA_OUT / "pull_receipts.json"

# The validation endpoint 500s under rapid submission; assume the compile
# endpoint dislikes a burst just as much.
PACE_SECONDS = 20


def window_key(date_from: str, date_to: str) -> str:
    return f"{date_from}_{date_to}"


def load_receipts() -> dict[str, dict]:
    return json.loads(RECEIPTS.read_text()) if RECEIPTS.exists() else {}


def save_receipts(receipts: dict[str, dict]) -> None:
    RECEIPTS.parent.mkdir(parents=True, exist_ok=True)
    RECEIPTS.write_text(json.dumps(receipts, indent=2, ensure_ascii=False) + "\n")


def measure(path) -> tuple[int, Counter, Counter]:
    """Count articles, languages and outlets by streaming the archive."""
    languages, media, n = Counter(), Counter(), 0
    for article in q.read_articles(path):
        n += 1
        languages[article.get("language")] += 1
        media[article.get("medium_code")] += 1
    return n, languages, media


def main(dry_run: bool = False) -> int:
    qrows = pd.read_csv(cfg.DATA_OUT / "queries.csv")
    events = pd.read_csv(cfg.DATA_OUT / "events.csv").set_index("event_id")

    # Group events by the window they share.
    windows: dict[str, list[str]] = defaultdict(list)
    yaml_for: dict[str, str] = {}
    for row in qrows.itertuples():
        key = window_key(row.date_from, row.date_to)
        windows[key].append(row.event_id)
        yaml_for.setdefault(key, row.yaml_path)

    receipts = load_receipts()
    shared = {k: v for k, v in windows.items() if len(v) > 1}

    print("=" * 78)
    print(f"PULL ALL -- {len(events)} events over {len(windows)} distinct windows")
    print("=" * 78)
    for key, ids in sorted(shared.items()):
        print(f"  shared window {key}: {', '.join(ids)} -> one archive")

    todo = [k for k in sorted(windows) if k not in receipts]
    done = [k for k in sorted(windows) if k in receipts]
    print(f"\n  already pulled {len(done)}, to pull {len(todo)}")
    if dry_run:
        for key in todo:
            print(f"    would pull {key}  ({', '.join(windows[key])})")
        return 0

    failures: list[str] = []
    for i, key in enumerate(todo, start=1):
        ids = windows[key]
        date_from, date_to = key.split("_")
        dest = CORPUS_DIR / f"{key}.tsv.xz"
        label = str(events.loc[ids[0], "label_de"])[:44]
        print(f"\n[{i}/{len(todo)}] {key}  ({', '.join(ids)})")
        print(f"          {label}")

        try:
            if i > 1:
                time.sleep(PACE_SECONDS)
            yaml_text = (cfg.REPO_ROOT / yaml_for[key]).read_text(encoding="utf-8")
            query_id = q.submit(
                yaml_text,
                name=f"mediapos-{key}",
                comment=f"mediapos window {key} for {','.join(ids)}",
            )
            print(f"          submitted {query_id}")
            row = q.wait_for(query_id)
            actual = row.get("actualResults")
            if not row.get("downloadUrl"):
                raise RuntimeError(f"finished with no downloadUrl (actual={actual})")

            q.download(row["downloadUrl"], dest)
            n, languages, media = measure(dest)
            size = dest.stat().st_size
            print(f"          {n:,} articles, {size / 1e6:,.0f} MB, "
                  f"de {languages.get('de', 0):,} / fr {languages.get('fr', 0):,}, "
                  f"{len(media)} outlets")

            receipts[key] = {
                "window": [date_from, date_to],
                "event_ids": ids,
                "query_id": query_id,
                "actual_results": actual,
                "articles_read": n,
                "compressed_bytes": size,
                "sha256": sha256_file(dest),
                "added_on": row.get("addedOn"),
                "finished_on": row.get("finishedOn"),
                "by_language": dict(languages),
                "by_medium": dict(media),
                "local_path": str(dest.relative_to(cfg.REPO_ROOT)),
            }
            save_receipts(receipts)  # after every window, so a crash loses one
        except (RuntimeError, TimeoutError, OSError) as exc:
            print(f"          FAILED: {exc}")
            failures.append(key)

    receipts = load_receipts()
    total_articles = sum(r["articles_read"] for r in receipts.values())
    total_bytes = sum(r["compressed_bytes"] for r in receipts.values())
    covered = {e for r in receipts.values() for e in r["event_ids"]}
    print("\n" + "=" * 78)
    print(f"  windows pulled   {len(receipts)}/{len(windows)}")
    print(f"  events covered   {len(covered)}/{len(events)}")
    print(f"  articles         {total_articles:,}")
    print(f"  on disk          {total_bytes / 1e9:,.2f} GB compressed")
    if failures:
        print(f"  FAILED           {failures} -- rerun to retry just these")
    print("=" * 78)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(dry_run="--dry-run" in sys.argv))
