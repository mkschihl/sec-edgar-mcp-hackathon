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

**Pending USAI model gateway credentials:**
- Run `eval/phoenix/run_experiment.py --dataset-name sec-edgar-eval-0` with prompt v1
- Run same experiment with `--system-prompt-version v2` (scope-bounded prompt)
- Compare `correctness` scores between v1 and v2 runs in Phoenix UI
- Expected improvement areas: BQ-09, BQ-10, BQ-18, BQ-20 (the server fix and
  instruction changes address the root causes found in the human audit)

**Future improvements (out of current scope):**
- Filter `get_company_fact` to the latest-filed observation per fiscal year end
  (addresses BQ-07 accuracy issue)
- Add an 8-K earnings release tool to surface Q4 figures directly
- Expand `sec_edgar_list_concepts` with a taxonomy-tree traversal option so users
  can browse the income statement hierarchy rather than guessing keywords

---

*Human audit: Michael Schihl, 2026-11-11*  
*Report generated: 2026-11-11*
