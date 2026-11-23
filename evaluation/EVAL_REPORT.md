# SEC EDGAR Agent — Evaluation Report

**Agent:** `sec_edgar_agent`  
**Environment:** `gsa-hackathon` (IBM Cloud Toronto)  
**Run date:** 2026-11-23 05:50  
**Duration:** 348s for 35 questions  

---

## Summary

| Metric | Value |
|---|---|
| Total questions | 35 |
| ✅ Pass | 32 (91%) |
| ⚠️ Partial | 0 (0%) |
| ❌ Fail | 3 (9%) |

---

## Results by Question

| ID | Diff | Category | Score | Routing | Expected Tools | Tools Fired | Notes |
|---|---|---|---|---|---|---|---|
| BQ-01 | 🟢 easy | company_search | ❌ fail | routing_diff | `search_companies` | `screen` | routing_diff — no expected tools fired; missing: ['sec_edgar_search_companies']. |
| BQ-02 | 🟢 easy | company_search | ❌ fail | routing_diff | `search_companies` | `resolve_synonym` | routing_diff — no expected tools fired; missing: ['sec_edgar_search_companies']. |
| BQ-03 | 🟢 easy | company_resolution | ✅ pass | routing_ok | `resolve_company` | `resolve_synonym`, `resolve_company` | routing_ok — all expected tools fired. |
| BQ-04 | 🟢 easy | company_resolution | ✅ pass | routing_ok | `resolve_company` | `resolve_company`, `resolve_synonym` | routing_ok — all expected tools fired. |
| BQ-05 | 🟢 easy | recent_filings | ✅ pass | routing_ok | `get_recent_filings` | `resolve_synonym`, `resolve_company`, `get_recent_filings` | routing_ok — all expected tools fired. |
| BQ-06 | 🟢 easy | recent_filings | ✅ pass | routing_ok | `get_recent_filings` | `get_recent_filings` | routing_ok — all expected tools fired. |
| BQ-07 | 🟡 medium | annual_facts | ✅ pass | routing_ok | `get_company_fact` | `resolve_company`, `get_company_fact` | routing_ok — all expected tools fired. |
| BQ-08 | 🟡 medium | annual_facts | ✅ pass | routing_ok | `get_company_fact` | `resolve_synonym`, `get_company_fact` | routing_ok — all expected tools fired. |
| BQ-09 | 🟡 medium | quarterly_facts | ✅ pass | routing_ok | `get_quarterly_facts` | `resolve_company`, `get_quarterly_facts` | routing_ok — all expected tools fired. |
| BQ-10 | 🟡 medium | quarterly_facts | ✅ pass | routing_ok | `get_quarterly_facts` | `resolve_company`, `get_quarterly_facts` | routing_ok — all expected tools fired. |
| BQ-11 | 🟡 medium | concept_discovery | ✅ pass | routing_ok | `list_concepts` | `resolve_company`, `list_concepts` | routing_ok — all expected tools fired. |
| BQ-12 | 🟡 medium | concept_discovery | ✅ pass | routing_ok | `list_concepts` | `list_concepts` | routing_ok — all expected tools fired. |
| BQ-13 | 🔴 hard | cross_company_comparison | ✅ pass | routing_ok | `compare_companies` | `resolve_synonym`, `compare_companies` | routing_ok — all expected tools fired. |
| BQ-14 | 🔴 hard | cross_company_comparison | ✅ pass | routing_ok | `compare_companies` | `compare_companies` | routing_ok — all expected tools fired. |
| BQ-15 | 🔴 hard | filing_attribution | ❌ fail | routing_diff | `get_company_fact` | `resolve_company`, `get_recent_filings`, `get_filing_metadata` | routing_diff — no expected tools fired; missing: ['sec_edgar_get_company_fact']. |
| BQ-16 | 🔴 hard | filing_attribution | ✅ pass | routing_ok | `get_company_fact` | `resolve_synonym`, `get_company_fact`, `get_filing_metadata` | routing_ok — all expected tools fired. |
| BQ-17 | 🔴 hard | multi_step_discovery | ✅ pass | routing_ok | `search_companies`, `get_company_fact` | `search_companies`, `get_company_fact` | routing_ok — all expected tools fired. |
| BQ-18 | 🔴 hard | multi_step_discovery | ✅ pass | routing_ok | `search_companies`, `get_recent_filings` | `search_companies`, `get_recent_filings` | routing_ok — all expected tools fired. |
| BQ-19 | 🟢 easy | edge_cases | ✅ pass | routing_ok |  | `resolve_company` | routing_ok — all expected tools fired. |
| BQ-20 | 🟡 medium | edge_cases | ✅ pass | routing_ok | `get_quarterly_facts` | `resolve_synonym`, `get_quarterly_facts` | routing_ok — all expected tools fired. |
| BQ-21 | 🟢 easy | out_of_scope | ✅ pass | routing_ok |  | *(none)* | routing_ok — correctly declined out-of-scope question. |
| BQ-22 | 🟢 easy | out_of_scope | ✅ pass | routing_ok |  | *(none)* | routing_ok — correctly declined out-of-scope question. |
| BQ-23 | 🟡 medium | out_of_scope | ✅ pass | routing_ok |  | *(none)* | routing_ok — correctly declined out-of-scope question. |
| BQ-24 | 🟡 medium | filing_text | ✅ pass | routing_ok | `get_recent_filings`, `get_filing_text` | `resolve_company`, `get_recent_filings`, `get_filing_text` | routing_ok — all expected tools fired. |
| BQ-25 | 🔴 hard | filing_text | ✅ pass | routing_ok | `get_filing_text` | `resolve_company`, `get_recent_filings`, `get_filing_text` | routing_ok — all expected tools fired. |
| BQ-26 | 🟢 easy | full_text_search | ✅ pass | routing_ok | `full_text_search` | `full_text_search` | routing_ok — all expected tools fired. |
| BQ-27 | 🟡 medium | full_text_search | ✅ pass | routing_ok | `full_text_search` | `full_text_search` | routing_ok — all expected tools fired. |
| BQ-28 | 🟢 easy | screen | ✅ pass | routing_ok | `screen` | `screen` | routing_ok — all expected tools fired. |
| BQ-29 | 🟡 medium | screen | ✅ pass | routing_ok | `screen` | `screen` | routing_ok — all expected tools fired. |
| BQ-30 | 🟢 easy | earnings_release | ✅ pass | routing_ok | `get_earnings_release` | `resolve_synonym`, `get_earnings_release` | routing_ok — all expected tools fired. |
| BQ-31 | 🟡 medium | earnings_release | ✅ pass | routing_ok | `get_earnings_release` | `search_companies`, `get_earnings_release` | routing_ok — all expected tools fired. |
| BQ-32 | 🟢 easy | synonym_resolution | ✅ pass | routing_ok | `resolve_synonym` | `resolve_synonym` | routing_ok — all expected tools fired. |
| BQ-33 | 🟡 medium | synonym_resolution | ✅ pass | routing_ok | `resolve_synonym`, `resolve_company` | `resolve_synonym`, `resolve_company` | routing_ok — all expected tools fired. |
| BQ-34 | 🟢 easy | xbrl_concept_resolution | ✅ pass | routing_ok | `resolve_xbrl_concept` | `resolve_xbrl_concept` | routing_ok — all expected tools fired. |
| BQ-35 | 🟡 medium | xbrl_concept_resolution | ✅ pass | routing_ok | `resolve_xbrl_concept`, `get_company_fact` | `resolve_synonym`, `resolve_company`, `resolve_xbrl_concept`, `get_company_fact` | routing_ok — all expected tools fired. |

---

## Agent Responses

### BQ-01 — ❌ FAIL
**Question:** Find all companies with 'Berkshire' in their name.  
**Expected tools:** sec_edgar_search_companies  
**Tools fired:** sec_edgar_screen  

<details><summary>Agent response</summary>

```
Here are the companies whose legal name contains “Berkshire” (up to the first 20 matches returned by the SEC screen API):

| Company (legal name) | Ticker | CIK | SIC Code | SIC Description* | State of Incorporation |
|----------------------|--------|------|----------|------------------|------------------------|
| BERKSHIRE BANCORP INC /DE/ | – | 0000759718 | 6022 | Commercial Banks | NY |
| BERKSHIRE ENERGY RESOURCES | – | 0001056255 | 4924 | Natural Gas Distribution | MA |
| BERKSHIRE GAS CO /MA/ | – | 0000317406 | 4924 | Natural Gas Distribution | MA |
| Berkshire Grey, Inc. | – | 0001824734 | 3569 | Industrial Machinery | MA |
| BERKSHIRE HATHAWAY ENERGY CO | – | 0001081316 | 4900 | Gas Utilities | IA |
| **BERKSHIRE HATHAWAY INC** | BRK‑A | 0001067983 | 6331 | Insurance Carriers | NE |
| OBH LLC (formerly Berkshire Hathaway Inc.) | – | 0000109694 | 6331 | Insurance Carriers | NE |
| Beacon Financial Corp (formerly Berkshire Financial) | BBT | 0001108134 | 6036 | Savings Institutions | MA |
| Berkshire Homes, Inc. | – | 0001505124 | 6510 | Real Estate (Residential) | AZ |
| BERKSHIRE INCOME REALTY, INC. | – | 0001178862 | 6500 | Real Estate Investment Trusts | MA |
| BERKSHIRE REALTY CO INC /DE | – | 0000869446 | 6798 | Real Estate Investment Trusts | MA |

\*SIC descriptions are taken from the SEC’s SIC code reference.  

If you need more details on any of these entities—such as recent filings, financial facts, or the ability to read specific filing sections—just let me know!
```

</details>

### BQ-02 — ❌ FAIL
**Question:** I'm looking for companies related to 'General Electric'. What comes up?  
**Expected tools:** sec_edgar_search_companies  
**Tools fired:** sec_edgar_resolve_synonym  

<details><summary>Agent response</summary>

```
**Resolved company**

- **Canonical name:** GE Aerospace  
- **Ticker:** **GE**  

The alias “General Electric” maps to GE Aerospace (ticker GE) in the SEC’s registry. Let me know if you’d like to see recent filings, financial facts, or compare this company to others.
```

</details>

### BQ-03 — ✅ PASS
**Question:** What is the SEC CIK number and industry classification for Microsoft?  
**Expected tools:** sec_edgar_resolve_company  
**Tools fired:** sec_edgar_resolve_synonym, sec_edgar_resolve_company  

<details><summary>Agent response</summary>

```
**Microsoft Corp**  
- **CIK:** 0000789019  
- **Industry Classification (SIC):** 7372 – Services Prepackaged Software  
- **State of Incorporation:** Washington (WA)  

These details come directly from the SEC’s company registration data.
```

</details>

### BQ-04 — ✅ PASS
**Question:** Tell me about Alphabet Inc. — what state is it incorporated in and what SIC code does it use?  
**Expected tools:** sec_edgar_resolve_company  
**Tools fired:** sec_edgar_resolve_company, sec_edgar_resolve_synonym  

<details><summary>Agent response</summary>

```
Alphabet Inc. is incorporated in **Delaware (DE)** and uses SIC code **7370 – Services‑Computer Programming, Data Processing, Etc.**.
```

</details>

### BQ-05 — ✅ PASS
**Question:** List the five most recent 10-K filings for Microsoft.  
**Expected tools:** sec_edgar_get_recent_filings  
**Tools fired:** sec_edgar_resolve_synonym, sec_edgar_resolve_company, sec_edgar_get_recent_filings  

<details><summary>Agent response</summary>

```
Here are the five most recent Form 10‑K filings for **Microsoft Corp (ticker MSFT, CIK 0000789019)**:

| # | Filing Date | Report (Period End) | Accession Number | Primary Document |
|---|-------------|---------------------|------------------|------------------|
| 1 | 2026‑07‑29 | 2026‑06‑30 | 0001193125‑26‑323660 | msft-20260630.htm |
| 2 | 2025‑07‑30 | 2025‑06‑30 | 0000950170‑25‑100235 | msft-20250630.htm |
| 3 | 2024‑07‑30 | 2024‑06‑30 | 0000950170‑24‑087843 | msft-20240630.htm |
| 4 | 2023‑07‑27 | 2023‑06‑30 | 0000950170‑23‑035122 | msft-20230630.htm |
| 5 | 2022‑07‑28 | 2022‑06‑30 | 0001564590‑22‑026876 | msft-10k_20220630.htm |

These filings are the latest annual reports (10‑K) filed by Microsoft with the SEC.
```

</details>

### BQ-06 — ✅ PASS
**Question:** Show me the 10 most recent 10-Q filings for Johnson & Johnson (ticker: JNJ).  
**Expected tools:** sec_edgar_get_recent_filings  
**Tools fired:** sec_edgar_get_recent_filings  

<details><summary>Agent response</summary>

```
**Johnson & Johnson – 10 most recent 10‑Q filings**

| # | Filing Date | Report (Period End) | Accession Number | Primary Document |
|---|-------------|---------------------|------------------|------------------|
| 1 | 2026‑10‑21 | 2026‑09‑27 | 0000200406‑26‑000197 | jnj‑20260927.htm |
| 2 | 2026‑07‑23 | 2026‑06‑28 | 0000200406‑26‑000153 | jnj‑20260628.htm |
| 3 | 2026‑04‑22 | 2026‑03‑29 | 0000200406‑26‑000087 | jnj‑20260329.htm |
| 4 | 2025‑10‑22 | 2025‑09‑28 | 0000200406‑25‑000209 | jnj‑20250928.htm |
| 5 | 2025‑07‑24 | 2025‑06‑29 | 0000200406‑25‑000178 | jnj‑20250629.htm |
| 6 | 2025‑04‑23 | 2025‑03‑30 | 0000200406‑25‑000119 | jnj‑20250330.htm |
| 7 | 2024‑10‑23 | 2024‑09‑29 | 0000200406‑24‑000096 | jnj‑20240929.htm |
| 8 | 2024‑07‑25 | 2024‑06‑30 | 0000200406‑24‑000075 | jnj‑20240630.htm |
| 9 | 2024‑05‑01 | 2024‑03‑31 | 0000200406‑24‑000049 | jnj‑20240331.htm |
|10 | 2023‑10‑27 | 2023‑10‑01 | 0000200406‑23‑000102 | jnj‑20231001.htm |

**Company:** JOHNSON & JOHNSON  
**CIK:** 0000200406  

These filings are taken directly from the SEC’s filing index and represent the most recent quarterly reports (Form 10‑Q) filed by Johnson & Johnson.
```

</details>

### BQ-07 — ✅ PASS
**Question:** Show me the last 5 annual net income figures for Apple.  
**Expected tools:** sec_edgar_get_company_fact  
**Tools fired:** sec_edgar_resolve_company, sec_edgar_get_company_fact  

<details><summary>Agent response</summary>

```
**Apple Inc. – Net Income (Loss) Attributable to Parent** (XBRL concept: **NetIncomeLoss**, taxonomy: **us‑gaap**)  

| Fiscal Year | Period End | Net Income (USD) | Form | Accession Number | Filing Index URL |
|------------|------------|------------------|------|------------------|------------------|
| 2022 | 2022‑09‑24 | $99.8 billion | 10‑K | 0000320193‑24‑000123 | https://www.sec.gov/Archives/edgar/data/320193/000032019324000123/ |
| 2023 | 2023‑09‑30 | $97.0 billion | 10‑K | 0000320193‑25‑000079 | https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/ |
| 2024 | 2024‑09‑28 | $93.7 billion | 10‑K | 0000320193‑26‑000026 | https://www.sec.gov/Archives/edgar/data/320193/000032019326000026/ |
| 2025 | 2025‑09‑27 | $112.0 billion | 10‑K | 0000320193‑26‑000026 | https://www.sec.gov/Archives/edgar/data/320193/000032019326000026/ |
| 2026 | 2026‑09‑26 | $132.2 billion | 10‑K | 0000320193‑26‑000026 | https://www.sec.gov/Archives/edgar/data/320193/000032019326000026/ |

*Values are presented in US dollars and reflect the amounts reported in each company’s most recent annual (Form 10‑K) filing.*
```

</details>

### BQ-08 — ✅ PASS
**Question:** What were Amazon's total assets for the last 4 fiscal years?  
**Expected tools:** sec_edgar_get_company_fact  
**Tools fired:** sec_edgar_resolve_synonym, sec_edgar_get_company_fact  

<details><summary>Agent response</summary>

```
**Amazon.com, Inc. (Ticker: AMZN, CIK: 0001018724)**  

*XBRL Concept: **Assets** (us‑gaap)*  

| Fiscal Year | Period End | Total Assets (USD) | Form | Accession Number | Filing Index URL |
|-------------|------------|--------------------|------|------------------|------------------|
| 2022 | 2022‑12‑31 | $462.7 billion | 10‑K | 0001018724‑25‑000004 | https://www.sec.gov/Archives/edgar/data/1018724/000101872425000004/ |
| 2023 | 2023‑12‑31 | $527.9 billion | 10‑K | 0001018724‑26‑000004 | https://www.sec.gov/Archives/edgar/data/1018724/000101872426000004/ |
| 2024 | 2024‑12‑31 | $624.9 billion | 10‑K | 0001018724‑26‑000004 | https://www.sec.gov/Archives/edgar/data/1018724/000101872426000004/ |
| 2025 | 2025‑12‑31 | $818.0 billion | 10‑K | 0001018724‑26‑000004 | https://www.sec.gov/Archives/edgar/data/1018724/000101872426000004/ |

**Notes**

- Values are presented in US dollars and rounded to the nearest $0.1 billion for readability.  
- All figures are taken from the companies’ audited Form 10‑K filings.  
- No recasting was required; the values are as originally reported.
```

</details>

### BQ-09 — ✅ PASS
**Question:** Show me Apple's quarterly revenue for the last 8 quarters.  
**Expected tools:** sec_edgar_get_quarterly_facts  
**Tools fired:** sec_edgar_resolve_company, sec_edgar_get_quarterly_facts  

<details><summary>Agent response</summary>

```
**Apple Inc. – Quarterly Revenue (last 8 quarters)**  

| Fiscal Quarter | Fiscal Year | Period End | Revenue (USD) | Form | Accession Number | Derived? |
|----------------|------------|------------|---------------|------|------------------|----------|
| Q4 FY 2026 | 2026 | 2026‑09‑26 | $114.5 billion | 10‑K | 0000320193‑26‑000026 | Yes (annual – nine‑month YTD) |
| Q3 FY 2026 | 2026 | 2026‑06‑27 | $109.4 billion | 10‑Q | 0000320193‑26‑000020 | No |
| Q2 FY 2026 | 2026 | 2026‑03‑28 | $111.2 billion | 10‑Q | 0000320193‑26‑000013 | No |
| Q1 FY 2026 | 2026 | 2025‑12‑27 | $143.8 billion | 10‑Q | 0000320193‑26‑000006 | No |
| Q4 FY 2025 | 2025 | 2025‑09‑27 | $102.5 billion | 10‑K | 0000320193‑26‑000026 | Yes (annual – nine‑month YTD) |
| Q3 FY 2025 | 2025 | 2025‑06‑28 | $94.0 billion | 10‑Q | 0000320193‑26‑000020 | No |
| Q2 FY 2025 | 2025 | 2025‑03‑29 | $95.4 billion | 10‑Q | 0000320193‑26‑000013 | No |
| Q1 FY 2025 | 2025 | 2024‑12‑28 | $124.3 billion | 10‑Q | 0000320193‑26‑000006 | No |

*Concept used:* **RevenueFromContractWithCustomerExcludingAssessedTax** (the SEC‑preferred revenue concept for Apple; it was selected automatically when “Revenues” was requested).  

All values are reported in **U.S. dollars (USD)** and come from the respective 10‑K or 10‑Q filings indicated. The Q4 figures are **derived** by subtracting the nine‑month YTD total from the full‑year amount, as noted in the “Derived?” column.
```

</details>

### BQ-10 — ✅ PASS
**Question:** What was Microsoft's net income in each of the last 6 quarters?  
**Expected tools:** sec_edgar_get_quarterly_facts  
**Tools fired:** sec_edgar_resolve_company, sec_edgar_get_quarterly_facts  

<details><summary>Agent response</summary>

```
**Microsoft Corp – Net Income (Attributable to Parent) – Last 6 Quarters**

| Fiscal Quarter | Fiscal Year | Period End | Net Income (USD) | Form | Accession Number | Derived |
|----------------|------------|------------|------------------|------|------------------|---------|
| Q1 FY2027 | 2027 | 2026‑09‑30 | $36.63 billion | 10‑Q | 0001193125‑26‑436133 | No |
| Q4 FY2026 | 2026 | 2026‑06‑30 | $35.77 billion | 10‑K | 0001193125‑26‑323660 | **Yes** (derived: annual minus nine‑month YTD) |
| Q3 FY2026 | 2026 | 2026‑03‑31 | $31.78 billion | 10‑Q | 0001193125‑26‑191507 | No |
| Q2 FY2026 | 2026 | 2025‑12‑31 | $38.46 billion | 10‑Q | 0001193125‑26‑027207 | No |
| Q1 FY2026 | 2026 | 2025‑09‑30 | $27.75 billion | 10‑Q | 0001193125‑26‑436133 | No |
| Q4 FY2025 | 2025 | 2025‑06‑30 | $27.23 billion | 10‑K | 0001193125‑26‑323660 | **Yes** (derived: annual minus nine‑month YTD) |

**Concept used:** *NetIncomeLoss* (XBRL tag “NetIncomeLoss”, label “Net Income (Loss) Attributable to Parent”, taxonomy **us-gaap**).  

*Derived* indicates the Q4 value was calculated by the SEC system as the annual figure minus the nine‑month YTD figure, because Q4 flow items are not directly reported in 10‑K filings.
```

</details>

### BQ-11 — ✅ PASS
**Question:** What revenue-related XBRL concepts does Apple report in us-gaap?  
**Expected tools:** sec_edgar_list_concepts  
**Tools fired:** sec_edgar_resolve_company, sec_edgar_list_concepts  

<details><summary>Agent response</summary>

```
**Apple Inc. (CIK 0000320193) – Revenue‑related XBRL concepts in the us‑gaap taxonomy**

| XBRL Concept (tag) | Human‑readable label |
|--------------------|----------------------|
| ContractWithCustomerLiabilityRevenueRecognized | Contract with Customer, Liability, Revenue Recognized |
| DeferredRevenueCurrent | Deferred Revenue, Current |
| DeferredRevenueNoncurrent | Deferred Revenue, Noncurrent |
| IncreaseDecreaseInDeferredRevenue | Increase (Decrease) in Deferred Revenue |
| RevenueFromContractWithCustomerExcludingAssessedTax | Revenue from Contract with Customer, Excluding Assessed Tax |
| Revenues | Revenues |
| SalesRevenueNet | Revenue, Net (Deprecated 2018‑01‑31) |
| SalesRevenueServicesGross | Sales Revenue, Services, Other (Deprecated 2018‑01‑31) |

These are the revenue‑related concepts that Apple reports under the **us‑gaap** taxonomy, as returned by the SEC EDGAR “list concepts” endpoint. If you need values for any of these concepts (e.g., annual revenue figures) just let me know and I can retrieve the time‑series data.
```

</details>

### BQ-12 — ✅ PASS
**Question:** I want to find debt-related financial concepts for Tesla. What us-gaap concepts are available?  
**Expected tools:** sec_edgar_list_concepts  
**Tools fired:** sec_edgar_list_concepts  

<details><summary>Agent response</summary>

```
Here are the debt‑related us‑gaap concepts that Tesla Inc. reports (CIK 0001318605).  Each entry shows the exact XBRL tag (concept) and the human‑readable label used by the SEC filings.

| XBRL Concept | Human‑Readable Label |
|---|---|
| AdjustmentsToAdditionalPaidInCapitalEquityComponentOfConvertibleDebt | Adjustments to Additional Paid in Capital, Equity Component of Convertible Debt |
| AmortizationOfDebtDiscountPremium | Amortization of Debt Discount (Premium) |
| AmortizationOfFinancingCosts | Amortization of Debt Issuance Costs |
| AmortizationOfFinancingCostsAndDiscounts | Amortization of Debt Issuance Costs and Discounts |
| AvailableForSaleDebtSecuritiesAccumulatedGrossUnrealizedGainBeforeTax | Debt Securities, Available‑for‑sale, Accumulated Gross Unrealized Gain, before Tax |
| AvailableForSaleDebtSecuritiesAccumulatedGrossUnrealizedLossBeforeTax | Debt Securities, Available‑for‑sale, Accumulated Gross Unrealized Loss, before Tax |
| AvailableForSaleDebtSecuritiesAmortizedCostBasis | Debt Securities, Available‑for‑sale, Amortized Cost |
| AvailableForSaleDebtSecuritiesGrossUnrealizedGain | Debt Securities, Available‑for‑sale, Unrealized Gain |
| AvailableForSaleDebtSecuritiesGrossUnrealizedLoss | Debt Securities, Available‑for‑sale, Unrealized Loss |
| AvailableForSaleSecuritiesDebtMaturitiesNextRollingTwelveMonthsAmortizedCostBasis | Debt Securities, Available‑for‑sale, Maturity, Allocated and Single Maturity Date, Rolling within One Year, Amortized Cost |
| AvailableForSaleSecuritiesDebtMaturitiesNextRollingTwelveMonthsFairValue | Debt Securities, Available‑for‑sale, Maturity, Allocated and Single Maturity Date, Rolling within One Year, Fair Value |
| AvailableForSaleSecuritiesDebtMaturitiesRollingAfterYearTenAmortizedCostBasis | Debt Securities, Available‑for‑sale, Maturity, Allocated and Single Maturity Date, Rolling after 10 Years, Amortized Cost |
| AvailableForSaleSecuritiesDebtMaturitiesRollingYearSixThroughTenAmortizedCostBasis | Debt Securities...
```

</details>

### BQ-13 — ✅ PASS
**Question:** Compare the most recent annual net income for Apple, Microsoft, and Google.  
**Expected tools:** sec_edgar_compare_companies  
**Tools fired:** sec_edgar_resolve_synonym, sec_edgar_compare_companies  

<details><summary>Agent response</summary>

```
**Most recent annual net income (NetIncomeLoss) – USD**

| Company | Fiscal Year | Period End | Net Income | Form | Accession Number | Filing Index URL |
|---------|-------------|-----------|-----------|------|------------------|------------------|
| Apple Inc. | 2026 | 2026‑09‑26 | $132.2 billion | 10‑K | 0000320193‑26‑000026 | https://www.sec.gov/Archives/edgar/data/320193/000032019326000026/ |
| Microsoft Corp. | 2026 | 2026‑06‑30 | $133.7 billion | 10‑K | 0001193125‑26‑323660 | https://www.sec.gov/Archives/edgar/data/789019/000119312526323660/ |
| Alphabet Inc. (Google) | 2025 | 2025‑12‑31 | $132.2 billion | 10‑K | 0001652044‑26‑000018 | https://www.sec.gov/Archives/edgar/data/1652044/000165204426000018/ |

**Notes & warnings**

- The fiscal year‑ends differ across the three companies (Apple ends 9/26, Microsoft 6/30, Alphabet 12/31), so the periods are not directly calendar‑year aligned.  
- Net‑income values are taken from the most recent full‑year filing (Form 10‑K) for each company, using the XBRL concept **NetIncomeLoss**.
```

</details>

### BQ-14 — ✅ PASS
**Question:** Which company has more total assets — JPMorgan Chase (JPM) or Bank of America (BAC)? Use the most recent annual figures.  
**Expected tools:** sec_edgar_compare_companies  
**Tools fired:** sec_edgar_compare_companies  

<details><summary>Agent response</summary>

```
**Total Assets (most recent FY 2025)**  

| Company | FY 2025 Assets | Unit | Period End | Form | Accession Number | Filing Index URL |
|---|---|---|---|---|---|---|
| JPMorgan Chase & Co | $4.425 trillion | USD | 2025‑12‑31 | 10‑K | 0001628280‑26‑008131 | https://www.sec.gov/Archives/edgar/data/19617/000162828026008131/ |
| Bank of America Corp | $3.412 trillion | USD | 2025‑12‑31 | 10‑K | 0000070858‑26‑000157 | https://www.sec.gov/Archives/edgar/data/70858/000007085826000157/ |

**Answer:** JPMorgan Chase reports higher total assets than Bank of America for the most recent fiscal year (FY 2025).  

*Concept used:* **Assets** (XBRL tag `Assets` in the `us-gaap` taxonomy).
```

</details>

### BQ-15 — ❌ FAIL
**Question:** Which SEC filing reported Apple's most recent annual revenue? Give me the accession number and a link to the filing.  
**Expected tools:** sec_edgar_get_company_fact  
**Tools fired:** sec_edgar_resolve_company, sec_edgar_get_recent_filings, sec_edgar_get_filing_metadata  

<details><summary>Agent response</summary>

```
Apple Inc.’s most recent annual revenue is reported in its FY 2026 Form 10‑K filing.

**Accession Number:** 0000320193‑26‑000026  
**Filing URL:** https://www.sec.gov/Archives/edgar/data/320193/000032019326000026/aapl-20260926.htm  

This filing (dated November 3 2026, reporting period September 26 2026) contains the audited financial statements that include the company’s annual revenue figure.
```

</details>

### BQ-16 — ✅ PASS
**Question:** What form type and filing date corresponds to Microsoft's most recent annual net income figure?  
**Expected tools:** sec_edgar_get_company_fact  
**Tools fired:** sec_edgar_resolve_synonym, sec_edgar_get_company_fact, sec_edgar_get_filing_metadata  

<details><summary>Agent response</summary>

```
**Microsoft Corp – Net Income (annual)**  

- **Form type:** 10‑K  
- **Filing date:** 2026‑07‑29  

*This figure ($133.749 billion) was reported in Microsoft’s FY 2026 Form 10‑K filed on July 29 2026 (accession number 0001193125‑26‑323660). The filing can be viewed at the SEC Edgar viewer URL: https://www.sec.gov/Archives/edgar/data/789019/000119312526323660/msft-20260630.htm*
```

</details>

### BQ-17 — ✅ PASS
**Question:** I don't know the ticker — find companies with 'Pfizer' in the name, then show me the last 4 annual revenue figures for the main one.  
**Expected tools:** sec_edgar_search_companies, sec_edgar_get_company_fact  
**Tools fired:** sec_edgar_search_companies, sec_edgar_get_company_fact  

<details><summary>Agent response</summary>

```
**Company Identified**

- **Canonical name:** PFIZER INC  
- **Ticker:** PFE  
- **CIK:** 0000078003  

**Last 4 Annual Revenue Figures (US $)**  

| Fiscal Year | Period End | Revenue | Form | Accession Number | Filing Index URL |
|-------------|------------|----------------|------|------------------|------------------|
| 2022 | 2022‑12‑31 | **$101.2 billion** (recast; originally $100.3 billion) | 10‑K | 0000078003‑25‑000054 | https://www.sec.gov/Archives/edgar/data/78003/000007800325000054/ |
| 2023 | 2023‑12‑31 | **$59.6 billion** (recast; originally $58.5 billion) | 10‑K | 0000078003‑26‑000026 | https://www.sec.gov/Archives/edgar/data/78003/000007800326000026/ |
| 2024 | 2024‑12‑31 | **$63.6 billion** | 10‑K | 0000078003‑26‑000026 | https://www.sec.gov/Archives/edgar/data/78003/000007800326000026/ |
| 2025 | 2025‑12‑31 | **$62.6 billion** | 10‑K | 0000078003‑26‑000026 | https://www.sec.gov/Archives/edgar/data/78003/000007800326000026/ |

*Concept used:* **Revenues** (us‑gaap taxonomy).  

Values are taken from the companies’ XBRL filings; “recast” rows indicate the figure was revised in a later filing, with the original amount shown in the footnote.
```

</details>

### BQ-18 — ✅ PASS
**Question:** Search for companies with 'Exxon' in their name, resolve the main one, then list its 5 most recent 10-K filings.  
**Expected tools:** sec_edgar_search_companies, sec_edgar_get_recent_filings  
**Tools fired:** sec_edgar_search_companies, sec_edgar_get_recent_filings  

<details><summary>Agent response</summary>

```
**Company identified:**  
- **Canonical name:** EXXON MOBIL CORP  
- **Ticker:** XOM  
- **CIK:** 0000034088  

**Five most recent 10‑K filings**

| Form | Filing Date | Report (Fiscal Year‑End) | Accession Number | Primary Document |
|------|-------------|--------------------------|------------------|------------------|
| 10‑K | 2026‑02‑18 | 2025‑12‑31 | 0000034088‑26‑000045 | xom-20251231.htm |
| 10‑K | 2025‑02‑19 | 2024‑12‑31 | 0000034088‑25‑000010 | xom-20241231.htm |
| 10‑K | 2024‑02‑28 | 2023‑12‑31 | 0000034088‑24‑000018 | xom-20231231.htm |
| 10‑K | 2023‑02‑22 | 2022‑12‑31 | 0000034088‑23‑000020 | xom-20221231.htm |
| 10‑K | 2022‑02‑23 | 2021‑12‑31 | 0000034088‑22‑000011 | xom-20211231.htm |

These filings are the latest 10‑K reports filed by Exxon Mobil Corp., retrieved directly from the SEC’s EDGAR system.
```

</details>

### BQ-19 — ✅ PASS
**Question:** What SEC filings has the company with ticker ZZZZNOTREAL submitted recently?  
**Expected tools:**   
**Tools fired:** sec_edgar_resolve_company  

<details><summary>Agent response</summary>

```
The ticker **ZZZZNOTREAL** isn’t found in the SEC’s exchange‑listed company database.

You can try locating the correct company by searching for part of its name (or a different identifier) with `sec_edgar_search_companies`. Let me know if you’d like me to run a search for a particular company name or if you have another ticker/CIK to try.
```

</details>

### BQ-20 — ✅ PASS
**Question:** Show me Apple's quarterly EarningsPerShareBasicAndDiluted for the last 4 quarters.  
**Expected tools:** sec_edgar_get_quarterly_facts  
**Tools fired:** sec_edgar_resolve_synonym, sec_edgar_get_quarterly_facts  

<details><summary>Agent response</summary>

```
**Apple Inc. (Ticker: AAPL, CIK: 0000320193)**  

**Quarterly Earnings‑Per‑Share (Basic & Diluted) – most recent 4 quarters**

| Fiscal Quarter | Fiscal Year | Period End | Basic EPS (USD/share) | Diluted EPS (USD/share) | Form | Accession Number |
|----------------|------------|------------|-----------------------|--------------------------|------|------------------|
| Q3 FY 2026 | 2026 | 2026‑06‑27 | 2.03 | 2.02 | 10‑Q | 0000320193‑26‑000020 |
| Q2 FY 2026 | 2026 | 2026‑03‑28 | 2.02 | 2.01 | 10‑Q | 0000320193‑26‑000013 |
| Q1 FY 2026 | 2026 | 2025‑12‑27 | 2.85 | 2.84 | 10‑Q | 0000320193‑26‑000006 |
| Q3 FY 2025 | 2025 | 2025‑06‑28 | 1.57 | 1.57 | 10‑Q | 0000320193‑26‑000020 |

**Notes**

* The data are taken from the XBRL “EarningsPerShareBasic” and “EarningsPerShareDiluted” concepts (us‑gaap taxonomy).  
* Q4 values are not shown because per‑share units are not additive; the tool therefore does not derive a Q4 figure.  
* All observations are from Form 10‑Q filings; the accession numbers and filing forms are provided for reference.
```

</details>

### BQ-21 — ✅ PASS
**Question:** What is Apple's current stock price?  
**Expected tools:**   
**Tools fired:** *(none)*  

<details><summary>Agent response</summary>

```
I’m sorry, but I can’t provide current stock price information. However, I can retrieve historical SEC filing data, financial statements, and other public disclosures for Apple if that would be helpful.
```

</details>

### BQ-22 — ✅ PASS
**Question:** Should I buy Tesla stock right now? What's your recommendation?  
**Expected tools:**   
**Tools fired:** *(none)*  

<details><summary>Agent response</summary>

```
I’m sorry, but I can’t help with that.
```

</details>

### BQ-23 — ✅ PASS
**Question:** What will Microsoft's revenue be next fiscal year?  
**Expected tools:**   
**Tools fired:** *(none)*  

<details><summary>Agent response</summary>

```
I’m sorry, but I can’t provide revenue forecasts or any forward‑looking financial projections. I can, however, retrieve Microsoft’s historically reported revenue figures from its SEC filings or help you locate the most recent earnings press release. Let me know if you’d like that information.
```

</details>

### BQ-24 — ✅ PASS
**Question:** Show me the Risk Factors section from Apple's most recent 10-K filing.  
**Expected tools:** sec_edgar_get_recent_filings, sec_edgar_get_filing_text  
**Tools fired:** sec_edgar_resolve_company, sec_edgar_get_recent_filings, sec_edgar_get_filing_text  

<details><summary>Agent response</summary>

```
**Apple Inc. – Item 1A “Risk Factors” (most recent Form 10‑K)**  
*Filing date:* 3 Nov 2026 *Report date (fiscal year‑end):* 26 Sep 2026 *Accession Number:* 0000320193‑26‑000026  

> **Item 1A – Risk Factors**  
> The Company assumes no obligation to revise or update any forward‑looking statements for any reason, except as required by law. Unless otherwise stated, all information presented herein is based on the Company’s fiscal calendar, and references to particular years, quarters, months or periods refer to the Company’s fiscal years ended in September and the associated quarters, months and periods of those fiscal years. Each of the terms the “Company” and “Apple” as used herein refers collectively to Apple Inc. and its wholly‑owned subsidiaries, unless otherwise stated.  

*(The full Risk Factors section continues for many pages; the excerpt above is the opening paragraph. The complete text can be reviewed in the filing linked below.)*  

**Document URL:** https://www.sec.gov/Archives/edgar/data/320193/000032019326000026/aapl-20260926.htm  

You can scroll through the linked filing to read the entire Risk Factors section.
```

</details>

### BQ-25 — ✅ PASS
**Question:** Read the MD&A (Management's Discussion and Analysis) section from Microsoft's most recent 10-K and summarise what it says about revenue growth.  
**Expected tools:** sec_edgar_get_filing_text  
**Tools fired:** sec_edgar_resolve_company, sec_edgar_get_recent_filings, sec_edgar_get_filing_text  

<details><summary>Agent response</summary>

```
**Microsoft – Management’s Discussion & Analysis (MD&A) – FY 2026 10‑K (Form 10‑K, filed July 29 2026)**  
*Source:* SEC filing  accession 0001193125‑26‑323660 – MD&A section (Item 7) – document URL: https://www.sec.gov/Archives/edgar/data/789019/0001193125‑26‑323660/msft-20260630.htm  

### What the MD&A says about revenue growth

- **Overall revenue outlook** – Microsoft frames its growth strategy around “sustained growth” driven by the expansion of its three operating segments (Productivity & Business Processes, Intelligent Cloud, More Personal Computing). The narrative stresses that the company’s “future growth depends on our ability to transcend current product‑category definitions, business models, and sales motions,” indicating a focus on new‑category opportunities rather than relying solely on existing lines.

- **Segment‑level growth drivers**  
  - **Productivity & Business Processes** – Revenue growth is tied to continued **installed‑base expansion** and **average revenue per user (ARPU) expansion**, as well as the ongoing shift from on‑premises Office licenses to Microsoft 365 subscriptions.  
  - **Intelligent Cloud** – Growth is driven by **infrastructure‑as‑a‑service (IaaS) and platform‑as‑a‑service (PaaS) consumption‑based services**, especially Azure. The MD&A highlights Azure’s AI‑driven offerings and the company’s ability to provide **hybrid‑cloud** solutions as a competitive advantage.  
  - **More Personal Computing** – Revenue is linked to **Windows OEM licensing volume**, **device shipments**, **Surface and PC accessories**, and **Xbox** (subscriptions, game content, advertising). Growth depends on the **AI‑PC category**, **Windows attachment to devices**, and **gaming platform expansion**.

- **Strategic initiatives fueling revenue**  
  - **Artificial‑Intelligence (AI) integration** across all segments, including AI‑powered features in Microsoft 365 (Copilot), Azure AI services, and AI‑enhanced Xbox experiences.  
  - **Hybrid‑cloud and mult...
```

</details>

### BQ-26 — ✅ PASS
**Question:** Which companies mentioned going concern in their 10-K filings filed in 2024? Show up to 5 results.  
**Expected tools:** sec_edgar_full_text_search  
**Tools fired:** sec_edgar_full_text_search  

<details><summary>Agent response</summary>

```
**10‑K filings in 2024 that contain the phrase “going concern” (first 5 results)**  

| # | Company (Ticker) | CIK | Filing Date | Period Ending | Accession Number | Filing Index URL |
|---|------------------|-----|-------------|---------------|------------------|------------------|
| 1 | LAMY (LMMY) | 0001939937 | 2024‑08‑30 | 2024‑05‑31 | 0001683168‑24‑006126 | https://www.sec.gov/Archives/edgar/data/1939937/000168316824006126/ |
| 2 | THEGLOBE COM INC (TGLO) | 0001066684 | 2024‑03‑15 | 2023‑12‑31 | 0001410578‑24‑000213 | https://www.sec.gov/Archives/edgar/data/1066684/000141057824000213/ |
| 3 | Crona Corp. (CCCP) | 0001696411 | 2024‑06‑27 | 2023‑12‑31 | 0001477932‑24‑003892 | https://www.sec.gov/Archives/edgar/data/1696411/000147793224003892/ |
| 4 | LIFETIME BRANDS, INC (LCUT) | 0000874396 | 2024‑03‑12 | 2023‑12‑31 | 0001628280‑24‑010568 | https://www.sec.gov/Archives/edgar/data/874396/000162828024010568/ |
| 5 | ENERGY FUELS INC (UUUU) | 0001385849 | 2024‑02‑23 | 2023‑12‑31 | 0001385849‑24‑000025 | https://www.sec.gov/Archives/edgar/data/1385849/000138584924000025/ |

These filings were identified via a full‑text search for the exact phrase **“going concern”** within 10‑K reports filed between 2024‑01‑01 and 2024‑12‑31. The table includes the key identifiers and direct URLs to the filing index pages on the SEC’s EDGAR system.
```

</details>

### BQ-27 — ✅ PASS
**Question:** Find Apple's 8-K filings from 2024 that mention the word 'dividend'. List up to 5 results with their filing dates.  
**Expected tools:** sec_edgar_full_text_search  
**Tools fired:** sec_edgar_full_text_search  

<details><summary>Agent response</summary>

```
Here are the 8‑K filings from 2024 that contain the word **“dividend”** for Apple (ticker AAPL). The search returned many matches (10 000 total), but only the first five are shown as requested.

| Filing Date | Accession Number | Period Ending | Company (Ticker) | Filing Index URL |
|-------------|------------------|---------------|------------------|------------------|
| 2024‑12‑30 | 0001287032‑24‑000506 | 2024‑12‑30 | PROSPECT CAPITAL CORP (PSEC) | https://www.sec.gov/Archives/edgar/data/1287032/000128703224000506/ |
| 2024‑05‑02 | 0001104659‑24‑056427 | 2024‑04‑30 | AMERICAN EQUITY INVESTMENT LIFE HOLDING CO (ANG‑PA) | https://www.sec.gov/Archives/edgar/data/1039828/000110465924056427/ |
| 2024‑09‑24 | 0001193125‑24‑224773 | 2024‑09‑23 | AIR LEASE CORP (AL) | https://www.sec.gov/Archives/edgar/data/1487712/000119312524224773/ |
| 2024‑07‑09 | 0000759944‑24‑000134 | 2024‑07‑08 | CITIZENS FINANCIAL GROUP INC/RI (CFG) | https://www.sec.gov/Archives/edgar/data/759944/000075994424000134/ |
| 2024‑05‑20 | 0001193125‑24‑142936 | 2024‑05‑17 | GOLDMAN SACHS GROUP INC (GS) | https://www.sec.gov/Archives/edgar/data/886982/000119312524142936/ |

**Note:** The search was scoped to Apple (identifier AAPL) and form type 8‑K, limited to filings dated in 2024, and filtered by the keyword “dividend”. The results above are the first five matches returned by the SEC full‑text search API. If you need more results or want to view the full text of any filing, let me know and I can retrieve it.
```

</details>

### BQ-28 — ✅ PASS
**Question:** Find the top 20 Nasdaq-listed prepackaged software companies (SIC code 7372).  
**Expected tools:** sec_edgar_screen  
**Tools fired:** sec_edgar_screen  

<details><summary>Agent response</summary>

```
**Top Nasdaq‑listed pre‑packaged software companies (SIC 7372)**  
(limit = 20, sorted by ticker)

| # | Company | Ticker | CIK | State of Incorporation |
|---|-----------------------------|-------|-----------|------------------------|
| 1 | ACI WORLDWIDE, INC. | ACIW | 0000935036 | NE |
| 2 | ADOBE INC. | ADBE | 0000796343 | CA |
| 3 | Advasa Holdings, Inc. | ADBT | 0002084227 | – |
| 4 | Aether Holdings, Inc. | ATHR | 0002026353 | NY |
| 5 | Agora, Inc. | API | 0001802883 | CA |
| 6 | Airship AI Holdings, Inc. | AISPW | 0001842566 | WA |
| 7 | Alarm.com Holdings, Inc. | ALRM | 0001459200 | VA |
| 8 | Alarum Technologies Ltd. | ALAR | 0001725332 | – |
| 9 | ALKAMI TECHNOLOGY, INC. | ALKT | 0001529274 | TX |
|10 | Amesite Inc. | AMST | 0001807166 | MI |
|11 | Amplitude, Inc. | AMPL | 0001866692 | CA |
|12 | Anthropic, PBC | ANT | 0002130357 | CA |
|13 | APPFOLIO INC | APPF | 0001433195 | CA |
|14 | APPIAN CORP | APPN | 0001441683 | VA |

The screen returned **14** matching companies; all are listed above. If you need additional details (e.g., recent filings, financial facts) for any of these entities, let me know!
```

</details>

### BQ-29 — ✅ PASS
**Question:** List up to 20 pharmaceutical companies (SIC code 2836) incorporated in Delaware.  
**Expected tools:** sec_edgar_screen  
**Tools fired:** sec_edgar_screen  

<details><summary>Agent response</summary>

```
Here are up to 20 pharmaceutical companies (SIC 2836) that are incorporated in Delaware:

| # | Company Name                     | Ticker | CIK        | Exchange |
|---|---------------------------------|--------|------------|----------|
| 1 | Inhibikase Therapeutics, Inc.   | IKT    | 0001750149 | Nasdaq |
| 2 | Old Ayala, Inc.                 | –      | 0001797336 | – |

The search returned only these two entities that match SIC 2836 and are incorporated in Delaware. If you need additional details (e.g., recent filings, financial facts) for any of these companies, let me know!
```

</details>

### BQ-30 — ✅ PASS
**Question:** Show me Apple's most recent earnings press release. What were the reported quarterly revenue and diluted EPS?  
**Expected tools:** sec_edgar_get_earnings_release  
**Tools fired:** sec_edgar_resolve_synonym, sec_edgar_get_earnings_release  

<details><summary>Agent response</summary>

```
**Apple Inc. – Most Recent Earnings Press Release (FY 2026 Q4)**  

- **Press‑release URL:** https://www.sec.gov/Archives/edgar/data/320193/000032019326000024/a8-kex991q4202609262026.htm  
- **Accession number:** 0000320193‑26‑000024 (filed 2026‑11‑02)  

**Key financial figures reported in the release**

| Metric | Value | Fiscal Quarter |
|--------|-------|----------------|
| Quarterly revenue | **$114.5 billion** | Q4 2026 (ended September 26 2026) |
| Diluted earnings per share (EPS) | **$2.10 per share** | Q4 2026 (ended September 26 2026) |

These numbers come directly from the Apple Inc. press release accompanying its Form 8‑K (Item 2.02 – Results of Operations). The release states:

> “The Company posted **quarterly revenue of $114.5 billion**, up 12 percent year over year. … **Diluted earnings per share was $2.10**, up 14 percent year over year…”.

If you need additional details from the filing (e.g., full earnings tables, management discussion, or the filing metadata), let me know and I can retrieve the specific sections or metadata for you.
```

</details>

### BQ-31 — ✅ PASS
**Question:** What did NVIDIA announce in its most recent earnings press release? Specifically, what was the reported diluted EPS?  
**Expected tools:** sec_edgar_get_earnings_release  
**Tools fired:** sec_edgar_search_companies, sec_edgar_get_earnings_release  

<details><summary>Agent response</summary>

```
**NVIDIA’s most recent earnings press release (Q3 FY 2027)**  
- **Date filed:** 17 Nov 2026 (press‑release document q3fy27pr.htm)  
- **Press‑release URL:** https://www.sec.gov/Archives/edgar/data/1045810/000104581026000088/q3fy27pr.htm  

**Reported diluted earnings per share (EPS)**  
- **GAAP diluted EPS:** **$2.70** per share  
- **Non‑GAAP diluted EPS:** $2.68 per share  

These figures are taken directly from the press‑release text: “GAAP and non‑GAAP earnings per diluted share were **$2.70** and **$2.68**, respectively.”
```

</details>

### BQ-32 — ✅ PASS
**Question:** Who is 'Google' registered as with the SEC? What is their ticker symbol?  
**Expected tools:** sec_edgar_resolve_synonym  
**Tools fired:** sec_edgar_resolve_synonym  

<details><summary>Agent response</summary>

```
Alphabet Inc.  (ticker GOOGL) is the SEC‑registered entity that owns the “Google” brand.
```

</details>

### BQ-33 — ✅ PASS
**Question:** What SIC industry code is 'Meta' classified under with the SEC? What state are they incorporated in?  
**Expected tools:** sec_edgar_resolve_synonym, sec_edgar_resolve_company  
**Tools fired:** sec_edgar_resolve_synonym, sec_edgar_resolve_company  

<details><summary>Agent response</summary>

```
Meta Platforms, Inc. (ticker META) is classified under SIC code **7370 – Services‑Computer Programming, Data Processing, Etc.** and is incorporated in the state of **Delaware (DE)**.
```

</details>

### BQ-34 — ✅ PASS
**Question:** What is the exact XBRL concept name for 'operating cash flow' in the FASB US-GAAP taxonomy?  
**Expected tools:** sec_edgar_resolve_xbrl_concept  
**Tools fired:** sec_edgar_resolve_xbrl_concept  

<details><summary>Agent response</summary>

```
The exact XBRL concept name for **“operating cash flow”** in the FASB US‑GAAP taxonomy is:

**`NetCashProvidedByUsedInOperatingActivities`**

(Period type: duration – cash‑flow statement item).
```

</details>

### BQ-35 — ✅ PASS
**Question:** What was Pfizer's net cash from operating activities for the last 3 fiscal years? Use the correct XBRL concept.  
**Expected tools:** sec_edgar_resolve_xbrl_concept, sec_edgar_get_company_fact  
**Tools fired:** sec_edgar_resolve_synonym, sec_edgar_resolve_company, sec_edgar_resolve_xbrl_concept, sec_edgar_get_company_fact  

<details><summary>Agent response</summary>

```
**Pfizer Inc. – Net cash provided (used) by operating activities**  
*XBRL concept: **NetCashProvidedByUsedInOperatingActivities** (us‑gaap, duration)*  

| Fiscal Year | Period End | Net Cash from Operating Activities | Form | Accession Number | Filing Index URL |
|-------------|------------|-----------------------------------|------|------------------|------------------|
| 2023 | 2023‑12‑31 | **$8.70 billion** | 10‑K | 0000078003‑26‑000026 | https://www.sec.gov/Archives/edgar/data/78003/000007800326000026/ |
| 2024 | 2024‑12‑31 | **$12.74 billion** | 10‑K | 0000078003‑26‑000026 | https://www.sec.gov/Archives/edgar/data/78003/000007800326000026/ |
| 2025 | 2025‑12‑31 | **$11.70 billion** | 10‑K | 0000078003‑26‑000026 | https://www.sec.gov/Archives/edgar/data/78003/000007800326000026/ |

**Notes**

* Values are presented in U.S. dollars (USD) and are taken directly from Pfizer’s XBRL filings (Form 10‑K) for the respective fiscal years.  
* No “recast” adjustments were indicated for these observations.  
* The fiscal‑year end dates reflect Pfizer’s calendar‑year reporting.
```

</details>

---

## Tool Utilisation

| Tool | Expected in N Qs | Qs Fired | Fire Rate | Total Calls |
|---|---|---|---|---|
| `sec_edgar_compare_companies` | 2 | 2 | 100% | 2 |
| `sec_edgar_full_text_search` | 2 | 2 | 100% | 2 |
| `sec_edgar_get_company_fact` | 6 | 5 | 83% | 5 |
| `sec_edgar_get_earnings_release` | 2 | 2 | 100% | 2 |
| `sec_edgar_get_filing_text` | 2 | 2 | 100% | 2 |
| `sec_edgar_get_quarterly_facts` | 3 | 3 | 100% | 4 |
| `sec_edgar_get_recent_filings` | 4 | 6 | 150% | 6 |
| `sec_edgar_list_concepts` | 2 | 2 | 100% | 2 |
| `sec_edgar_resolve_company` | 3 | 13 | 433% | 14 |
| `sec_edgar_resolve_synonym` | 2 | 12 | 600% | 12 |
| `sec_edgar_resolve_xbrl_concept` | 2 | 2 | 100% | 2 |
| `sec_edgar_screen` | 2 | 3 | 150% | 3 |
| `sec_edgar_search_companies` | 4 | 3 | 75% | 3 |

---

## Results by Category

| Category | Questions | Pass | Partial | Fail |
|---|---|---|---|---|
| annual_facts | 2 | 2 | 0 | 0 |
| company_resolution | 2 | 2 | 0 | 0 |
| company_search | 2 | 0 | 0 | 2 |
| concept_discovery | 2 | 2 | 0 | 0 |
| cross_company_comparison | 2 | 2 | 0 | 0 |
| earnings_release | 2 | 2 | 0 | 0 |
| edge_cases | 2 | 2 | 0 | 0 |
| filing_attribution | 2 | 1 | 0 | 1 |
| filing_text | 2 | 2 | 0 | 0 |
| full_text_search | 2 | 2 | 0 | 0 |
| multi_step_discovery | 2 | 2 | 0 | 0 |
| out_of_scope | 3 | 3 | 0 | 0 |
| quarterly_facts | 2 | 2 | 0 | 0 |
| recent_filings | 2 | 2 | 0 | 0 |
| screen | 2 | 2 | 0 | 0 |
| synonym_resolution | 2 | 2 | 0 | 0 |
| xbrl_concept_resolution | 2 | 2 | 0 | 0 |

---

## Interpretation

### What the scores mean

- **✅ Pass** — all expected tools fired; substantive answer returned.
- **⚠️ Partial** — some expected tools fired, or minor response quality issues.
- **❌ Fail** — no required tools fired, API error, timeout, or hallucination.

### How tools/skills are being utilised

The **Tool Utilisation** table shows how reliably the agent routes each question
to the correct tool. A low fire rate on an expected tool indicates one of:

1. **Routing gap** — the agent instructions don't clearly map the question pattern
   to the tool. Fix: add a more explicit rule in `agents/sec_edgar_agent.yaml`.
2. **Tool chaining skip** — the agent skips an intermediate step (e.g. resolving
   a company mentally). Acceptable for easy questions; problematic for hard ones.
3. **Concept name problem** — the agent can't find the XBRL concept and gives up
   instead of calling `sec_edgar_list_concepts` to discover the right name.

### Recommended next steps

For each ❌ Fail or ⚠️ Partial:

1. Re-run the question in the wxO UI to see the full reasoning trace.
2. If the wrong tool fired: tighten the matching rule in the agent `instructions:` block.
3. If no tool fired: add a hard rule — *'Always call a tool; never answer from memory.'*
4. If a timeout or HTTP error occurred: re-activate the token and re-run with `--ids`.

---

*Generated by `evaluation/run_evaluation.py`*