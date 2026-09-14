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


def participant_actors(qids: list[str]) -> dict[str, list[dict[str, Any]]]:
    """Named participants (P710) of Wikidata events, for blocks C and E.

    These arrive already reconciled -- the event item points at entity items,
    so there is no surface string to match and no chance of a homonym. That is
    exactly why blocks C and E are the cheap part and block A is not.
    """
    if not qids:
        return {}
    values = " ".join(f"wd:{q}" for q in sorted(set(qids)))
    rows = wd.sparql(
        "SELECT ?item ?part ?l_de ?l_fr ?l_en WHERE {\n"
        f"  VALUES ?item {{ {values} }}\n"
        "  ?item wdt:P710 ?part .\n"
        '  OPTIONAL { ?part rdfs:label ?l_de FILTER(lang(?l_de)="de") }\n'
        '  OPTIONAL { ?part rdfs:label ?l_fr FILTER(lang(?l_fr)="fr") }\n'
        '  OPTIONAL { ?part rdfs:label ?l_en FILTER(lang(?l_en)="en") }\n'
        "}"
    )
    out: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        event_q, part_q = wd.qid(r["item"]), wd.qid(r["part"])
        for lang in ("de", "fr"):
            label = r.get(f"l_{lang}") or r.get("l_en")
            out[event_q].append(
                {
                    "qid": part_q,
                    "label": label,
                    "role": "participant",
                    "lang": lang,
                    "surface_form": label,
                    "source": "wikidata:P710",
                    "source_key": "P710",
                    "match_status": "matched",
                }
            )
    return dict(out)
