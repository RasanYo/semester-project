---
name: swissdox
description: Use when querying, downloading, or planning a pull from the Swissdox@LiRI corpus of Swiss media articles — endpoints, YAML query schema, and the gotchas that cost a round-trip.
---

# Swissdox@LiRI

Not a search API. A **corpus ordering** API: submit → the server compiles for
minutes to hours → poll → download a `.tsv.xz`. Never loop on it like REST.

Credentials are in `.env`: `SWISSDOX_API_KEY` and `SWISSDOX_API_SECRET`. Both
headers are required — `X-API-Key` alone gets you nothing.

## Endpoints

Base `https://swissdox.linguistik.uzh.ch/api`

| Endpoint | Method | Returns |
|---|---|---|
| `/query` | POST | `id` of the submitted query |
| `/status` | GET | all queries, with `status` and `downloadUrl` |
| `/status/<id>` | GET | one query |
| `/download/<filename>` | GET | the `.tsv.xz` |

POST form fields: `query` (YAML string) and `name` are required; `test="1"`,
`comment`, `expirationDate` (`YYYY-MM-DD`) are optional.

**Always submit with `test="1"` first.** It validates without compiling and
returns a usable error list on HTTP 406.

## Query YAML

```yaml
query:
    sources:            # medium codes; omit for all
        - NZZ
        - TPS
    dates:              # REQUIRED
        - from: 2022-12-01
          to: 2022-12-31
    languages:          # de fr it rm en; omit for all
        - de
    doctypes:           # PND PRD PLD PLW PJO PMA PID NNE WWE TNT; omit for all
        - PND
    content:            # flat list = OR; or an AND/OR/NOT tree
        - Bundesrat
result:                 # REQUIRED
    format: TSV
    maxResults: 10000   # hard cap, not a hint
    columns: [id, pubtime, medium_code, medium_name, rubric, regional,
              doctype, doctype_description, language, char_count, dateline,
              head, subhead, article_link, content_id, content]
version: 1.2
```

Keywords are **case-sensitive**, match whole words, and `*` is a wildcard
(`find*`, `*finden`). They apply to body text only — not captions, bylines, or
tables. An omitted filter means no filtering, not an empty result.

## Verified, and not in the manual

- `dates` and `result` are required — omitting them is a 406.
- `doctypes` is a valid filter key.
- `content` accepts a flat list (OR), no tree needed.
- `article_link` is a real column.
- `estimateResults` in `/status` is garbage — one query estimated 1 and
  returned 1953. Never size a pull from it.
- `result.columns` **must** contain `content`, and `result.maxResults` is
  mandatory. Omit either and `/query` returns a bare HTTP 500 with no error
  list — not a 406. Consequence: there is no cheap metadata-only counting
  query, so every pull carries full article text.
- An **unknown medium code passes validation silently** (HTTP 200, "valid").
  A typo just drops that outlet from the pull and you find out after the
  compile. Check every code against `swissdox_sources.json` locally first —
  and note that file is `{"rows": [...], "totals": {...}}`, not a bare list.
- **Pace a batch of `test=1` submissions, ~12 s apart.** The endpoint 500s
  (sometimes 504s) under rapid sequential validation. Measured: 20 back-to-back
  queries reported 7 false failures; 5 s apart still reported 4; every one of
  those validated when submitted alone. A 500 is only real if it survives
  retries *and* pacing.

## Reading the output

`content` is XML, not plain text: `<tx>` root, `<ld>` lead, `<p>`, `<zt>`
crossheads, `<lg>` legends, `<ka>` boxes, `<au>` author, plus leftover HTML.
Parse it. Stream the archive rather than decompressing:

```python
import lzma, csv
with lzma.open(path, mode="rt", encoding="utf-8", newline="") as fh:
    for row in csv.DictReader(fh, delimiter="\t"):
        ...
```

## Before a real pull

The corpus never enters git — download to a cache, version the **manifest**:
sources, window, filters, article count, hash. The corpus is a cache; the
manifest is the fact.

Full source list (272 entries, codes + coverage periods):
`https://swissdox.linguistik.uzh.ch/manual/auto/swissdox/swissdox_sources.json`

Corpus skew to keep in mind: 83% German, 16% French overall — but recent
windows lean heavily online and French-first. Source and doctype mix is part of
the language/region confounder, not separate from it.

Manual: https://swissdox.linguistik.uzh.ch/manual/api.html
