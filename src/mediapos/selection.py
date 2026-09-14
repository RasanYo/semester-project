"""The mechanical selection rule.

No hand-picking anywhere. Given the same downloaded files, this module returns
the same events -- that is the contract, and `selection_trace` exists so the
report can show the rule as applied rather than merely assert it.
"""

from __future__ import annotations

import statistics as st
from typing import Any

from .config import (
    BLOCK_A_MIN_MIGRATION_EU,
    BLOCK_A_PER_CELL,
)

CELLS = (("HIGH", "HIGH"), ("HIGH", "LOW"), ("LOW", "HIGH"), ("LOW", "LOW"))


def _rank_key(row: dict[str, Any]) -> tuple[float, int]:
    """Within a cell: most-covered first, ties broken by ballot number.

    Salience is the fog Abstimmungsmonitor count of editorial items in the 12
    weeks before the vote -- an external measure, not one of ours. An object
    nobody covered yields no articles, hence no graph; so among equally
    stratified objects we take the ones there is something to measure.
    """
    return (-row["_salience"], int(float(row["_anr"])))


def block_a(
    scorable: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Eight federal popular votes on a 2x2 grid, two per cell.

    The grid is cut at the median of each axis over the candidate pool, so the
    cells are defined by the data rather than by a threshold we chose.
    """
    med_pol = st.median(r["_pol"] for r in scorable)
    med_gap = st.median(abs(r["_gap"]) for r in scorable)

    cells: dict[tuple[str, str], list[dict[str, Any]]] = {c: [] for c in CELLS}
    for r in scorable:
        key = (
            "HIGH" if r["_pol"] > med_pol else "LOW",
            "HIGH" if abs(r["_gap"]) > med_gap else "LOW",
        )
        cells[key].append(r)
    for bucket in cells.values():
        bucket.sort(key=_rank_key)

    picked: list[dict[str, Any]] = []
    repairs: list[dict[str, Any]] = []
    for cell in CELLS:
        bucket = cells[cell]
        take = bucket[:BLOCK_A_PER_CELL]

        # Constraint: at least two objects on migration / asylum / EU. If a cell
        # contributes none and the quota is still unmet, the lowest-ranked slot
        # in that cell goes to the cell's highest-ranked migration/EU object.
        # Deterministic, and recorded so it is visible rather than silent.
        n_so_far = sum(1 for p in picked if p["_is_migration_eu"])
        unmet = n_so_far < BLOCK_A_MIN_MIGRATION_EU
        if unmet and not any(r["_is_migration_eu"] for r in take):
            promoted = next((r for r in bucket if r["_is_migration_eu"]), None)
            if promoted is not None:
                dropped = take[-1]
                take = take[: BLOCK_A_PER_CELL - 1] + [promoted]
                repairs.append(
                    {
                        "cell": f"pol={cell[0]}/rg={cell[1]}",
                        "promoted": promoted["_anr"],
                        "displaced": dropped["_anr"],
                        "reason": "migration/asylum/EU quota",
                    }
                )

        for r in take:
            r["_cell"] = f"pol={cell[0]}/rg={cell[1]}"
            r["_block"] = "A"
        picked += take

    trace = {
        "pool_size": len(scorable),
        "median_polarization": round(med_pol, 6),
        "median_abs_roestigraben": round(med_gap, 6),
        "cell_sizes": {f"pol={c[0]}/rg={c[1]}": len(cells[c]) for c in CELLS},
        "within_cell_rule": "highest fog media salience (mediares-tot), ties by anr",
        "per_cell": BLOCK_A_PER_CELL,
        "migration_eu_selected": sum(1 for r in picked if r["_is_migration_eu"]),
        "constraint_repairs": repairs,
    }
    return picked, trace


def block_d(
    scorable: list[dict[str, Any]], already_picked: list[dict[str, Any]]
) -> tuple[dict[str, Any], dict[str, Any]]:
    """The consensual object: the negative control.

    The object on which the party system was least divided and the language
    regions least apart. If outlets separate here, the method is measuring
    noise -- every other result depends on this one coming back flat.
    """
    taken = {r["_anr"] for r in already_picked}
    pool = [r for r in scorable if r["_anr"] not in taken]
    ranked = sorted(
        pool, key=lambda r: (r["_pol"], abs(r["_gap"]), int(float(r["_anr"])))
    )

    chosen = ranked[0]
    chosen["_block"] = "D"
    chosen["_cell"] = "consensual"
    trace = {
        "rule": "minimise polarization, then |Roestigraben|, then anr",
        "chosen": chosen["_anr"],
        "polarization": round(chosen["_pol"], 6),
        "roestigraben": round(chosen["_gap"], 6),
        "runners_up": [
            {"anr": r["_anr"], "polarization": round(r["_pol"], 6)} for r in ranked[1:4]
        ],
    }
    return chosen, trace


# ------------------------------------------------ blocks B, C, E (Wikidata) ----


def _pool_excluding(
    pool: list[dict[str, Any]], excluded_types: set[str]
) -> list[dict[str, Any]]:
    """Drop items whose every type is excluded, keep the ranking by sitelinks.

    An item is dropped only if *all* its P31 values are excluded. A takeover
    that is also tagged as some sport-adjacent class should survive on the
    strength of the type that matters.
    """
    kept = []
    for r in pool:
        types = r.get("type_qids") or []
        if types and all(t in excluded_types for t in types):
            continue
        kept.append(r)
    return sorted(kept, key=lambda r: (-r["sitelinks"], r["qid"]))


def block_b(
    elections: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Every Federal Council election in the window -- no ranking, no cut.

    The block exists as the easy reference case: the electors are the two
    chambers, the candidates are few and named, so a linking error is visible
    rather than buried. Taking the complete enumeration instead of a top-N
    removes the last place a choice could hide.
    """
    chosen = sorted(elections, key=lambda r: r["date"])
    for r in chosen:
        r["_block"] = "B"
        r["_cell"] = "federal council election"
    return chosen, {
        "rule": "every item of type Q1006573 (Swiss Federal Council election) "
                "with a day-precision date in the window",
        "n": len(chosen),
        "dates": [r["date"] for r in chosen],
    }


def block_c(
    pool: list[dict[str, Any]],
    excluded_types: set[str],
    excluded_qids: set[str],
    n: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Swiss events not carried by the institutional calendar.

    NOT "unplanned" in the strict sense: Wikidata knows only two genuinely
    unplanned Swiss events over the whole seven-year window, so the criterion
    is relaxed one notch and said out loud. The women's strike was announced
    months ahead; what it shares with the other two is that no institution put
    it on the calendar.
    """
    ranked = [
        r for r in _pool_excluding(pool, excluded_types)
        if r["qid"] not in excluded_qids
    ]
    chosen = ranked[:n]
    for r in chosen:
        r["_block"] = "C"
        r["_cell"] = "non-institutional"
    return chosen, {
        "rule": "Swiss events (P17=Q39), day-precision date in window, "
                "sport/entertainment and votes/elections excluded by class "
                "hierarchy, events with only foreign participants excluded "
                "via P710, top-N by sitelinks",
        "pool_after_exclusions": len(ranked),
        "excluded_foreign_actors": sorted(excluded_qids),
        "chosen": [r["qid"] for r in chosen],
        "next_unchosen": [r["qid"] for r in ranked[n : n + 3]],
    }


def block_e(
    pool: list[dict[str, Any]], excluded_types: set[str], n: int
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """International events, diagnostic only, never in the calibration set.

    Their one job is identical actors on both sides of the Roestigraben, so
    that any separation measured here is the language confounder and nothing
    else. Switzerland's neighbours are excluded at query time: a French or
    German national event is covered asymmetrically by the corresponding
    language region, which is exactly the artefact this block must not carry.
    """
    ranked = _pool_excluding(pool, excluded_types)
    chosen = ranked[:n]
    for r in chosen:
        r["_block"] = "E"
        r["_cell"] = "diagnostic"
    return chosen, {
        "rule": "non-Swiss, non-neighbour events, day-precision date in window, "
                "sport/entertainment excluded by class hierarchy, top-N by sitelinks",
        "pool_after_exclusions": len(ranked),
        "chosen": [r["qid"] for r in chosen],
        "next_unchosen": [r["qid"] for r in ranked[n : n + 3]],
    }
