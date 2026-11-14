# SEC EDGAR Facts Explorer — What We Built

*A plain-language guide to the full hackathon project.*
*Companion to the HTML summary at `.bob/artifacts/session-handoff-2026-11-14.md`.*

---

## The Big Picture

We built a system that lets an AI assistant answer questions about public company
SEC filings — things like "What was Apple's revenue last quarter?" or "Which filing
first reported Microsoft's most recent net income?" — by going directly to the SEC's
official database, not by guessing from training data.

The system has three layers, built in order:

```
Layer 1 — The Tools (MCP Server)
        8 functions that know how to talk to the SEC's APIs

              ↓

Layer 2 — The Agent
        An AI that decides which tools to call and how to explain the results

              ↓

Layer 3 — The Evaluation
        A test suite that measures whether the agent gives correct, useful answers
```

---

## Layer 1 — The MCP Server (`sec_edgar_tools`)

**The toolkit is the MCP server.** MCP stands for "Model Context Protocol," an
open standard for giving AI models access to external tools. Think of it like a
power strip: you plug in functions, and any AI that speaks MCP can use them.

The server runs as a containerised web service on **IBM Code Engine** (IBM's
serverless container platform) and is always available at a public HTTPS URL.
It calls the SEC's public APIs — no login required, all public data.

### The 8 tools

| # | Tool | What it does |
|---|---|---|
| 1 | `search_companies` | Find companies by partial name ("Berkshire" → BRK-A, BRK-B) |
| 2 | `resolve_company` | Look up a company by ticker or CIK — returns SIC code, state, etc. |
| 3 | `get_recent_filings` | List the most recent 10-K, 10-Q, or 8-K filings for a company |
| 4 | `get_company_fact` | Get annual financial data time-series — e.g. 8 years of net income |
| 5 | `get_quarterly_facts` | Same but for individual quarters (Q1/Q2/Q3/Q4 only, not YTD) |
| 6 | `compare_companies` | Compare the same financial metric across multiple companies |
| 7 | `get_filing_metadata` | Look up a specific filing by accession number; returns a direct SEC link |
| 8 | `list_concepts` | Discover what XBRL financial tags a company reports |

### What is XBRL?

XBRL (eXtensible Business Reporting Language) is the standardised tagging system
the SEC requires public companies to use. Instead of a PDF number, each figure
gets a machine-readable tag like `NetIncomeLoss`. This makes it possible to
programmatically retrieve Apple's revenue without scraping a PDF.

### Why Code Engine and not inside watsonx Orchestrate?

WXO originally ran MCP toolkits as local subprocesses. By deploying to Code Engine
instead and connecting via HTTPS, the toolkit becomes an independent, always-warm
service that *any* MCP-compatible client can reach — not just WXO. It also means
you can update the server without touching the agent.

---

## Layer 2 — The Agent (`sec_edgar_agent`)

The agent is an AI that sits in front of the tools and handles the conversation
with the user. Here is what it does that the tools alone cannot:

1. **Understands natural language.** A user says "Show me Apple's quarterly
   revenue." The agent figures out that means: call `get_quarterly_facts` with
   AAPL, us-gaap, RevenueFromContractWithCustomerExcludingAssessedTax. The user
   doesn't know (or care) about XBRL tag names.

2. **Chains multiple tools together.** "Find companies with Pfizer in the name,
   then show me their last 4 annual revenues." That requires two tool calls in
   sequence: search first, then retrieve. The agent handles this automatically.

3. **Formats and explains results.** Raw SEC data is numbers and accession codes.
   The agent turns "$94,000,000,000" into "$94.0 billion", adds fiscal year labels,
   presents comparison tables, and flags fiscal year misalignments ("Apple's year
   ends September; Microsoft's ends June — these figures may not be comparable").

4. **Recovers from errors gracefully.** If a concept name fails, the agent tries
   an alternate name or calls `list_concepts` to find the right one.

The agent lives inside **IBM watsonx Orchestrate**. It can be used as a
collaborator by other agents, or the MCP server can be connected directly to any
MCP-compatible AI client without the WXO layer at all.

---

## Layer 3 — The Evaluation Harness

A **harness** is a testing framework. The word comes from physical test harnesses
in engineering — the cables and fixtures that hold a component in place while you
measure it. A software test harness is the scaffolding that runs your system under
controlled conditions and measures the results.

We built two harnesses:

### Harness 1 — REST-based tool-routing evaluator (`evaluation/run_evaluation.py`)

Sends 20 questions to the live agent and checks: **did the right tools fire?**
It doesn't judge answer quality — only whether the correct SEC API calls were made.
Result: **20/20 pass on 2026-11-07.**

### Harness 2 — Phoenix LLM-as-judge evaluator (`eval/phoenix/`)

Measures actual **answer quality** — not just which tools fired, but whether the
numbers are correct and the response is in-scope. It uses a second, independent AI
model (a "judge") to read each response and score it. Using a *different* model
as judge than the one being tested reduces "self-preference bias."

**Status:** Fully built, waiting on USAI model gateway credentials from the GSA
hackathon lab portal (a separate OpenAI-compatible service, not your WXO instance).

### Why a 100% tool-routing pass rate didn't mean the agent was correct

The evaluator confirmed the agent *did something* (called the right tool, returned
a number) — not that it did the *right thing* (returned the correct number). Like
writing a SQL query that sums a column when the question asked for an average: it
ran, it returned a value, it "passed" — but the answer is wrong. This is the gap
the LLM-as-judge layer is designed to close.

---

## What the Human Audit Found (and Fixed)

You read all 20 agent responses against the actual SEC EDGAR data and found issues
the automated scorer couldn't see. The most important ones, now fixed:

| Issue | Root cause | Fix |
|---|---|---|
| Q3 Apple revenue showed $364B instead of $109B | XBRL stores both 3-month and 9-month figures under the same `Q3` label; the tool wasn't filtering by duration | Server now filters observations to ≤104 days (true single quarter) |
| ExxonMobil returned a holding-company shell with no 10-K filings | Search returned the first alphabetical result, not the main operating entity | Agent now prefers entities with matching tickers; retries if no 10-K found |
| Revenue/debt concept searches returned incomplete lists | XBRL tags like `PremiumsEarnedNet` or `ShortTermBorrowings` don't contain the word "revenue" or "debt" | Agent now runs synonym searches when first keyword returns few results |

---

## Milestone Summary

| Milestone | Status |
|---|---|
| M1 — 8-tool MCP server built and deployed to Code Engine | ✅ Complete |
| M2 — Agent deployed to WXO, toolkit re-imported as remote HTTP | ✅ Complete |
| M3 — Evaluation: REST run (20/20), human audit, Phoenix harness built | ✅ Mostly complete — LLM-as-judge run waiting on USAI credentials |

---

## Where Things Live

| Component | Location |
|---|---|
| MCP server source | `toolkits/sec_edgar_tools/server.py` |
| MCP server (live) | IBM Code Engine, `ca-tor` region |
| Agent definition | `agents/sec_edgar_agent.yaml` |
| Agent (live) | IBM watsonx Orchestrate, `gsa-hackathon` environment |
| REST evaluator | `evaluation/run_evaluation.py` |
| Eval results | `evaluation/EVAL_REPORT.md` |
| Human audit | `evaluation/response_quality_audit.md` |
| Evaluation narrative | `evaluation/interpretation.md` |
| Phoenix harness | `eval/phoenix/` |
| This document | `docs/project_overview.md` |

---

*Written: 2026-11-14 | Author: Michael Schihl*
