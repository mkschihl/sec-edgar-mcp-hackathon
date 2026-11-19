# SEC EDGAR Facts Explorer — Evaluation Interpretation

**Agent:** `sec_edgar_agent` (native, react_core style)  
**Toolkit:** `sec_edgar_tools` (8 MCP tools, deployed to IBM Code Engine)  
**Environment:** `gsa-hackathon` (IBM Cloud Toronto, ca-tor)  
**Initial evaluation run:** 2026-11-07 (20 questions, 557 seconds)  
**Human audit completed:** 2026-11-11 (review of all 20 agent responses)  
**Production WXO scoring:** 2026-11-18 (23 questions, Mistral Small 3-vote majority judge)

---

## 1. What this evaluation measured

The evaluation covered three distinct layers:

**Layer 1 — Tool routing** (automated, `evaluation/run_evaluation.py`): Did the
agent call the right tools for each question? This was the primary gate for the
initial 20-question run. *Caveat: the 2026-11-07 run counted tool appearances once
per question by text-matching the SSE stream and response text — not from live WXO
tool-call events. Fire rates above 100% mean the tool name appeared in questions
where it was not expected, not that retries were counted. The runner now uses real
WXO `tool_calls` events.*

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

All 20 questions passed the tool-routing check. Every expected tool fired.

> **Note on counting methodology (2026-11-07 run):** The evaluator counted each
> tool once per question by text-matching the SSE stream and response content. Fire
> rates above 100% (e.g. 400% for `resolve_company`) indicate the tool name
> appeared in questions where it was not listed as expected, not that extra retries
> were observed. These counts are estimates; the runner was later updated to consume
> real WXO `tool_calls` events.

**Tool utilisation summary:**

| Tool | Expected in N Qs | Times Fired | Fire Rate |
|---|---|---|---|
| `sec_edgar_search_companies` | 4 | 4 | 100% |
| `sec_edgar_resolve_company` | 2 | 8 | ~400% (text-match estimate) |
| `sec_edgar_get_recent_filings` | 4 | 4 | 100% |
| `sec_edgar_get_company_fact` | 5 | 6 | ~120% (text-match estimate) |
| `sec_edgar_compare_companies` | 2 | 3 | ~150% (text-match estimate) |
| `sec_edgar_get_quarterly_facts` | 3 | 3 | 100% |
| `sec_edgar_list_concepts` | 2 | 2 | 100% |
| `sec_edgar_get_filing_metadata` | 2 | 2 | 100% |

**Interpretation:** The tool routing instructions are working. The agent did not
refuse answerable questions and correctly chained multi-tool sequences
(search → resolve → retrieve) for hard questions.

---

## 3. Response quality findings (Layer 2)

The 2026-11-11 audit found five issues. Two more (revenue concept selection, URL
construction) were found during later evaluation and Phoenix runs. All seven have
been addressed.

The human audit reviewed all 20 responses across the eight quality dimensions
(accuracy, completeness, clarity, units, temporal labels, source traceability,
hedging, and scope behaviour). Key findings are summarised below.

### 3a. What the agent does well

**Clean, consistent table formatting.** Across all 20 responses the agent presented
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
measures this directly (23/23 scope, 22/23 correctness, 8/8 numeric).

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

*Note:* ExxonMobil Holdings Corp does file 10-Qs and may eventually become the
primary registrant; if that happens, the BQ-18 routing assumption would need to
be revisited.

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

*Partly addressed:* updated Rule 7 in `agents/sec_edgar_agent.yaml` — the agent now
runs synonym keywords when a single search returns few results, and the COMMON XBRL
CONCEPTS table was expanded to include debt and lease liability concepts. A
server-side synonym/metric tool remains future work.

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

The 20/20 pass rate from Layer 1 (tool routing) is real and meaningful, but it masks
the issues above. The automated scorer asked "did the right tool fire?" — it did not
ask "was the value correct?" or "did the response confuse the user?".

The Layer 1 scorer would mark BQ-09 (Apple quarterly revenue) as a pass because
`sec_edgar_get_quarterly_facts` fired. It cannot detect that the returned values
were nine-month totals rather than three-month figures. This is exactly the
measurement gap that LLM-as-judge scoring is designed to close.

---

## 5. Next steps

**Completed fixes (all deployed or committed):**
- ✅ YTD filtering: `sec_edgar_get_quarterly_facts` filters to 80–100 day duration
- ✅ Q4 derivation: annual minus nine-month YTD for USD flow concepts
- ✅ Annual fact labelling: `fiscal_year` derived from period-end date; one row per fiscal-year end; `as_originally_filed`/`recast` fields
- ✅ Revenue concept selection: REVENUE_CANDIDATES evaluated server-side
- ✅ Entity ranking: server ranks by `has_recent_10k=true` and `all_filers` source
- ✅ Concept synonym guidance: Rule 7 expanded (partly; server synonym tool is future work)
- ✅ Q4 derivation disclosure: Rule 8 updated to describe derived rows
- ✅ Source filing mandate: Rule 6 requires value stated before filing details; URL construction prohibited
- ✅ Dependency versions pinned: `fastmcp==4.1.3`, `httpx==0.28.1`, `pydantic==2.14.3`

**Future improvements (out of current scope):**
- Server-side synonym/metric tool for XBRL concept discovery
- `companyconcept` endpoint with TTL caching to reduce redundant EDGAR calls
- Global SEC rate limiter shared across all tools
- 8-K earnings release tool to cross-check Q4 derived values
- `sec_edgar_list_concepts` taxonomy-tree traversal

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

### 6b. Production WXO agent scoring (2026-11-19)

The production `sec_edgar_agent` on `gsa-hackathon` was run against 23 benchmark
questions (`sec-edgar-eval-2`). Responses were scored using
`mistralai/mistral-small-3-1-24b-instruct-2503` as the judge with a **3-vote
majority** per question (each question judged three times independently; label
awarded to the majority; a 2-of-3 split is reported as "unstable"). Run date:
2026-11-19, commit `329b46c`.

**Results:**

| Dimension | Score | Notes |
|---|---|---|
| Correctness | **22 / 23** | 1 unstable (2-of-3 split): BQ-20 |
| Scope | **23 / 23** | Agent never answered out-of-scope questions from training data |
| Numeric | **8 / 8** | All 8 questions with numeric anchors pass within stated tolerances (0.5–2%) |

The 1 unstable question (BQ-20) was manually reviewed; the agent response was
correct. No question was classified incorrect.

### 6c. Root causes of remaining unstable results

| BQ | Question | Judge ambiguity |
|---|---|---|
| BQ-20 | Apple EPS (last 4 quarters) | One vote flags Q1 FY2026 value ($2.85/share) as outside reference range; value is correct — historical period ended before today |

This is a training-cutoff contamination artifact in the judge. The reference range
in the dataset ($1.00–$2.50/share) reflects FY2024 quarters; FY2026 quarters are
higher and correct. The reference answer has been updated in `build_dataset.py`
to explicitly allow FY2025/FY2026 EPS values above $2.50.

### 6d. Consistency with human audit and production scoring

- Production scoring: scope = 23/23 — the agent never fabricated an answer for an
  out-of-scope question. The Llama-agent runs predate the refusal rules and are
  superseded; scope 100% is a production-only result.
- YTD-vs-quarterly fix (BQ-09, BQ-10): production scoring shows these passing after
  the 80–100 day duration filter and Q4 derivation. The Llama runs predate those
  fixes and are not comparable.
- Revenue concept selection fix (BQ-17): production scoring shows BQ-17 correct with
  numeric pass, confirming the REVENUE_CANDIDATES server fix is working.
- Annual fact labelling fix (BQ-07): production scoring shows BQ-07 correct with
  numeric pass ($93.7B and $97.0B both present).

### 6e. Evaluation method changes

The evaluation harness evolved significantly across three dataset generations:

| Change | Detail |
|---|---|
| `sec-edgar-eval-0` → `sec-edgar-eval-1` | Added 3 questions (20 → 23); first scope/relevance judge |
| `sec-edgar-eval-1` → `sec-edgar-eval-2` | Corrected schema; numeric judge; date-aware judge prompt; 3-vote majority |
| Deterministic numeric judge | `must_include`, `rel_tol`, `max_value` checks separate from LLM correctness |
| Date-aware judge prompt | Fiscal-year clarification paragraph prevents training-cutoff contamination |
| 3-vote majority judge | Each question judged 3× independently; 2-of-3 split reported as "unstable" |
| 11-case sanity suite | `eval/phoenix/judges/sanity_check.py` — ground-truth fixture cases; 11/11 PASS |

---

*Human audit: Michael Schihl, 2026-11-11*
*Llama-agent Phoenix experiments: 2026-11-17*
*Production WXO scoring: 2026-11-18*
*Report updated: 2026-11-19*
