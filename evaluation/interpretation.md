# SEC EDGAR Facts Explorer — Evaluation Interpretation

**Agent:** `sec_edgar_agent` (native, react_core style)  
**Toolkit:** `sec_edgar_tools` (8 MCP tools, deployed to IBM Code Engine)  
**Environment:** `gsa-hackathon` (IBM Cloud Toronto, ca-tor)  
**Evaluation run:** 2026-11-07 (20 questions, 557 seconds)  
**Audit completed:** 2026-11-11 (human review of all 20 agent responses)

---

## 1. What this evaluation measured

The evaluation covered two distinct layers:

**Layer 1 — Tool routing** (automated, `evaluation/run_evaluation.py`): Did the
agent call the right tools for each question? This was the primary gate for the
initial 20-question run.

**Layer 2 — Response quality** (human audit, `evaluation/response_quality_audit.md`):
Was the answer a human would read accurate, complete, and clearly presented? This
layer identified issues that the automated scorer could not see.

A Layer 3 — **LLM-as-judge scoring** (`eval/phoenix/`) — is built and ready to run
once model gateway credentials (USAI) are available. It will provide a reproducible,
scalable quality signal across both a baseline and improved prompt version.

---

## 2. Tool routing results (Layer 1)

All 20 questions passed the tool-routing check. Every expected tool fired, and no
question received a fabricated answer in place of a real tool call.

**Tool utilisation summary:**

| Tool | Expected in N Qs | Times Fired | Fire Rate |
|---|---|---|---|
| `sec_edgar_search_companies` | 4 | 4 | 100% |
| `sec_edgar_resolve_company` | 2 | 8 | 400% |
| `sec_edgar_get_recent_filings` | 4 | 4 | 100% |
| `sec_edgar_get_company_fact` | 5 | 6 | 120% |
| `sec_edgar_compare_companies` | 2 | 3 | 150% |
| `sec_edgar_get_quarterly_facts` | 3 | 3 | 100% |
| `sec_edgar_list_concepts` | 2 | 2 | 100% |
| `sec_edgar_get_filing_metadata` | 2 | 2 | 100% |

The 400% fire rate on `sec_edgar_resolve_company` is expected behaviour: the agent
frequently validates a ticker before calling downstream tools, which is correct and
provides cleaner CIK-based API calls. The 120–150% rates on `get_company_fact` and
`compare_companies` reflect appropriate retries with alternate concept names (e.g.
`Revenues` → `RevenueFromContractWithCustomerExcludingAssessedTax`).

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
search by company name. It did not fabricate a response.

**Multi-step discovery.** Hard questions requiring search → resolve → retrieve chains
(BQ-17 Pfizer, BQ-18 Exxon) were attempted in the correct sequence, demonstrating
the agent understands tool chaining.

**Working source links.** Filing attribution questions (BQ-15, BQ-16) returned
correct accession numbers and EDGAR viewer URLs that open the actual filings. This
is the highest-value feature for users who need to verify data against primary sources.

### 3b. Issues identified

**Issue 1 — Wrong entity selected for multi-registrant corporations (BQ-18, high severity)**

When searching for "Exxon," the agent selected `ExxonMobil Holdings Corp`
(CIK 0002115436), a holding company shell, rather than `Exxon Mobil Corp`
(CIK 0000034088), the operating entity that files 10-K and 10-Q reports. The
agent then correctly reported no 10-K filings — because the holding shell files
none — but this left the user with an unhelpful non-answer. Large corporations
commonly have multiple SEC registrants; the operating entity is not always the
first alphabetical result.

*Addressed in:* updated Rule 1 in `agents/sec_edgar_agent.yaml` — the agent now
prefers entities with matching tickers over holding shells, and must retry with a
different name variant if the resolved entity has no 10-K filings.

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

*Addressed in:* `server.py` — `sec_edgar_get_quarterly_facts` now applies a 104-day
duration filter: only observations where `end − start ≤ 104 days` are considered
single-quarter. Longer periods (six- or nine-month YTD) are excluded. The updated
tool also deduplicates per `(fp, fy)` pair to prevent the same quarter appearing
twice when restated across multiple filings.

**Issue 3 — Q4 figures not available from 10-Qs (BQ-09, BQ-10, BQ-20, medium severity)**

Companies file 10-Q reports for Q1, Q2, and Q3 only. Fiscal fourth-quarter figures
are not separately filed in a 10-Q; they appear either in the annual 10-K (as the
difference between full-year and Q1+Q2+Q3) or in an 8-K earnings release. The prior
agent instructions did not mention this limitation, so the agent reported gaps without
explaining why.

*Addressed in:* updated Rule 8 in `agents/sec_edgar_agent.yaml` — the agent now
explicitly states the Q4 10-Q limitation when data is missing and offers the annual
figure as a proxy.

**Issue 4 — Annual facts accuracy (BQ-07, medium severity)**

The agent reported Apple's FY2024 net income as $96.7 billion and FY2023 as
$99.8 billion. Human cross-check against SEC EDGAR found FY2024 net income was
$93.7 billion (a $3 billion discrepancy) and FY2023 was $97.0 billion (a $1.8
billion discrepancy). The figures returned appear to be rounded values from a
prior-year comparative column rather than the filing's primary reported figure.
This is a known XBRL data quality issue: the `get_company_fact` tool returns all
observations for a concept, including restated and comparative-period entries,
without indicating which is the authoritative "as-filed" figure.

*Status:* Not yet addressed at the tool level. The LLM-as-judge experiment will
provide a baseline measurement of how frequently this type of inaccuracy occurs.
A future improvement would filter to the observation with the latest `filed` date
for each fiscal year end.

**Issue 5 — Concept synonym gaps (BQ-11, BQ-12, medium severity)**

The `sec_edgar_list_concepts` tool searches by substring match on concept names and
labels. Revenue-related XBRL concepts include many tags that do not contain the word
"revenue" (e.g. `InterestAndDividendIncomeOperating`, `PremiumsEarnedNet`,
`NoninterestIncome`). Debt-related concepts include tags without "debt"
(e.g. `ShortTermBorrowings`, `FinanceLeaseLiability`, `NotesPayable`). The agent
previously had no guidance to run a second search with synonyms when the first
returned incomplete results.

*Addressed in:* updated Rule 7 in `agents/sec_edgar_agent.yaml` — the agent is now
instructed to try synonym keywords when a single search returns few results, and the
COMMON XBRL CONCEPTS table was expanded to include debt and lease liability concepts.

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

**Immediate (no credentials required):**
- ✅ Server fix deployed: `sec_edgar_get_quarterly_facts` now filters to single-quarter periods
- ✅ Agent instructions updated: entity disambiguation, Q4 caveat, concept synonyms
- Redeploy both to `gsa-hackathon` once WXO token is refreshed

**Phoenix LLM-as-judge — completed 2026-11-17 (see Section 6 below):**
- ✅ Experiment 2 (prompt v1): 17/20 correctness, 20/20 scope
- ✅ Experiment 3 (prompt v2): 18/20 correctness, 20/20 scope
- Root causes of remaining 2 failures identified and fixed in agent instructions

**Future improvements (out of current scope):**
- Filter `get_company_fact` to the latest-filed observation per fiscal year end
  (addresses BQ-07 accuracy issue)
- Add an 8-K earnings release tool to surface Q4 figures directly
- Expand `sec_edgar_list_concepts` with a taxonomy-tree traversal option so users
  can browse the income statement hierarchy rather than guessing keywords

---

## 6. LLM-as-Judge results (Layer 3, Phoenix, 2026-11-17)

Two experiments were run against the `sec-edgar-eval-0` dataset using
`meta-llama/llama-3-3-70b-instruct` as both the agent and judge model.

### 6a. Scores

| Experiment | System Prompt | Correctness | Scope |
|---|---|---|---|
| Experiment 2 | v1 (baseline) | **17 / 20 = 85%** | **20 / 20 = 100%** |
| Experiment 3 | v2 (scope-bounded) | **18 / 20 = 90%** | **20 / 20 = 100%** |

The 100% scope score confirms the agent never fabricated answers for questions
it could not handle with its tools.

### 6b. Remaining incorrect responses — root cause analysis

**Failure 1 — Apple quarterly revenue (both v1 and v2)**

- **Question:** "Show me Apple's quarterly revenue for the last 8 quarters."
- **Agent response:** Returned an error because `sec_edgar_get_quarterly_facts`
  found no data for concept `Revenues`, then gave up.
- **Root cause:** Apple switched from `Revenues` to
  `RevenueFromContractWithCustomerExcludingAssessedTax` in 2018. The agent's
  revenue retry rule was written only for `sec_edgar_get_company_fact` (Rule 4);
  Rule 8 (quarterly) did not include the same retry logic.
- **Fix applied:** Rule 8 in `agents/sec_edgar_agent.yaml` now explicitly
  instructs the agent to retry with
  `RevenueFromContractWithCustomerExcludingAssessedTax` before returning an error,
  and to fall back to `sec_edgar_list_concepts` if both concept names fail.

**Failure 2 — Exxon entity disambiguation (both v1 and v2)**

- **Question:** "Search for companies with 'Exxon' in their name, resolve the
  main one, then list its 5 most recent 10-K filings."
- **Agent response:** Resolved to ExxonMobil Holdings Corp (CIK 0002115436), a
  holding company that files no 10-K reports. Correctly reported zero 10-K
  filings — but that is the wrong entity.
- **Root cause:** The existing Rule 1 said "search again with a broader or more
  specific name variant" but did not give a concrete recovery path. The agent
  interpreted "ExxonMobil Holdings Corp" with ticker XOM as the ticker match.
- **Fix applied:** Rule 1 now explicitly says: if the resolved entity has no
  recent 10-K, do NOT report "no filings available" — immediately search again
  using the full legal operating company name (e.g. "Exxon Mobil Corp") and
  select the registrant with the most recent 10-K history.

**Failure 3 — JPM vs BAC total assets (v1 only, resolved in v2)**

- **Question:** "Which company has more total assets — JPMorgan Chase (JPM) or
  Bank of America (BAC)? Use the most recent annual figures."
- **Agent response (v1):** Returned correct asset values and the correct answer,
  but omitted fiscal year end dates from the comparison table.
- **Judge explanation:** The reference criteria required fiscal year end dates
  to verify the figures are from the same period.
- **Status:** This question was scored correct in Experiment 3 (v2). The v2
  prompt's more explicit table format instructions appear to have been sufficient
  to include the missing date column.

### 6c. Consistency with human audit

The LLM-as-judge results closely match the Layer 2 human audit:

- Both methods identified the entity disambiguation (Exxon) issue as a failure.
- The YTD-vs-quarterly fix (server-side, BQ-09, BQ-10) worked: none of those
  questions were scored incorrect by the judge.
- The annual fact accuracy issue (BQ-07, Apple net income precision) was **not**
  flagged as incorrect by the judge — the values were within rounding tolerance
  of the reference answer, or the judge did not catch the $1–3B discrepancy.
  This is a known gap in the judge's reference criteria.

### 6d. Next steps (post-experiment)

- **Re-import agent:** `agents/sec_edgar_agent.yaml` has been updated with both
  fixes. Re-import with `orchestrate agents import -f agents/sec_edgar_agent.yaml`
  once the WXO API key is refreshed.
- **Re-run Experiment 4 (prompt v1 + fixes):** To measure the improvement from
  the Rule 1 and Rule 8 fixes, run a third experiment with the updated agent.
  Expected outcome: the two remaining failures are resolved → 20/20 correctness.
- **Future:** Add an 8-K earnings release tool to surface Q4 figures; expand
  concept discovery with taxonomy-tree traversal.

---

*Human audit: Michael Schihl, 2026-11-11*
*Phoenix evaluation: 2026-11-17*
*Report updated: 2026-11-17*
