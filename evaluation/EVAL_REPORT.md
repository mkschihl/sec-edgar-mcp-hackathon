# SEC EDGAR Agent — Evaluation Report

**Agent:** `sec_edgar_agent`  
**Environment:** `gsa-hackathon` (IBM Cloud Toronto)  
**Run date:** 2026-11-19 01:26  
**Duration:** 94s for 23 questions  

---

## Summary

| Metric | Value |
|---|---|
| Total questions | 23 |
| ✅ Pass | 22 (96%) |
| ⚠️ Partial | 0 (0%) |
| ❌ Fail | 1 (4%) |

---

## Results by Question

| ID | Diff | Category | Score | Routing | Expected Tools | Tools Fired | Notes |
|---|---|---|---|---|---|---|---|
| BQ-01 | 🟢 easy | company_search | ✅ pass |  | `search_companies` | `search_companies` | All expected tools fired. |
| BQ-02 | 🟢 easy | company_search | ✅ pass |  | `search_companies` | `search_companies` | All expected tools fired. |
| BQ-03 | 🟢 easy | company_resolution | ✅ pass |  | `resolve_company` | `resolve_company` | All expected tools fired. |
| BQ-04 | 🟢 easy | company_resolution | ✅ pass |  | `resolve_company` | `resolve_company` | All expected tools fired. |
| BQ-05 | 🟢 easy | recent_filings | ✅ pass |  | `get_recent_filings` | `resolve_company`, `get_recent_filings` | All expected tools fired. |
| BQ-06 | 🟢 easy | recent_filings | ✅ pass |  | `get_recent_filings` | `resolve_company`, `get_recent_filings` | All expected tools fired. |
| BQ-07 | 🟡 medium | annual_facts | ✅ pass | routing_ok | `get_company_fact` | `resolve_company`, `get_company_fact` | routing_ok — all expected tools fired. |
| BQ-08 | 🟡 medium | annual_facts | ✅ pass |  | `get_company_fact` | `search_companies`, `get_company_fact` | All expected tools fired. |
| BQ-09 | 🟡 medium | quarterly_facts | ✅ pass | routing_ok | `get_quarterly_facts` | `resolve_company`, `get_quarterly_facts` | routing_ok — all expected tools fired. |
| BQ-10 | 🟡 medium | quarterly_facts | ✅ pass | routing_ok | `get_quarterly_facts` | `resolve_company`, `get_quarterly_facts` | routing_ok — all expected tools fired. |
| BQ-11 | 🟡 medium | concept_discovery | ✅ pass |  | `list_concepts` | `list_concepts` | All expected tools fired. |
| BQ-12 | 🟡 medium | concept_discovery | ✅ pass |  | `list_concepts` | `list_concepts` | All expected tools fired. |
| BQ-13 | 🔴 hard | cross_company_comparison | ✅ pass |  | `compare_companies` | `resolve_company`, `compare_companies` | All expected tools fired. |
| BQ-14 | 🔴 hard | cross_company_comparison | ✅ pass |  | `compare_companies` | `compare_companies` | All expected tools fired. |
| BQ-15 | 🔴 hard | filing_attribution | ✅ pass | routing_ok | `get_company_fact` | `resolve_company`, `get_company_fact`, `get_filing_metadata` | routing_ok — all expected tools fired. |
| BQ-16 | 🔴 hard | filing_attribution | ✅ pass | routing_ok | `get_company_fact` | `resolve_company`, `get_company_fact`, `get_filing_metadata` | routing_ok — all expected tools fired. |
| BQ-17 | 🔴 hard | multi_step_discovery | ✅ pass |  | `search_companies`, `get_company_fact` | `search_companies`, `get_company_fact` | All expected tools fired. |
| BQ-18 | 🔴 hard | multi_step_discovery | ✅ pass | routing_ok | `search_companies`, `get_recent_filings` | `search_companies`, `resolve_company`, `get_recent_filings` | routing_ok — all expected tools fired. |
| BQ-19 | 🟢 easy | edge_cases | ❌ fail |  | `get_recent_filings` | `search_companies` | No expected tools fired. Missing: ['sec_edgar_get_recent_filings']. |
| BQ-20 | 🟡 medium | edge_cases | ✅ pass | routing_ok | `get_quarterly_facts` | `resolve_company`, `get_quarterly_facts` | routing_ok — all expected tools fired. |
| BQ-21 | 🟢 easy | out_of_scope | ✅ pass |  |  | *(none)* | Correctly declined to answer out-of-scope question. |
| BQ-22 | 🟢 easy | out_of_scope | ✅ pass |  |  | *(none)* | Correctly declined to answer out-of-scope question. |
| BQ-23 | 🟡 medium | out_of_scope | ✅ pass |  |  | *(none)* | Correctly declined to answer out-of-scope question. |

---

## Agent Responses

### BQ-01 — ✅ PASS
**Question:** Find all companies with 'Berkshire' in their name.  
**Expected tools:** sec_edgar_search_companies  
**Tools fired:** sec_edgar_search_companies  

<details><summary>Agent response</summary>

```
Here are the companies whose name contains **“Berkshire.”** The list includes both exchange‑listed tickers and entities found in recent filings.

| # | Company Name | Ticker (if any) | CIK | Source | Recent 10‑K? |
|---|--------------|----------------|------|--------|--------------|
| 1 | **BERKSHIRE HATHAWAY INC** | BRK‑B / BRK‑A (dual‑class) | 0001067983 | exchange_listed | ✅ |
| 2 | **BERKSHIRE HILLS BANCORP INC** | BHLB | 0001108134 | all_filers | ✅ |
| 3 | **Berkshire Grey, Inc.** | – | 0001824734 | all_filers | ✅ |
| 4 | **BERKSHIRE INCOME REALTY INC** | – | 0001178862 | all_filers | ✅ |
| 5 | **BERKSHIRE HATHAWAY ENERGY CO** | – | 0001081316 | all_filers | ✅ |
| 6 | **BERKSHIRE BANCORP INC /DE/** | – | 0000759718 | all_filers | ✅ |

All of the matches have recent 10‑K filings (`has_recent_10k` = true). If you’d like more details about any of these entities (e.g., SIC code, state of incorporation, recent filings, or financial facts), just let me know which one(s) to focus on.
```

</details>

### BQ-02 — ✅ PASS
**Question:** I'm looking for companies related to 'General Electric'. What comes up?  
**Expected tools:** sec_edgar_search_companies  
**Tools fired:** sec_edgar_search_companies  

<details><summary>Agent response</summary>

```
Here are the companies that match the name **“General Electric”** in the SEC’s filings database:

| # | Company Name | Ticker | CIK | Source | Recent 10‑K? |
|---|--------------|--------|-----|--------|--------------|
| 1 | GENERAL ELECTRIC CO | GE | 0000040545 | exchange_listed | ✅ |
| 2 | PORTLAND GENERAL ELECTRIC CO /OR/ | POR | 0000784977 | exchange_listed | ✅ |
| 3 | GENERAL ELECTRIC CAPITAL CORP | *(no ticker listed)* | 0000040554 | all_filers | ✅ |
| 4 | GENERAL ELECTRIC CAPITAL SERVICES INC/CT | *(no ticker listed)* | 0000797463 | all_filers | ✅ |

**What’s next?**  
- If you’re interested in the primary operating company, **General Electric Co. (ticker GE, CIK 0000040545)** is the main listed entity and has recent 10‑K filings.  
- Let me know which company you’d like to explore further (e.g., recent filings, financial facts, etc.), or if you’d like details on any of the other entities.
```

</details>

### BQ-03 — ✅ PASS
**Question:** What is the SEC CIK number and industry classification for Microsoft?  
**Expected tools:** sec_edgar_resolve_company  
**Tools fired:** sec_edgar_resolve_company  

<details><summary>Agent response</summary>

```
**SEC CIK:** 0000789019  
**Industry Classification (SIC):** 7372 – Services‑Prepackaged Software  

*State of Incorporation:* Washington (WA)  

These details are taken directly from the SEC’s company registry for Microsoft Corp.
```

</details>

### BQ-04 — ✅ PASS
**Question:** Tell me about Alphabet Inc. — what state is it incorporated in and what SIC code does it use?  
**Expected tools:** sec_edgar_resolve_company  
**Tools fired:** sec_edgar_resolve_company  

<details><summary>Agent response</summary>

```
**Alphabet Inc. (ticker GOOGL, CIK 0001652044)**  

- **State of Incorporation:** Delaware (DE)  
- **SIC Code:** 7370 – “Services‑Computer Programming, Data Processing, Etc.”
```

</details>

### BQ-05 — ✅ PASS
**Question:** List the five most recent 10-K filings for Microsoft.  
**Expected tools:** sec_edgar_get_recent_filings  
**Tools fired:** sec_edgar_resolve_company, sec_edgar_get_recent_filings  

<details><summary>Agent response</summary>

```
**Microsoft Corp – Five Most Recent Form 10‑K Filings**

| Filing Date | Report (Fiscal) Period End | Accession Number | Primary Document |
|------------|----------------------------|------------------|------------------|
| 2026‑07‑29 | 2026‑06‑30 | 0001193125‑26‑323660 | msft-20260630.htm |
| 2025‑07‑30 | 2025‑06‑30 | 0000950170‑25‑100235 | msft-20250630.htm |
| 2024‑07‑30 | 2024‑06‑30 | 0000950170‑24‑087843 | msft-20240630.htm |
| 2023‑07‑27 | 2023‑06‑30 | 0000950170‑23‑035122 | msft-20230630.htm |
| 2022‑07‑28 | 2022‑06‑30 | 0001564590‑22‑026876 | msft-10k_20220630.htm |

These entries are taken directly from the SEC’s filing database for Microsoft Corp (CIK 0000789019).
```

</details>

### BQ-06 — ✅ PASS
**Question:** Show me the 10 most recent 10-Q filings for Johnson & Johnson (ticker: JNJ).  
**Expected tools:** sec_edgar_get_recent_filings  
**Tools fired:** sec_edgar_resolve_company, sec_edgar_get_recent_filings  

<details><summary>Agent response</summary>

```
**Johnson & Johnson – 10 most recent Form 10‑Q filings**

| # | Filing Date | Report Date | Accession Number | Primary Document |
|---|-------------|------------|------------------|------------------|
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

These filings are the most recent 10‑Q submissions for **Johnson & Johnson (CIK 0000200406, ticker JNJ)** as recorded by the SEC.
```

</details>

### BQ-07 — ✅ PASS
**Question:** Show me the last 5 annual net income figures for Apple.  
**Expected tools:** sec_edgar_get_company_fact  
**Tools fired:** sec_edgar_resolve_company, sec_edgar_get_company_fact  

<details><summary>Agent response</summary>

```
**Apple Inc. – Net Income (NetIncomeLoss)**  
*XBRL concept: NetIncomeLoss (us‑gaap)*  

| Fiscal Year | Period End | Net Income (USD) | Form | Accession Number |
|-------------|------------|------------------|------|-------------------|
| 2022 | 2022‑09‑24 | $99.8 billion | 10‑K | 0000320193‑24‑000123 |
| 2023 | 2023‑09‑30 | $97.0 billion | 10‑K | 0000320193‑25‑000079 |
| 2024 | 2024‑09‑28 | $93.7 billion | 10‑K | 0000320193‑26‑000026 |
| 2025 | 2025‑09‑27 | $112.0 billion | 10‑K | 0000320193‑26‑000026 |
| 2026 | 2026‑09‑26 | $132.2 billion | 10‑K | 0000320193‑26‑000026 |

*All values are presented in U.S. dollars (USD) as reported in the most recent 10‑K filings.*
```

</details>

### BQ-08 — ✅ PASS
**Question:** What were Amazon's total assets for the last 4 fiscal years?  
**Expected tools:** sec_edgar_get_company_fact  
**Tools fired:** sec_edgar_search_companies, sec_edgar_get_company_fact  

<details><summary>Agent response</summary>

```
**Amazon.com, Inc. – Total Assets (last 4 fiscal years)**  

| Fiscal Year | Period End | Total Assets (USD) | Form | Accession Number |
|-------------|------------|-------------------|------|------------------|
| 2025 | 2025‑12‑31 | $818.0 billion | 10‑K | 0001018724‑26‑000004 |
| 2024 | 2024‑12‑31 | $624.9 billion | 10‑K | 0001018724‑26‑000004 |
| 2023 | 2023‑12‑31 | $527.9 billion | 10‑K | 0001018724‑26‑000004 |
| 2022 | 2022‑12‑31 | $462.7 billion | 10‑K | 0001018724‑25‑000004 |

**XBRL concept used:** `Assets` (us‑gaap taxonomy).  

All values are reported in U.S. dollars (USD) as disclosed in Amazon’s annual Form 10‑K filings.
```

</details>

### BQ-09 — ✅ PASS
**Question:** Show me Apple's quarterly revenue for the last 8 quarters.  
**Expected tools:** sec_edgar_get_quarterly_facts  
**Tools fired:** sec_edgar_resolve_company, sec_edgar_get_quarterly_facts  

<details><summary>Agent response</summary>

```
**Apple Inc. – Quarterly Revenue (last 8 quarters)**  
*XBRL concept used: **RevenueFromContractWithCustomerExcludingAssessedTax** (us‑gaap)*  

| Fiscal Year | Quarter | Period End | Revenue (USD) | Form | Accession Number | Note |
|-------------|---------|------------|---------------|------|------------------|------|
| 2026 | Q4 (derived) | 2026‑09‑26 | $114.5 billion | 10‑K | 0000320193-26-000026 | Derived: annual filing minus nine‑month YTD |
| 2026 | Q3 | 2026‑06‑27 | $109.4 billion | 10‑Q | 0000320193-26-000020 | |
| 2026 | Q2 | 2026‑03‑28 | $111.2 billion | 10‑Q | 0000320193-26-000013 | |
| 2026 | Q1 | 2025‑12‑27 | $143.8 billion | 10‑Q | 0000320193-26-000006 | |
| 2025 | Q4 (derived) | 2025‑09‑27 | $102.5 billion | 10‑K | 0000320193-26-000026 | Derived: annual filing minus nine‑month YTD |
| 2025 | Q3 | 2025‑06‑28 | $94.0 billion | 10‑Q | 0000320193-26-000020 | |
| 2025 | Q2 | 2025‑03‑29 | $95.4 billion | 10‑Q | 0000320193-26-000013 | |
| 2025 | Q1 | 2024‑12‑28 | $124.3 billion | 10‑Q | 0000320193-26-000006 | |

**Notes**

* Q4 values are marked **derived** because they are calculated as the full‑year revenue (from the 10‑K filing) minus the nine‑month YTD figure reported in the prior 10‑Q.  
* All figures are in **USD** and represent total revenue for the quarter.  

If you need the source filing URLs or further details for any specific quarter, just let me know!
```

</details>

### BQ-10 — ✅ PASS
**Question:** What was Microsoft's net income in each of the last 6 quarters?  
**Expected tools:** sec_edgar_get_quarterly_facts  
**Tools fired:** sec_edgar_resolve_company, sec_edgar_get_quarterly_facts  

<details><summary>Agent response</summary>

```
**Microsoft Corp – Net Income (Loss) – Last 6 Reported Quarters**  
*(Concept: **NetIncomeLoss**, taxonomy: us‑gaap, unit: USD)*  

| Fiscal Quarter | Fiscal Year | Period End | Net Income (USD) | Form | Accession Number | Derived? |
|----------------|------------|------------|------------------|------|------------------|----------|
| Q1 | 2027 | 2026‑09‑30 | $36.63 billion | 10‑Q | 0001193125‑26‑436133 | No |
| Q4 | 2026 | 2026‑06‑30 | $35.77 billion | 10‑K | 0001193125‑26‑323660 | Yes (derived: annual minus nine‑month YTD) |
| Q3 | 2026 | 2026‑03‑31 | $31.78 billion | 10‑Q | 0001193125‑26‑191507 | No |
| Q2 | 2026 | 2025‑12‑31 | $38.46 billion | 10‑Q | 0001193125‑26‑027207 | No |
| Q1 | 2026 | 2025‑09‑30 | $27.75 billion | 10‑Q | 0001193125‑26‑436133 | No |
| Q4 | 2025 | 2025‑06‑30 | $27.23 billion | 10‑K | 0001193125‑26‑323660 | Yes (derived: annual minus nine‑month YTD) |

**Notes**

* “Derived” quarters (Q4) are calculated by the SEC as the full‑year amount minus the nine‑month YTD amount, because the 10‑K filing reports the annual total and the nine‑month YTD figure.  
* All values are in **USD** and are taken directly from Microsoft’s XBRL filings (10‑Q and 10‑K) as returned by the SEC’s company‑facts endpoint.  

If you need the filing URLs or further details for any of these quarters, let me know!
```

</details>

### BQ-11 — ✅ PASS
**Question:** What revenue-related XBRL concepts does Apple report in us-gaap?  
**Expected tools:** sec_edgar_list_concepts  
**Tools fired:** sec_edgar_list_concepts  

<details><summary>Agent response</summary>

```
**Apple Inc. (CIK 0000320193) – us‑gaap revenue‑related XBRL concepts**

| Concept (tag) | Human‑readable label |
|---------------------------|-----------------------------------------------|
| Revenues | Revenues |
| RevenueFromContractWithCustomerExcludingAssessedTax | Revenue from Contract with Customer, Excluding Assessed Tax |
| ContractWithCustomerLiabilityRevenueRecognized | Contract with Customer, Liability, Revenue Recognized |
| DeferredRevenueCurrent | Deferred Revenue, Current |
| DeferredRevenueNoncurrent | Deferred Revenue, Non‑current |
| IncreaseDecreaseInDeferredRevenue | Increase (Decrease) in Deferred Revenue |
| SalesRevenueNet | Revenue, Net (Deprecated 2018‑01‑31) |
| SalesRevenueServicesGross | Sales Revenue, Services, Other (Deprecated 2018‑01‑31) |

These are the revenue‑related tags that Apple reports under the **us‑gaap** taxonomy, as returned by the SEC’s company‑facts endpoint. If you need the actual numeric values for any of these concepts, let me know which one(s) and I can retrieve the time‑series data.
```

</details>

### BQ-12 — ✅ PASS
**Question:** I want to find debt-related financial concepts for Tesla. What us-gaap concepts are available?  
**Expected tools:** sec_edgar_list_concepts  
**Tools fired:** sec_edgar_list_concepts  

<details><summary>Agent response</summary>

```
**Debt‑related us‑gaap concepts reported by Tesla, Inc. (CIK 0001318605)**  

| Concept (XBRL tag) | Label (human‑readable description) |
|---------------------|-------------------------------------|
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
| AvailableForSaleSecuritiesDebtMaturitiesRollingAfterYearTenAmortizedCostBasis | Debt Securities, Available‑for‑sale, Maturity, Rolling after 10 Years, Amortized Cost |
| AvailableForSaleSecuritiesDebtMaturitiesRollingYearSixThroughTenAmortizedCostBasis | Debt Securities, Available‑for‑sale, Maturity, Rolling after 5‑10 Years, Amortized Cost |
| AvailableForSaleSecuritiesDebtMaturitiesRollingYearSixThroughTenFair...
```

</details>

### BQ-13 — ✅ PASS
**Question:** Compare the most recent annual net income for Apple, Microsoft, and Google.  
**Expected tools:** sec_edgar_compare_companies  
**Tools fired:** sec_edgar_resolve_company, sec_edgar_compare_companies  

<details><summary>Agent response</summary>

```
**Most recent annual Net Income (NetIncomeLoss) – SEC‑reported values**

| Company | Net Income | Unit | Fiscal Year | Period End | Form | Accession Number |
|---------|------------|------|-------------|------------|------|------------------|
| Apple Inc. | $132.2 billion | USD | 2026 | 2026‑09‑26 | 10‑K | 0000320193‑26‑000026 |
| MICROSOFT CORP | $133.7 billion | USD | 2026 | 2026‑06‑30 | 10‑K | 0001193125‑26‑323660 |
| Alphabet Inc. (Google) | $132.2 billion | USD | 2025 | 2025‑12‑31 | 10‑K | 0001652044‑26‑000018 |

**Notes**

* The XBRL concept used is **NetIncomeLoss** (us‑gaap taxonomy).  
* Fiscal year‑ends differ across the companies (Apple ends 26 Sep 2026, Microsoft ends 30 Jun 2026, Alphabet ends 31 Dec 2025). This mis‑alignment is reported in the tool warnings and should be considered when comparing the figures.  
* All values are taken directly from the most recent Form 10‑K filings on the SEC EDGAR system. No estimates or market data are involved.
```

</details>

### BQ-14 — ✅ PASS
**Question:** Which company has more total assets — JPMorgan Chase (JPM) or Bank of America (BAC)? Use the most recent annual figures.  
**Expected tools:** sec_edgar_compare_companies  
**Tools fired:** sec_edgar_compare_companies  

<details><summary>Agent response</summary>

```
**Total assets (most recent annual figures, FY 2025)**  

| Company | Fiscal Year | Period End | Assets | Unit | Form | Accession Number |
|---------|-------------|------------|--------|------|------|------------------|
| JPMorgan Chase & Co. | 2025 | 2025‑12‑31 | $4.425 trillion | USD | 10‑K | 0001628280‑26‑008131 |
| Bank of America Corp. | 2025 | 2025‑12‑31 | $3.412 trillion | USD | 10‑K | 0000070858‑26‑000157 |

**Result:** JPMorgan Chase reports higher total assets than Bank of America.  

*Concept used:* **Assets** (us‑gaap). No warnings were returned, so the fiscal‑year dates and units are directly comparable.
```

</details>

### BQ-15 — ✅ PASS
**Question:** Which SEC filing reported Apple's most recent annual revenue? Give me the accession number and a link to the filing.  
**Expected tools:** sec_edgar_get_company_fact  
**Tools fired:** sec_edgar_resolve_company, sec_edgar_get_company_fact, sec_edgar_get_filing_metadata  

<details><summary>Agent response</summary>

```
**Apple Inc. – Most recent annual revenue**

- **Revenue (Fiscal Year ended 2026‑09‑26):** **$478.8 billion**  
- **XBRL concept used:** `RevenueFromContractWithCustomerExcludingAssessedTax` (the SEC maps the generic “Revenues” request to this concept)
- **Accession number:** **0000320193-26-000026**  
- **Filing type:** 10‑K  
- **Filing date:** 2026‑11‑03  
- **Report date (fiscal year end):** 2026‑09‑26  
- **EDGAR viewer URL:** https://www.sec.gov/Archives/edgar/data/320193/000032019326000026/aapl-20260926.htm  

This filing contains the reported annual revenue figure for Apple’s most recent fiscal year.
```

</details>

### BQ-16 — ✅ PASS
**Question:** What form type and filing date corresponds to Microsoft's most recent annual net income figure?  
**Expected tools:** sec_edgar_get_company_fact  
**Tools fired:** sec_edgar_resolve_company, sec_edgar_get_company_fact, sec_edgar_get_filing_metadata  

<details><summary>Agent response</summary>

```
**Microsoft Corp – Most recent annual Net Income**

- **Net Income (FY 2026):** $133.7 billion (USD)  
- **Fiscal Year End:** 2026‑06‑30  
- **Form Type:** 10‑K  
- **Filing Date:** 2026‑07‑29  
- **Accession Number:** 0001193125‑26‑323660  
- **EDGAR Viewer URL:** https://www.sec.gov/Archives/edgar/data/789019/000119312526323660/msft-20260630.htm  

*XBRL concept used:* **NetIncomeLoss** (us‑gaap).
```

</details>

### BQ-17 — ✅ PASS
**Question:** I don't know the ticker — find companies with 'Pfizer' in the name, then show me the last 4 annual revenue figures for the main one.  
**Expected tools:** sec_edgar_search_companies, sec_edgar_get_company_fact  
**Tools fired:** sec_edgar_search_companies, sec_edgar_get_company_fact  

<details><summary>Agent response</summary>

```
**Company found**

| Company | Ticker | CIK | SIC | SIC Description | State of Incorporation |
|---------|--------|------|-----|-----------------|------------------------|
| PFIZER INC | PFE | 0000078003 | 2834 | Pharmaceutical Preparations | Delaware |

**Last 4 annual revenue figures (concept: “Revenues”)**

| Fiscal Year | Period End | Revenue (USD) | Form | Accession Number |
|-------------|------------|--------------|------|------------------|
| 2022 | 2022‑12‑31 | $101.2 billion* | 10‑K | 0000078003‑25‑000054 |
| 2023 | 2023‑12‑31 | $59.6 billion* | 10‑K | 0000078003‑26‑000026 |
| 2024 | 2024‑12‑31 | $63.6 billion | 10‑K | 0000078003‑26‑000026 |
| 2025 | 2025‑12‑31 | $62.6 billion | 10‑K | 0000078003‑26‑000026 |

\*These values were **recast** in a later filing; the original amounts reported were $100.33 billion (2022) and $58.50 billion (2023). The recast values are shown above, per the SEC filing.  

**Sources** – The revenue figures come from Pfizer’s XBRL “Revenues” concept in its recent Form 10‑K filings (accession numbers shown). The filing index URLs are provided in each row if you need to view the full documents.
```

</details>

### BQ-18 — ✅ PASS
**Question:** Search for companies with 'Exxon' in their name, resolve the main one, then list its 5 most recent 10-K filings.  
**Expected tools:** sec_edgar_search_companies, sec_edgar_get_recent_filings  
**Tools fired:** sec_edgar_search_companies, sec_edgar_resolve_company, sec_edgar_get_recent_filings  

<details><summary>Agent response</summary>

```
**Resolved Company (with recent 10‑K filings)**  
- **Name:** EXXON MOBIL CORP  
- **Ticker:** XOM  
- **CIK:** 0000034088  
- **SIC:** 2911 – Petroleum Refining  
- **State of Incorporation:** TX  

**5 Most Recent Form 10‑K Filings**

| Filing Date | Report (Fiscal) Year End | Accession Number | Primary Document |
|-------------|--------------------------|------------------|------------------|
| 2026‑02‑18 | 2025‑12‑31 | 0000034088‑26‑000045 | xom-20251231.htm |
| 2025‑02‑19 | 2024‑12‑31 | 0000034088‑25‑000010 | xom-20241231.htm |
| 2024‑02‑28 | 2023‑12‑31 | 0000034088‑24‑000018 | xom-20231231.htm |
| 2023‑02‑22 | 2022‑12‑31 | 0000034088‑23‑000020 | xom-20221231.htm |
| 2022‑02‑23 | 2021‑12‑31 | 0000034088‑22‑000011 | xom-20211231.htm |

These are the latest five annual reports (Form 10‑K) filed by Exxon Mobil Corp as recorded by the SEC.
```

</details>

### BQ-19 — ❌ FAIL
**Question:** What SEC filings has the company with ticker ZZZZNOTREAL submitted recently?  
**Expected tools:** sec_edgar_get_recent_filings  
**Tools fired:** sec_edgar_search_companies  

<details><summary>Agent response</summary>

```
I’m sorry, but I couldn’t find any SEC‑registered company or ticker matching **ZZZZNOTREAL**. If you have an alternative name, ticker, or CIK for the entity you’re interested in, please let me know and I can look up its recent filings.
```

</details>

### BQ-20 — ✅ PASS
**Question:** Show me Apple's quarterly EarningsPerShareBasicAndDiluted for the last 4 quarters.  
**Expected tools:** sec_edgar_get_quarterly_facts  
**Tools fired:** sec_edgar_resolve_company, sec_edgar_get_quarterly_facts  

<details><summary>Agent response</summary>

```
**Apple Inc. – Quarterly EPS (Basic & Diluted)**  

| Fiscal Quarter | Fiscal Year | Period End | EPS Basic (USD/share) | EPS Diluted (USD/share) | Form | Accession Number |
|----------------|------------|------------|-----------------------|--------------------------|------|-------------------|
| Q3 | 2026 | 2026‑06‑27 | 2.03 | 2.02 | 10‑Q | 0000320193‑26‑000020 |
| Q2 | 2026 | 2026‑03‑28 | 2.02 | 2.01 | 10‑Q | 0000320193‑26‑000013 |
| Q1 | 2026 | 2025‑12‑27 | 2.85 | 2.84 | 10‑Q | 0000320193‑26‑000006 |
| Q3 | 2025 | 2025‑06‑28 | 1.57 | 1.57 | 10‑Q | 0000320193‑26‑000020 |

**Notes**

* The data come from the XBRL concept **EarningsPerShareBasic** (basic EPS) and **EarningsPerShareDiluted** (diluted EPS) in the **us‑gaap** taxonomy.  
* Q4 values are not shown because per‑share figures are not additive; the SEC does not provide derived Q4 per‑share numbers.  
* All observations are from Apple’s 10‑Q filings (the accession numbers are provided for reference).
```

</details>

### BQ-21 — ✅ PASS
**Question:** What is Apple's current stock price?  
**Expected tools:**   
**Tools fired:** *(none)*  

<details><summary>Agent response</summary>

```
I’m sorry, but I can’t help with that.
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
I’m sorry, but I can’t provide revenue forecasts or any forward‑looking estimates. I can, however, retrieve Microsoft’s historical revenue figures from its SEC filings if that would be helpful. Let me know if you’d like to see those numbers.
```

</details>

---

## Tool Utilisation

| Tool | Expected in N Qs | Qs Fired | Fire Rate | Total Calls |
|---|---|---|---|---|
| `sec_edgar_compare_companies` | 2 | 2 | 100% | 2 |
| `sec_edgar_get_company_fact` | 5 | 5 | 100% | 5 |
| `sec_edgar_get_quarterly_facts` | 3 | 3 | 100% | 4 |
| `sec_edgar_get_recent_filings` | 4 | 3 | 75% | 3 |
| `sec_edgar_list_concepts` | 2 | 2 | 100% | 2 |
| `sec_edgar_resolve_company` | 2 | 12 | 600% | 14 |
| `sec_edgar_search_companies` | 4 | 6 | 150% | 6 |

---

## Results by Category

| Category | Questions | Pass | Partial | Fail |
|---|---|---|---|---|
| annual_facts | 2 | 2 | 0 | 0 |
| company_resolution | 2 | 2 | 0 | 0 |
| company_search | 2 | 2 | 0 | 0 |
| concept_discovery | 2 | 2 | 0 | 0 |
| cross_company_comparison | 2 | 2 | 0 | 0 |
| edge_cases | 2 | 1 | 0 | 1 |
| filing_attribution | 2 | 2 | 0 | 0 |
| multi_step_discovery | 2 | 2 | 0 | 0 |
| out_of_scope | 3 | 3 | 0 | 0 |
| quarterly_facts | 2 | 2 | 0 | 0 |
| recent_filings | 2 | 2 | 0 | 0 |

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