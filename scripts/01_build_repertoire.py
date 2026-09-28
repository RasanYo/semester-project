"""Build the bootstrap event repertoire, end to end.

    .venv/bin/python scripts/01_build_repertoire.py

Writes to data/out/ (versioned): events, entities and Swissdox queries, plus a
manifest recording every source with its URL, fetch date, sha256 and the
selection rule as applied. Raw downloads go to data/raw/, which is gitignored:
the corpus is a cache, the manifest is the fact.

Rerunning this on the same published inputs must yield the same events. If it
does not, the work is not done.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import pandas as pd

from mediapos import axes, entities, queries, selection
from mediapos import config as cfg
from mediapos.manifest import Manifest, fetch
from mediapos.sources import curia
from mediapos.sources import swissvotes as sv
from mediapos.sources import wikidata as wd

WINDOW = {
    "date_from": cfg.WINDOW_FROM.isoformat(),
    "date_to": cfg.WINDOW_TO.isoformat(),
}


def _coverage(when: date) -> tuple[date, date]:
    return (
        when - timedelta(days=cfg.COVERAGE_DAYS_BEFORE),
        when + timedelta(days=cfg.COVERAGE_DAYS_AFTER),
    )


def _vote_event(vote: dict[str, Any], block: str) -> dict[str, Any]:
    start, end = _coverage(vote["_date"])
    return {
        "event_id": f"{block}-{vote['_anr']}",
        "block": block,
        "source": "swissvotes",
        "source_id": vote["_anr"],
        "date": vote["_date"].isoformat(),
        "label_de": vote["titel_kurz_d"],
        "label_fr": vote["titel_kurz_f"],
        "title_official_de": vote["titel_off_d"],
        "title_official_fr": vote["titel_off_f"],
        "window_from": start.isoformat(),
        "window_to": end.isoformat(),
        "polarization": round(vote["_pol"], 6),
        "polarization_count": round(vote["_pol_count"], 6),
        "roestigraben": round(vote["_gap"], 6),
        "cell": vote["_cell"],
        "is_migration_eu": vote["_is_migration_eu"],
        "is_control": block == "D",
        "is_diagnostic": False,
        "domains": "|".join(vote["_domains"]),
        "national_yes_pct": vote.get("volkja-proz"),
        "salience_total": vote["_salience"],
        "salience_de": vote.get("mediares-d"),
        "salience_fr": vote.get("mediares-f"),
        "curia_business": vote.get("gesch_nr"),
        "sitelinks": None,
    }


def _wikidata_event(item: dict[str, Any], block: str) -> dict[str, Any]:
    when = date.fromisoformat(item["date"])
    start, end = _coverage(when)
    return {
        "event_id": f"{block}-{item['qid']}",
        "block": block,
        "source": "wikidata",
        "source_id": item["qid"],
        "date": item["date"],
        "label_de": item.get("l_de") or item.get("l_en"),
        "label_fr": item.get("l_fr") or item.get("l_en"),
        "title_official_de": None,
        "title_official_fr": None,
        "window_from": start.isoformat(),
        "window_to": end.isoformat(),
        "polarization": None,
        "polarization_count": None,
        "roestigraben": None,
        "cell": item["_cell"],
        "is_migration_eu": False,
        "is_control": False,
        # Block E never enters the calibration set; the flag travels with the
        # data so nothing downstream has to remember the rule.
        "is_diagnostic": block == "E",
        "domains": "|".join(item.get("type_qids", [])),
        "national_yes_pct": None,
        "salience_total": None,
        "salience_de": None,
        "salience_fr": None,
        "curia_business": None,
        "sitelinks": item.get("sitelinks"),
    }


def main() -> int:
    manifest = Manifest()
    cfg.DATA_OUT.mkdir(parents=True, exist_ok=True)
    events: list[dict[str, Any]] = []
    entity_rows: list[dict[str, Any]] = []

    # ---------------------------------------------------- blocks A and D ----
    print("[1/6] Swissvotes")
    votes = sv.in_window(sv.load(sv.download(manifest)))
    repaired = sv.fill_cantonal_gap(votes, manifest)
    non_media = [v for v in votes if not v["_is_media"]]
    pool = axes.scorable(axes.annotate(non_media))
    print(f"      {len(votes)} in-window, {len(non_media)} after the media-domain "
          f"exclusion, {len(pool)} scorable, {len(repaired)} cantonal repairs")

    block_a, trace_a = selection.block_a(pool)
    control, trace_d = selection.block_d(pool, block_a)
    events += [_vote_event(v, "A") for v in block_a]
    events.append(_vote_event(control, "D"))
    print(f"      block A: {len(block_a)}  block D: 1")

    # -------------------------------------------------- blocks B, C and E ----
    print("[2/6] Wikidata event pools")
    fce = wd.events_of_type(cfg.TYPE_FEDERAL_COUNCIL_ELECTION, **WINDOW)
    block_b, trace_b = selection.block_b(fce)

    pool_ch = wd.event_pool(
        min_sitelinks=cfg.POOL_MIN_SITELINKS_CH, swiss=True, **WINDOW
    )
    pool_intl = wd.event_pool(
        min_sitelinks=cfg.POOL_MIN_SITELINKS_INTL, swiss=False, **WINDOW
    )
    all_types = sorted({t for r in pool_ch + pool_intl for t in r["type_qids"]})
    drop_sport = wd.expand_types(all_types, cfg.TYPE_ROOTS_SPORT_ENTERTAINMENT)
    drop_votes = wd.expand_types(all_types, cfg.TYPE_ROOTS_VOTES_ELECTIONS)
    foreign = wd.foreign_actor_events([r["qid"] for r in pool_ch])

    block_c, trace_c = selection.block_c(
        pool_ch, drop_sport | drop_votes, foreign, cfg.BLOCK_C_N
    )
    block_e, trace_e = selection.block_e(pool_intl, drop_sport, cfg.BLOCK_E_N)
    events += [_wikidata_event(i, "B") for i in block_b]
    events += [_wikidata_event(i, "C") for i in block_c]
    events += [_wikidata_event(i, "E") for i in block_e]
    print(f"      block B: {len(block_b)}  block C: {len(block_c)}  "
          f"block E: {len(block_e)}")

    # --------------------------------------------------------- the actors ----
    print("[3/6] actors: parties (date-gated)")
    parties = entities.load_parties()
    for vote, block in [(v, "A") for v in block_a] + [(control, "D")]:
        for row in entities.party_actors(vote, parties):
            entity_rows.append({"event_id": f"{block}-{vote['_anr']}", **row})

    print("[4/6] actors: people, via PersonNumber -> P1307")
    for vote, block in [(v, "A") for v in block_a] + [(control, "D")]:
        short = (vote.get("gesch_nr") or "").strip()
        if not short:
            continue
        curia_actors = curia.actors_for_business(short)
        resolved = entities.qids_for_person_numbers(
            [a["person_number"] for a in curia_actors]
        )
        for row in entities.person_actors(curia_actors, resolved):
            entity_rows.append({"event_id": f"{block}-{vote['_anr']}", **row})

    for item in block_b:
        for row in entities.federal_council_actors(date.fromisoformat(item["date"])):
            entity_rows.append({"event_id": f"B-{item['qid']}", **row})

    participants = entities.event_actors(
        [i["qid"] for i in block_c + block_e]
    )
    for item in block_c + block_e:
        for row in participants.get(item["qid"], []):
            entity_rows.append({"event_id": f"{item['_block']}-{item['qid']}", **row})

    # An event with no named actor on Wikidata still supports the
    # agenda-controlled comparison -- it only loses its ground truth. Flag it
    # instead of dropping it, and say so rather than let a reader assume every
    # row is a usable linking test case.
    actor_counts: dict[str, int] = {}
    for row in entity_rows:
        actor_counts[row["event_id"]] = actor_counts.get(row["event_id"], 0) + 1
    for ev in events:
        n_rows = actor_counts.get(ev["event_id"], 0)
        ev["n_reference_actors"] = n_rows // 2  # two language rows per actor
        ev["has_reference_actors"] = n_rows > 0

    # ------------------------------------------------------ the queries ----
    print("[5/6] Swissdox queries (validation only, nothing pulled)")
    source_list = fetch(
        queries.SOURCE_LIST_URL,
        "swissdox/swissdox_sources.json",
        manifest=manifest,
        name="swissdox_sources",
        role="medium codes and coverage periods",
    )
    present, missing = queries.check_sources(source_list)
    if missing:
        print(f"      WARNING unknown medium codes (would pass validation "
              f"silently): {missing}")

    query_dir = cfg.DATA_OUT / "queries"
    query_dir.mkdir(exist_ok=True)
    query_rows = []
    for ev in events:
        yaml_text = queries.build_query(
            date_from=date.fromisoformat(ev["window_from"]),
            date_to=date.fromisoformat(ev["window_to"]),
            sources=tuple(present),
        )
        path = query_dir / f"{ev['event_id']}.yaml"
        path.write_text(yaml_text, encoding="utf-8")
        query_rows.append(
            {
                "event_id": ev["event_id"],
                "query_name": f"mediapos-{ev['event_id']}",
                "yaml_path": str(path.relative_to(cfg.REPO_ROOT)),
                "date_from": ev["window_from"],
                "date_to": ev["window_to"],
                "n_sources": len(present),
                "languages": "de|fr",
                "submitted": False,
            }
        )

    # ------------------------------------------------------------ output ----
    print("[6/6] writing outputs")
    # Deterministic row order. SPARQL makes no ordering promise and several
    # steps go through sets, so without this the files differ between runs
    # that selected exactly the same events -- and "rerun and land on the same
    # dataset" is the contract this whole module exists to keep.
    frames = {
        "events": pd.DataFrame(events).sort_values(
            ["block", "date", "event_id"], kind="stable"
        ),
        "entities": pd.DataFrame(entity_rows).sort_values(
            ["event_id", "source", "source_key", "qid", "lang"], kind="stable"
        ),
        "queries": pd.DataFrame(query_rows).sort_values(["event_id"], kind="stable"),
    }
    for name, df in frames.items():
        df.to_csv(cfg.DATA_OUT / f"{name}.csv", index=False)
        df.to_parquet(cfg.DATA_OUT / f"{name}.parquet", index=False)

    manifest.note("window", [cfg.WINDOW_FROM.isoformat(), cfg.WINDOW_TO.isoformat()])
    manifest.note("counts", {
        "events": len(events),
        "by_block": pd.DataFrame(events)["block"].value_counts().to_dict(),
        "entity_rows": len(entity_rows),
        "queries": len(query_rows),
    })
    manifest.note("selection_rule", {
        "block_A": trace_a, "block_B": trace_b, "block_C": trace_c,
        "block_D": trace_d, "block_E": trace_e,
    })
    manifest.note("cantonal_gap_repairs", repaired)
    manifest.note("swissdox_sources", {"used": present, "unknown": missing})
    manifest.note("canton_language_mapping", {
        "fr": list(cfg.CANTONS_FR),
        "de": list(cfg.CANTONS_DE),
        "excluded": list(cfg.CANTONS_EXCLUDED),
        "why": "bilingual (BE, FR, VS), Italian (TI) and trilingual (GR) cantons "
               "are excluded from both sides; assigning them would put our thumb "
               "on the axis",
    })
    path = manifest.write()
    print(f"      {len(events)} events, {len(entity_rows)} entity rows, "
          f"{len(query_rows)} queries")
    print(f"      manifest -> {path.relative_to(cfg.REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
