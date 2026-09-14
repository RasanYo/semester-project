"""Run the whole chain on ONE federal popular vote, end to end.

A method earns its infrastructure by working on a slice first. This script
takes a single ballot object, computes both axes, resolves every party actor to
a QID through the date gate, builds the Swissdox query, and validates that
query against the live API without pulling a single article.

    .venv/bin/python scripts/00_prototype_one_vote.py [anr]

Defaults to the Begrenzungsinitiative (anr 631): a migration/EU object with a
negative Roestigraben gap, which exercises the parts most likely to be wrong.
"""

from __future__ import annotations

import sys
from datetime import timedelta

from mediapos import axes, entities, queries
from mediapos.config import (
    CANTONS_DE,
    CANTONS_FR,
    COVERAGE_DAYS_AFTER,
    COVERAGE_DAYS_BEFORE,
)
from mediapos.manifest import Manifest
from mediapos.sources import swissvotes as sv


def main(anr: str = "631") -> int:
    manifest = Manifest()

    print("=" * 78)
    print(f"PROTOTYPE -- one vote, end to end (anr {anr})")
    print("=" * 78)

    rows = sv.in_window(sv.load(sv.download(manifest)))
    sv.fill_cantonal_gap(rows, manifest)
    vote = next((r for r in rows if r["_anr"] == anr), None)
    if vote is None:
        print(f"no in-window ballot object with anr={anr}")
        return 1
    axes.annotate([vote])

    print(f"\n[1] OBJECT       {vote['datum']}  anr={vote['_anr']}")
    print(f"    DE           {vote['titel_kurz_d']}")
    print(f"    FR           {vote['titel_kurz_f']}")
    print(f"    domains      {vote['_domains']}")
    print(f"    migration/EU {vote['_is_migration_eu']}")
    print(f"    Curia Vista  {vote['gesch_nr']}")

    fr = [vote['_japroz'][k] for k in CANTONS_FR]
    de = [vote['_japroz'][k] for k in CANTONS_DE]
    print(f"\n[2] AXES         polarization {vote['_pol']:.3f} "
          f"(count variant {vote['_pol_count']:.3f})")
    print(f"                 Roestigraben {vote['_gap']:+.2f}")
    print(f"                 = mean(FR {min(fr):.1f}..{max(fr):.1f})"
          f" - mean(DE {min(de):.1f}..{max(de):.1f})")
    print(f"                 national yes {vote['volkja-proz']}%")

    parties = entities.load_parties()
    actors = entities.party_actors(vote, parties)
    de_actors = [a for a in actors if a["lang"] == "de"]
    print(f"\n[3] ACTORS       {len(de_actors)} parties took a side "
          f"({len(actors)} rows, one per language)")
    for a in de_actors:
        fr_label = next(
            x["label"] for x in actors
            if x["source_key"] == a["source_key"] and x["lang"] == "fr"
        )
        print(f"    {a['source_key']:<9} {str(a['qid']):<12} {a['match_status']:<18} "
              f"{a['role']:<15} {str(a['label'])[:30]:<32} | {str(fr_label)[:30]}")

    nil = [a for a in actors if a["qid"] is None]
    review = [a for a in actors if a["match_status"].startswith("review")]
    print(f"    reconciled {len(actors) - len(nil)}/{len(actors)} "
          f"| NIL {len(nil)} | needs review {len(review)}")

    start = vote["_date"] - timedelta(days=COVERAGE_DAYS_BEFORE)
    end = vote["_date"] + timedelta(days=COVERAGE_DAYS_AFTER)
    yaml_text = queries.build_query(date_from=start, date_to=end)
    print(f"\n[4] SWISSDOX     window {start} -> {end} "
          f"({(end - start).days} days), {len(queries.SOURCES)} sources")

    ok, message = queries.validate(yaml_text, name=f"mediapos-proto-{anr}")
    print(f"    validation   {'PASS' if ok else 'FAIL'}: {message}")
    print("\n" + "=" * 78)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "631"))
