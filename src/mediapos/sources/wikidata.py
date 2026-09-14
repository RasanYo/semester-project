"""Wikidata: entity reconciliation, and the event pools for blocks B, C and E.

Reconciliation is the core of the project, not a detail: SVP, UDC and Swiss
People's Party must resolve to one node or the graph fragments. Three access
paths are used, each for what it is good at:

* SPARQL       -- generate candidate sets (actors in office, events in a window)
* wbgetentities -- fetch attributes in batches of 50
* reconcile    -- match a surface string to a QID, with a confidence verdict

Operational facts learned the hard way and encoded here: an empty User-Agent is
HTTP 403; an uncompressed SPARQL response is silently truncated at 128 KiB;
the endpoint times out around 60 s and occasionally 502s, so calls retry.
"""

from __future__ import annotations

import json
import time
from typing import Any

import requests

from ..manifest import USER_AGENT

SPARQL_URL = "https://query.wikidata.org/sparql"
API_URL = "https://www.wikidata.org/w/api.php"
RECONCILE_URL = "https://wikidata.reconci.link/en/api"

_HEADERS = {"User-Agent": USER_AGENT, "Accept-Encoding": "gzip"}


def sparql(query: str, *, retries: int = 3, timeout: int = 90) -> list[dict[str, Any]]:
    """Run a SPARQL query, returning simplified bindings.

    `Accept-Encoding: gzip` is not optional: without it the endpoint truncates
    the body at exactly 131072 bytes, mid-JSON, and the parse failure looks
    like a syntax error rather than a size limit.
    """
    last: Exception | None = None
    for attempt in range(retries):
        try:
            resp = requests.post(
                SPARQL_URL,
                data={"query": query},
                headers={**_HEADERS, "Accept": "application/sparql-results+json"},
                timeout=timeout,
            )
            if resp.status_code in (429, 502, 503, 504):
                raise requests.HTTPError(f"HTTP {resp.status_code}")
            resp.raise_for_status()
            rows = resp.json()["results"]["bindings"]
            return [{k: v["value"] for k, v in row.items()} for row in rows]
        except (requests.RequestException, ValueError, KeyError) as exc:
            # 429/502/503/504 and the occasional truncated body are transient.
            last = exc
            time.sleep(2 ** attempt)
    raise RuntimeError(f"SPARQL failed after {retries} attempts: {last}")


def qid(uri: str) -> str:
    return uri.rsplit("/", 1)[-1]


def get_entities(
    qids: list[str], *, props: str = "labels|aliases|claims"
) -> dict[str, Any]:
    """Fetch full entities, 50 at a time (a hard API cap: 51 is `toomanyvalues`)."""
    out: dict[str, Any] = {}
    for i in range(0, len(qids), 50):
        batch = qids[i : i + 50]
        resp = requests.get(
            API_URL,
            params={
                "action": "wbgetentities",
                "ids": "|".join(batch),
                "props": props,
                "format": "json",
            },
            headers=_HEADERS,
            timeout=60,
        )
        resp.raise_for_status()
        out.update(resp.json().get("entities", {}))
        time.sleep(0.2)
    return out


def reconcile(
    queries: dict[str, dict[str, Any]], *, retries: int = 3
) -> dict[str, list[dict[str, Any]]]:
    """Batch-match surface strings to QIDs via the OpenRefine service.

    The decisive property of this endpoint is that it returns `match: true`
    only when it is confident. "Alfred Heer" alone returns two items at score
    100 with `match: false`; the same query constrained by P102 resolves. We
    never auto-accept a `match: false` -- it goes to review instead.
    """
    last: Exception | None = None
    for attempt in range(retries):
        try:
            resp = requests.post(
                RECONCILE_URL,
                data={"queries": json.dumps(queries)},
                headers=_HEADERS,
                timeout=60,
            )
            resp.raise_for_status()
            payload = resp.json()
            return {k: v.get("result", []) for k, v in payload.items()}
        except (requests.RequestException, ValueError) as exc:
            last = exc
            time.sleep(2 ** attempt)
    raise RuntimeError(f"reconciliation failed after {retries} attempts: {last}")


# ------------------------------------------------------------ event pools ----

_EVENT_POOL = """
SELECT ?item ?l_de ?l_fr ?l_en ?date ?sl
       (GROUP_CONCAT(DISTINCT ?type; separator=" ") AS ?types) WHERE {
  ?item wikibase:sitelinks ?sl .
  FILTER(?sl >= @MIN_SITELINKS@)
  ?item p:P585/psv:P585 ?tv .
  ?tv wikibase:timeValue ?date ; wikibase:timePrecision ?prec .
  FILTER(?prec >= 11)
  FILTER(?date >= "@FROM@T00:00:00Z"^^xsd:dateTime
      && ?date <= "@TO@T23:59:59Z"^^xsd:dateTime)
  @COUNTRY@
  OPTIONAL { ?item wdt:P31 ?type }
  OPTIONAL { ?item rdfs:label ?l_de FILTER(lang(?l_de)="de") }
  OPTIONAL { ?item rdfs:label ?l_fr FILTER(lang(?l_fr)="fr") }
  OPTIONAL { ?item rdfs:label ?l_en FILTER(lang(?l_en)="en") }
}
GROUP BY ?item ?l_de ?l_fr ?l_en ?date ?sl
ORDER BY DESC(?sl)
LIMIT @LIMIT@
"""


def event_pool(
    *,
    date_from: str,
    date_to: str,
    min_sitelinks: int,
    swiss: bool,
    limit: int = 250,
) -> list[dict[str, Any]]:
    """Candidate events, ranked by number of Wikipedia language editions.

    Sitelinks are the notability proxy. They are deliberately *not* a media
    measure: selecting events by how much the Swiss press covered them would
    pre-select on the very quantity this project sets out to measure. Sitelinks
    are global, slow-moving, and caused by something other than a Swiss
    newsroom's attention.

    Day precision is required. An unplanned event happens on a day; a tennis
    tournament spanning a week is stored at year precision, so this single
    filter removes most of the sports noise the raw ranking is full of.
    """
    excluded = " ".join(f"wd:{q}" for q in (CH, *NEIGHBOURS))
    country = (
        "?item wdt:P17 wd:Q39 ."
        if swiss
        else f"FILTER NOT EXISTS {{ ?item wdt:P17 ?c . VALUES ?c {{ {excluded} }} }}"
    )
    query = _EVENT_POOL
    for token, value in (
        ("@MIN_SITELINKS@", str(min_sitelinks)),
        ("@FROM@", date_from),
        ("@TO@", date_to),
        ("@COUNTRY@", country),
        ("@LIMIT@", str(limit)),
    ):
        query = query.replace(token, value)
    rows = sparql(query)
    for r in rows:
        r["qid"] = qid(r["item"])
        r["sitelinks"] = int(r["sl"])
        r["type_qids"] = [qid(t) for t in r.get("types", "").split() if t]
        r["date"] = r["date"][:10]
    return rows


CH = "Q39"
# Switzerland's neighbours. Block E exists to put *identical* actors on both
# sides of the Roestigraben, so a neighbour's national event is disqualifying:
# Romandie follows France and German-speaking Switzerland follows Germany, and
# the asymmetric coverage support is exactly the artefact block E must not have.
NEIGHBOURS = ("Q183", "Q142", "Q38", "Q40", "Q347")  # DE, FR, IT, AT, LI


def expand_types(type_qids: list[str], roots: tuple[str, ...]) -> set[str]:
    """Which of `type_qids` are `roots` or any subclass of them.

    Asking Wikidata's own class hierarchy instead of writing a list of type
    QIDs by hand: the rule stays mechanical, and it keeps working when the
    pool turns up a class nobody anticipated. The VALUES clause is restricted
    to the types actually present, which is what makes the P279* traversal
    cheap enough not to time out.
    """
    if not type_qids:
        return set()
    values_t = " ".join(f"wd:{q}" for q in sorted(set(type_qids)))
    values_root = " ".join(f"wd:{q}" for q in roots)
    rows = sparql(
        "SELECT DISTINCT ?t WHERE {\n"
        f"  VALUES ?t {{ {values_t} }}\n"
        f"  VALUES ?root {{ {values_root} }}\n"
        "  ?t wdt:P279* ?root .\n"
        "}"
    )
    return {qid(r["t"]) for r in rows}


def events_of_type(
    type_qid: str, *, date_from: str, date_to: str, limit: int = 100
) -> list[dict[str, Any]]:
    """Every event of a given class with a day-precision date in the window.

    Used for block B, where the point is a complete enumeration rather than a
    ranking: taking all Federal Council elections removes the last place a
    choice could hide.
    """
    rows = sparql(
        "SELECT ?item ?l_de ?l_fr ?l_en ?date ?sl WHERE {\n"
        f"  ?item wdt:P31/wdt:P279* wd:{type_qid} ;\n"
        "        wikibase:sitelinks ?sl ;\n"
        "        p:P585/psv:P585 ?tv .\n"
        "  ?tv wikibase:timeValue ?date ; wikibase:timePrecision ?prec .\n"
        "  FILTER(?prec >= 11)\n"
        f'  FILTER(?date >= "{date_from}T00:00:00Z"^^xsd:dateTime\n'
        f'      && ?date <= "{date_to}T23:59:59Z"^^xsd:dateTime)\n'
        '  OPTIONAL { ?item rdfs:label ?l_de FILTER(lang(?l_de)="de") }\n'
        '  OPTIONAL { ?item rdfs:label ?l_fr FILTER(lang(?l_fr)="fr") }\n'
        '  OPTIONAL { ?item rdfs:label ?l_en FILTER(lang(?l_en)="en") }\n'
        "}\n"
        f"ORDER BY ?date LIMIT {limit}"
    )
    for r in rows:
        r["qid"] = qid(r["item"])
        r["sitelinks"] = int(r["sl"])
        r["date"] = r["date"][:10]
        r["type_qids"] = [type_qid]
    return rows


def foreign_actor_events(qids: list[str], country: str = "Q39") -> set[str]:
    """Items whose named participants are all foreign.

    The brief excludes "events dominated by foreign actors" outside block E,
    because the validation references (Smartvote, roll-call votes, MARPOR and
    CHES) only cover Swiss actors. P710 (participant) operationalises it: the
    2021 Geneva summit lists Biden and Putin, while the Credit Suisse takeover
    lists Credit Suisse and UBS. An item with no participants at all is not
    excluded -- absence of the property is not evidence of foreignness.
    """
    if not qids:
        return set()
    values = " ".join(f"wd:{q}" for q in sorted(set(qids)))
    rows = sparql(
        "SELECT ?item (COUNT(DISTINCT ?part) AS ?n_part) "
        "(COUNT(DISTINCT ?local) AS ?n_local) WHERE {\n"
        f"  VALUES ?item {{ {values} }}\n"
        "  ?item wdt:P710 ?part .\n"
        "  OPTIONAL { ?part (wdt:P27|wdt:P17) wd:" + country + " .\n"
        "             BIND(?part AS ?local) }\n"
        "}\nGROUP BY ?item"
    )
    return {
        qid(r["item"])
        for r in rows
        if int(r["n_part"]) > 0 and int(r["n_local"]) == 0
    }
