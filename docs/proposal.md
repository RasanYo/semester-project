# Semester Project Proposal

**Political Positioning of Swiss News Media via Outlet–Actor Network Analysis**

*Semester Project — MSc Data Science, ETH Zürich · Swiss Data Science Center*

---

## Context and Motivation

The literature on media bias detection is extensive but dominated by two limitations. First, it relies heavily on content-based sentiment analysis, even though recent work shows this approach is fragile on journalistic text and is outperformed by *stance*- or *actor-visibility*-based approaches. Second, it is almost entirely centered on the two-party, English-language U.S. system.

This project adopts the **visibility** approach: instead of analyzing what a media outlet *says*, it measures *which political actors it makes visible and with what tone*. An outlet's ideological position then emerges from its editorial amplification choices, turning a noisy NLP problem into a graph and latent-position estimation problem that is more robust and statistically richer. The Swiss setting — multilingual and multi-party — is a largely unexplored testbed.

## Research Questions

1. Can the political position of a Swiss news outlet be quantified solely from the visibility structure of the actors it covers, without fine-grained content analysis?
2. Applied over time windows, does this measure reveal **co-positioning** dynamics between outlets, and do these survive controlling for common external shocks (elections, popular votes)?

## Data

A large corpus of Swiss web news articles, multilingual (DE / FR / IT / EN), covering all major outlets over 5–10 years at daily granularity.

## Method

```
NER + cross-lingual entity linking (→ Wikidata)   →  who is mentioned, by whom
        ↓
bipartite outlet–actor graph (weighted by frequency × tone)
        ↓
latent position estimation (correspondence analysis / ideal point / matrix factorization)
        ↓
per-outlet position time series (sliding windows, change-point detection)
        ↓
co-movement analysis: VARX / lead-lag, external shocks as exogenous variables
```

The data science core lies in the latent-position estimation, the multivariate time-series analysis (VARX, Granger causality), and the handling of the linguistic/regional confounder.

## Validation (Ground Truth)

The latent axis produced by the model is only interpretable against an independent external reference. Switzerland offers strong sources:

| Source | Contribution | Granularity |
|---|---|---|
| Smartvote / smartmap | **2D** political space (left–right / liberal–conservative) per candidate and party | Actor |
| Parliamentary roll-call votes (open data) | Ideal points computable from voting records | Member of Parliament |
| Manifesto Project (MARPOR), CHES | Longitudinal party positions | Party |

Because the Swiss reference space is **two-dimensional**, validation is stronger than in the unidimensional U.S. case: the first latent axis is expected to correlate with the left–right dimension and the second with the liberal–conservative one.

## Technical Challenges and Contributions

- **Cross-lingual entity linking**: the same actor (UDC / SVP / *Swiss People's Party*) must be reconciled into a single canonical node via Wikidata; otherwise the graph fragments. This is the central NLP/DS contribution and what sets the work apart from the U.S. literature.
- **Language/region confounder**: the French- and German-speaking media spaces differ in covered actors and topics; the dominant latent axis may capture region before ideology. Diagnosing and correcting this bias (leveraging the ground truth) is a methodological contribution in its own right.

## Honest Scoping

"Contagion" is a causal term beyond the reach of observational data over this period. The goal is therefore not to *prove* inter-outlet influence, but to **characterize co-positioning dynamics and test whether they persist once common shocks are controlled for** (VARX). This control is precisely what distinguishes an academic contribution from a purely descriptive dashboard.
