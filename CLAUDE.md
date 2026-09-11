# CLAUDE.md

## What we are looking for

A Swiss news outlet's political position, estimated from **who it makes visible
and with what tone** — not from what it says. Actor mentions become a weighted
bipartite outlet–actor graph; the position is a latent coordinate in that graph,
tracked over sliding windows. Semester project, MSc Data Science, ETH Zürich ·
Swiss Data Science Center. `docs/proposal.md` holds the full proposal.

The deliverable is two things that ship together: a **written report**, and the
**code in this repository that produced everything in it**. Due **early November
2026** — roughly eight weeks from the first commit, which is short for a pipeline
this long. When something has to give, it is scope, never the honesty of a claim.

The work is supervised, and the supervisor **stays anonymous**: no name in the
repo, the commits, the report metadata, or anything published from here.

Two questions, in order:

1. Can an outlet's position be recovered from visibility structure alone?
2. Over time, do outlets **co-position** — and does that survive controlling for
   common shocks (elections, popular votes) via VARX?

**The scope is honest and stays honest.** Contagion is a causal claim that
observational data over this period cannot support. We characterize
co-positioning and test whether it persists once shocks are controlled for. Any
sentence that upgrades this to influence or contagion is wrong, in code comments
as in the report.

Two things decide whether the whole thing works, and both are the contribution:

- **Cross-lingual entity linking.** UDC, SVP and *Swiss People's Party* are one
  node, reconciled through Wikidata. If they stay three, the graph fragments and
  every position downstream is noise.
- **The language/region confounder.** The French- and German-speaking media
  spaces cover different actors. The dominant latent axis may be measuring
  *region* rather than ideology. Assume it does until a diagnostic says
  otherwise.

## How we work

**Python**, in a local virtualenv. If `.venv/` exists, call `.venv/bin/python` —
the system `python3` has none of the dependencies. No dependency manifest yet;
when one lands, it gets a line here.

**No test suite yet.** That is a fact, not a standard: when code carries a claim
about the data, write the check that proves it and show the output. Never call
something verified because it ran.

**English in the repo** — code, comments, docs, commit messages. `TODO.md` and
`DEVLOG.md` stay in French, like the conversation.

**Git.** Work lands on `develop` through a branch and a PR. `main` holds what is
defensible.

## Research, not product

The normal yield of this work is dead ends. That is not a licence for rough
work — it decides where the effort goes.

- **Every number and every figure in the report comes from a script in this
  repo**, rerunnable end to end. A result living only in a notebook cell or a
  screenshot cannot go in the report.
- **Prototype before building around it.** One window, one language, one outlet
  — a method earns its infrastructure by working on a slice first.
- **A negative result is a result.** A method that fails gets a `DEVLOG.md`
  entry saying so and why. Deleting the branch in silence means the same dead
  end gets walked again in six weeks.
- **Two bars for code.** Exploratory code is allowed to be rough. Code whose
  output reaches the report is not: it gets a seed, a manifest, and a way to
  check it.

## The board and the trace

`TODO.md` is the board: `[ ]` open, `[.]` running, `[x]` done. **Before touching
anything, look for the task there.** Not there? Add it — one line, the same voice
as its neighbours — and mark it `[.]` before the first edit. Done: `[x]`, dated,
moved under `## Fait`. Abandoned: back to `[ ]`. A stale `[.]` is worse than no
line at all.

`DEVLOG.md` is the trace: one entry per lot of work merged into `develop` that
changes what the system *is* or *can do*. Format in `.claude/commands/devlog.md`;
a `PostToolUse` hook reminds after a merge. A merge made in the GitHub web UI
fires no hook — that entry is on you.

Same bar for both: a question, a config sync, a typo, a one-file fix gets no
line. Just do it.

## Non-negotiables

**The corpus never enters git.** It is licensed, it is large, and a file in the
history stays in the history. What gets versioned is the **manifest** — source,
window, filters, counts, a hash — never the bytes. The corpus is a cache; the
manifest is the fact.

**Secrets live in `.env`** (gitignored). No key in a notebook, a commit, or a
log line.

**The ground truth is not a knob.** Smartvote, parliamentary roll-calls, MARPOR
and CHES validate the latent axes — they do not tune them. If a reference is
used to calibrate (sign, rotation, scale), say so explicitly and validate against
something else. An axis fitted to its own benchmark has been assumed, not shown.
