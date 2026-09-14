"""Swissdox@LiRI query construction and validation.

Not a search API: a corpus ordering API. A query is submitted, the server
compiles for minutes to hours, then a `.tsv.xz` becomes available. Everything
here stops at validation (`test=1`), which checks a query without compiling it
and costs nothing.

Two traps worth stating in code, because neither is in the manual and both
return HTTP 500 rather than a usable error list: `content` is mandatory in
`result.columns`, and `result.maxResults` is mandatory. A third is worse
because it is silent -- an unknown medium code passes validation and simply
removes that outlet from the pull, discovered only after the compile.
"""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path
from typing import Any

import requests
import yaml
from dotenv import load_dotenv

API_BASE = "https://swissdox.linguistik.uzh.ch/api"
SOURCE_LIST_URL = (
    "https://swissdox.linguistik.uzh.ch/manual/auto/swissdox/swissdox_sources.json"
)

# German- and French-language Swiss titles present in the corpus across the
# window. Read from swissdox_sources.json, not from memory -- and validated
# against that file by `check_sources` before any query is submitted, because
# an unknown code passes validation silently.
#
# The French side is not a French-language media space: every fr title here is
# a TX Group / Tamedia Romandy paper except Le Temps and rts.ch. Le Nouvelliste,
# La Liberte, ArcInfo, Le Courrier and Le Quotidien Jurassien are absent from
# the corpus entirely, and there is no news agency at all. Language and
# ownership are therefore collinear by construction; that is a corpus
# limitation to state in the report, not a diagnostic to discover later.
SOURCES_DE = (
    "NZZ", "NZZO", "NZZS", "TA", "NNTA", "TAS", "BZ", "NNBE", "BU", "NNBU",
    "BAZ", "NNBS", "BLI", "BLIO", "SGT", "SGTO", "AZM", "LUZ", "ZWA", "ZWAO",
    "SRF", "WEW", "WOZ",
)
SOURCES_FR = (
    "TPS", "TPSO", "TDG", "NNTDG", "HEU", "NNHEU", "TLMD", "NNTLM", "RTS",
    "ZWAS", "ZWSO",
)
SOURCES = SOURCES_DE + SOURCES_FR

# Every column the API offers. `content` is not optional: without it /query
# returns a bare HTTP 500. There is therefore no cheap metadata-only counting
# query, and every pull carries full article text.
COLUMNS = (
    "id", "pubtime", "medium_code", "medium_name", "rubric", "regional",
    "doctype", "doctype_description", "language", "char_count", "dateline",
    "head", "subhead", "article_link", "content_id", "content",
)

MAX_RESULTS = 1_000_000


def build_query(
    *,
    date_from: date,
    date_to: date,
    sources: tuple[str, ...] = SOURCES,
    languages: tuple[str, ...] = ("de", "fr"),
    content: list[str] | None = None,
) -> str:
    """Build the YAML for one event's coverage window.

    `content` keywords are left off by default. They are case-sensitive, match
    whole words, and apply to body text only -- so a keyword filter trades
    recall for volume in a way that cannot be measured before the pull. One
    query per event keeps each window's keywords separable; the API does accept
    several date ranges in one query, but `content` would then be global to all
    of them.
    """
    query: dict[str, Any] = {
        "sources": list(sources),
        "dates": [{"from": date_from.isoformat(), "to": date_to.isoformat()}],
        "languages": list(languages),
    }
    if content:
        query["content"] = list(content)
    return yaml.safe_dump(
        {
            "query": query,
            "result": {
                "format": "TSV",
                "maxResults": MAX_RESULTS,
                "columns": list(COLUMNS),
            },
            "version": 1.2,
        },
        sort_keys=False,
        allow_unicode=True,
    )


def _credentials() -> dict[str, str]:
    load_dotenv()
    key, secret = os.getenv("SWISSDOX_API_KEY"), os.getenv("SWISSDOX_API_SECRET")
    if not key or not secret:
        raise RuntimeError("SWISSDOX_API_KEY / SWISSDOX_API_SECRET missing from .env")
    # Both headers are required; X-API-Key alone gets you nothing.
    return {"X-API-Key": key, "X-API-Secret": secret}


def validate(yaml_text: str, *, name: str) -> tuple[bool, str]:
    """Submit with `test=1`: validates without compiling, and costs nothing.

    Returns (ok, message). A 406 carries a usable error list; a 500 almost
    always means a required `result.*` key is missing rather than an outage.
    """
    resp = requests.post(
        f"{API_BASE}/query",
        headers=_credentials(),
        data={"query": yaml_text, "name": name, "test": "1"},
        timeout=120,
    )
    if resp.status_code == 200:
        return True, resp.json().get("message", "valid")
    if resp.status_code == 500:
        return False, (
            "HTTP 500 -- a required result.* key is missing "
            "(content? maxResults?)"
        )
    return False, f"HTTP {resp.status_code}: {resp.text[:400]}"


def check_sources(
    source_list_path: Path, codes: tuple[str, ...] = SOURCES
) -> tuple[list[str], list[str]]:
    """Split `codes` into those present in swissdox_sources.json and those not.

    Necessary because an unknown medium code PASSES server-side validation: a
    typo silently drops an outlet from the pull and is only discovered after
    the compile. A code is not a key in that file -- 49 codes appear on several
    rows with different names and periods -- so presence is all we check here.
    """
    import json

    known = {
        entry["code"].strip()
        for entry in json.loads(source_list_path.read_text(encoding="utf-8"))
        if entry.get("code")
    }
    present = [c for c in codes if c in known]
    missing = [c for c in codes if c not in known]
    return present, missing
