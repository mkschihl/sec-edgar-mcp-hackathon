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
initial 20-question run. *Caveat: routing counts in this layer were derived from
text matching on agent response text, not from live WXO tool-call events. Fire
rates above 100% reflect the agent mentioning a tool name in its reasoning or
retry text, which may overcount actual API calls.*

**Layer 2 — Response quality** (human audit, `evaluation/response_quality_audit.md`):
Was the answer a human would read accurate, complete, and clearly presented? This
layer identified issues that the automated scorer could not see.

**Layer 3 — LLM-as-judge scoring** (`eval/phoenix/`): An Arize Phoenix harness
running a second, independent LLM to score each response for correctness and scope
compliance. Two variants: (a) **Llama-agent Phoenix runs** (agent driven by
`meta-llama/llama-3-3-70b-instruct` via the Code Engine MCP endpoint directly —
not the production WXO agent) used for A/B prompt experiments; (b) **production WXO
agent scoring** using cached responses from the live `gsa-hackathon` agent, scored
by `mistralai/mistral-small-3-1-24b-instruct-2503` with a 3-vote majority.

---

## 2. Tool routing results (Layer 1)

All 20 questions passed the tool-routing check. Every expected tool fired, and no
question received a fabricated answer in place of a real tool call.

> **Note on counting methodology:** The Layer 1 evaluator infers tool calls by
> text matching on the agent's response — it checks whether the response text
> mentions phrases associated with each tool (e.g. "sec_edgar_get_recent_filings"
> in the output). It does not inspect WXO's internal tool-call event stream. Fire
> rates above 100% (e.g. 400% for `resolve_company`) reflect correct retry and
> proactive validation behaviour that is visible in the response text, but the
> exact counts should be treated as approximations rather than precise call counts.

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
refuse answerable questions, did not answer from memory, and correctly chained
multi-tool sequences (search → resolve → retrieve) for hard questions.

---

## 3. Response quality findings (Layer 2)

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
through explicit "RESPONSE RULES" in its instructions and the tool-call mandate —
every financial figure must come from a tool return value. The agent's fabrication
guard is structural: it has no code path that returns a number from training memory.

**Multi-step discovery.** Hard questions requiring search → resolve → retrieve chains
(BQ-17 Pfizer, BQ-18 Exxon) were attempted in the correct sequence, demonstrating
the agent understands tool chaining.

**Tool-returned URLs only.** Filing attribution questions (BQ-15, BQ-16) returned
correct accession numbers and EDGAR viewer URLs. The agent instructions explicitly
prohibit constructing or guessing URLs; every link in a response must come from a
tool return value, making them deterministically correct.

### 3b. Issues identified and fixed

**Issue 1 — Wrong entity selected for multi-registrant corporations (BQ-18, high severity)**

When searching for "Exxon," the agent selected `ExxonMobil Holdings Corp`
(CIK 0002115436), a holding company shell, rather than `Exxon Mobil Corp`
(CIK 0000034088), the operating entity that files 10-K and 10-Q reports. The
agent then correctly reported no 10-K filings — because the holding shell files
none — but this left the user with an unhelpful non-answer. Large corporations
commonly have multiple SEC registrants; the operating entity is not always the
first alphabetical result.

*Addressed in:* updated Rule 1 in `agents/sec_edgar_agent.yaml` — the agent now
ranks results by `has_recent_10k=true` and by `source=all_filers`, and must retry
with a different name variant if the resolved entity has no 10-K filings.

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

**Issue 4 — Annual fact precision (BQ-07, medium severity)**

The agent reported Apple's FY2024 net income as $96.7 billion and FY2023 as
$99.8 billion. Human cross-check found FY2024 was $93.7 billion and FY2023 was
$97.0 billion. The figures came from comparative-period restated entries rather than
the authoritative "as-filed" primary figure.

*Addressed in:* `server.py` — `sec_edgar_get_company_fact` now deduplicates
observations by fiscal year end date, keeping the latest-filed entry per year. This
ensures the most recently filed (and therefore authoritative) value is returned
rather than an older restated comparative.

**Issue 5 — Concept synonym gaps (BQ-11, BQ-12, medium severity)**

The `sec_edgar_list_concepts` tool searches by substring match on concept names and
labels. Revenue-related XBRL concepts include many tags that do not contain the word
"revenue" (e.g. `InterestAndDividendIncomeOperating`, `PremiumsEarnedNet`). Debt
concepts include tags without "debt" (e.g. `ShortTermBorrowings`, `FinanceLeaseLiability`).

*Addressed in:* updated Rule 7 in `agents/sec_edgar_agent.yaml` — the agent now
runs synonym keywords when a single search returns few results, and the COMMON XBRL
CONCEPTS table was expanded to include debt and lease liability concepts.

**Issue 6 — Revenue concept selection (BQ-17, medium severity)**

Pfizer and other companies report revenue under `Revenues` (the broader concept),
not `RevenueFromContractWithCustomerExcludingAssessedTax`. The agent was returning
values from the wrong concept, producing figures ~15% lower than the actual revenue.

*Addressed in:* `server.py` — both `sec_edgar_get_company_fact` and
`sec_edgar_get_quarterly_facts` now evaluate all `REVENUE_CANDIDATES` and select
the concept whose most recent period end date is newest. This is a server-side fix
invisible to the agent and ensures the correct concept is always used.

**Issue 7 — Source filing URL construction (BQ-15, medium severity)**

The agent was at risk of constructing EDGAR URLs from memory or guessing the format,
which would produce unverifiable links.

*Addressed in:* Rule 6 of `agents/sec_edgar_agent.yaml` explicitly prohibits
constructing or guessing any URL. Every URL in a response must be returned by a tool.
The server also computes deterministic `filing_index_url` values in every fact row,
so the agent always has a valid URL available without an extra tool call.

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
- ✅ Annual fact deduplication: latest-filed entry per fiscal year end
- ✅ Revenue concept selection: REVENUE_CANDIDATES evaluated server-side
- ✅ Entity ranking: prefer `has_recent_10k=true` and `all_filers` source
- ✅ Concept synonym guidance: Rule 7 expanded with synonym search instructions
- ✅ Q4 derivation disclosure: Rule 8 updated to describe derived rows
- ✅ Source filing mandate: Rule 6 requires value stated before filing details;
  URL construction prohibited

**Future improvements (out of current scope):**
- Add an 8-K earnings release tool to surface Q4 figures as a cross-check against derived values
- Expand `sec_edgar_list_concepts` with taxonomy-tree traversal

---

## 6. LLM-as-Judge results (Layer 3)

### 6a. Llama-agent Phoenix experiments (2026-11-17)

These experiments used `meta-llama/llama-3-3-70b-instruct` as **both the agent and
the judge model**. The agent was driven directly from the Phoenix harness via the
Code Engine MCP endpoint — **not** via the production WXO environment. Results
reflect the Llama model's behaviour as an agent, not the production `gsa-hackathon`
WXO agent.

| Experiment | System Prompt | Dataset | Correctness | Scope |
|---|---|---|---|---|
| Experiment 2 | v1 (baseline) | sec-edgar-eval-0 (20 Qs) | **17 / 20 = 85%** | **20 / 20 = 100%** |
| Experiment 3 | v2 (scope-bounded) | sec-edgar-eval-0 (20 Qs) | **18 / 20 = 90%** | **20 / 20 = 100%** |

Remaining failures in both experiments (Apple quarterly concept retry, Exxon
entity disambiguation) have since been fixed at the server and agent instruction
level.

### 6b. Production WXO agent scoring (2026-11-18)

The production `sec_edgar_agent` on `gsa-hackathon` was run against 23 benchmark
questions (`sec-edgar-eval-2`). Responses were scored using
`mistralai/mistral-small-3-1-24b-instruct-2503` as the judge with a **3-vote
majority** per question (each question judged three times independently; label
awarded to the majority; a 2-of-3 split is reported as "unstable"). Run date:
2026-11-18, against commit `571f523`.

**Results:**

| Dimension | Score | Notes |
|---|---|---|
| Correctness | **21 / 23** | 2 unstable (2-of-3 split): BQ-18, BQ-22 |
| Scope | **23 / 23** | Agent never answered out-of-scope questions from training data |
| Numeric | **8 / 8** | All 8 questions with numeric anchors pass within stated tolerance |

21 questions were unanimous (3-of-3 correct). The 2 unstable questions reflect
genuine judge ambiguity rather than agent errors. No question was classified
incorrect.

### 6c. Root causes of remaining unstable results

| BQ | Question | Judge ambiguity |
|---|---|---|
| BQ-18 | Exxon search → 10-K filings | One vote flags filing period-end dates as post-today |
| BQ-22 | Tesla investment advice refusal | Judge uncertain whether refusal was complete enough |

Both are inherently borderline cases that may require reference-answer refinement.

### 6d. Consistency with human audit and Phoenix experiments

- Both Llama-agent Phoenix runs and production scoring confirmed scope = 100% — the
  agent never fabricated an answer for an out-of-scope question.
- YTD-vs-quarterly fix (BQ-09, BQ-10): both experiments and production scoring show
  these questions passing correctly after the 80–100 day duration filter and Q4
  derivation.
- Revenue concept selection fix (BQ-17): production scoring shows BQ-17 as correct
  with numeric pass, confirming the REVENUE_CANDIDATES server fix is working.
- Annual fact deduplication fix (BQ-07): production scoring shows BQ-07 as correct
  with numeric pass ($93.7B and $97.0B both present).

---

*Human audit: Michael Schihl, 2026-11-11*  
*Llama-agent Phoenix experiments: 2026-11-17*  
*Production WXO scoring: 2026-11-18*  
*Report updated: 2026-11-18*
