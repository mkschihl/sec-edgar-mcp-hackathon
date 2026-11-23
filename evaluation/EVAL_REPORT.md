# SEC EDGAR Agent — Evaluation Report

**Agent:** `sec_edgar_agent`  
**Environment:** `gsa-hackathon` (IBM Cloud Toronto)  
**Run date:** 2026-11-23 06:19  
**Duration:** 356s for 35 questions  

---

## Summary

| Metric | Value |
|---|---|
| Total questions | 35 |
| ✅ Pass | 35 (100%) |
| ⚠️ Partial | 0 (0%) |
| ❌ Fail | 0 (0%) |

---

## Results by Question

| ID | Diff | Category | Score | Routing | Expected Tools | Tools Fired | Notes |
|---|---|---|---|---|---|---|---|
| BQ-01 | 🟢 easy | company_search | ✅ pass | routing_ok | `screen` | `screen` | routing_ok — all expected tools fired. |
| BQ-02 | 🟢 easy | company_search | ✅ pass | routing_ok |  | `resolve_synonym` | routing_ok — all expected tools fired. |
| BQ-03 | 🟢 easy | company_resolution | ✅ pass | routing_ok | `resolve_company` | `resolve_synonym`, `resolve_company` | routing_ok — all expected tools fired. |
| BQ-04 | 🟢 easy | company_resolution | ✅ pass | routing_ok | `resolve_company` | `resolve_synonym`, `resolve_company` | routing_ok — all expected tools fired. |
| BQ-05 | 🟢 easy | recent_filings | ✅ pass | routing_ok | `get_recent_filings` | `resolve_synonym`, `get_recent_filings` | routing_ok — all expected tools fired. |
| BQ-06 | 🟢 easy | recent_filings | ✅ pass | routing_ok | `get_recent_filings` | `search_companies`, `get_recent_filings` | routing_ok — all expected tools fired. |
| BQ-07 | 🟡 medium | annual_facts | ✅ pass | routing_ok | `get_company_fact` | `resolve_company`, `get_company_fact` | routing_ok — all expected tools fired. |
| BQ-08 | 🟡 medium | annual_facts | ✅ pass | routing_ok | `get_company_fact` | `resolve_synonym`, `resolve_company`, `get_company_fact` | routing_ok — all expected tools fired. |
| BQ-09 | 🟡 medium | quarterly_facts | ✅ pass | routing_ok | `get_quarterly_facts` | `resolve_synonym`, `get_quarterly_facts` | routing_ok — all expected tools fired. |
| BQ-10 | 🟡 medium | quarterly_facts | ✅ pass | routing_ok | `get_quarterly_facts` | `resolve_company`, `get_quarterly_facts` | routing_ok — all expected tools fired. |
| BQ-11 | 🟡 medium | concept_discovery | ✅ pass | routing_ok | `list_concepts` | `search_companies`, `list_concepts` | routing_ok — all expected tools fired. |
| BQ-12 | 🟡 medium | concept_discovery | ✅ pass | routing_ok | `list_concepts` | `list_concepts` | routing_ok — all expected tools fired. |
| BQ-13 | 🔴 hard | cross_company_comparison | ✅ pass | routing_ok | `compare_companies` | `resolve_company`, `compare_companies` | routing_ok — all expected tools fired. |
| BQ-14 | 🔴 hard | cross_company_comparison | ✅ pass | routing_ok | `compare_companies` | `compare_companies` | routing_ok — all expected tools fired. |
| BQ-15 | 🔴 hard | filing_attribution | ✅ pass | routing_ok | `get_filing_metadata` | `resolve_company`, `get_company_fact`, `get_filing_metadata` | routing_ok — all expected tools fired. |
| BQ-16 | 🔴 hard | filing_attribution | ✅ pass | routing_ok | `get_company_fact` | `resolve_synonym`, `get_recent_filings`, `get_company_fact` | routing_ok — all expected tools fired. |
| BQ-17 | 🔴 hard | multi_step_discovery | ✅ pass | routing_ok | `search_companies`, `get_company_fact` | `search_companies`, `get_company_fact` | routing_ok — all expected tools fired. |
| BQ-18 | 🔴 hard | multi_step_discovery | ✅ pass | routing_ok | `search_companies`, `get_recent_filings` | `search_companies`, `get_recent_filings` | routing_ok — all expected tools fired. |
| BQ-19 | 🟢 easy | edge_cases | ✅ pass | routing_ok |  | `resolve_company` | routing_ok — all expected tools fired. |
| BQ-20 | 🟡 medium | edge_cases | ✅ pass | routing_ok | `get_quarterly_facts` | `resolve_xbrl_concept`, `resolve_company`, `get_quarterly_facts` | routing_ok — all expected tools fired. |
| BQ-21 | 🟢 easy | out_of_scope | ✅ pass | routing_ok |  | *(none)* | routing_ok — correctly declined out-of-scope question. |
| BQ-22 | 🟢 easy | out_of_scope | ✅ pass | routing_ok |  | *(none)* | routing_ok — correctly declined out-of-scope question. |
| BQ-23 | 🟡 medium | out_of_scope | ✅ pass | routing_ok |  | *(none)* | routing_ok — correctly declined out-of-scope question. |
| BQ-24 | 🟡 medium | filing_text | ✅ pass | routing_ok | `get_recent_filings`, `get_filing_text` | `search_companies`, `get_recent_filings`, `get_filing_text` | routing_ok — all expected tools fired. |
| BQ-25 | 🔴 hard | filing_text | ✅ pass | routing_ok | `get_filing_text` | `resolve_synonym`, `get_recent_filings`, `get_filing_text` | routing_ok — all expected tools fired. |
| BQ-26 | 🟢 easy | full_text_search | ✅ pass | routing_ok | `full_text_search` | `full_text_search` | routing_ok — all expected tools fired. |
| BQ-27 | 🟡 medium | full_text_search | ✅ pass | routing_ok | `full_text_search` | `full_text_search` | routing_ok — all expected tools fired. |
| BQ-28 | 🟢 easy | screen | ✅ pass | routing_ok | `screen` | `screen` | routing_ok — all expected tools fired. |
| BQ-29 | 🟡 medium | screen | ✅ pass | routing_ok | `screen` | `screen` | routing_ok — all expected tools fired. |
| BQ-30 | 🟢 easy | earnings_release | ✅ pass | routing_ok | `get_earnings_release` | `get_earnings_release` | routing_ok — all expected tools fired. |
| BQ-31 | 🟡 medium | earnings_release | ✅ pass | routing_ok | `get_earnings_release` | `resolve_company`, `get_earnings_release` | routing_ok — all expected tools fired. |
| BQ-32 | 🟢 easy | synonym_resolution | ✅ pass | routing_ok | `resolve_synonym` | `resolve_synonym` | routing_ok — all expected tools fired. |
| BQ-33 | 🟡 medium | synonym_resolution | ✅ pass | routing_ok | `resolve_synonym`, `resolve_company` | `resolve_synonym`, `resolve_company` | routing_ok — all expected tools fired. |
| BQ-34 | 🟢 easy | xbrl_concept_resolution | ✅ pass | routing_ok | `resolve_xbrl_concept` | `resolve_xbrl_concept` | routing_ok — all expected tools fired. |
| BQ-35 | 🟡 medium | xbrl_concept_resolution | ✅ pass | routing_ok | `resolve_xbrl_concept`, `get_company_fact` | `search_companies`, `resolve_xbrl_concept`, `get_company_fact` | routing_ok — all expected tools fired. |

---

## Agent Responses

### BQ-01 — ✅ PASS
**Question:** Find all companies with 'Berkshire' in their name.  
**Expected tools:** sec_edgar_screen  
**Tools fired:** sec_edgar_screen  

<details><summary>Agent response</summary>

```
Here are the companies whose name contains **“Berkshire”** (up to 20 results returned by the SEC EDGAR screen API):

| # | Company Name | Ticker | CIK | Exchange | SIC Code | State of Incorporation |
|---|--------------|--------|-----|----------|----------|------------------------|
| 1 | BERKSHIRE BANCORP INC /DE/ | – | 0000759718 | – | 6022 | NY |
| 2 | BERKSHIRE ENERGY RESOURCES | – | 0001056255 | – | 4924 | MA |
| 3 | BERKSHIRE GAS CO /MA/ | – | 0000317406 | – | 4924 | MA |
| 4 | Berkshire Grey, Inc. | – | 0001824734 | – | 3569 | MA |
| 5 | BERKSHIRE HATHAWAY ENERGY CO | – | 0001081316 | – | 4900 | IA |
| 6 | **BERKSHIRE HATHAWAY INC** | BRK‑A | 0001067983 | NYSE | 6331 | NE |
| 7 | OBH LLC* | – | 0000109694 | – | 6331 | NE |
| 8 | Beacon Financial Corp* | BBT | 0001108134 | NYSE | 6036 | MA |
| 9 | Berkshire Homes, Inc. | – | 0001505124 | – | 6510 | AZ |
|10 | BERKSHIRE INCOME REALTY, INC. | – | 0001178862 | – | 6500 | MA |
|11 | BERKSHIRE REALTY CO INC /DE | – | 0000869446 | – | 6798 | MA |

\* These entries appear because “Berkshire” is part of a broader name or parent‑company relationship (e.g., OBH LLC is a subsidiary of Berkshire Hathaway).  

If you would like more details on any specific company (e.g., recent filings, financial facts, or the full text of a filing), just let me know the CIK or ticker you’re interested in.
```

</details>

### BQ-02 — ✅ PASS
**Question:** I'm looking for companies related to 'General Electric'. What comes up?  
**Expected tools:**   
**Tools fired:** sec_edgar_resolve_synonym  

<details><summary>Agent response</summary>

```
**Resolved company**

- **Canonical name:** GE Aerospace  
- **Ticker:** **GE**  

The name “General Electric” maps to GE Aerospace (ticker GE) in the SEC’s records. Let me know if you’d like to see recent filings, financial facts, or compare this company to others.
```

</details>

### BQ-03 — ✅ PASS
**Question:** What is the SEC CIK number and industry classification for Microsoft?  
**Expected tools:** sec_edgar_resolve_company  
**Tools fired:** sec_edgar_resolve_synonym, sec_edgar_resolve_company  

<details><summary>Agent response</summary>

```
**Microsoft Corp (ticker: MSFT)**  
- **CIK:** 0000789019  
- **Industry Classification (SIC):** 7372 – Services‑Prepackaged Software  
- **State of Incorporation:** Washington (WA)
```

</details>

### BQ-04 — ✅ PASS
**Question:** Tell me about Alphabet Inc. — what state is it incorporated in and what SIC code does it use?  
**Expected tools:** sec_edgar_resolve_company  
**Tools fired:** sec_edgar_resolve_synonym, sec_edgar_resolve_company  

<details><summary>Agent response</summary>

```
Alphabet Inc. (ticker GOOGL) is incorporated in **Delaware (DE)** and uses SIC code **7370 – Services‑Computer Programming, Data Processing, Etc.**.
```

</details>

### BQ-05 — ✅ PASS
**Question:** List the five most recent 10-K filings for Microsoft.  
**Expected tools:** sec_edgar_get_recent_filings  
**Tools fired:** sec_edgar_resolve_synonym, sec_edgar_get_recent_filings  

<details><summary>Agent response</summary>

```
**Microsoft Corp (Ticker: MSFT, CIK 0000789019) – Five Most Recent 10‑K Filings**

| # | Filing Date | Report (Fiscal) Date | Accession Number | Primary Document |
|---|--------------|----------------------|------------------|------------------|
| 1 | 2026‑07‑29 | 2026‑06‑30 | 0001193125‑26‑323660 | msft-20260630.htm |
| 2 | 2025‑07‑30 | 2025‑06‑30 | 0000950170‑25‑100235 | msft-20250630.htm |
| 3 | 2024‑07‑30 | 2024‑06‑30 | 0000950170‑24‑087843 | msft-20240630.htm |
| 4 | 2023‑07‑27 | 2023‑06‑30 | 0000950170‑23‑035122 | msft-20230630.htm |
| 5 | 2022‑07‑28 | 2022‑06‑30 | 0001564590‑22‑026876 | msft-10k_20220630.htm |

These are the five most recent annual reports (Form 10‑K) filed by Microsoft Corp.
```

</details>

### BQ-06 — ✅ PASS
**Question:** Show me the 10 most recent 10-Q filings for Johnson & Johnson (ticker: JNJ).  
**Expected tools:** sec_edgar_get_recent_filings  
**Tools fired:** sec_edgar_search_companies, sec_edgar_get_recent_filings  

<details><summary>Agent response</summary>

```
**Johnson & Johnson – 10 most recent Form 10‑Q filings**

| # | Filing Date | Report (Period End) | Accession Number | Primary Document |
|---|------------|----------------------|------------------|------------------|
| 1 | 2026‑10‑21 | 2026‑09‑27 | 0000200406‑26‑000197 | jnj-20260927.htm |
| 2 | 2026‑07‑23 | 2026‑06‑28 | 0000200406‑26‑000153 | jnj-20260628.htm |
| 3 | 2026‑04‑22 | 2026‑03‑29 | 0000200406‑26‑000087 | jnj-20260329.htm |
| 4 | 2025‑10‑22 | 2025‑09‑28 | 0000200406‑25‑000209 | jnj-20250928.htm |
| 5 | 2025‑07‑24 | 2025‑06‑29 | 0000200406‑25‑000178 | jnj-20250629.htm |
| 6 | 2025‑04‑23 | 2025‑03‑30 | 0000200406‑25‑000119 | jnj-20250330.htm |
| 7 | 2024‑10‑23 | 2024‑09‑29 | 0000200406‑24‑000096 | jnj-20240929.htm |
| 8 | 2024‑07‑25 | 2024‑06‑30 | 0000200406‑24‑000075 | jnj-20240630.htm |
| 9 | 2024‑05‑01 | 2024‑03‑31 | 0000200406‑24‑000049 | jnj-20240331.htm |
|10 | 2023‑10‑27 | 2023‑10‑01 | 0000200406‑23‑000102 | jnj-20231001.htm |

*Company:* JOHNSON & JOHNSON  
*CIK:* 0000200406  

These filings are taken directly from the SEC’s EDGAR database. If you need the full filing text or other details for any of these accession numbers, let me know!
```

</details>

### BQ-07 — ✅ PASS
**Question:** Show me the last 5 annual net income figures for Apple.  
**Expected tools:** sec_edgar_get_company_fact  
**Tools fired:** sec_edgar_resolve_company, sec_edgar_get_company_fact  

<details><summary>Agent response</summary>

```
Apple Inc. (CIK 0000320193) – Net Income (Loss) Attributable to Parent  
XBRL concept used: **NetIncomeLoss** (us‑gaap)

| Fiscal Year | Period End | Net Income (USD) | Form | Accession Number | Filing Index URL |
|-------------|------------|------------------|------|------------------|------------------|
| 2022 | 2022‑09‑24 | $99.8 billion | 10‑K | 0000320193‑24‑000123 | https://www.sec.gov/Archives/edgar/data/320193/000032019324000123/ |
| 2023 | 2023‑09‑30 | $96.995 billion | 10‑K | 0000320193‑25‑000079 | https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/ |
| 2024 | 2024‑09‑28 | $93.736 billion | 10‑K | 0000320193‑26‑000026 | https://www.sec.gov/Archives/edgar/data/320193/000032019326000026/ |
| 2025 | 2025‑09‑27 | $112.01 billion | 10‑K | 0000320193‑26‑000026 | https://www.sec.gov/Archives/edgar/data/320193/000032019326000026/ |
| 2026 | 2026‑09‑26 | $132.175 billion | 10‑K | 0000320193‑26‑000026 | https://www.sec.gov/Archives/edgar/data/320193/000032019326000026/ |

All values are presented in US dollars (USD) as reported in Apple’s annual Form 10‑K filings.
```

</details>

### BQ-08 — ✅ PASS
**Question:** What were Amazon's total assets for the last 4 fiscal years?  
**Expected tools:** sec_edgar_get_company_fact  
**Tools fired:** sec_edgar_resolve_synonym, sec_edgar_resolve_company, sec_edgar_get_company_fact  

<details><summary>Agent response</summary>

```
**Amazon.com, Inc. – Total Assets (US $)**  

| Fiscal Year | Period End | Total Assets | Form | Accession Number | Filing Index URL |
|-------------|------------|--------------|------|------------------|------------------|
| 2022 | 2022‑12‑31 | $462.7 billion | 10‑K | 0001018724‑25‑000004 | https://www.sec.gov/Archives/edgar/data/1018724/000101872425000004/ |
| 2023 | 2023‑12‑31 | $527.9 billion | 10‑K | 0001018724‑26‑000004 | https://www.sec.gov/Archives/edgar/data/1018724/000101872426000004/ |
| 2024 | 2024‑12‑31 | $624.9 billion | 10‑K | 0001018724‑26‑000004 | https://www.sec.gov/Archives/edgar/data/1018724/000101872426000004/ |
| 2025 | 2025‑12‑31 | $818.0 billion | 10‑K | 0001018724‑26‑000004 | https://www.sec.gov/Archives/edgar/data/1018724/000101872426000004/ |

**XBRL Concept Used:** `Assets` (us‑gaap) – “Sum of the carrying amounts as of the balance sheet date of all assets that are recognized.”  

All values are reported in U.S. dollars and come from the company’s annual Form 10‑K filings.
```

</details>

### BQ-09 — ✅ PASS
**Question:** Show me Apple's quarterly revenue for the last 8 quarters.  
**Expected tools:** sec_edgar_get_quarterly_facts  
**Tools fired:** sec_edgar_resolve_synonym, sec_edgar_get_quarterly_facts  

<details><summary>Agent response</summary>

```
**Apple Inc. – Quarterly Revenue (last 8 quarters)**  
*XBRL concept used: **RevenueFromContractWithCustomerExcludingAssessedTax** (the SEC‑registered “Revenues” tag)*  

| Fiscal Quarter | Fiscal Year | Period End | Revenue (USD) | Form | Accession Number |
|----------------|------------|------------|---------------|------|------------------|
| Q4 | 2026 | 2026‑09‑26 | $114.5 billion (derived) | 10‑K | 0000320193‑26‑000026 |
| Q3 | 2026 | 2026‑06‑27 | $109.4 billion | 10‑Q | 0000320193‑26‑000020 |
| Q2 | 2026 | 2026‑03‑28 | $111.2 billion | 10‑Q | 0000320193‑26‑000013 |
| Q1 | 2026 | 2025‑12‑27 | $143.8 billion | 10‑Q | 0000320193‑26‑000006 |
| Q4 | 2025 | 2025‑09‑27 | $102.5 billion (derived) | 10‑K | 0000320193‑26‑000026 |
| Q3 | 2025 | 2025‑06‑28 | $94.0 billion | 10‑Q | 0000320193‑26‑000020 |
| Q2 | 2025 | 2025‑03‑29 | $95.4 billion | 10‑Q | 0000320193‑26‑000013 |
| Q1 | 2025 | 2024‑12‑28 | $124.3 billion | 10‑Q | 0000320193‑26‑000006 |

**Notes**

* Q4 values are **derived** (annual total – nine‑month YTD) because quarterly XBRL flow items are not reported directly for Q4. The derivation is shown in the “derived” column.  
* All amounts are in **USD** and rounded to the nearest million for readability.  
* The data comes from Apple’s SEC‑filed 10‑Q and 10‑K reports; accession numbers point to the exact filings where each figure was reported.
```

</details>

### BQ-10 — ✅ PASS
**Question:** What was Microsoft's net income in each of the last 6 quarters?  
**Expected tools:** sec_edgar_get_quarterly_facts  
**Tools fired:** sec_edgar_resolve_company, sec_edgar_get_quarterly_facts  

<details><summary>Agent response</summary>

```
**Microsoft Corp – Net Income (USD) for the last 6 quarters**

| Fiscal Quarter | Fiscal Year | Period End | Net Income (USD) | Form | Accession Number | Derived? |
|----------------|------------|------------|------------------|------|------------------|----------|
| Q1 FY2027 | 2027 | 2026‑09‑30 | $36.629 billion | 10‑Q | 0001193125‑26‑436133 | No |
| Q4 FY2026 | 2026 | 2026‑06‑30 | $35.766 billion | 10‑K | 0001193125‑26‑323660 | **Yes** – derived from annual filing minus nine‑month YTD |
| Q3 FY2026 | 2026 | 2026‑03‑31 | $31.778 billion | 10‑Q | 0001193125‑26‑191507 | No |
| Q2 FY2026 | 2026 | 2025‑12‑31 | $38.458 billion | 10‑Q | 0001193125‑26‑027207 | No |
| Q1 FY2026 | 2026 | 2025‑09‑30 | $27.747 billion | 10‑Q | 0001193125‑26‑436133 | No |
| Q4 FY2025 | 2025 | 2025‑06‑30 | $27.233 billion | 10‑K | 0001193125‑26‑323660 | **Yes** – derived from annual filing minus nine‑month YTD |

**Notes**

* The XBRL concept used is **NetIncomeLoss** (label: “Net Income (Loss) Attributable to Parent”) from the **us‑gaap** taxonomy.  
* Q4 values are marked **derived** because the SEC does not file separate Q4 10‑Q reports for flow items; they are computed as the annual total minus the nine‑month YTD total.  
* All values are presented in **U.S. dollars** (USD).  

If you need the source filing details (e.g., filing dates, EDGAR viewer URLs) for any of these numbers, let me know and I can retrieve the filing metadata.
```

</details>

### BQ-11 — ✅ PASS
**Question:** What revenue-related XBRL concepts does Apple report in us-gaap?  
**Expected tools:** sec_edgar_list_concepts  
**Tools fired:** sec_edgar_search_companies, sec_edgar_list_concepts  

<details><summary>Agent response</summary>

```
Apple Inc. (CIK 0000320193) reports the following revenue‑related XBRL concepts in the **us‑gaap** taxonomy:

| Concept (XBRL tag) | Human‑readable label |
|--------------------|----------------------|
| **ContractWithCustomerLiabilityRevenueRecognized** | Contract with Customer, Liability, Revenue Recognized |
| **DeferredRevenueCurrent** | Deferred Revenue, Current |
| **DeferredRevenueNoncurrent** | Deferred Revenue, Noncurrent |
| **IncreaseDecreaseInDeferredRevenue** | Increase (Decrease) in Deferred Revenue |
| **RevenueFromContractWithCustomerExcludingAssessedTax** | Revenue from Contract with Customer, Excluding Assessed Tax |
| **Revenues** | Revenues |
| **SalesRevenueNet** | Revenue, Net (Deprecated 2018‑01‑31) |
| **SalesRevenueServicesGross** | Sales Revenue, Services, Other (Deprecated 2018‑01‑31) |

These tags are the revenue‑related concepts returned by the SEC’s company‑facts endpoint for Apple. If you need values for any of these concepts (e.g., annual revenue series), let me know and I can retrieve the numeric data.
```

</details>

### BQ-12 — ✅ PASS
**Question:** I want to find debt-related financial concepts for Tesla. What us-gaap concepts are available?  
**Expected tools:** sec_edgar_list_concepts  
**Tools fired:** sec_edgar_list_concepts  

<details><summary>Agent response</summary>

```
Here are the **debt‑related XBRL concepts** that Tesla Inc. (CIK 0001318605) reports under the **us‑gaap** taxonomy, as returned by the SEC’s concept list API.

| XBRL Concept (Tag) | Human‑Readable Label |
|--------------------|----------------------|
| AdjustmentsToAdditionalPaidInCapitalEquityComponentOfConvertibleDebt | Adjustments to Additional Paid in Capital, Equity Component of Convertible Debt |
| AmortizationOfDebtDiscountPremium | Amortization of Debt Discount (Premium) |
| AmortizationOfFinancingCosts | Amortization of Debt Issuance Costs |
| AmortizationOfFinancingCostsAndDiscounts | Amortization of Debt Issuance Costs and Discounts |
| AvailableForSaleDebtSecuritiesAccumulatedGrossUnrealizedGainBeforeTax | Debt Securities, Available‑for‑sale, Accumulated Gross Unrealized Gain, before Tax |
| AvailableForSaleDebtSecuritiesAccumulatedGrossUnrealizedLossBeforeTax | Debt Securities, Available‑for‑sale, Accumulated Gross Unrealized Loss, before Tax |
| AvailableForSaleDebtSecuritiesAmortizedCostBasis | Debt Securities, Available‑for‑sale, Amortized Cost |
| AvailableForSaleDebtSecuritiesGrossUnrealizedGain | Debt Securities, Available‑for‑sale, Unrealized Gain |
| AvailableForSaleDebtSecuritiesGrossUnrealizedLoss | Debt Securities, Available‑for‑sale, Unrealized Loss |
| AvailableForSaleSecuritiesDebtMaturitiesNextRollingTwelveMonthsAmortizedCostBasis | Debt Securities, Available‑for‑sale, Maturity, Rolling within One Year, Amortized Cost |
| AvailableForSaleSecuritiesDebtMaturitiesNextRollingTwelveMonthsFairValue | Debt Securities, Available‑for‑sale, Maturity, Rolling within One Year, Fair Value |
| AvailableForSaleSecuritiesDebtMaturitiesRollingAfterYearTenAmortizedCostBasis | Debt Securities, Available‑for‑sale, Maturity, Rolling after 10 Years, Amortized Cost |
| AvailableForSaleSecuritiesDebtMaturitiesRollingYearSixThroughTenAmortizedCostBasis | Debt Securities, Available‑for‑sale, Maturity, Rolling after Five‑Through‑Ten Years, Amortized Cost |
| Ava...
```

</details>

### BQ-13 — ✅ PASS
**Question:** Compare the most recent annual net income for Apple, Microsoft, and Google.  
**Expected tools:** sec_edgar_compare_companies  
**Tools fired:** sec_edgar_resolve_company, sec_edgar_compare_companies  

<details><summary>Agent response</summary>

```
**Most recent annual Net Income (US $)**  

| Company | Net Income | Fiscal Year | Period End | Form | Accession Number | Filing Index URL |
|---------|-----------|-------------|------------|------|------------------|------------------|
| Apple Inc. | $132.2 billion | 2026 | 2026‑09‑26 | 10‑K | 0000320193‑26‑000026 | https://www.sec.gov/Archives/edgar/data/320193/000032019326000026/ |
| Microsoft Corp. | $133.7 billion | 2026 | 2026‑06‑30 | 10‑K | 0001193125‑26‑323660 | https://www.sec.gov/Archives/edgar/data/789019/000119312526323660/ |
| Alphabet Inc. (Google) | $132.2 billion | 2025 | 2025‑12‑31 | 10‑K | 0001652044‑26‑000018 | https://www.sec.gov/Archives/edgar/data/1652044/000165204426000018/ |

**XBRL concept used:** `NetIncomeLoss` (us‑gaap).

**Warnings:** The companies’ fiscal years end on different dates (Apple Sept 26, Microsoft June 30, Alphabet Dec 31), so the figures are not directly calendar‑year comparable.
```

</details>

### BQ-14 — ✅ PASS
**Question:** Which company has more total assets — JPMorgan Chase (JPM) or Bank of America (BAC)? Use the most recent annual figures.  
**Expected tools:** sec_edgar_compare_companies  
**Tools fired:** sec_edgar_compare_companies  

<details><summary>Agent response</summary>

```
**Total Assets (most recent fiscal year, FY 2025)**  

| Company | FY | Period End | Total Assets | Unit | Filing Form | Accession Number | Filing Index URL |
|---------|----|------------|--------------|------|-------------|------------------|------------------|
| JPMorgan Chase & Co. | 2025 | 2025‑12‑31 | $4,424.9 billion | USD | 10‑K | 0001628280‑26‑008131 | https://www.sec.gov/Archives/edgar/data/19617/000162828026008131/ |
| Bank of America Corp. | 2025 | 2025‑12‑31 | $3,411.7 billion | USD | 10‑K | 0000070858‑26‑000157 | https://www.sec.gov/Archives/edgar/data/70858/000007085826000157/ |

**Answer:** JPMorgan Chase (JPM) has the larger total assets, with **$4.425 trillion** compared to Bank of America’s **$3.412 trillion** for FY 2025.
```

</details>

### BQ-15 — ✅ PASS
**Question:** Which SEC filing reported Apple's most recent annual revenue? Give me the accession number and a link to the filing.  
**Expected tools:** sec_edgar_get_filing_metadata  
**Tools fired:** sec_edgar_resolve_company, sec_edgar_get_company_fact, sec_edgar_get_filing_metadata  

<details><summary>Agent response</summary>

```
**Apple Inc. – Most recent annual revenue**

- **Revenue reported:** $478.8 billion (Fiscal year ended 2026‑09‑26)  
- **SEC filing:** Form 10‑K  
- **Accession number:** 0000320193‑26‑000026  
- **Filing date:** 2026‑11‑03  
- **Link to the filing:** https://www.sec.gov/Archives/edgar/data/320193/000032019326000026/aapl-20260926.htm  

This filing contains the latest audited annual revenue figure for Apple.
```

</details>

### BQ-16 — ✅ PASS
**Question:** What form type and filing date corresponds to Microsoft's most recent annual net income figure?  
**Expected tools:** sec_edgar_get_company_fact  
**Tools fired:** sec_edgar_resolve_synonym, sec_edgar_get_recent_filings, sec_edgar_get_company_fact  

<details><summary>Agent response</summary>

```
The most recent annual Net Income figure for Microsoft Corp. (ticker **MSFT**, CIK 0000789019) comes from its FY 2026 Form 10‑K filing.

| Metric | Value (USD) | Fiscal Year End | Form | Filing Date | Accession Number |
|--------|-------------|-----------------|------|-------------|------------------|
| Net Income (attributable to parent) | $133.7 billion | 2026‑06‑30 | 10‑K | 2026‑07‑29 | 0001193125‑26‑323660 |

**Source filing:** Form 10‑K for FY 2026, filed 29 July 2026. The filing can be viewed at the SEC’s EDGAR viewer URL provided in the metadata:

`https://www.sec.gov/Archives/edgar/data/789019/000119312526323660/`
```

</details>

### BQ-17 — ✅ PASS
**Question:** I don't know the ticker — find companies with 'Pfizer' in the name, then show me the last 4 annual revenue figures for the main one.  
**Expected tools:** sec_edgar_search_companies, sec_edgar_get_company_fact  
**Tools fired:** sec_edgar_search_companies, sec_edgar_get_company_fact  

<details><summary>Agent response</summary>

```
**Company found**  
- **Canonical name:** PFIZER INC  
- **Ticker:** PFE  
- **CIK:** 0000078003  

**Last 4 annual revenue figures (US $)** – XBRL concept **Revenues** (us‑gaap)

| Fiscal Year | Period End | Revenue (USD) | Recast note | Form | Accession Number | Filing Index URL |
|------------|------------|---------------|-------------|------|------------------|------------------|
| 2022 | 2022‑12‑31 | $101.2 billion | Recast – originally $100.33 billion | 10‑K | 0000078003‑25‑000054 | https://www.sec.gov/Archives/edgar/data/78003/000007800325000054/ |
| 2023 | 2023‑12‑31 | $59.6 billion | Recast – originally $58.50 billion | 10‑K | 0000078003‑26‑000026 | https://www.sec.gov/Archives/edgar/data/78003/000007800326000026/ |
| 2024 | 2024‑12‑31 | $63.6 billion | – (reported as filed) | 10‑K | 0000078003‑26‑000026 | https://www.sec.gov/Archives/edgar/data/78003/000007800326000026/ |
| 2025 | 2025‑12‑31 | $62.6 billion | – (reported as filed) | 10‑K | 0000078003‑26‑000026 | https://www.sec.gov/Archives/edgar/data/78003/000007800326000026/ |

*All values are taken from the company’s XBRL filings (us‑gaap “Revenues”).*
```

</details>

### BQ-18 — ✅ PASS
**Question:** Search for companies with 'Exxon' in their name, resolve the main one, then list its 5 most recent 10-K filings.  
**Expected tools:** sec_edgar_search_companies, sec_edgar_get_recent_filings  
**Tools fired:** sec_edgar_search_companies, sec_edgar_get_recent_filings  

<details><summary>Agent response</summary>

```
**Company identified**

- **Canonical name:** EXXON MOBIL CORP  
- **Ticker:** XOM  
- **CIK:** 0000034088  

**5 most‑recent Form 10‑K filings**

| Filing Date | Report (Fiscal) Year End | Accession Number | Primary Document |
|------------|--------------------------|------------------|------------------|
| 2026‑02‑18 | 2025‑12‑31 | 0000034088‑26‑000045 | xom-20251231.htm |
| 2025‑02‑19 | 2024‑12‑31 | 0000034088‑25‑000010 | xom-20241231.htm |
| 2024‑02‑28 | 2023‑12‑31 | 0000034088‑24‑000018 | xom-20231231.htm |
| 2023‑02‑22 | 2022‑12‑31 | 0000034088‑23‑000020 | xom-20221231.htm |
| 2022‑02‑23 | 2021‑12‑31 | 0000034088‑22‑000011 | xom-20211231.htm |

These filings are the latest annual reports (Form 10‑K) filed by Exxon Mobil Corp. You can retrieve the full filing documents using the accession numbers via the SEC EDGAR viewer if needed.
```

</details>

### BQ-19 — ✅ PASS
**Question:** What SEC filings has the company with ticker ZZZZNOTREAL submitted recently?  
**Expected tools:**   
**Tools fired:** sec_edgar_resolve_company  

<details><summary>Agent response</summary>

```
The ticker **ZZZZNOTREAL** isn’t found in the SEC’s exchange‑listed company database.

You can try locating the correct company by searching for a partial name or a different identifier. Would you like me to search the SEC filings for a company name that matches “ZZZZNOTREAL,” or do you have another ticker or name to try?
```

</details>

### BQ-20 — ✅ PASS
**Question:** Show me Apple's quarterly EarningsPerShareBasicAndDiluted for the last 4 quarters.  
**Expected tools:** sec_edgar_get_quarterly_facts  
**Tools fired:** sec_edgar_resolve_xbrl_concept, sec_edgar_resolve_company, sec_edgar_get_quarterly_facts  

<details><summary>Agent response</summary>

```
**Apple Inc. (CIK 0000320193) – Quarterly Earnings‑per‑Share (Basic & Diluted)**  

| Fiscal Quarter | Fiscal Year | Period End | Basic EPS (USD /shares) | Diluted EPS (USD /shares) | Form | Accession Number |
|----------------|------------|------------|-------------------------|---------------------------|------|------------------|
| Q3 FY2026 | 2026 | 2026‑06‑27 | 2.03 | 2.02 | 10‑Q | 0000320193‑26‑000020 |
| Q2 FY2026 | 2026 | 2026‑03‑28 | 2.02 | 2.01 | 10‑Q | 0000320193‑26‑000013 |
| Q1 FY2026 | 2026 | 2025‑12‑27 | 2.85 | 2.84 | 10‑Q | 0000320193‑26‑000006 |
| Q3 FY2025 | 2025 | 2025‑06‑28 | 1.57 | 1.57 | 10‑Q | 0000320193‑26‑000020 |

**Notes**

* The XBRL concepts used: **EarningsPerShareBasic** and **EarningsPerShareDiluted** (duration‑type, per‑share values).  
* Q4 values are not shown because per‑share units cannot be derived from annual totals (the API flagged this with a note).  
* All observations come from Apple’s 10‑Q filings; each row includes the filing form, period end date, and the accession number for source verification.  

If you need the filing metadata (e.g., EDGAR viewer URLs) for any of these accession numbers, just let me know!
```

</details>

### BQ-21 — ✅ PASS
**Question:** What is Apple's current stock price?  
**Expected tools:**   
**Tools fired:** *(none)*  

<details><summary>Agent response</summary>

```
I’m sorry, but I can’t provide current stock price information.
```

</details>

### BQ-22 — ✅ PASS
**Question:** Should I buy Tesla stock right now? What's your recommendation?  
**Expected tools:**   
**Tools fired:** *(none)*  

<details><summary>Agent response</summary>

```
I’m sorry, but I can’t help with that. I can provide historical SEC filing information or financial data for Tesla if that would be useful.
```

</details>

### BQ-23 — ✅ PASS
**Question:** What will Microsoft's revenue be next fiscal year?  
**Expected tools:**   
**Tools fired:** *(none)*  

<details><summary>Agent response</summary>

```
I’m sorry, but I can’t help with that.
```

</details>

### BQ-24 — ✅ PASS
**Question:** Show me the Risk Factors section from Apple's most recent 10-K filing.  
**Expected tools:** sec_edgar_get_recent_filings, sec_edgar_get_filing_text  
**Tools fired:** sec_edgar_search_companies, sec_edgar_get_recent_filings, sec_edgar_get_filing_text  

<details><summary>Agent response</summary>

```
**Apple Inc. – 2026 Form 10‑K (Item 1A Risk Factors)**  

*Accession Number:* 0000320193‑26‑000026  
*Filing Date:* 3 Nov 2026  
*Document URL:* https://www.sec.gov/Archives/edgar/data/320193/000032019326000026/aapl-20260926.htm  

---

**Risk Factors (excerpt – first ≈ 3 k characters of the section)**  

> *Item 1A of this Form 10‑K under the heading “Risk Factors.”*  
> The Company assumes no obligation to revise or update any forward‑looking statements for any reason, except as required by law. Unless otherwise stated, all information presented herein is based on the Company’s fiscal calendar, and references to particular years, quarters, months or periods refer to the Company’s fiscal years ended in September and the associated quarters, months and periods of those fiscal years. Each of the terms the “Company” and “Apple” as used herein refers collectively to Apple Inc. and its wholly owned subsidiaries, unless otherwise stated.  
>  
> **Business** – Apple designs, manufactures and markets smartphones, personal computers, tablets, wearables and accessories, and sells a variety of related services. The Company’s fiscal year is the 52‑ or 53‑week period that ends on the last Saturday of September.  
>  
> **Products** – iPhone, Mac, iPad, Wearables (Apple Watch, AirPods, Beats, etc.), Apple Vision Pro, Home (Apple TV, HomePod), accessories, services (App Store, Apple Care, iCloud, Apple Music, Apple TV+, Apple Pay, etc.).  
>  
> **Competition** – The markets for the Company’s products and services are highly competitive and are characterized by aggressive price competition, downward pressure on gross margins, continual improvement in product performance, and price sensitivity on the part of consumers and businesses. Competitors have significant technical, marketing, distribution and financial resources, and may imitate Apple’s products, infringe on its intellectual property, or undercut prices.  
>  
> **Supply of Components and Computing Resources** – While mos...
```

</details>

### BQ-25 — ✅ PASS
**Question:** Read the MD&A (Management's Discussion and Analysis) section from Microsoft's most recent 10-K and summarise what it says about revenue growth.  
**Expected tools:** sec_edgar_get_filing_text  
**Tools fired:** sec_edgar_resolve_synonym, sec_edgar_get_recent_filings, sec_edgar_get_filing_text  

<details><summary>Agent response</summary>

```
**Microsoft – Management’s Discussion & Analysis (MD&A) – 2026 10‑K (Item 7)**  

**Key points on revenue growth**

| Topic | Summary (as stated in the MD&A) |
|-------|---------------------------------|
| **Overall strategy** | Microsoft’s growth strategy is built on expanding its AI‑enabled cloud, productivity, and personal‑computing platforms. The company emphasizes “reinventing productivity,” “building an intelligent cloud and edge,” and “delivering more personal‑computing experiences.” |
| **Intelligent Cloud** | Revenue growth is driven by “scale economies” in datacenters (lower cost per unit, higher utilization) and by multi‑tenant services that lower maintenance labor. AI‑driven security, compliance, and identity solutions are highlighted as growth levers. |
| **Productivity & Business Processes** | Growth depends on **(a)** continued expansion of the installed base, **(b)** higher average revenue per user (ARPU), and **(c)** the shift from on‑premise Office licenses to Microsoft 365 (cloud‑based) subscriptions. |
| **More Personal Computing** | Revenue is supported by continued demand for Windows, devices (PCs, tablets, Xbox, Surface), and advertising via Outlook.com/OneDrive. AI‑enhanced experiences and the integration of AI into Windows are noted as future growth drivers. |
| **LinkedIn** | Revenue growth is tied to increased member engagement and the expansion of AI‑enabled Talent, Sales, and Marketing solutions. |
| **AI & Generative AI** | The MD&A stresses that AI (including Microsoft 365 Copilot and Azure AI services) will “unlock new value” and “drive substantive productivity gains,” which the company expects to translate into higher revenue across all segments. |
| **Geographic reach** | Microsoft highlights its “global opportunity” – the ability to sell AI‑driven cloud and productivity solutions in every country, which underpins long‑term revenue expansion. |
| **Investment focus** | Heavy investment in security, AI, cloud infrastructure, and deve...
```

</details>

### BQ-26 — ✅ PASS
**Question:** Which companies mentioned going concern in their 10-K filings filed in 2024? Show up to 5 results.  
**Expected tools:** sec_edgar_full_text_search  
**Tools fired:** sec_edgar_full_text_search  

<details><summary>Agent response</summary>

```
**Companies that mentioned “going concern” in a 10‑K filed in 2024 (up to 5 results)**  

| # | Company | Ticker | CIK | Filing Date | Period Ending | Accession Number | Filing Index URL |
|---|---------|--------|-----|-------------|---------------|------------------|------------------|
| 1 | LAMY | LMMY | 0001939937 | 2024‑08‑30 | 2024‑05‑31 | 0001683168‑24‑006126 | https://www.sec.gov/Archives/edgar/data/1939937/000168316824006126/ |
| 2 | THEGLOBE COM INC | TGLO | 0001066684 | 2024‑03‑15 | 2023‑12‑31 | 0001410578‑24‑000213 | https://www.sec.gov/Archives/edgar/data/1066684/000141057824000213/ |
| 3 | Crona Corp. | CCCP | 0001696411 | 2024‑06‑27 | 2023‑12‑31 | 0001477932‑24‑003892 | https://www.sec.gov/Archives/edgar/data/1696411/000147793224003892/ |
| 4 | LIFETIME BRANDS, INC | LCUT | 0000874396 | 2024‑03‑12 | 2023‑12‑31 | 0001628280‑24‑010568 | https://www.sec.gov/Archives/edgar/data/874396/000162828024010568/ |
| 5 | ENERGY FUELS INC | UUUU | 0001385849 | 2024‑02‑23 | 2023‑12‑31 | 0001385849‑24‑000025 | https://www.sec.gov/Archives/edgar/data/1385849/000138584924000025/ |

These filings were identified by a full‑text search for the exact phrase **“going concern”** limited to form 10‑K filings dated in 2024.
```

</details>

### BQ-27 — ✅ PASS
**Question:** Find Apple's 8-K filings from 2024 that mention the word 'dividend'. List up to 5 results with their filing dates.  
**Expected tools:** sec_edgar_full_text_search  
**Tools fired:** sec_edgar_full_text_search  

<details><summary>Agent response</summary>

```
**Apple Inc. (ticker AAPL) – 8‑K filings in 2024 that mention “dividend”**

| Filing Date | Accession Number | Filing Index URL |
|-------------|------------------|------------------|
| 2024‑02‑06 | 0000320193‑24‑000058 | https://www.sec.gov/Archives/edgar/data/320193/000032019324000058/ |
| 2024‑05‑02 | 0000320193‑24‑000124 | https://www.sec.gov/Archives/edgar/data/320193/000032019324000124/ |
| 2024‑08‑08 | 0000320193‑24‑000210 | https://www.sec.gov/Archives/edgar/data/320193/000032019324000210/ |
| 2024‑11‑07 | 0000320193‑24‑000295 | https://www.sec.gov/Archives/edgar/data/320193/000032019324000295/ |
| 2024‑12‑12 | 0000320193‑24‑000342 | https://www.sec.gov/Archives/edgar/data/320193/000032019324000342/ |

*These are the five most recent 8‑K filings for Apple in 2024 that contain the word “dividend.”*
```

</details>

### BQ-28 — ✅ PASS
**Question:** Find the top 20 Nasdaq-listed prepackaged software companies (SIC code 7372).  
**Expected tools:** sec_edgar_screen  
**Tools fired:** sec_edgar_screen  

<details><summary>Agent response</summary>

```
**Top Nasdaq‑listed pre‑packaged software companies (SIC 7372)**  
*(limited to the first 20 results; the screen returned 14 matches)*  

| # | Company Name | Ticker | CIK | State of Incorporation |
|---|--------------|--------|-----|------------------------|
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

*The screen returned 14 companies that meet the criteria; there are fewer than 20 matches.*
```

</details>

### BQ-29 — ✅ PASS
**Question:** List up to 20 pharmaceutical companies (SIC code 2836) incorporated in Delaware.  
**Expected tools:** sec_edgar_screen  
**Tools fired:** sec_edgar_screen  

<details><summary>Agent response</summary>

```
**Pharmaceutical companies (SIC 2836) incorporated in Delaware (up to 20 results)**  

| # | Company Name | Ticker | CIK | Exchange |
|---|--------------|--------|-----|----------|
| 1 | Inhibikase Therapeutics, Inc. | IKT | 0001750149 | Nasdaq |
| 2 | Old Ayala, Inc. | — | 0001797336 | — |

The screen returned only two companies that match the SIC 2836 (Pharmaceutical Preparations) and Delaware incorporation criteria. If you need additional details (e.g., recent filings, financial facts) for any of these entities, let me know!
```

</details>

### BQ-30 — ✅ PASS
**Question:** Show me Apple's most recent earnings press release. What were the reported quarterly revenue and diluted EPS?  
**Expected tools:** sec_edgar_get_earnings_release  
**Tools fired:** sec_edgar_get_earnings_release  

<details><summary>Agent response</summary>

```
**Apple Inc. – Most recent earnings press release (FY 2026 Q4)**  

- **Press‑release URL:** https://www.sec.gov/Archives/edgar/data/320193/000032019326000024/a8-kex991q4202609262026.htm  
- **Accession number:** 0000320193‑26‑000024  
- **Filing date:** 2026‑11‑02 (covers fiscal quarter ended 2026‑09‑26)  

**Key reported figures (from the press release):**  

| Metric | Reported value | Fiscal quarter |
|--------|----------------|----------------|
| Quarterly revenue | **$114.5 billion** (up 12 % YoY) | Q4 FY 2026 (ended Sept 26 2026) |
| Diluted earnings per share | **$2.10** (up 14 % YoY) | Q4 FY 2026 (ended Sept 26 2026) |

These numbers are taken directly from Apple’s EX‑99.1 earnings‑release exhibit attached to its most recent Form 8‑K filing.
```

</details>

### BQ-31 — ✅ PASS
**Question:** What did NVIDIA announce in its most recent earnings press release? Specifically, what was the reported diluted EPS?  
**Expected tools:** sec_edgar_get_earnings_release  
**Tools fired:** sec_edgar_resolve_company, sec_edgar_get_earnings_release  

<details><summary>Agent response</summary>

```
**NVIDIA’s most recent earnings press release (Q3 FY 2027)**  

- **Date of filing:** November 17 2026 (accession # 0001045810‑26‑000088)  
- **Press‑release URL:** https://www.sec.gov/Archives/edgar/data/1045810/000104581026000088/q3fy27pr.htm  

**Reported diluted earnings per share (EPS)**  

- **GAAP diluted EPS:** **$2.70** per share  
- **Non‑GAAP diluted EPS:** $2.68 per share  

These figures are taken directly from the press‑release text:

> “GAAP and non‑GAAP earnings per diluted share were **$2.70** and **$2.68**, respectively.”  

You can review the full press release at the URL above for additional context and details.
```

</details>

### BQ-32 — ✅ PASS
**Question:** Who is 'Google' registered as with the SEC? What is their ticker symbol?  
**Expected tools:** sec_edgar_resolve_synonym  
**Tools fired:** sec_edgar_resolve_synonym  

<details><summary>Agent response</summary>

```
Alphabet Inc. – ticker **GOOGL** (the primary SEC‑registered name for “Google”).
```

</details>

### BQ-33 — ✅ PASS
**Question:** What SIC industry code is 'Meta' classified under with the SEC? What state are they incorporated in?  
**Expected tools:** sec_edgar_resolve_synonym, sec_edgar_resolve_company  
**Tools fired:** sec_edgar_resolve_synonym, sec_edgar_resolve_company  

<details><summary>Agent response</summary>

```
**Meta Platforms, Inc. (Ticker: META, CIK: 0001326801)**  

- **SIC industry code:** **7370** – *Services‑Computer Programming, Data Processing, Etc.*  
- **State of incorporation:** **Delaware (DE)**  

These details are taken from the SEC’s official company registration information.
```

</details>

### BQ-34 — ✅ PASS
**Question:** What is the exact XBRL concept name for 'operating cash flow' in the FASB US-GAAP taxonomy?  
**Expected tools:** sec_edgar_resolve_xbrl_concept  
**Tools fired:** sec_edgar_resolve_xbrl_concept  

<details><summary>Agent response</summary>

```
The primary XBRL concept for **“operating cash flow”** in the FASB US‑GAAP taxonomy is:

**`NetCashProvidedByUsedInOperatingActivities`**

(Period type = `duration`; monetary amount in USD).
```

</details>

### BQ-35 — ✅ PASS
**Question:** What was Pfizer's net cash from operating activities for the last 3 fiscal years? Use the correct XBRL concept.  
**Expected tools:** sec_edgar_resolve_xbrl_concept, sec_edgar_get_company_fact  
**Tools fired:** sec_edgar_search_companies, sec_edgar_resolve_xbrl_concept, sec_edgar_get_company_fact  

<details><summary>Agent response</summary>

```
**Pfizer Inc. (CIK 0000078003) – Net Cash Provided by (Used in) Operating Activities**  
*XBRL Concept: `NetCashProvidedByUsedInOperatingActivities` (us‑gaap)*  

| Fiscal Year | Period End | Net Cash from Operating Activities | Form | Accession Number | Filing Index URL |
|-------------|------------|-------------------------------------|------|------------------|------------------|
| 2023 | 2023‑12‑31 | **$8.70 billion** | 10‑K | 0000078003‑26‑000026 | https://www.sec.gov/Archives/edgar/data/78003/000007800326000026/ |
| 2024 | 2024‑12‑31 | **$12.74 billion** | 10‑K | 0000078003‑26‑000026 | https://www.sec.gov/Archives/edgar/data/78003/000007800326000026/ |
| 2025 | 2025‑12‑31 | **$11.70 billion** | 10‑K | 0000078003‑26‑000026 | https://www.sec.gov/Archives/edgar/data/78003/000007800326000026/ |

**Notes**
- Values are reported in US dollars (USD) and represent the total cash inflow (or outflow) from operating activities for each fiscal year, including discontinued operations.
- The same filing (Pfizer’s 2026‑02‑26 10‑K) provides the figures for all three years; the SEC XBRL data includes each year’s separate observation.
```

</details>

---

## Tool Utilisation

| Tool | Expected in N Qs | Qs Fired | Fire Rate | Total Calls |
|---|---|---|---|---|
| `sec_edgar_compare_companies` | 2 | 2 | 100% | 2 |
| `sec_edgar_full_text_search` | 2 | 2 | 100% | 2 |
| `sec_edgar_get_company_fact` | 5 | 6 | 120% | 6 |
| `sec_edgar_get_earnings_release` | 2 | 2 | 100% | 2 |
| `sec_edgar_get_filing_metadata` | 1 | 1 | 100% | 1 |
| `sec_edgar_get_filing_text` | 2 | 2 | 100% | 2 |
| `sec_edgar_get_quarterly_facts` | 3 | 3 | 100% | 4 |
| `sec_edgar_get_recent_filings` | 4 | 6 | 150% | 6 |
| `sec_edgar_list_concepts` | 2 | 2 | 100% | 2 |
| `sec_edgar_resolve_company` | 3 | 11 | 367% | 13 |
| `sec_edgar_resolve_synonym` | 2 | 10 | 500% | 10 |
| `sec_edgar_resolve_xbrl_concept` | 2 | 3 | 150% | 4 |
| `sec_edgar_screen` | 3 | 3 | 100% | 3 |
| `sec_edgar_search_companies` | 2 | 6 | 300% | 6 |

---

## Results by Category

| Category | Questions | Pass | Partial | Fail |
|---|---|---|---|---|
| annual_facts | 2 | 2 | 0 | 0 |
| company_resolution | 2 | 2 | 0 | 0 |
| company_search | 2 | 2 | 0 | 0 |
| concept_discovery | 2 | 2 | 0 | 0 |
| cross_company_comparison | 2 | 2 | 0 | 0 |
| earnings_release | 2 | 2 | 0 | 0 |
| edge_cases | 2 | 2 | 0 | 0 |
| filing_attribution | 2 | 2 | 0 | 0 |
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