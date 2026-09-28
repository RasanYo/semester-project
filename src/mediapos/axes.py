"""The two stratification axes.

Both are *computed* from published data. Neither is chosen, and neither is
tuned against any downstream result -- that is the whole point of stratifying
on them rather than on a topic label someone picked.
"""

from __future__ import annotations

import statistics as st
from typing import Any

from .config import CANTONS_DE, CANTONS_FR, MAIN_PARTIES, RECO_NO, RECO_YES
from .sources.swissvotes import _num


def polarization(row: dict[str, Any]) -> float | None:
    """How divided the party system was, weighted by electorate. 0..1.

    Swissvotes publishes `ja-lager` / `nein-lager`: the share of the electorate
    held by the parties recommending Yes / No, using the preceding National
    Council election result. 0 = every party on the same side, 1 = an even
    split. Weighted rather than counted so that a split between two governing
    parties does not score the same as a split between two fringe ones, and so
    the values are continuous (a count over six parties has four possible
    values and ties constantly).
    """
    yes, no = _num(row.get("ja-lager")), _num(row.get("nein-lager"))
    if not yes or not no:
        return None
    return 1 - abs(yes - no) / (yes + no)


def polarization_by_count(row: dict[str, Any]) -> float | None:
    """Robustness variant: unweighted, over the six main parties.

    Reported next to `polarization` so the report can show the stratification
    does not hinge on the electorate weighting.
    """
    codes = [_num(row.get(p)) for p in MAIN_PARTIES]
    sided = [c for c in codes if c in (RECO_YES, RECO_NO)]
    if not sided:
        return None
    share_yes = sum(1 for c in sided if c == RECO_YES) / len(sided)
    return 1 - abs(2 * share_yes - 1)


def roestigraben(row: dict[str, Any]) -> float | None:
    """Signed gap in yes-share: French-speaking minus German-speaking cantons.

    Positive = the French-speaking side backed the object more. Only the
    unambiguous cantons take part (see config.CANTONS_*): the bilingual ones
    would have to be assigned to a side, and that assignment would silently
    become part of the measurement.
    """
    fr = [row["_japroz"][kt] for kt in CANTONS_FR]
    de = [row["_japroz"][kt] for kt in CANTONS_DE]
    if any(v is None for v in fr + de):
        return None
    return st.mean(fr) - st.mean(de)


def annotate(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Attach both axes to every row, in place."""
    for r in rows:
        r["_pol"] = polarization(r)
        r["_pol_count"] = polarization_by_count(r)
        r["_gap"] = roestigraben(r)
    return rows


def scorable(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Rows that carry both axes, i.e. the ones the rule can actually rank."""
    return [r for r in rows if r.get("_pol") is not None and r.get("_gap") is not None]
