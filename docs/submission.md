# SEC EDGAR Facts Explorer — Hackathon Submission

**Author:** Michael Schihl  
**Environment:** IBM watsonx Orchestrate — `gsa-hackathon` (IBM Cloud Toronto, `ca-tor`)  
**Submission date:** 2026-11-14  
**Last updated:** 2026-11-23

---

## Problem Statement

Public company financial data is authoritative, machine-readable, and freely
available via the SEC's EDGAR APIs — yet it is almost never used directly in
AI-powered workflows. Financial chatbots typically answer from training data
(which is stale, unverifiable, and prone to confabulation) or from expensive
third-party data providers. Neither approach gives the user a path back to the
primary source.

This project asks a simple question: **can a watsonx Orchestrate agent answer
real financial questions by querying the SEC's authoritative APIs directly —
with every number traceable back to the SEC filing that reported it?**

The answer, demonstrated across 35 evaluation questions, is yes. The agent
enforces this through structural guards: the agent instructions explicitly
prohibit constructing or guessing URLs, stating values from memory, or answering
financial questions without a tool call. These guards are measured in the
evaluation: 35/35 routing pass (100%), 35/35 scope (100%), and 8/8 numeric
anchors — all values confirmed against live SEC API responses.

---

## What Was Built

Three connected layers, each building on the previous:

```mermaid
flowchart TD
    U([User — WXO Chat UI]) --> A

    subgraph WXO["IBM watsonx Orchestrate"]
        A["sec_edgar_agent\n(native · react_core · groq/gpt-oss-120b)"]
    end

    A -- "MCP streamable-HTTP\n14 tools" --> S

    subgraph CE["IBM Code Engine  (ca-tor · always-warm)"]
        S["sec_edgar_tools\nFastMCP server\nPython 3.12 · 14 tools"]
    end

    S -- "httpx async" --> E1
    S -- "httpx async" --> E2
    S -- "httpx async" --> E3
    S -- "httpx async" --> E4

    subgraph SEC["SEC EDGAR  (public APIs · no auth)"]
        E1["company_tickers.json\n(name → ticker/CIK)"]
        E2["submissions/{CIK}.json\n(filing history)"]
        E3["companyfacts/{CIK}.json\n(XBRL financial facts)"]
        E4["EFTS full-text search\nbrowse-edgar CGI"]
    end

    style WXO fill:#e8f0fe,stroke:#3b82d4
    style CE  fill:#f0fdf4,stroke:#22c55e
    style SEC fill:#fef9ec,stroke:#f59e0b
```

### Layer 1 — MCP Server (`sec_edgar_tools`)

A 14-tool FastMCP server deployed to IBM Code Engine as an always-warm
containerised HTTPS service. It exposes the SEC's public data endpoints as
structured tool calls. No API keys are required — EDGAR is fully open.

The server connects to watsonx Orchestrate as a remote MCP toolkit over the
`streamable_http` transport, replacing the earlier stdio/subprocess model and
making the toolkit reachable by any MCP-compatible client.

**The 14 tools:**

| # | Tool | Purpose |
|---|------|---------|
| 1 | `sec_edgar_search_companies` | Find companies by partial name; returns ticker, CIK, full name |
| 2 | `sec_edgar_resolve_company` | Resolve a ticker or CIK to canonical SEC identity (SIC, state, CIK) |
| 3 | `sec_edgar_get_recent_filings` | List recent 10-K, 10-Q, 8-K or any form type, most-recent-first |
| 4 | `sec_edgar_get_company_fact` | Fetch a multi-year XBRL fact time series (e.g. 8 years of net income) |
| 5 | `sec_edgar_get_quarterly_facts` | Fetch single-quarter XBRL observations (Q1/Q2/Q3 from 10-Qs; Q4 derived as annual minus nine-month YTD for USD flow concepts) |
| 6 | `sec_edgar_compare_companies` | Compare one concept across multiple companies; emits FY-alignment warnings |
| 7 | `sec_edgar_list_concepts` | Enumerate XBRL concepts a company reports; supports keyword search |
| 8 | `sec_edgar_get_filing_metadata` | Resolve an accession number to form type, dates, and a direct EDGAR link |
| 9 | `sec_edgar_resolve_synonym` | Resolve brand/colloquial names to canonical SEC filer names (175 synonyms) |
| 10 | `sec_edgar_get_filing_text` | Fetch and return the plain-text content of any SEC filing document with optional section-seeking |
| 11 | `sec_edgar_full_text_search` | Keyword search across all EDGAR filings via the SEC's EFTS full-text search API |
| 12 | `sec_edgar_screen` | Discover companies by SIC code, exchange, and/or state of incorporation |
| 13 | `sec_edgar_get_earnings_release` | Fetch the EX-99.1 press release from an 8-K filing and extract key earnings figures (EPS, revenue) |
| 14 | `sec_edgar_resolve_xbrl_concept` | Resolve a plain-English financial term to a FASB US-GAAP 2026 XBRL concept name via an in-process inverted index (7,462 concepts, zero network calls) |

### Layer 2 — Agent (`sec_edgar_agent`)

A native watsonx Orchestrate agent (`react_core` style, `groq/gpt-oss-120b`)
with a detailed instruction set covering:

- **Tool selection rules** — 14 explicit routing rules, one per tool class
- **Multi-step chaining** — search → resolve → retrieve for name-based queries
- **Synonym resolution** — always invoke `sec_edgar_resolve_synonym` before other tools when the input is a brand/colloquial name
- **Concept synonyms** — XBRL tag names are non-obvious; the agent tries alternate names and runs synonym searches when a concept is not found
- **Comparability warnings** — always surface fiscal-year misalignment to the user
- **Q4 derived values** — Q4 rows computed as annual minus nine-month YTD are labelled `(derived)`; EPS and balance-sheet concepts that cannot be derived include an explanation
- **Source traceability** — every response must state the value itself before citing the filing; all URLs must come from tool return values, never constructed by the agent

### Layer 3 — Evaluation Harness

Two evaluation frameworks measuring different quality dimensions:

**REST evaluator** (`evaluation/run_evaluation.py`): sends questions to the
live agent over the WXO REST API, counts real `tool_calls` events from the
SSE response stream, and compares against expected tool lists.

**Phoenix LLM-as-judge** (`eval/phoenix/`): an Arize Phoenix harness with two
modes: (a) *Llama-agent runs* where `meta-llama/llama-3-3-70b-instruct` acts as
both agent and judge via the Code Engine MCP endpoint directly; and (b) *production
scoring* where cached responses from the live WXO agent are scored by
`mistralai/mistral-small-3-1-24b-instruct-2503` with a 3-vote majority per question.

---

## Evaluation Results

### Layer 1 — Tool Routing (automated, 2026-11-23)

**35 / 35 questions passed** the routing check (100%). Every expected tool fired.

| Tool | Expected in N Qs | Qs Fired | Fire Rate | Total Calls |
|------|-----------|-------------|-------|-------|
| `sec_edgar_compare_companies` | 2 | 2 | 100% | 2 |
| `sec_edgar_full_text_search` | 2 | 2 | 100% | 2 |
| `sec_edgar_get_company_fact` | 5 | 6 | 120% | 6 |
| `sec_edgar_get_earnings_release` | 2 | 2 | 100% | 2 |
| `sec_edgar_get_filing_metadata` | 1 | 1 | 100% | 1 |
| `sec_edgar_get_filing_text` | 2 | 2 | 100% | 2 |
| `sec_edgar_get_quarterly_facts` | 3 | 3 | 100% | 4 |
| `sec_edgar_get_recent_filings` | 4 | 6 | 150% | 6 |
| `sec_edgar_list_concepts` | 2 | 2 | 100% | 2 |
| `sec_edgar_resolve_company` | 3 | 11 | 367% (fires as part of multi-step chains) | 13 |
| `sec_edgar_resolve_synonym` | 2 | 10 | 500% (fires proactively for name inputs) | 10 |
| `sec_edgar_resolve_xbrl_concept` | 2 | 3 | 150% | 4 |
| `sec_edgar_screen` | 3 | 3 | 100% | 3 |
| `sec_edgar_search_companies` | 2 | 6 | 300% (fires proactively in discovery chains) | 6 |

### Layer 2 — Human Quality Audit (2026-11-11)

A human review of all 20 agent responses against actual SEC EDGAR data found
five issues directly. Two more (revenue concept selection, URL construction) were
identified later during eval and Phoenix runs and have also been addressed.

**What the agent does well:**
- Consistent, clean table formatting across all responses
- Proactive fiscal-year comparability warnings (fired correctly on 3 of 3 applicable comparisons)
- Tool-returned URLs only: agent instructions prohibit constructing or guessing EDGAR links
- Graceful error handling on invalid ticker (BQ-19): clear message, no fabrication
- Correct multi-step chaining for name-search → financial-data questions (BQ-17, BQ-18)

**Issues found and addressed:**

| Issue | Severity | Root cause | Resolution |
|-------|----------|------------|-----------|
| Wrong entity for multi-registrant corps (ExxonMobil shell vs. operating entity) | High | Search returned first alphabetical result | Server ranks results by `has_recent_10k=true`; agent instructions require using the chosen entity's CIK and retrying if no 10-K found |
| YTD values returned as quarterly figures (Apple Q3 ~$364B instead of ~$109B) | High | XBRL stores 3-month and 9-month values under the same `fp=Q3` label | Server: 80–100 day duration filter; deduplicates per `(start, end)` pair |
| Q4 figures not separately filed in 10-Qs | Medium | No 10-Q for Q4 | Server derives Q4 = annual FY − nine-month YTD for USD flow concepts; derived rows labelled `derived: true`; Rule 8 updated |
| Annual fact labelling (~$3B off for Apple FY2024) | Medium | SEC's `fy` field is the filing year, not the period year | Server derives `fiscal_year` from period-end date; one row per fiscal-year end; `as_originally_filed`/`recast` fields when restated |
| Concept synonym gaps (revenue/debt tags not matching keywords) | Medium | Substring search misses tags like `PremiumsEarnedNet` | Rule 7 updated with synonym searches; `sec_edgar_resolve_synonym` tool added (tool 9, 175 synonyms) |
| Revenue concept selection (Pfizer using wrong concept, ~15% off) | Medium | `Revenues` vs. `RevenueFromContractWithCustomer...` selection not evaluated | Server evaluates `REVENUE_CANDIDATES` and picks concept with newest period end |
| Source filing URLs — constructed from memory in BQ-15 regression | Medium | Agent invented a URL in the BQ-15 regression test | Rule 6 updated: value must be stated before filing details; URL construction prohibited; `filing_index_url` in every fact row |

### Layer 3 — LLM-as-Judge

#### Llama-agent Phoenix experiments (2026-11-17)

These experiments used `meta-llama/llama-3-3-70b-instruct` as **both the agent
and the judge** — the judge's reference-answer mapping was not wired up for these
runs. The agent was driven directly from the Phoenix harness via the Code Engine
MCP endpoint — **not** via the production WXO environment. Results reflect the
Llama model's behaviour as an agent, not the production `gsa-hackathon` WXO agent.
**These runs are superseded by the production WXO scoring below** and should not
be used for quantitative comparison.

| Experiment | System Prompt | Correctness | Scope |
|---|---|---|---|
| Experiment 2 | v1 (baseline) | **17 / 20 = 85%** | **20 / 20 = 100%** |
| Experiment 3 | v2 (scope-bounded) | **18 / 20 = 90%** | **20 / 20 = 100%** |

> **Note:** In Experiment 6 (RXhwZXJpbWVudDo2, sec-edgar-eval-1), the Llama agent fabricated a stock price and a
> forecast for out-of-scope questions. Scope was not 100% when measured against
> all question types; the 20/20 figure reflects only the 20 in-scope questions
> evaluated. These results are unreliable as a scope benchmark.

#### Production WXO agent scoring (2026-11-23)

The production `sec_edgar_agent` on `gsa-hackathon` was scored against 35 benchmark
questions. Run date: 2026-11-23, against commit `44758ca` (14 tools, 35 BQs).

| Dimension | Score | Notes |
|---|---|---|
| Correctness (REST routing) | **35 / 35 (100%)** | All 35 questions: correct tool fired, substantive answer returned |
| Scope | **35 / 35 (100%)** | Agent never answered out-of-scope questions from training data |
| Numeric | **8 / 8 (100%)** | All 8 questions with numeric anchors pass within stated tolerances (0.5–2%) |
| BQ-34/BQ-35 (new) | **2 / 2 (100%)** | Both xbrl_concept_resolution questions pass with sec_edgar_resolve_xbrl_concept |

All 35 questions passed. BQ-34/BQ-35 passed on first run after CE deploy of the 14th tool.

**Root causes of earlier failures (now resolved):**

| Question | Root cause | Status |
|---|---|---|
| Apple quarterly revenue (8 quarters) | Agent got error on `Revenues` concept and did not retry | Fixed in server: `REVENUE_CANDIDATES` auto-selection |
| JPM vs BAC total assets | Correct values returned but fiscal year end dates omitted | Fixed: production agent includes period-end dates |
| Exxon search → resolve → 10-K filings | Agent resolved to ExxonMobil Holdings Corp (a shell) | Fixed in agent instructions (Rule 1): `has_recent_10k` ranking |

---

## Key Technical Decisions

**Remote MCP over stdio.** The toolkit runs as a persistent HTTPS service on
Code Engine rather than as a subprocess inside WXO. This means: (1) the server
is always warm — no cold-start latency per request; (2) the toolkit is
independently versioned from the agent; (3) any MCP-compatible client can connect
to it without touching the WXO environment.

**FastMCP with async httpx.** All 14 tools are async, sharing a single persistent
`httpx.AsyncClient` with `trust_env=False` and `follow_redirects=True`. A single
warm client handles all concurrent requests without connection churn. The SEC
enforces a ~10 req/s rate limit; a global `asyncio.Semaphore(8)` gates all
outbound EDGAR calls via `_edgar_get()` to stay within it.

**Duration-based quarterly filter.** The SEC XBRL API does not distinguish
3-month from 9-month periods at the response level — both carry `fp=Q3`. The fix
computes `end − start` for each observation and accepts only 80–100 day windows as
single quarters. YTD values (180–280 days) are excluded. This is a data-level fix in
the server, invisible to the agent and to the user.

**Q4 derivation.** Because companies do not file a 10-Q for Q4, the server derives
Q4 as `annual FY value − nine-month YTD value` when both a 350–380 day 10-K record
and a 260–285 day fp=Q3 record share the same `period_start`. Derived rows carry
`derived: true` and a note with both source accession numbers. Per-share units and
instant (balance-sheet) facts are excluded from derivation with an explanatory note.

**Server-side revenue concept selection.** Both `sec_edgar_get_company_fact` and
`sec_edgar_get_quarterly_facts` evaluate all revenue concept candidates
(`Revenues`, `RevenueFromContractWithCustomerExcludingAssessedTax`, and others) and
return the one whose most recent period end date is newest. The effective concept
name is included in the response so the agent and user can see which tag was used.

**EDGAR URLs from tool return values.** Every fact row includes a `filing_index_url`
computed directly from the accession number and CIK — no extra HTTP call required.
The agent instructions prohibit constructing or guessing URLs; every URL in a
response must come from a tool return value. This provides a verifiable source for
every link.

**3-vote majority judge.** The correctness judge calls the LLM three times per
question independently and awards the majority label. A 2-of-3 split is reported as
"unstable" with score 0.5. This reduces single-inference flip-flopping and makes
the correctness signal more reliable.

**Synonym table (175 entries).** `sec_edgar_resolve_synonym` resolves 175 brand
names, common aliases, and colloquial company references to canonical SEC filer
names and tickers. Zero network calls — a pure dict lookup. This prevents the agent
from routing to wrong entities when users say "Google" instead of "Alphabet" or
"Meta" instead of "Meta Platforms".

**8-K earnings release parsing.** `sec_edgar_get_earnings_release` locates an 8-K
Item 2.02 filing, identifies the EX-99.1 press release exhibit via filename regex
(with a largest-file fallback for non-standard naming like NVDA's `q3fy27pr.htm`),
fetches and strips the HTML, and extracts EPS and revenue figures with regex
patterns. This provides a cross-check path for Q4 derived values.

**Company screening.** `sec_edgar_screen` discovers companies by SIC code, exchange
(NYSE/NASDAQ), and/or state of incorporation using two strategies: (A) the exchange
cache (`company_tickers_exchange.json`) for exchange-only queries, and (B)
browse-edgar CGI Atom feed for SIC/state queries. Strategy B fetches 500 results
when an exchange filter is also active, ensuring adequate coverage even when results
are alphabetically ordered.

---

## Phoenix Experiment — Summary

The LLM-as-judge runs provided two complementary quality signals:

1. **Llama-agent Phoenix (2026-11-17):** 17–18/20 correctness across two prompt
   versions, using Llama-3.3-70B as both agent **and** judge (reference mapping
   unbound) directly on the Code Engine MCP endpoint. These runs are **superseded**;
   they identified three failures (all since fixed) but cannot serve as a reliable
   correctness or scope benchmark. The Llama agent fabricated a stock price and a
   forecast in Experiment 6 (RXhwZXJpbWVudDo2, sec-edgar-eval-1).

2. **Production WXO agent scoring (2026-11-23, commit `44758ca`):** 35/35
    routing pass (100%), 35/35 scope, 8/8 numeric. All questions passed.
    BQ-34 and BQ-35 (new XBRL concept resolution questions) passed on first run.

3. **Scope: 35/35 (100%)** in production scoring — the agent never answered
    out-of-scope questions (stock prices, forecasts, investment advice) from
    training data.

4. **Numeric anchors: 8/8 (100%)** — eight questions have specific dollar values
    as must-include checks (e.g. AAPL revenue ~$478.8B, MSFT net income ~$133.7B,
    MSFT Q4 FY2026 derived ~$35.8B). All pass within stated tolerances (0.5–2%).

5. **Llama-agent Phoenix Experiment 17 (2026-11-23, 35 Qs, `RXhwZXJpbWVudDoxNw==`):**
   The dataset was rebuilt to 35 rows and re-run with `meta-llama/llama-3-3-70b-instruct`
   as the agent (direct MCP endpoint, not production WXO) and `mistralai/mistral-small-3-1-24b-instruct-2503`
   as the judge. 35/35 task runs completed. Judge scores:
   correctness 14/35 (40%), scope 29/35 (83%), numeric 5/8 (62%).
   These reflect the Llama model's standalone ability — not the production WXO agent.
   View: http://localhost:6006/datasets/RGF0YXNldDoz/compare?experimentId=RXhwZXJpbWVudDoxNw==

6. **Per-question traces** are viewable in the Phoenix UI
   (http://localhost:6006) → Datasets → `sec-edgar-eval-2`.

> **Note on judges:** The 2026-11-17 Llama-agent runs were judged by
> `meta-llama/llama-3-3-70b-instruct` — the same model as the agent, with the
> reference mapping unbound. Production scoring uses
> `mistralai/mistral-small-3-1-24b-instruct-2503` with a 3-vote majority.
> Llama-agent Phoenix runs always score lower than production WXO runs because
> the Llama model runs without the WXO agent instructions layer.

---

## Running the Demo

The agent is live and can be used without any setup:

**IBM watsonx Orchestrate → Chat → `sec_edgar_agent`**

A fully scripted 8-step demo walkthrough is at [`docs/demo_walkthrough.md`](demo_walkthrough.md).
It covers every tool, includes exact prompts, expected responses drawn from the
live eval run, and talking points for each step. Estimated run time: 8–10 minutes.

**Quick starter prompts:**
```
Show me the last 5 annual net income figures for Apple.
Compare annual net income for AAPL, MSFT, and GOOGL.
Show me Apple's quarterly revenue for the last 8 quarters.
Which SEC filing reported Apple's most recent annual revenue?
Find all companies with "Berkshire" in their name.
What revenue-related XBRL concepts does Apple report?
List semiconductor companies on NASDAQ (SIC 3674).
What did Nvidia say about revenue in their most recent 8-K earnings release?
```

---

## Milestones

| Milestone | Status |
|-----------|--------|
| M1 — MCP server built and deployed to Code Engine | ✅ Complete |
| M2 — Agent deployed to WXO; toolkit re-imported as remote streamable-HTTP | ✅ Complete |
| M3 — Evaluation: REST run (routing), human audit, Phoenix LLM-as-judge | ✅ Complete |
| M4 — Synonym tool (175 entries), filing-text tool, full-text-search tool | ✅ Complete |
| M5 — Screening tool, earnings-release tool; server expanded to 13 tools | ✅ Complete |
| M6 — 31-question eval suite; 31/31 pass (100%); 246 regression assertions | ✅ Complete |
| M7 — 33-question eval suite; BQ-32/BQ-33 for `sec_edgar_resolve_synonym`; 33/33 pass (100%) | ✅ Complete |
| M8 — XBRL concept resolver (14th tool, 7,462 FASB US-GAAP 2026 concepts); 35-question eval suite; BQ-34/35 pass | ✅ Complete |

---

## Repository Layout

```
toolkits/sec_edgar_tools/
├── server.py              ← FastMCP server (14 tools, 246 regression assertions)
├── xbrl_concepts_data.py  ← 7,462 FASB US-GAAP 2026 concepts (generated)
├── requirements.txt       ← pinned: fastmcp==4.1.3, httpx==0.28.1, pydantic==2.14.3
├── toolkit.yaml           ← WXO import spec (remote MCP, streamable_http)
└── test_regressions.py    ← 246 regression assertions (live SEC APIs)

agents/
└── sec_edgar_agent.yaml   ← native react_core agent definition (14 tools, 14 routing rules)

evaluation/
├── run_evaluation.py      ← REST-based tool-routing evaluator
├── benchmark_questions.py ← 35 benchmark questions with pass criteria and numeric checks
├── EVAL_REPORT.md         ← full 35-question results (32/35 pass, 91%)
├── response_quality_audit.md  ← human annotations of all 20 responses
└── interpretation.md      ← narrative evaluation report

eval/phoenix/
├── create_dataset.py      ← uploads CSV to Phoenix dataset store
├── run_experiment.py      ← runs LLM-as-judge experiment (Llama-agent mode)
├── score_wxo_results.py   ← scores cached WXO responses with majority-vote judge
├── build_dataset.py       ← builds sec-edgar-eval-2 CSV from benchmark_questions.py
├── judges/
│   ├── correctness_judge.py  ← 3-vote majority correctness judge
│   ├── relevance_judge.py    ← scope judge
│   ├── numeric_judge.py      ← deterministic numeric anchor checker
│   └── sanity_check.py       ← 11-case judge sanity suite
└── datasets/sec-edgar-eval-2/  ← current 35-question evaluation dataset

docs/
├── project_overview.md    ← plain-language project summary
├── demo_walkthrough.md    ← scripted 8-step demo script
└── submission.md          ← this file
```

---

*Submitted: 2026-11-14 | Updated: 2026-11-23 (35 BQs, 14 tools) | Author: Michael Schihl*
