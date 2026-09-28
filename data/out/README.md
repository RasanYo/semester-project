# Bootstrap event repertoire

Produced by `scripts/01_build_repertoire.py`; verified by `scripts/02_verify.py`,
whose executed output is in `docs/verification_report.txt`. Rerunning the build
on the same published inputs yields byte-identical `events.csv`, `entities.csv`
and `queries.csv` -- that is the contract.

| File | One row = | Notes |
|---|---|---|
| `events.{csv,parquet}` | one event | block A-E, date, bilingual labels, the two computed axes, coverage window |
| `entities.{csv,parquet}` | one (event, actor, language) | long edge list: add `outlet` and `window` and it is the bipartite graph |
| `queries.{csv,parquet}` | one Swissdox query | `submitted` is False for all -- no article has been downloaded |
| `queries/*.yaml` | the query itself | validated against the live API with `test=1` |
| `manifest.json` | -- | every source with URL, fetch date, sha256; the selection rule as applied |

Raw downloads live in `data/raw/`, which is gitignored. The corpus is a cache;
the manifest is the fact.

## Reading the blocks

* **A** -- 8 federal popular votes, stratified 2x2 on polarization x Roestigraben, 2 per cell, >= 2 on migration/asylum/EU.
* **B** -- every Federal Council election in the window. Small, fully known cast: the easy reference case.
* **C** -- Swiss events not carried by the institutional calendar. Not "unplanned": Wikidata knows only two of those in seven years.
* **D** -- the consensual object. Negative control. If outlets separate here, the method is measuring noise.
* **E** -- international, `is_diagnostic = True`. **Never enters the calibration set.** Its only job is identical actors on both sides of the Roestigraben.

## Two things the numbers do not mean

Reconciliation is 100%, but that is the ceiling of an identifier join, not
evidence the linker works. No row came from a surface form found in text --
deliberately, because this file is the answer key.

`has_reference_actors` is False for three events: Wikidata names no actor for
them. They keep their use for the agenda-controlled comparison and lose it as
linking test cases.
