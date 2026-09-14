"""Curia Vista: the parliamentary record behind a ballot object.

Swissvotes gives every in-window object a `gesch_nr`, the parliamentary
business number. That is the bridge from a vote to *named people* -- authors,
co-signatories, spokespersons, committees -- and from a person to a QID,
because Wikidata property P1307 keys exactly on the parlament.ch PersonNumber.
That external-id join is what lets the actor set avoid fuzzy name matching
entirely, which matters: one in five Swiss parliamentarian names has more than
one exact-label Wikidata item.

The service is an OData v1/v2-era endpoint with no surviving documentation
page; `$metadata` is the only specification. Its traps are encoded below.
"""

from __future__ import annotations

import re
from typing import Any

import requests

from ..manifest import USER_AGENT

BASE = "https://ws.parlament.ch/odata.svc"
_TIMEOUT = 90

# Every row exists five times, once per language, and Language is part of the
# primary key -- forgetting the filter inflates every count by exactly 5.
# DE/FR/IT are real translations; EN and RM are fallbacks carrying another
# language's text verbatim, so they must never be used as English or Romansh.
LANGUAGES = ("DE", "FR", "IT")

_MS_DATE = re.compile(r"/Date\((-?\d+)([+-]\d+)?\)/")


def _get(entity: str, **params: str) -> list[dict[str, Any]]:
    resp = requests.get(
        f"{BASE}/{entity}",
        params={"$format": "json", **params},
        # A session cookie is set on every response; it is not required, and a
        # client that stores and replays it across a long harvest may hit
        # Akamai edge behaviour. Send none.
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
        timeout=_TIMEOUT,
    )
    resp.raise_for_status()
    payload = resp.json().get("d", [])
    # The service returns `d` as a bare list for some entity sets and as
    # {"results": [...]} for others; accept both.
    if isinstance(payload, dict):
        return payload.get("results", [])
    return payload


def parse_ms_date(raw: str | None) -> str | None:
    """`/Date(1519662625798)/` -> "2018-02-26". Every date field needs this."""
    if not raw:
        return None
    m = _MS_DATE.match(raw)
    if not m:
        return None
    from datetime import UTC, datetime

    return datetime.fromtimestamp(int(m.group(1)) / 1000, UTC).date().isoformat()


def business_by_short_number(
    short_number: str, language: str = "FR"
) -> dict[str, Any] | None:
    """Look up one parliamentary object by its human-facing number ("19.026")."""
    rows = _get(
        "Business",
        **{
            "$filter": (
                f"BusinessShortNumber eq '{short_number}' "
                f"and Language eq '{language}'"
            ),
            "$top": "1",
        },
    )
    return rows[0] if rows else None


def business_roles(business_id: int, language: str = "FR") -> list[dict[str, Any]]:
    """Authors, co-signatories, spokespersons and opponents of an object.

    `$expand` is unreliable on this navigation -- it returns empty arrays for
    objects that demonstrably have roles -- so the join to people is done
    manually through MemberCouncilNumber, which equals MemberCouncil.PersonNumber.
    """
    return _get(
        "BusinessRole",
        **{
            "$filter": f"BusinessNumber eq {business_id} and Language eq '{language}'",
            "$top": "200",
        },
    )


def member_council_history(
    person_numbers: list[int], language: str = "FR"
) -> list[dict[str, Any]]:
    """Mandate segments, so party and chamber resolve *as of the event date*.

    MemberCouncil holds only the current mandate -- a councillor who changed
    chamber in 2023 looks like they were always in the new one. For anything
    dated inside the window, this is the table to use.
    """
    out: list[dict[str, Any]] = []
    for i in range(0, len(person_numbers), 20):
        batch = person_numbers[i : i + 20]
        clause = " or ".join(f"PersonNumber eq {n}" for n in batch)
        out += _get(
            "MemberCouncilHistory",
            **{"$filter": f"({clause}) and Language eq '{language}'", "$top": "500"},
        )
    return out


def rapporteurs(business_id: int, language: str = "FR") -> list[dict[str, Any]]:
    """The parliamentarians who reported an object to their chamber.

    For a Federal Council object -- which most popular-vote objects are --
    BusinessRole is empty: there are no authors or co-signatories to list. The
    rapporteurs are then the named, visible actors the object actually had, and
    they carry a MemberCouncilNumber, hence a QID.
    """
    return _get(
        "Rapporteur",
        **{
            "$filter": f"BusinessNumber eq {business_id} and Language eq '{language}'",
            "$top": "200",
        },
    )


def actors_for_business(
    short_number: str, language: str = "FR"
) -> list[dict[str, Any]]:
    """Every named actor attached to a parliamentary object, with its role.

    Union of BusinessRole (authors, co-signatories, spokespersons) and
    Rapporteur, because which of the two is populated depends on where the
    object came from.
    """
    business = business_by_short_number(short_number, language)
    if business is None:
        return []
    bid = business["ID"]

    out: list[dict[str, Any]] = []
    for role in business_roles(bid, language):
        if role.get("MemberCouncilNumber"):
            out.append(
                {
                    "person_number": int(role["MemberCouncilNumber"]),
                    "role": role.get("RoleName") or f"role_{role.get('Role')}",
                    "source": "curia:BusinessRole",
                }
            )
    for rap in rapporteurs(bid, language):
        if rap.get("MemberCouncilNumber"):
            out.append(
                {
                    "person_number": int(rap["MemberCouncilNumber"]),
                    "role": "rapporteur",
                    "source": "curia:Rapporteur",
                    "surname": rap.get("LastName"),
                    "first_name": rap.get("FirstName"),
                }
            )

    seen: set[tuple[int, str]] = set()
    unique = []
    for a in out:
        key = (a["person_number"], a["role"])
        if key not in seen:
            seen.add(key)
            unique.append(a)
    return unique
