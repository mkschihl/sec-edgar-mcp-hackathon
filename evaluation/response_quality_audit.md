# SEC EDGAR Agent — Response Quality Audit

**Purpose:** Human annotation of the 20 agent responses from the 2026-11-07 evaluation run.
These notes feed directly into two outputs:
1. Prompt/instruction improvements in `agents/sec_edgar_agent.yaml`
2. The narrative section of `evaluation/interpretation.md`

**Scoring key for each response:**

| Mark | Meaning |
|---|---|
| ✅ | Good — meets the quality bar; no action needed |
| ⚠️ | Minor issue — response is usable but has a specific, fixable problem |
| ❌ | Real problem — response is confusing, misleading, or incomplete in a meaningful way |

**Dimensions to evaluate** (not every dimension applies to every question):

| Dimension | What to look for |
|---|---|
| **Accuracy** | Are the numbers correct? (spot-check one or two against SEC EDGAR) |
| **Completeness** | Did it answer the whole question, or leave parts out? |
| **Clarity** | Is the structure easy to scan? Appropriate use of tables/lists? |
| **Units** | Are dollar amounts labelled (USD, billions, per share)? |
| **Temporal labels** | Are fiscal years / quarter labels explicit (FY2025, Q3 FY2026)? |
| **Source traceability** | Are accession numbers present when needed? |
| **Hedging / caveats** | Are warnings appropriate and proportionate — or excessive? |
| **Scope behaviour** | For edge-case questions: did it stay in scope / refuse correctly? |

---

> **How to fill this in:**
> Write a 1–4 sentence note for each question using the dimensions above.
> Use the mark (✅ / ⚠️ / ❌) at the start of each note.
> Focus on what a human user would actually experience reading that response.
> Notes don't need to be exhaustive — flag the most important thing per question.
> Positive notes are just as useful as negative ones (they confirm what to keep).

---

## BQ-01 — company_search (easy)
**Question:** Find all companies with 'Berkshire' in their name.

<!-- 
✅   The format of the response is what I expect.
⚠️   The class of stock is obvious in this case, but in other cases the stock class may not be clear. Separating the "main" ticker from the class designator may be useful for users. 
 -->
<!-- Pre-loaded observation: Response correctly returns BRK-A and BRK-B in a clean table.
     Note it says "limited to the first 10 matches" but only returns 2 — is that because
     only 2 exist, or because the tool hit a limit? Worth verifying in EDGAR. -->


---

## BQ-02 — company_search (easy)
**Question:** I'm looking for companies related to 'General Electric'. What comes up?

<!-- 
✅   The format of the response is what I expect.
⚠️   Why do the tickers have leading and trailing asterisks (**TICKER**)? 
 -->
<!-- Pre-loaded observation: Returns GE and Portland General Electric. Missing GEV
     (GE Vernova, spun off 2024) which is a separately-listed entity. Worth checking
     whether the search tool would surface it with a broader limit. -->


---

## BQ-03 — company_resolution (easy)
**Question:** What is the SEC CIK number and industry classification for Microsoft?

<!-- 
✅   Information seems accurate.
⚠️   Will presenting the SIC number together with the description lead to problems with systems that ingest this? 
-->
<!-- Pre-loaded observation: Clean, correct, concise. CIK 0000789019 and SIC 7372 are accurate.
     No issues. -->


---

## BQ-04 — company_resolution (easy)
**Question:** Tell me about Alphabet Inc. — what state is it incorporated in and what SIC code does it use?

<!-- 
⚠️   I agree that the information here is terse, but it answered the specific question. Having the ticker (or tickers) and the CIK seem useful, although the question did not ask for this.
 -->
<!-- Pre-loaded observation: Correct (DE, SIC 7370). Very terse — a single sentence.
     Consider whether the user would also want the CIK and ticker, which the tool returns
     but the agent chose not to include. -->


---

## BQ-05 — recent_filings (easy)
**Question:** List the five most recent 10-K filings for Microsoft.

<!-- 
✅   Information is accurate and completely answers the question.
✅   The most recent filing (2026-07-29) is not future-dated, as the pre-loaded observation states. -->
<!-- Pre-loaded observation: Excellent response. Full table with filing date, period end,
     accession number, form type, and primary document filename. The most recent filing
     (2026-07-29) is future-dated relative to evaluation time — confirm this is real SEC data,
     not hallucinated. -->


---

## BQ-06 — recent_filings (easy)
**Question:** Show me the 10 most recent 10-Q filings for Johnson & Johnson (ticker: JNJ).

<!-- 
✅   The response completely answered the question. -->
<!-- Pre-loaded observation: Full 10-row table, clean format, correct form type throughout.
     No issues flagged. -->


---

## BQ-07 — annual_facts (medium)
**Question:** Show me the last 5 annual net income figures for Apple.

<!-- 
❌    2024 Net income is incorrect. The 2024 filing lists net income at $93,736 million (or $93.7 billion). This is the same figure in the 2026 filing showing 2024's net income.
❌   2023 Net income is incorrect. The 2023 filing lists net income at $96,995 million (or $97.0 billion). This is the same figure in the 2024 filing showing 2023's net income.   -->
<!-- Pre-loaded observation: Clean table, fiscal years labelled, accession numbers present.
     FY2022 and FY2023 both show $99.8B — worth confirming this is accurate (Apple's net
     income was essentially flat in those years) rather than a data artifact. -->


---

## BQ-08 — annual_facts (medium)
**Question:** What were Amazon's total assets for the last 4 fiscal years?

<!-- 
✅   Figures are accurate. 
✅   Table presents information requested. -->
<!-- Pre-loaded observation: Clean table with fiscal year end dates, bold values, accession
     numbers. Mentions balance-sheet / Form 10-K in the footnote. No issues flagged. -->


---

## BQ-09 — quarterly_facts (medium)
**Question:** Show me Apple's quarterly revenue for the last 8 quarters.

<!-- 
❌   Net sales (revenue) for the quarter ending June 27, 2026 (2026-06-27) was $109,417 million. The response gave the net sales (revenue) for the nine (9) months ending on 2026-06-27. The agent picked up the information under the columns with the heading "Nine Months Ended" instead of "Three Months Ended."
❌   Net sales (revenue) for the quarter ending March 28, 2026 (2026-03-28) was $111,184 million. The response gave the net sales (revenue) for the nine (9) months ending on 2026-03-28. The agent picked up the information under the columns with the heading "Nine Months Ended" instead of "Three Months Ended."
⚠️   Net sales (revenue) for the quarter ending December 27, 2025 (2025-12-27) was accurate, probably because the form only included columns for "Three Months Ended," whereas other quarters included columns for "Nine Months Ended." 
❌   Net sales (revenue) for the quarter ending June 28, 2025 (2025-06-28) was $146,860 million. The response gave the net sales (revenue) for the nine (9) months ending on 2025-06-28. The agent picked up the information under the columns with the heading "Nine Months Ended" instead of "Three Months Ended."
❌   I agree with the pre-loaded observations.
❌   Fiscal fourth quarter figures are not included in the output. Companies do not file a 10-Q for the fourth quarter of their fiscal year. That quarterly data could be derived from its 10-K data (i.e., subtract Q1, Q2, Q3 figures from annual figure) or should be in its 8-K.
-->
<!-- ⚠️ PRE-LOADED OBSERVATION — NEEDS ATTENTION:
     Response only returns 3 populated rows out of 8 requested. The remaining 5 show
     "data not returned in the last 8 observations" with em-dashes. Additionally there
     is a confusing "alternate series" row for Q3 FY2025 ($94B vs $313.7B) with no
     explanation of why two values exist for the same quarter. The agent's note at the
     bottom is helpful but buried. A user would likely be confused by this response.
     This is a candidate for an instruction improvement: tell the agent to increase the
     observation limit before reporting missing data. -->


---

## BQ-10 — quarterly_facts (medium)
**Question:** What was Microsoft's net income in each of the last 6 quarters?

<!-- 
❌  The agent response states that "the most recent six *distinct* quarters are Q1 FY 2027, Q3 FY 2026, Q2 FY 2026, Q1 FY 2026, and the prior‑year counterparts for Q3 FY 2025 and Q2 FY 2025." However, the most recent distinct quarters, by construction, are Q1 FY 2027, Q4 FY 2026, Q3 FY 2026, Q2 FY 2026, Q1 FY 2026, and Q4 2025. 
⚠️   The fiscal years are correct, but since fiscal years differ among companies, having the calendar end date would be useful.
❌   There were no fourth quarter figures. Companies do not file a 10-Q for the fourth quarter of their fiscal year. That quarterly data could be derived from its 10-K data (i.e., subtract Q1, Q2, Q3 figures from annual figure) or should be in its 8-K.   

 -->
<!-- ⚠️ PRE-LOADED OBSERVATION — NEEDS ATTENTION:
     Q3 FY2025 shows $97.98B and Q2 FY2025 shows $66.21B as "prior-year counterparts"
     from the same filing as the current-year quarters. These are annual (YTD) figures
     misrepresented as quarterly. A user asking for "last 6 quarters" would expect six
     distinct single-quarter values, not a mix of quarterly and cumulative YTD numbers.
     The footnote tries to explain it, but this is a real data-quality issue worth
     addressing in the agent instructions. -->


---

## BQ-11 — concept_discovery (medium)
**Question:** What revenue-related XBRL concepts does Apple report in us-gaap?

<!-- 
❌   "Revenue" and "Sales" are sometimes used interchangeably.  
❌   Other revenue-related concepts do not have the word revenue embedded in them, e.g., InterestAndDividendIncomeOperating, InterestIncomeOperating, InterestIncomeExpenseNet, NoninterestIncome, InvestmentBankingAdvisoryBrokerageAndUnderwritingFeesAndCommissions, PremiumsEarnedNet, NetInvestmentIncome, PolicyChargesAndFeeIncome, OperatingLeaseLeaseIncome, DirectFinancingLeaseInterestIncome, SalesTypeLeaseInterestIncome, RealEstateRevenueNet, SalesGoodsNet, SalesServicesNet, RegulatedAndUnregulatedOperatingRevenue, ElectricUtilitySales, GasUtilitySales, OilAndGasSales, FeesAndCommissions, RoyaltyIncomeNonoperating, LicenseAndServiceFees, BrokerageCommissions-->
<!-- Pre-loaded observation: Good response. Returns 8 concepts in a clean table with
     human-readable labels. Correctly flags deprecated concepts (SalesRevenueNet,
     SalesRevenueServicesGross). Offers to retrieve actual data. No issues flagged. -->


---

## BQ-12 — concept_discovery (medium)
**Question:** I want to find debt-related financial concepts for Tesla. What us-gaap concepts are available?

<!-- 
❌   Some debt-related concepts, such as ShortTermBorrowings, CommercialPaper,  FinanceLeaseLiabilityCurrent, FinanceLeaseLiabilityNoncurrent, OperatingLeaseLiabilityCurrent, OperatingLeaseLiabilityNoncurrent, CapitalLeaseObligationsCurrent, CapitalLeaseObligationsNoncurrent, SeniorNotes, SeniorLongTermNotes, LineOfCredit, LongTermLineOfCredit, NotesPayable, LoansPayable, etc. do not have the term "Debt" in their title.  -->
<!-- ⚠️ PRE-LOADED OBSERVATION:
     Response fires 3 tools (sec_edgar_get_company_fact, sec_edgar_list_concepts,
     sec_edgar_compare_companies) for a question that should only need list_concepts.
     The extra tool calls suggest over-routing. The actual concept list returned is
     useful (20 of 72 matches shown), but the table is truncated mid-cell on the last row.
     Also note: "AvailableForSale" debt securities concepts are investment-side items,
     not operational debt — a more targeted search might filter for LongTermDebt,
     DebtInstrument, etc. first. -->


---

## BQ-13 — cross_company_comparison (hard)
**Question:** Compare the most recent annual net income for Apple, Microsoft, and Google.

<!-- 
⚠️   We have already discussed misalignment, but it's worth keeping in mind. -->
<!-- Pre-loaded observation: Excellent response. Clean comparison table, fiscal year end
     dates included, fiscal year misalignment warning surfaced proactively. All three
     companies present. Net income values appear plausible. No issues flagged. -->


---

## BQ-14 — cross_company_comparison (hard)
**Question:** Which company has more total assets — JPMorgan Chase (JPM) or Bank of America (BAC)?

<!-- 
✅   Figures are accurate. -->
<!-- Pre-loaded observation: Clean, direct answer with a "Conclusion" statement.
     Both fiscal year ends are 2025-12-31 (aligned), so no comparability warning needed
     and none was given — correct judgement. No issues flagged. -->


---

## BQ-15 — filing_attribution (hard)
**Question:** Which SEC filing reported Apple's most recent annual revenue? Give me the accession number and a link to the filing.

<!-- 
✅   This response is accurate and the link worked correctly.  -->
<!-- Pre-loaded observation: Good response. Provides accession number, a hyperlinked filing
     title, form type, filing date, report date, and the revenue figure with the concept
     name. The EDGAR viewer URL format looks correct. Revenue figure ($478.8B) is plausible
     for FY2026. No issues flagged. -->


---

## BQ-16 — filing_attribution (hard)
**Question:** What form type and filing date corresponds to Microsoft's most recent annual net income figure?

<!-- 
✅   This response answered the question completely and accurately. -->
<!-- Pre-loaded observation: Accurate, clean. Provides form type, filing date, period end,
     accession number, and a direct EDGAR link. The table format is slightly over-engineered
     for a single row — a prose answer might scan better — but this is minor. -->


---

## BQ-17 — multi_step_discovery (hard)
**Question:** I don't know the ticker — find companies with 'Pfizer' in the name, then show me the last 4 annual revenue figures for the main one.

<!-- 
⚠️   The figure provided for 2023‑12‑31 ($58.5 billion) matches the 10‑K filing for that year, but the 10-K for 2025-12-31 states that the revenue for 2023 was $59.553 billion. I don't know if we want to worry about minor discrepancies like this. The response answered accurately based on the filing for that year.  -->
<!-- Pre-loaded observation: Good multi-step execution. Identified PFE, retrieved 4 annual
     revenue figures with dates and accession numbers. Note the 2022 figure ($100.3B)
     reflects the COVID vaccine revenue spike — the agent reports the data without flagging
     this context. Consider whether the agent should note unusual year-over-year swings. -->


---

## BQ-18 — multi_step_discovery (hard)
**Question:** Search for companies with 'Exxon' in their name, resolve the main one, then list its 5 most recent 10-K filings.

<!-- 
❌   I agree with the pre-loaded observation.
⚠️   This was difficult for me to find with the SEC's EDGAR search tool (https://www.sec.gov/edgar/search/#/category=custom&entityName=exxon&forms=10-K). 
⚠️   Exxon Mobil (XOM) is different than ExxonMobil (XOM). The entity with 10-Ks is Exxon Mobil Corp (XOM), CIK 0000034088 -->
<!-- ❌ PRE-LOADED OBSERVATION — REAL PROBLEM:
     The search returned "ExxonMobil Holdings Corp" (CIK 0002115436) — this appears to be
     a holding company shell, NOT the main ExxonMobil Corp (ticker XOM, CIK 0000034088).
     The real ExxonMobil has extensive 10-K history. The agent then correctly reported
     that no 10-K was found in the recent submissions window for this CIK — but the root
     cause is that the wrong entity was selected from search results.
     This is the most significant quality failure in the evaluation set. The agent should
     either: (a) search more broadly and surface the top result by ticker match rather than
     first alphabetical match, or (b) warn the user when a resolved company has no recent
     10-K filings and suggest searching again. -->


---

## BQ-19 — edge_cases (easy)
**Question:** What SEC filings has the company with ticker ZZZZNOTREAL submitted recently?

<!-- 
✅   I agree with the pre-loaded observation. This ticker does not exist.  -->
<!-- Pre-loaded observation: Correct scope behaviour — politely reports not found and
     offers to search by company name instead. Appropriately concise. No issues. -->


---

## BQ-20 — edge_cases (medium)
**Question:** Show me Apple's quarterly EarningsPerShareBasicAndDiluted for the last 4 quarters.

<!-- 
❌   I agree with the pre-loaded observation.
❌   As noted above, there were no fourth quarter figures. Companies do not file a 10-Q for the fourth quarter of their fiscal year. That quarterly data should be in its 8-K.   
❌   Earnings per share for the quarter ending June 27, 2026 (2026-06-27) were: (1) basic - $2.03 and (2) diluted - $2.02. The response gave the figures for the nine (9) months ending on 2026-06-27. The agent picked up the information under the columns with the heading "Nine Months Ended" instead of "Three Months Ended."
❌   Earnings per share for the quarter ending March 28, 2026 (2026-03-28) were: (1) basic - $2.02 and (2) diluted - $2.01. The response gave the figures for the nine (9) months ending on 2026-03-28. The agent picked up the information under the columns with the heading "Nine Months Ended" instead of "Three Months Ended." -->
<!-- ⚠️ PRE-LOADED OBSERVATION:
     Only 2 of the requested 4 quarters are returned (Q3 FY2026 and Q2 FY2026). The agent
     correctly states the other two are unavailable but does not attempt to retrieve them
     with a larger observation window or try the annual EPS concept as a fallback.
     Positively: it correctly handles the non-standard concept name and returns both basic
     and diluted EPS in separate columns with per-share units. -->


---

## Summary Notes

<!-- After completing all 20 annotations, add a brief synthesis here:
     - Which 2-3 issues are most worth fixing in the agent instructions?
     1. Provide quarterly figures for FY end quarters, whether with 8-K data or, possibly, using math based on 10-K data combined with 8-K data and 10-Q data
     2. Make sure concept "synonyms" are provided. This may require another tool. 
     3. Make sure quarterly figures are truly for the three months ended and not the nine months ended or some other period. 
     4. Make sure that a thorough search for companies like ExxonMobil provides data. There were multiple CIKs, but only one had data (i.e., 10-K, 10-Q, 8-K). 
     - Which responses were unexpectedly good?
     1. The ticker search seemed to be pretty thorough, though I'd like to see more complicated patterns.
     - Any patterns across categories? 
     1. Quarterly data was missing for the fiscal-year end quarters. This may be due to relying on 10-Qs, which are not filed for the same end period as the 10-K. This data is in the 8-K. -->

---

## Recommended Agent Instruction Changes

<!-- List specific changes to propose for agents/sec_edgar_agent.yaml based on your notes.
     BQ-09/BQ-10/BQ-20: "Quartly data must include every quarter, including fiscal-year end data. Look for most quarters in 10-Qs, but fiscal-year end data should be in 8-Ks or be able to be derived from 10-K and the other data from Q1, Q2, and Q3 from the 10-Qs."
     BQ-09/BQ-10/BQ-20: "When reporting quarterly facts, verify values are single-period (not YTD or nine months ended, etc.) before presenting. Consider using multiple sources 10-Q for most quarters, 8-K for fourth quarter. Warn the user if YTD or non-quarter values are mixed in."
     BQ-18: "Multiple entities/CIKs for, effectively, the same company may have only one entity that reports 10-K, 10-Q, 8-Q, etc. Find that entity that actually reports or provide an option to choose which one, noting which entities have actual filings and which do not. When searching by name, prefer entities with a matching ticker over holding-company shells. Warn if the resolved company has no recent 10-K."
     BQ-11/BQ-12: "Concepts may include terms that do not include the term included for searching. For example, there are many revenue-related terms that do not include the text "revenue." Is it possible to build a tool to map tag names without relying on this string matching? Some proposals from a web search included the following:
     1. Check the Income Statement Presentation Tree (_pre.xml). Locate the abstract header IncomeStatementAbstract and grab the first positive line items appearing above CostOfGoodsAndServicesSold or OperatingExpenses.
     2. Filter by SIC Code. Apply industry-specific tag lists based on the company's Standard Industrial Classification (SIC) code (e.g., looking for InterestAndDividendIncomeOperating + NoninterestIncome for SIC codes 6021?6029).
 -->



