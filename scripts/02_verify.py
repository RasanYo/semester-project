"""Verification report for the bootstrap event repertoire.

    .venv/bin/python scripts/02_verify.py

Nothing here is asserted; everything is measured against the files
`01_build_repertoire.py` wrote and against live Wikidata. The hard cases are
checked explicitly rather than hoped for, because the whole dataset exists to
be a test bench for exactly these:

  * UDC / SVP / Swiss People's Party must be ONE node
  * "Le Centre" is a lexical collision, not a party name
  * CVP + BDP -> Die Mitte / Le Centre on 2021-01-01 must resolve by date
  * one in five parliamentarian names has an exact-label homonym
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import date

import pandas as pd
import requests

from mediapos import config as cfg
from mediapos import entities
from mediapos.manifest import USER_AGENT
from mediapos.sources import wikidata as wd


def rule(title: str) -> None:
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


def search_wikidata(term: str, lang: str, limit: int = 8) -> list[dict[str, str]]:
    """Raw wbsearchentities -- what a naive string lookup would have returned."""
    resp = requests.get(
        wd.API_URL,
        params={
            "action": "wbsearchentities", "search": term, "language": lang,
            "uselang": lang, "limit": limit, "format": "json",
        },
        headers={"User-Agent": USER_AGENT},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json().get("search", [])


def main() -> int:
    events = pd.read_csv(cfg.DATA_OUT / "events.csv")
    ents = pd.read_csv(cfg.DATA_OUT / "entities.csv")
    manifest = json.loads((cfg.DATA_OUT / "manifest.json").read_text())

    rule("1. THE DATASET")
    print(f"events      {len(events)}")
    for block, n in sorted(events["block"].value_counts().items()):
        label = {"A": "federal popular votes", "B": "Federal Council elections",
                 "C": "non-institutional Swiss", "D": "consensual control",
                 "E": "international (diagnostic)"}[block]
        print(f"   {block}  {n:>2}  {label}")
    print(f"entity rows {len(ents)}  "
          f"({ents['qid'].nunique()} distinct QIDs, 2 language rows per actor)")
    print(f"queries     {len(list((cfg.DATA_OUT / 'queries').glob('*.yaml')))} "
          f"YAML files, none submitted")

    rule("2. RECONCILIATION")
    status = Counter(ents["match_status"])
    total = len(ents)
    nil = sum(n for s, n in status.items() if s.startswith("nil"))
    review = sum(n for s, n in status.items() if s.startswith("review"))
    for s, n in status.most_common():
        print(f"   {s:<20} {n:>5}  {n / total:>6.1%}")
    print(f"\n   reconciled {total - nil}/{total} ({(total - nil) / total:.1%})"
          f" | NIL {nil} | needs review {review}")
    by_source = ents.groupby("source")["qid"].agg(["count", lambda s: s.isna().sum()])
    by_source.columns = ["rows", "nil"]
    print(f"\n   by source:\n{by_source.to_string()}")

    print("\n   READ THIS BEFORE BELIEVING THE NUMBER ABOVE.")
    print("   100% is the ceiling of an identifier join, not evidence that")
    print("   entity linking works. Every actor here arrived through a key:")
    print("     * parties      -- short name + life dates, no string search")
    print("     * people       -- PersonNumber -> P1307, an external identifier")
    print("     * event actors -- item-to-item links inside Wikidata")
    print("   Not one row was produced by matching a surface form found in")
    print("   text. That is deliberate: this file is the ANSWER KEY, and an")
    print("   answer key built by fuzzy matching would be worthless. The linker")
    print("   is tested when article text arrives and is scored against it.")

    missing = events.loc[~events["has_reference_actors"], "event_id"].tolist()
    print(f"\n   events carrying NO reference actor: {len(missing)}/{len(events)}"
          f" -> {missing}")
    print("   These keep their use for the agenda-controlled comparison; they")
    print("   lose their use as linking test cases. Wikidata names no actor for")
    print("   them, and that is reported rather than patched.")
    print(f"\n   reference actors per event: "
          f"min {events['n_reference_actors'].min()}, "
          f"median {events['n_reference_actors'].median():.0f}, "
          f"max {events['n_reference_actors'].max()}")

    rule("3. HARD CASE -- UDC / SVP / Swiss People's Party is ONE node")
    ent = wd.get_entities(["Q385258"], props="labels|aliases|claims")["Q385258"]
    for lang in ("de", "fr", "it", "en"):
        print(f"   label[{lang}]  {ent['labels'].get(lang, {}).get('value', '-')}")
    shorts = [
        f"{c['mainsnak']['datavalue']['value']['text']}@"
        f"{c['mainsnak']['datavalue']['value']['language']}"
        for c in ent["claims"].get("P1813", [])
    ]
    print(f"   P1813      {', '.join(shorts)}")
    used = sorted(set(ents.loc[ents["source_key"] == "p-svp", "qid"].dropna()))
    print(f"   in dataset the p-svp column resolves to: {used}  "
          f"-> {'ONE node' if len(used) == 1 else 'FRAGMENTED'}")

    print("\n   What a naive string lookup would have done instead:")
    for term, lang in (("UDC", "fr"), ("SVP", "fr")):
        hits = search_wikidata(term, lang, limit=5)
        print(f"     '{term}' in {lang}: " + " | ".join(
            f"{h['id']}={h.get('label', '')[:28]}" for h in hits))

    rule("4. HARD CASE -- 'Le Centre' is a lexical collision")
    for term, lang in (("Le Centre", "fr"), ("Die Mitte", "de")):
        hits = search_wikidata(term, lang, limit=6)
        print(f"   '{term}' ({lang}):")
        for h in hits:
            print(f"     {h['id']:<12} {h.get('label', '')[:32]:<34} "
                  f"{h.get('description', '')[:44]}")
    print("\n   The pipeline never searches these strings: the p-mitte column is")
    print("   resolved by short name + life dates, so the collision cannot fire.")

    rule("5. HARD CASE -- the CVP + BDP -> Die Mitte transition of 2021-01-01")
    parties = entities.load_parties()
    for when in (date(2020, 11, 29), date(2021, 3, 7), date(2024, 3, 3)):
        row = []
        for col in ("p-cvp", "p-bdp", "p-mitte"):
            p, st = entities.party_for_column(col, when, parties)
            row.append(f"{col}->{p.qid if p else 'NIL':<12}({st})")
        print(f"   {when}  " + "  ".join(row))
    centre_qids = sorted(set(
        ents.loc[ents["source_key"].isin(["p-cvp", "p-mitte"]), "qid"].dropna()
    ))
    print(f"\n   distinct centre-party QIDs in the dataset: {centre_qids}")
    print("   Two nodes, correctly: one lineage, two legal entities. A pre-2021")
    print("   mention on the Die Mitte node would be an anachronism.")

    rule("6. HARD CASE -- homonyms among the people in the dataset")
    people = ents[ents["source_key"].astype(str).str.startswith("PersonNumber:")]
    names = sorted(set(people["label"].dropna()))
    print(f"   {len(names)} distinct people reached through PersonNumber -> P1307")
    collisions = []
    for name in names:
        hits = search_wikidata(name, "de", limit=10)
        exact = [h for h in hits if h.get("label", "").lower() == name.lower()]
        if len(exact) > 1:
            collisions.append((name, exact))
    print(f"   exact-label collisions: {len(collisions)}/{len(names)}")
    for name, exact in collisions[:5]:
        print(f"     '{name}':")
        for h in exact:
            print(f"        {h['id']:<12} {h.get('description', '')[:56]}")
    print("\n   None of these can reach the dataset: P1307 is an external")
    print("   identifier whose literal value IS the PersonNumber, so no string")
    print("   is ever matched for a person.")

    rule("7. SWISSDOX QUERIES -- validated, nothing pulled")
    import time

    from mediapos import queries as q

    ok_n = 0
    rows = pd.read_csv(cfg.DATA_OUT / "queries.csv")
    for i, (_, row) in enumerate(rows.iterrows()):
        if i:
            time.sleep(q.PACE_SECONDS)  # paced: the endpoint 500s on a fast batch
        yaml_text = (cfg.REPO_ROOT / row["yaml_path"]).read_text(encoding="utf-8")
        ok, message = q.validate(yaml_text, name=row["query_name"])
        ok_n += ok
        if not ok:
            print(f"   FAIL {row['event_id']}: {message[:120]}")
    print(f"   {ok_n}/{len(list((cfg.DATA_OUT / 'queries').glob('*.yaml')))} "
          f"queries validate against the live API (test=1)")
    print("   No query was submitted for compilation: no article was downloaded.")
    print("   Volume cannot be known before pulling -- estimateResults is")
    print("   confirmed useless (1 against an actual 1,953), and `content` is a")
    print("   mandatory column, so there is no cheap metadata-only count. Sizing")
    print("   needs one calibration pull, then linear extrapolation.")

    rule("8. PROVENANCE")
    print(f"   sources recorded: {len(manifest['sources'])}")
    for s in manifest["sources"][:12]:
        print(f"     {s['name']:<26} {s['bytes']:>10,} B  {s['sha256'][:16]}...")
    if len(manifest["sources"]) > 12:
        print(f"     ... and {len(manifest['sources']) - 12} more")
    repairs = manifest["notes"].get("cantonal_gap_repairs", {})
    print(f"\n   cantonal-gap repairs: {len(repairs)} objects")
    for anr, src in sorted(repairs.items()):
        print(f"     anr {anr} <- {src}")

    rule("9. WHAT THIS DATASET CANNOT DO")
    print("   * The French side of Swissdox is one publisher group (TX Group)")
    print("     plus Le Temps and rts.ch. Le Nouvelliste, La Liberte, ArcInfo,")
    print("     Le Courrier and Le Quotidien Jurassien are absent from the")
    print("     corpus. Language and ownership are collinear by construction.")
    print("   * No news agency is in the corpus, so wire copy appears under")
    print("     several medium codes. Near-duplicate detection is required")
    print("     before any co-positioning claim.")
    print("   * Italian Switzerland is rsi.ch alone.")
    print("   * Block E is diagnostic and never enters the calibration set.")
    print("   * Block C is 'non-institutional', not 'unplanned': Wikidata knows")
    print("     only two genuinely unplanned Swiss events in the whole window.")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
