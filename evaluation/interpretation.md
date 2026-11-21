# SEC EDGAR Facts Explorer — Evaluation Interpretation

**Agent:** `sec_edgar_agent` (native, react_core style)  
**Toolkit:** `sec_edgar_tools` (13 MCP tools, deployed to IBM Code Engine)  
**Environment:** `gsa-hackathon` (IBM Cloud Toronto, ca-tor)  
**Initial evaluation run:** 2026-11-07 (20 questions, 557 seconds)  
**Human audit completed:** 2026-11-11 (review of all 20 agent responses)  
**Production WXO scoring:** 2026-11-21 (31 questions, Mistral Small 3-vote majority judge)

---

## 1. What this evaluation measured

The evaluation covered three distinct layers:

**Layer 1 — Tool routing** (automated, `evaluation/run_evaluation.py`): Did the
agent call the right tools for each question? This is the primary gate for all
evaluation runs. Routing is detected from real WXO `tool_calls` events in the SSE
response stream — not text-matching. Fire rates above 100% mean the agent proactively
called a tool as part of a multi-step chain on questions where it was not explicitly
expected (e.g. `resolve_company` firing 500% because the agent resolves company
identity before retrieving any financial fact).

**Layer 2 — Response quality** (human audit, `evaluation/response_quality_audit.md`):
Was the answer a human would read accurate, complete, and clearly presented? This
layer identified issues that the automated scorer could not see.

**Layer 3 — LLM-as-judge scoring** (`eval/phoenix/`): An Arize Phoenix harness
scoring each response for correctness and scope compliance. Two variants:
(a) **Llama-agent Phoenix runs** (agent and judge both `meta-llama/llama-3-3-70b-instruct`,
reference mapping unbound — superseded; see §6a) used for A/B prompt experiments;
(b) **production WXO agent scoring** using cached responses from the live
`gsa-hackathon` agent, scored by `mistralai/mistral-small-3-1-24b-instruct-2503`
with a 3-vote majority.

---

## 2. Tool routing results (Layer 1)

All 31 questions passed the tool-routing check. Every expected tool fired.

**Tool utilisation summary (2026-11-21, 31 questions):**

| Tool | Expected in N Qs | Times Fired | Fire Rate |
|---|---|---|---|
| `sec_edgar_compare_companies` | 2 | 2 | 100% |
| `sec_edgar_full_text_search` | 2 | 2 | 100% |
| `sec_edgar_get_company_fact` | 5 | 5 | 100% |
| `sec_edgar_get_earnings_release` | 2 | 2 | 100% |
| `sec_edgar_get_filing_text` | 2 | 2 | 100% |
| `sec_edgar_get_quarterly_facts` | 3 | 4 | 133% |
| `sec_edgar_get_recent_filings` | 4 | 5 | 125% |
| `sec_edgar_list_concepts` | 2 | 2 | 100% |
| `sec_edgar_resolve_company` | 2 | 10 | 500% |
| `sec_edgar_screen` | 2 | 2 | 100% |
| `sec_edgar_search_companies` | 4 | 7 | 175% |

**Interpretation:** The tool routing instructions are working. The agent did not
refuse answerable questions and correctly chained multi-tool sequences
(search → resolve → retrieve) for hard questions. Tools firing above expected (e.g.
`resolve_company` at 500%) reflect the agent proactively resolving company identity
before retrieving financial data — the correct behaviour for name-based queries.

> **Note on the 2026-11-07 run (now superseded):** That initial run counted tool
> appearances by text-matching the SSE stream and response content. Fire rates
> above 100% in those results (e.g. ~400% for `resolve_company`) indicated the
> tool name appeared in unexpected questions' text, not actual additional calls.
> The runner was updated to consume real WXO `tool_calls` events; all subsequent
> runs use this accurate methodology.

---

## 3. Response quality findings (Layer 2)

The 2026-11-11 audit found five issues. Two more (revenue concept selection, URL
construction) were found during later evaluation and Phoenix runs. All seven have
been addressed.

The human audit reviewed all 20 responses across the eight quality dimensions
(accuracy, completeness, clarity, units, temporal labels, source traceability,
hedging, and scope behaviour). Key findings are summarised below.

### 3a. What the agent does well

**Clean, consistent table formatting.** Across all responses the agent presented
data in well-structured markdown tables with appropriate columns. Filing metadata
(accession numbers, form types, filing and period-end dates) was included without
being asked, which is the correct behaviour for an SEC research tool.

**Proactive comparability warnings.** For cross-company comparisons (BQ-13, BQ-14),
the agent correctly surfaced fiscal year misalignment when it existed (Apple/Microsoft/
Alphabet) and correctly omitted the warning when both companies shared a year-end
(JPMorgan/Bank of America). This shows the `compare_companies` tool's warning signal
is being used appropriately.

**Correct scope handling.** The edge-case question (BQ-19, fictitious ticker
ZZZZNOTREAL) was handled gracefully: the agent reported no results and offered to
search by company name. It did not fabricate a response. The agent enforces this
through structural guards: a tool-call mandate (every financial figure must come
from a tool return value), URL prohibition, and refusal rules. These reduce, but
cannot eliminate, the risk of an LLM stating unsupported figures; the evaluation
measures this directly (31/31 scope, 31/31 correctness, 8/8 numeric).

**Multi-step discovery.** Hard questions requiring search → resolve → retrieve chains
(BQ-17 Pfizer, BQ-18 Exxon) were attempted in the correct sequence, demonstrating
the agent understands tool chaining.

**Tool-returned URLs only.** Filing attribution questions (BQ-15, BQ-16) returned
correct accession numbers and EDGAR viewer URLs. The agent instructions explicitly
prohibit constructing or guessing URLs; every link in a response must come from a
tool return value.

### 3b. Issues identified and fixed

**Issue 1 — Wrong entity selected for multi-registrant corporations (BQ-18, high severity)**

When searching for "Exxon," the agent selected `ExxonMobil Holdings Corp`
(CIK 0002115436), a shell entity that files 10-Qs but no 10-Ks, rather than
`Exxon Mobil Corp` (CIK 0000034088), the operating entity. The agent then
correctly reported no 10-K filings — because the shell has none — but this left
the user with an unhelpful non-answer. Large corporations commonly have multiple
SEC registrants; the operating entity is not always the first alphabetical result.

*Addressed in:* server ranks search results by `has_recent_10k=true`; agent
instructions (Rule 1) require using the chosen entity's CIK and retrying with a
different name variant if no 10-K filings are found.

**Issue 2 — Year-to-date values returned as quarterly figures (BQ-09, BQ-10, BQ-20, high severity)**

SEC EDGAR XBRL stores both single-quarter (three-month) and year-to-date values
under the same fiscal period label (`fp=Q3`). The prior version of
`sec_edgar_get_quarterly_facts` did not distinguish between them. As a result, the
Q3 FY2026 revenue figure returned for Apple was ~$364 billion (the nine-month YTD)
rather than ~$109 billion (the true three-month quarter). Likewise, Q2 figures were
six-month totals rather than single quarters.

*Root cause:* XBRL observations are distinguished by their `start` and `end` date
fields — a three-month period and a nine-month period share the same `fp=Q3` tag
but span different durations. The tool was not filtering on duration.

*Addressed in:* `server.py` — `sec_edgar_get_quarterly_facts` now applies an 80–100
day duration filter: only observations where `end − start` falls in that window are
considered single-quarter. Longer periods (six- or nine-month YTD) are excluded. The
updated tool also deduplicates per `(start, end)` pair to prevent the same quarter
appearing twice when restated across multiple filings.

**Issue 3 — Q4 figures not separately filed in 10-Qs (BQ-09, BQ-10, BQ-20, medium severity)**

Companies file 10-Q reports for Q1, Q2, and Q3 only. Fiscal fourth-quarter figures
are not separately filed in a 10-Q; they appear either in the annual 10-K (as the
difference between full-year and Q1+Q2+Q3) or in an 8-K earnings release. The prior
agent instructions disclosed this as a limitation without providing data.

*Addressed in:* `server.py` — `sec_edgar_get_quarterly_facts` now derives Q4 for
USD monetary flow concepts by computing `annual FY value − nine-month YTD value`.
Derived rows are marked `derived: true` with a derivation note referencing both
accession numbers. Per-share units (e.g. EPS) and instant balance-sheet facts are
excluded from derivation with an explanatory note. Agent Rule 8 updated to describe
derived rows and explain when Q4 cannot be derived.

**Issue 4 — Annual fact labelling error (BQ-07, medium severity)**

The agent reported Apple's FY2024 net income as $96.7 billion and FY2023 as
$99.8 billion. Human cross-check found FY2024 was $93.7 billion and FY2023 was
$97.0 billion.

*Root cause:* The SEC's `fy` field on each observation records the fiscal year of the
**filing**, not the period being reported. A 10-K filed in fiscal year 2024 can
contain a comparative row for fiscal year 2023, and that row carries `fy=2024`. The
prior code used `fy` as the label, so each value was shown under the wrong year (e.g.
the FY2023 net income appeared as FY2024).

*Addressed in:* `server.py` — `sec_edgar_get_company_fact` now derives `fiscal_year`
from each observation's period-end date and the company's `fiscalYearEnd` field.
Observations are deduplicated to one row per fiscal-year end. The returned row shows
the latest-filed value; when a later filing revised an earlier period, the response
includes `as_originally_filed` and `recast` fields so the history is transparent.

**Issue 5 — Concept synonym gaps (BQ-11, BQ-12, medium severity)**

The `sec_edgar_list_concepts` tool searches by substring match on concept names and
labels. Revenue-related XBRL concepts include many tags that do not contain the word
"revenue" (e.g. `InterestAndDividendIncomeOperating`, `PremiumsEarnedNet`). Debt
concepts include tags without "debt" (e.g. `ShortTermBorrowings`, `FinanceLeaseLiability`).

*Addressed in:* Rule 7 updated in `agents/sec_edgar_agent.yaml` — the agent now
runs synonym keywords when a single search returns few results. Tool 9
(`sec_edgar_resolve_synonym`) added with 175 brand/colloquial name mappings, invoked
before any company lookup to ensure canonical SEC names are used.

**Issue 6 — Revenue concept selection (BQ-17, medium severity)**

Pfizer and other companies report revenue under `Revenues` (the broader concept),
not `RevenueFromContractWithCustomerExcludingAssessedTax`. The agent was returning
values from the wrong concept, producing figures ~15% lower than the actual revenue.

*Addressed in:* `server.py` — both `sec_edgar_get_company_fact` and
`sec_edgar_get_quarterly_facts` now evaluate all `REVENUE_CANDIDATES` and select
the concept whose most recent period end date is newest. This is a server-side fix
invisible to the agent and ensures the correct concept is always used.

**Issue 7 — Source filing URL construction (BQ-15, medium severity)**

In a BQ-15 regression run, the agent invented an EDGAR URL rather than using a
tool-returned value. The fabricated URL pointed to a plausible-looking but
unverifiable archive path.

*Addressed in:* server now computes a `filing_index_url` in every fact row
(deterministic from accession number and CIK, no extra HTTP call). Rule 6 of
`agents/sec_edgar_agent.yaml` explicitly prohibits constructing or guessing any URL;
every URL in a response must come from a tool return value.

---

## 4. What the automated scorer missed

The 20/20 pass rate from Layer 1 (tool routing) on the initial run was real and
meaningful, but it masked the issues above. The automated scorer asked "did the right
tool fire?" — it did not ask "was the value correct?" or "did the response confuse
the user?".

The Layer 1 scorer would mark BQ-09 (Apple quarterly revenue) as a pass because
`sec_edgar_get_quarterly_facts` fired. It cannot detect that the returned values
were nine-month totals rather than three-month figures. This is exactly the
measurement gap that LLM-as-judge scoring is designed to close.

---

## 5. Completed improvements

**All issues from the human audit and Phoenix runs are resolved:**
- ✅ YTD filtering: `sec_edgar_get_quarterly_facts` filters to 80–100 day duration
- ✅ Q4 derivation: annual minus nine-month YTD for USD flow concepts
- ✅ Annual fact labelling: `fiscal_year` derived from period-end date; one row per fiscal-year end; `as_originally_filed`/`recast` fields
- ✅ Revenue concept selection: REVENUE_CANDIDATES evaluated server-side
- ✅ Entity ranking: server ranks by `has_recent_10k=true` and `all_filers` source
- ✅ Concept synonym guidance: Rule 7 expanded; `sec_edgar_resolve_synonym` tool added (175 entries)
- ✅ Q4 derivation disclosure: Rule 8 updated to describe derived rows
- ✅ Source filing mandate: Rule 6 requires value stated before filing details; URL construction prohibited
- ✅ Dependency versions pinned: `fastmcp==4.1.3`, `httpx==0.28.1`, `pydantic==2.14.3`
- ✅ Global SEC rate limiter: `asyncio.Semaphore(8)` via `_edgar_get()` across all outbound calls
- ✅ 24h TTL companyfacts cache: `_FACTS_CACHE` reduces redundant EDGAR fetches within a session
- ✅ `sec_edgar_get_filing_text`: plain-text extraction of any SEC filing with TOC-aware section seeking
- ✅ `sec_edgar_full_text_search`: EFTS full-text search across all EDGAR filings
- ✅ `sec_edgar_screen`: company discovery by SIC code, exchange, state of incorporation
- ✅ `sec_edgar_get_earnings_release`: 8-K EX-99.1 press release parsing with EPS/revenue extraction

**Regression test coverage:** 246 assertions across 20 test functions (all passing).

---

## 6. LLM-as-Judge results (Layer 3)

### 6a. Llama-agent Phoenix experiments (2026-11-17) — superseded

These experiments used `meta-llama/llama-3-3-70b-instruct` as **both the agent and
the judge model**, and the judge's reference-answer mapping was not wired up. The
agent was driven directly from the Phoenix harness via the Code Engine MCP endpoint
— **not** via the production WXO environment. Results reflect the Llama model's
behaviour as an agent, not the production `gsa-hackathon` WXO agent. **These runs
are superseded by the production WXO scoring (§6b) and should not be used as a
quantitative benchmark.**

| Experiment | System Prompt | Dataset | Correctness | Scope |
|---|---|---|---|---|
| Experiment 2 | v1 (baseline) | sec-edgar-eval-0 (20 Qs) | **17 / 20 = 85%** | — |
| Experiment 3 | v2 (scope-bounded) | sec-edgar-eval-0 (20 Qs) | **18 / 20 = 90%** | — |

In Experiment 6 (RXhwZXJpbWVudDo2, sec-edgar-eval-1), the Llama agent fabricated a stock price and a
forecast for out-of-scope questions before refusal rules were added. Scope is not
shown for these runs because the judge's reference mapping was unbound and the
datasets predate the refusal rules. Remaining correctness failures (Apple quarterly
concept retry, Exxon entity disambiguation) have since been fixed.

### 6b. Production WXO agent scoring (2026-11-21)

The production `sec_edgar_agent` on `gsa-hackathon` was run against 31 benchmark
questions (`sec-edgar-eval-2`). Responses were scored using
`mistralai/mistral-small-3-1-24b-instruct-2503` as the judge with a **3-vote
majority** per question (each question judged three times independently; label
awarded to the majority; a 2-of-3 split is reported as "unstable"). Run date:
2026-11-21, commit `b7c6e6a`.

**Results:**

| Dimension | Score | Notes |
|---|---|---|
| Correctness (REST routing) | **31 / 31 (100%)** | All 31 questions: correct tool fired, substantive answer returned |
| Scope | **31 / 31 (100%)** | Agent never answered out-of-scope questions from training data |
| Numeric | **8 / 8 (100%)** | All 8 questions with numeric anchors pass within stated tolerances (0.5–2%) |

All 31 questions passed unanimously. No question was classified incorrect or partial.

### 6c. Consistency with human audit and production scoring

- Production scoring: scope = 31/31 — the agent never fabricated an answer for an
  out-of-scope question. The Llama-agent runs predate the refusal rules and are
  superseded; scope 100% is a production-only result.
- YTD-vs-quarterly fix (BQ-09, BQ-10): production scoring shows these passing after
  the 80–100 day duration filter and Q4 derivation. The Llama runs predate those
  fixes and are not comparable.
- Revenue concept selection fix (BQ-17): production scoring shows BQ-17 correct with
  numeric pass, confirming the REVENUE_CANDIDATES server fix is working.
- Annual fact labelling fix (BQ-07): production scoring shows BQ-07 correct with
  numeric pass ($93.7B and $97.0B both present).
- New tool coverage (BQ-24–BQ-31): all 8 new questions covering `get_filing_text`,
  `full_text_search`, `screen`, and `get_earnings_release` passed on first run.

### 6d. Evaluation method changes

The evaluation harness evolved significantly across three dataset generations:

| Change | Detail |
|---|---|
| `sec-edgar-eval-0` → `sec-edgar-eval-1` | Added 3 questions (20 → 23); first scope/relevance judge |
| `sec-edgar-eval-1` → `sec-edgar-eval-2` | Corrected schema; numeric judge; date-aware judge prompt; 3-vote majority |
| `sec-edgar-eval-2` extended (27 → 31 Qs) | Added BQ-24–BQ-27 (filing_text, full_text_search); BQ-28–31 (screen, earnings_release) |
| Deterministic numeric judge | `must_include`, `rel_tol`, `max_value` checks separate from LLM correctness |
| Date-aware judge prompt | Fiscal-year clarification paragraph prevents training-cutoff contamination |
| 3-vote majority judge | Each question judged 3× independently; 2-of-3 split reported as "unstable" |
| 11-case sanity suite | `eval/phoenix/judges/sanity_check.py` — ground-truth fixture cases; 11/11 PASS |

---

*Human audit: Michael Schihl, 2026-11-11*  
*Llama-agent Phoenix experiments: 2026-11-17*  
*Production WXO scoring (31 Qs): 2026-11-21*  
*Report updated: 2026-11-21*
