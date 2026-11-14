# SEC EDGAR Facts Explorer — Hackathon Submission

**Author:** Michael Schihl  
**Environment:** IBM watsonx Orchestrate — `gsa-hackathon` (IBM Cloud Toronto, `ca-tor`)  
**Submission date:** 2026-11-14

---

## Problem Statement

Public company financial data is authoritative, machine-readable, and freely
available via the SEC's EDGAR APIs — yet it is almost never used directly in
AI-powered workflows. Financial chatbots typically answer from training data
(which is stale, unverifiable, and prone to hallucination) or from expensive
third-party data providers. Neither approach gives the user a path back to the
primary source.

This project asks a simple question: **can a watsonx Orchestrate agent answer
real financial questions by querying the SEC's authoritative APIs directly —
with zero hallucination risk and a live link to every number it returns?**

The answer, demonstrated across 20 evaluation questions, is yes.

---

## What Was Built

Three connected layers, each building on the previous:

```mermaid
flowchart TD
    U([User — WXO Chat UI]) --> A

    subgraph WXO["IBM watsonx Orchestrate"]
        A["sec_edgar_agent\n(native · react_core · groq/gpt-oss-120b)"]
    end

    A -- "MCP streamable-HTTP\n8 tools" --> S

    subgraph CE["IBM Code Engine  (ca-tor · always-warm)"]
        S["sec_edgar_tools\nFastMCP server\nPython 3.12"]
    end

    S -- "httpx async" --> E1
    S -- "httpx async" --> E2
    S -- "httpx async" --> E3

    subgraph SEC["SEC EDGAR  (public APIs · no auth)"]
        E1["company_tickers.json\n(name → ticker/CIK)"]
        E2["submissions/{CIK}.json\n(filing history)"]
        E3["companyfacts/{CIK}.json\n(XBRL financial facts)"]
    end

    style WXO fill:#e8f0fe,stroke:#3b82d4
    style CE  fill:#f0fdf4,stroke:#22c55e
    style SEC fill:#fef9ec,stroke:#f59e0b
```

### Layer 1 — MCP Server (`sec_edgar_tools`)

An 8-tool FastMCP server deployed to IBM Code Engine as an always-warm
containerised HTTPS service. It exposes the SEC's three public data endpoints
as structured tool calls. No API keys are required — EDGAR is fully open.

The server connects to watsonx Orchestrate as a remote MCP toolkit over the
`streamable_http` transport, replacing the earlier stdio/subprocess model and
making the toolkit reachable by any MCP-compatible client.

**The 8 tools:**

| # | Tool | Purpose |
|---|------|---------|
| 1 | `sec_edgar_search_companies` | Find companies by partial name; returns ticker, CIK, full name |
| 2 | `sec_edgar_resolve_company` | Resolve a ticker or CIK to canonical SEC identity (SIC, state, CIK) |
| 3 | `sec_edgar_get_recent_filings` | List recent 10-K, 10-Q, 8-K or any form type, most-recent-first |
| 4 | `sec_edgar_get_company_fact` | Fetch a multi-year XBRL fact time series (e.g. 8 years of net income) |
| 5 | `sec_edgar_get_quarterly_facts` | Fetch single-quarter XBRL observations (Q1/Q2/Q3 only; Q4 noted) |
| 6 | `sec_edgar_compare_companies` | Compare one concept across multiple companies; emits FY-alignment warnings |
| 7 | `sec_edgar_list_concepts` | Enumerate XBRL concepts a company reports; supports keyword search |
| 8 | `sec_edgar_get_filing_metadata` | Resolve an accession number to form type, dates, and a direct EDGAR link |

### Layer 2 — Agent (`sec_edgar_agent`)

A native watsonx Orchestrate agent (`react_core` style, `groq/gpt-oss-120b`)
with a detailed instruction set covering:

- **Tool selection rules** — which tool to call for each class of question
- **Multi-step chaining** — search → resolve → retrieve for name-based queries
- **Concept synonyms** — XBRL tag names are non-obvious; the agent tries alternate
  names and runs synonym searches when a concept is not found
- **Comparability warnings** — always surface fiscal-year misalignment to the user
- **Q4 limitation disclosure** — companies do not file a 10-Q for Q4; the agent
  explains this explicitly when data is missing
- **Source traceability** — every response includes accession numbers and EDGAR links

### Layer 3 — Evaluation Harness

Two evaluation frameworks measuring different quality dimensions:

**REST evaluator** (`evaluation/run_evaluation.py`): sends 20 questions to the
live agent over the WXO REST API, checks which tools fired, and compares against
expected tool lists. Fully automated; runs against the production agent.

**Phoenix LLM-as-judge** (`eval/phoenix/`): an Arize Phoenix harness that
connects directly to the Code Engine MCP endpoint and uses a second, independent
LLM to score each response for correctness and scope compliance. Two evaluators,
two system prompt versions for A/B comparison. Built and ready; pending USAI
model gateway credentials.

---

## Evaluation Results

### Layer 1 — Tool Routing (automated, 2026-11-07)

**20 / 20 questions passed.** Every expected tool fired; no question was answered
from the LLM's training data.

| Tool | Questions | Times Fired | Notes |
|------|-----------|-------------|-------|
| `sec_edgar_search_companies` | 4 | 4 | 100% — exact routing |
| `sec_edgar_resolve_company` | 2 | 8 | 400% — agent proactively validates tickers |
| `sec_edgar_get_recent_filings` | 4 | 4 | 100% |
| `sec_edgar_get_company_fact` | 5 | 6 | 120% — retries with alternate concept names |
| `sec_edgar_compare_companies` | 2 | 3 | 150% — retries on stale concept data |
| `sec_edgar_get_quarterly_facts` | 3 | 3 | 100% |
| `sec_edgar_list_concepts` | 2 | 2 | 100% |
| `sec_edgar_get_filing_metadata` | 2 | 2 | 100% |

The over-firing on `resolve_company` and `get_company_fact` reflects correct
behaviour: the agent validates tickers before downstream calls and tries alternate
XBRL concept names when the primary one returns stale data.

### Layer 2 — Human Quality Audit (2026-11-11)

A human review of all 20 agent responses against actual SEC EDGAR data found
five response quality issues. All high-severity issues have been addressed.

**What the agent does well:**
- Consistent, clean table formatting across all 20 responses
- Proactive fiscal-year comparability warnings (fired correctly on 3 of 3 applicable comparisons)
- Working, deterministic EDGAR viewer URLs in all filing attribution responses
- Graceful error handling on invalid ticker (BQ-19): clear message, no fabrication
- Correct multi-step chaining for name-search → financial-data questions (BQ-17, BQ-18)

**Issues found and addressed:**

| Issue | Severity | Root cause | Resolution |
|-------|----------|------------|-----------|
| Wrong entity for multi-registrant corps (ExxonMobil shell vs. operating entity) | High | Search returned first alphabetical result | Agent instructions updated: prefer ticker-matching entity; retry if no 10-K found |
| YTD values returned as quarterly figures (Apple Q3 ~$364B instead of ~$109B) | High | XBRL stores 3-month and 9-month values under the same `fp=Q3` label | Server fix: filter observations to ≤104-day duration; deduplicate per `(fp, fy)` |
| Q4 missing without explanation | Medium | No instruction covering the 10-Q gap | Agent instructions updated: explicitly disclose Q4/10-Q limitation; offer annual proxy |
| Annual fact precision (~$3B off for Apple FY2024) | Medium | `get_company_fact` returns all observations including comparative-period restated entries | Identified; fix planned (filter to latest-filed observation per FY end date) |
| Concept synonym gaps (revenue/debt tags not matching keywords) | Medium | Substring search misses tags like `PremiumsEarnedNet` | Agent instructions updated: run synonym searches; XBRL concept table expanded |

### Layer 3 — LLM-as-Judge (Phoenix, pending USAI credentials)

The Phoenix harness is fully built (`eval/phoenix/`). It includes:
- 20-question dataset CSV covering all 8 tools
- Two LLM-as-judge evaluators: `match_expected_response` (correctness) and
  `check_answer_scope` (scope compliance)
- Two system prompt versions for A/B comparison (baseline vs. scope-bounded)
- Direct MCP connection to the Code Engine endpoint (no subprocess overhead)

Expected improvement areas once the run completes: BQ-09, BQ-10 (quarterly
YTD fix), BQ-18 (entity disambiguation fix), BQ-20 (EPS quarterly data).

---

## Key Technical Decisions

**Remote MCP over stdio.** The toolkit runs as a persistent HTTPS service on
Code Engine rather than as a subprocess inside WXO. This means: (1) the server
is always warm — no cold-start latency per request; (2) the toolkit is
independently versioned from the agent; (3) any MCP-compatible client can connect
to it without touching the WXO environment.

**FastMCP with async httpx.** All 8 tools are async, sharing a single persistent
`httpx.AsyncClient` with `trust_env=False` and `follow_redirects=True`. A single
warm client handles all concurrent requests without connection churn. The SEC
enforces a ~10 req/s rate limit; the `compare_companies` tool adds a 120ms delay
between companies to stay within it.

**Duration-based quarterly filter.** The SEC XBRL API does not distinguish
3-month from 9-month periods at the response level — both carry `fp=Q3`. The fix
computes `end − start` for each observation and rejects anything over 104 days.
This is a data-level fix in the server, invisible to the agent and to the user.

**Deterministic EDGAR URLs.** The `get_filing_metadata` tool constructs EDGAR
viewer URLs from the accession number and CIK alone:
`https://www.sec.gov/Archives/edgar/data/{numeric_cik}/{accession_path}/{primary_doc}`.
No external lookup is required; the URL is guaranteed correct if the accession
number is valid.

---

## What the Phoenix Experiment Will Add

Once USAI credentials are available, the LLM-as-judge run will provide:

1. **A numerical correctness baseline** for the current agent (prompt v1)
2. **An A/B comparison** against prompt v2 (scope-bounded, more explicit
   about tool selection rules) on the same 20 questions
3. **Per-question trace inspection** in the Phoenix UI — full reasoning chains,
   tool call inputs/outputs, and judge scores for each response
4. **Reproducibility** — the experiment is committed and version-controlled;
   re-running it after any agent or server change produces comparable scores

The existing human audit provides the ground truth that the LLM-as-judge scores
can be validated against.

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
```

---

## Milestones

| Milestone | Status |
|-----------|--------|
| M1 — 8-tool MCP server built and deployed to Code Engine | ✅ Complete |
| M2 — Agent deployed to WXO; toolkit re-imported as remote streamable-HTTP | ✅ Complete |
| M3 — Evaluation: REST run (20/20), human audit, Phoenix harness built | ✅ Mostly complete — LLM-as-judge run pending USAI credentials |

---

## Repository Layout

```
toolkits/sec_edgar_tools/
├── server.py              ← FastMCP server (8 tools)
├── requirements.txt
├── toolkit.yaml           ← WXO import spec (remote MCP, streamable_http)
└── test_local.py          ← 13-check local test suite (live SEC APIs)

agents/
└── sec_edgar_agent.yaml   ← native react_core agent definition

evaluation/
├── run_evaluation.py      ← REST-based tool-routing evaluator
├── eval_questions.csv     ← 20 evaluation questions with expected tools
├── EVAL_REPORT.md         ← full 20-question results (2026-11-07)
├── response_quality_audit.md  ← human annotations of all 20 responses
└── interpretation.md      ← narrative evaluation report

eval/phoenix/
├── create_dataset.py      ← uploads CSV to Phoenix dataset store
├── run_experiment.py      ← runs LLM-as-judge experiment
├── evaluators.py          ← two judge functions (correctness + scope)
├── agent_runner.py        ← MCP client connecting to Code Engine endpoint
└── README.md              ← usage guide

docs/
├── project_overview.md    ← plain-language project summary
├── demo_walkthrough.md    ← scripted 8-step demo script
└── submission.md          ← this file
```

---

*Submitted: 2026-11-14 | Author: Michael Schihl*
