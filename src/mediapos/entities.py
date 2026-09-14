"""Actors attached to events, reconciled to Wikidata QIDs.

This is the part the project stands or falls on. SVP, UDC and Swiss People's
Party must become one node; CVP before 2021 and Die Mitte after must be one
lineage without being one node; and "Le Centre" must not resolve to a French
newspaper that folded in 1944.

Nothing here hard-codes a QID. Party identity is resolved from a live query on
Wikidata's own data and then gated by the party's life dates, which is what
makes the CVP+BDP merger of 2021-01-01 and the FDP rename of 2009 fall out of
one mechanism instead of two special cases.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from .sources import wikidata as wd

# Swissvotes column -> the abbreviations that column stands for. The columns
# are a fixed, documented set; the QIDs behind them are not written here.
PARTY_COLUMN_ABBREVIATIONS = {
    "p-svp": ("svp", "udc"),
    "p-sps": ("sp", "ps"),
    "p-fdp": ("fdp", "plr"),
    "p-cvp": ("cvp", "pdc"),
    "p-bdp": ("bdp", "pbd"),
    "p-mitte": ("dm", "lc", "adc"),
    "p-gps": ("pes", "gps"),
    "p-glp": ("glp", "pvl"),
    "p-evp": ("evp", "pev"),
    "p-edu": ("edu", "udf"),
}

_PARTY_QUERY = """
SELECT ?item ?l_de ?l_fr ?l_it ?short ?inception ?dissolved ?sl WHERE {
  ?item wdt:P31/wdt:P279* wd:Q7278 ; wdt:P17 wd:Q39 ; wikibase:sitelinks ?sl .
  OPTIONAL { ?item wdt:P1813 ?short }
  OPTIONAL { ?item wdt:P571 ?inception }
  OPTIONAL { ?item wdt:P576 ?dissolved }
  OPTIONAL { ?item rdfs:label ?l_de FILTER(lang(?l_de)="de") }
  OPTIONAL { ?item rdfs:label ?l_fr FILTER(lang(?l_fr)="fr") }
  OPTIONAL { ?item rdfs:label ?l_it FILTER(lang(?l_it)="it") }
}
"""


@dataclass
class Party:
    qid: str
    labels: dict[str, str] = field(default_factory=dict)
    short_names: set[str] = field(default_factory=set)
    inception: date | None = None
    dissolved: date | None = None
    sitelinks: int = 0

    def alive_on(self, when: date) -> bool:
        """Inclusive at both ends: CVP is still CVP on 2020-12-31."""
        if self.inception and when < self.inception:
            return False
        if self.dissolved and when > self.dissolved:
            return False
        return True


def _as_date(raw: str | None) -> date | None:
    if not raw:
        return None
    try:
        return date.fromisoformat(raw[:10].lstrip("+"))
    except ValueError:
        return None


def load_parties() -> dict[str, Party]:
    """Every Swiss political party on Wikidata, keyed by QID."""
    out: dict[str, Party] = {}
    for row in wd.sparql(_PARTY_QUERY):
        q = wd.qid(row["item"])
        p = out.setdefault(q, Party(qid=q))
        for key, lang in (("l_de", "de"), ("l_fr", "fr"), ("l_it", "it")):
            if row.get(key):
                p.labels[lang] = row[key]
        if row.get("short"):
            # "BDP/PBD" and "SP/PS" pack two languages into one value.
            for token in row["short"].replace("-", "").split("/"):
                p.short_names.add(token.strip().lower())
        p.inception = p.inception or _as_date(row.get("inception"))
        p.dissolved = p.dissolved or _as_date(row.get("dissolved"))
        p.sitelinks = max(p.sitelinks, int(row["sl"]))
    return out


def party_for_column(
    column: str, when: date, parties: dict[str, Party]
) -> tuple[Party | None, str]:
    """Resolve a Swissvotes party column to the party as it stood on `when`.

    Returns the party and a status. Candidates are found by short name, then
    gated by their own life dates -- which is what disambiguates `p-fdp`
    (Freisinnig-Demokratische Partei until 2009, FDP.Die Liberalen since) and
    what keeps a pre-2021 CVP mention off the Die Mitte node, using the same
    rule for both rather than an exception for each.
    """
    abbrs = set(PARTY_COLUMN_ABBREVIATIONS.get(column, ()))
    if not abbrs:
        return None, "unknown_column"

    candidates = [p for p in parties.values() if p.short_names & abbrs]
    if not candidates:
        return None, "nil_no_candidate"

    alive = [p for p in candidates if p.alive_on(when)]
    if len(alive) == 1:
        return alive[0], "matched"
    if not alive:
        return None, "nil_none_alive"
    # Still ambiguous after the date gate: take the better-attested item but
    # say so, rather than pretending the ambiguity was resolved.
    alive.sort(key=lambda p: -p.sitelinks)
    return alive[0], "review_ambiguous"


# ------------------------------------------------------------- event actors ----


def party_actors(
    vote: dict[str, Any], parties: dict[str, Party]
) -> list[dict[str, Any]]:
    """One actor row per party that took a side on a ballot object.

    Role records the recommendation itself, so the entities file already
    carries which side each visible actor was on.
    """
    from .sources.swissvotes import _num

    rows: list[dict[str, Any]] = []
    for column in PARTY_COLUMN_ABBREVIATIONS:
        code = _num(vote.get(column))
        if code is None:
            continue  # 9999 = did not exist, "." / "" = unknown
        role = {1.0: "recommends_yes", 2.0: "recommends_no", 5.0: "free_vote"}.get(
            code, f"reco_code_{int(code)}"
        )
        party, status = party_for_column(column, vote["_date"], parties)
        for lang in ("de", "fr"):
            rows.append(
                {
                    "qid": party.qid if party else None,
                    "label": (party.labels.get(lang) if party else None),
                    "role": role,
                    "lang": lang,
                    "surface_form": (party.labels.get(lang) if party else column),
                    "source": "swissvotes:party_recommendation",
                    "source_key": column,
                    "match_status": status,
                }
            )
    return rows


# Wikidata properties that name an actor of an event, and the role each one
# means. P710 covers summits and takeovers; elections carry their cast under
# P726 / P991 / P1346 instead, and an election with no P710 would otherwise
# contribute no actors at all.
EVENT_ACTOR_PROPERTIES = {
    "P710": "participant",
    "P991": "successful_candidate",
    "P1346": "winner",
    "P726": "candidate",
}

# A US presidential election lists 83 candidates. The visible ones in Swiss
# coverage are the handful with international standing, so candidates are
# ranked by sitelinks and capped -- the same notability rule already used to
# rank the events themselves, rather than a second, different criterion.
MAX_CANDIDATES = 10


def event_actors(qids: list[str]) -> dict[str, list[dict[str, Any]]]:
    """Named actors of Wikidata events, for blocks B, C and E.

    These arrive already reconciled: the event item points at entity items, so
    there is no surface string to match and no homonym can fire. That is
    exactly why blocks C and E are the cheap part and block A is not.

    An event with none of these properties yields no actors, and that is
    reported rather than patched -- the Ju-52 crash, the women's strike and the
    2023 Turkey-Syria earthquakes genuinely name no actor on Wikidata.
    """
    if not qids:
        return {}
    values = " ".join(f"wd:{q}" for q in sorted(set(qids)))
    props = " ".join(f"wdt:{p}" for p in EVENT_ACTOR_PROPERTIES)
    rows = wd.sparql(
        "SELECT ?item ?prop ?actor ?sl ?l_de ?l_fr ?l_en WHERE {\n"
        f"  VALUES ?item {{ {values} }}\n"
        f"  VALUES ?p {{ {props} }}\n"
        "  ?item ?p ?actor .\n"
        "  BIND(REPLACE(STR(?p), '.*/', '') AS ?prop)\n"
        "  OPTIONAL { ?actor wikibase:sitelinks ?sl }\n"
        '  OPTIONAL { ?actor rdfs:label ?l_de FILTER(lang(?l_de)="de") }\n'
        '  OPTIONAL { ?actor rdfs:label ?l_fr FILTER(lang(?l_fr)="fr") }\n'
        '  OPTIONAL { ?actor rdfs:label ?l_en FILTER(lang(?l_en)="en") }\n'
        "}"
    )

    grouped: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for r in rows:
        event_q, actor_q = wd.qid(r["item"]), wd.qid(r["actor"])
        role = EVENT_ACTOR_PROPERTIES.get(r.get("prop", ""), "participant")
        entry = grouped[event_q].setdefault(
            actor_q,
            {
                "qid": actor_q,
                "roles": set(),
                "sitelinks": int(r["sl"]) if r.get("sl") else 0,
                "labels": {},
            },
        )
        entry["roles"].add(role)
        for lang in ("de", "fr"):
            if r.get(f"l_{lang}"):
                entry["labels"][lang] = r[f"l_{lang}"]
        entry["labels"].setdefault("en", r.get("l_en", ""))

    out: dict[str, list[dict[str, Any]]] = {}
    for event_q, actors in grouped.items():
        # Everything named by a property other than P726 is kept; bare
        # candidates are ranked by sitelinks and capped.
        named = [a for a in actors.values() if a["roles"] - {"candidate"}]
        cands = [a for a in actors.values() if a["roles"] == {"candidate"}]
        cands.sort(key=lambda a: (-a["sitelinks"], a["qid"]))
        chosen = named + cands[:MAX_CANDIDATES]

        rows_out: list[dict[str, Any]] = []
        for a in chosen:
            role = sorted(a["roles"])[0]
            for lang in ("de", "fr"):
                label = a["labels"].get(lang) or a["labels"].get("en")
                rows_out.append(
                    {
                        "qid": a["qid"],
                        "label": label,
                        "role": role,
                        "lang": lang,
                        "surface_form": label,
                        "source": "wikidata:event_actor",
                        "source_key": role,
                        "match_status": "matched",
                    }
                )
        out[event_q] = rows_out
    return out


# ------------------------------------------------ people, via the id bridge ----


def qids_for_person_numbers(person_numbers: list[int]) -> dict[int, dict[str, Any]]:
    """Map parlament.ch PersonNumbers to QIDs through Wikidata property P1307.

    This is the one place in the pipeline where reconciliation is free of doubt:
    P1307 is an external identifier whose literal value IS the PersonNumber, so
    no string is matched and no homonym can slip through. It matters -- 86 of
    423 in-window parliamentarian names have more than one exact-label Wikidata
    item, including two Swiss National Councillors called Alfred Heer who sat
    for different parties and whom no citizenship or occupation filter
    separates.
    """
    if not person_numbers:
        return {}
    values = " ".join(f'"{n}"' for n in sorted(set(person_numbers)))
    rows = wd.sparql(
        "SELECT ?item ?pn ?l_de ?l_fr ?party ?partyLabelDe WHERE {\n"
        f"  VALUES ?pn {{ {values} }}\n"
        "  ?item wdt:P1307 ?pn .\n"
        "  OPTIONAL { ?item wdt:P102 ?party .\n"
        '            OPTIONAL { ?party rdfs:label ?partyLabelDe\n'
        '                       FILTER(lang(?partyLabelDe)="de") } }\n'
        '  OPTIONAL { ?item rdfs:label ?l_de FILTER(lang(?l_de)="de") }\n'
        '  OPTIONAL { ?item rdfs:label ?l_fr FILTER(lang(?l_fr)="fr") }\n'
        "}"
    )
    out: dict[int, dict[str, Any]] = {}
    for r in rows:
        pn = int(r["pn"])
        entry = out.setdefault(
            pn, {"qid": wd.qid(r["item"]), "labels": {}, "parties": set()}
        )
        for lang in ("de", "fr"):
            if r.get(f"l_{lang}"):
                entry["labels"][lang] = r[f"l_{lang}"]
        if r.get("party"):
            entry["parties"].add(wd.qid(r["party"]))
    return out


def person_actors(
    curia_actors: list[dict[str, Any]], resolved: dict[int, dict[str, Any]]
) -> list[dict[str, Any]]:
    """Turn Curia Vista actor records into entity rows, one per language."""
    rows: list[dict[str, Any]] = []
    for actor in curia_actors:
        pn = actor["person_number"]
        hit = resolved.get(pn)
        for lang in ("de", "fr"):
            label = hit["labels"].get(lang) if hit else None
            rows.append(
                {
                    "qid": hit["qid"] if hit else None,
                    "label": label,
                    "role": actor["role"],
                    "lang": lang,
                    "surface_form": label or actor.get("surname"),
                    "source": actor["source"],
                    "source_key": f"PersonNumber:{pn}",
                    "match_status": "matched" if hit else "nil_no_p1307",
                }
            )
    return rows


def federal_council_actors(when: date, window_days: int = 45) -> list[dict[str, Any]]:
    """The Federal Council around a Federal Council election.

    The visible cast of such an election is the sitting government plus whoever
    joins it, so the actor set is every holder of the office whose mandate
    overlaps a window around the election date.

    The date matters and is easy to get wrong: a newly elected councillor's P39
    start date is the term start in January, not the December election that was
    the media event. The event item carries the real date (P585); the person
    does not.
    """
    lo = (when - __import__("datetime").timedelta(days=window_days)).isoformat()
    hi = (when + __import__("datetime").timedelta(days=window_days)).isoformat()
    rows = wd.sparql(
        "SELECT DISTINCT ?item ?l_de ?l_fr ?start ?end WHERE {\n"
        "  ?item p:P39 ?st .\n"
        "  ?st ps:P39 wd:Q11811941 .\n"
        "  OPTIONAL { ?st pq:P580 ?start }\n"
        "  OPTIONAL { ?st pq:P582 ?end }\n"
        f'  FILTER(BOUND(?start) && ?start <= "{hi}T00:00:00Z"^^xsd:dateTime)\n'
        f'  FILTER(!BOUND(?end) || ?end >= "{lo}T00:00:00Z"^^xsd:dateTime)\n'
        '  OPTIONAL { ?item rdfs:label ?l_de FILTER(lang(?l_de)="de") }\n'
        '  OPTIONAL { ?item rdfs:label ?l_fr FILTER(lang(?l_fr)="fr") }\n'
        "}"
    )
    out: list[dict[str, Any]] = []
    for r in rows:
        for lang in ("de", "fr"):
            label = r.get(f"l_{lang}")
            out.append(
                {
                    "qid": wd.qid(r["item"]),
                    "label": label,
                    "role": "federal_councillor",
                    "lang": lang,
                    "surface_form": label,
                    "source": "wikidata:P39",
                    "source_key": "Q11811941",
                    "match_status": "matched",
                }
            )
    return out
