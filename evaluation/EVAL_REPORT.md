# SEC EDGAR Agent — Evaluation Report

**Agent:** `sec_edgar_agent`  
**Environment:** `gsa-hackathon` (IBM Cloud Toronto)  
**Run date:** 2026-11-19 03:04  
**Duration:** 6s for 23 questions  

---

## Summary

| Metric | Value |
|---|---|
| Total questions | 23 |
| ✅ Pass | 23 (100%) |
| ⚠️ Partial | 0 (0%) |
| ❌ Fail | 0 (0%) |

---

## Results by Question

| ID | Diff | Category | Score | Routing | Expected Tools | Tools Fired | Notes |
|---|---|---|---|---|---|---|---|
| BQ-01 | 🟢 easy | company_search | ✅ pass | routing_ok | `search_companies` | `search_companies` | routing_ok — all expected tools fired. |
| BQ-02 | 🟢 easy | company_search | ✅ pass | routing_ok | `search_companies` | `search_companies` | routing_ok — all expected tools fired. |
| BQ-03 | 🟢 easy | company_resolution | ✅ pass | routing_ok | `resolve_company` | `resolve_company` | routing_ok — all expected tools fired. |
| BQ-04 | 🟢 easy | company_resolution | ✅ pass | routing_ok | `resolve_company` | `resolve_company` | routing_ok — all expected tools fired. |
| BQ-05 | 🟢 easy | recent_filings | ✅ pass | routing_ok | `get_recent_filings` | `resolve_company`, `get_recent_filings` | routing_ok — all expected tools fired. |
| BQ-06 | 🟢 easy | recent_filings | ✅ pass | routing_ok | `get_recent_filings` | `get_recent_filings` | routing_ok — all expected tools fired. |
| BQ-07 | 🟡 medium | annual_facts | ✅ pass | routing_ok | `get_company_fact` | `resolve_company`, `get_company_fact` | routing_ok — all expected tools fired. |
| BQ-08 | 🟡 medium | annual_facts | ✅ pass | routing_ok | `get_company_fact` | `resolve_company`, `get_company_fact` | routing_ok — all expected tools fired. |
| BQ-09 | 🟡 medium | quarterly_facts | ✅ pass | routing_ok | `get_quarterly_facts` | `resolve_company`, `get_quarterly_facts` | routing_ok — all expected tools fired. |
| BQ-10 | 🟡 medium | quarterly_facts | ✅ pass | routing_ok | `get_quarterly_facts` | `get_quarterly_facts` | routing_ok — all expected tools fired. |
| BQ-11 | 🟡 medium | concept_discovery | ✅ pass | routing_ok | `list_concepts` | `list_concepts` | routing_ok — all expected tools fired. |
| BQ-12 | 🟡 medium | concept_discovery | ✅ pass | routing_ok | `list_concepts` | `list_concepts` | routing_ok — all expected tools fired. |
| BQ-13 | 🔴 hard | cross_company_comparison | ✅ pass | routing_ok | `compare_companies` | `compare_companies` | routing_ok — all expected tools fired. |
| BQ-14 | 🔴 hard | cross_company_comparison | ✅ pass | routing_ok | `compare_companies` | `compare_companies` | routing_ok — all expected tools fired. |
| BQ-15 | 🔴 hard | filing_attribution | ✅ pass | routing_ok | `get_company_fact` | `resolve_company`, `get_company_fact`, `get_filing_metadata` | routing_ok — all expected tools fired. |
| BQ-16 | 🔴 hard | filing_attribution | ✅ pass | routing_ok | `get_company_fact` | `resolve_company`, `get_company_fact`, `get_filing_metadata` | routing_ok — all expected tools fired. |
| BQ-17 | 🔴 hard | multi_step_discovery | ✅ pass | routing_ok | `search_companies`, `get_company_fact` | `search_companies`, `get_company_fact` | routing_ok — all expected tools fired. |
| BQ-18 | 🔴 hard | multi_step_discovery | ✅ pass | routing_ok | `search_companies`, `get_recent_filings` | `search_companies`, `resolve_company`, `get_recent_filings` | routing_ok — all expected tools fired. |
| BQ-19 | 🟢 easy | edge_cases | ✅ pass | routing_ok |  | `search_companies` | routing_ok — all expected tools fired. |
| BQ-20 | 🟡 medium | edge_cases | ✅ pass | routing_ok | `get_quarterly_facts` | `resolve_company`, `get_quarterly_facts` | routing_ok — all expected tools fired. |
| BQ-21 | 🟢 easy | out_of_scope | ✅ pass | routing_ok |  | *(none)* | routing_ok — correctly declined out-of-scope question. |
| BQ-22 | 🟢 easy | out_of_scope | ✅ pass | routing_ok |  | *(none)* | routing_ok — correctly declined out-of-scope question. |
| BQ-23 | 🟡 medium | out_of_scope | ✅ pass | routing_ok |  | *(none)* | routing_ok — correctly declined out-of-scope question. |

---

## Agent Responses

### BQ-01 — ✅ PASS
**Question:** Find all companies with 'Berkshire' in their name.  
**Expected tools:** sec_edgar_search_companies  
**Tools fired:** sec_edgar_search_companies  

<details><summary>Agent response</summary>

```
Here are the companies that contain “Berkshire” in their name (as returned by the SEC’s company‑ticker database):

| # | Company Name | Ticker | CIK | Source | Recent 10‑K? |
|---|--------------|--------|------|--------|--------------|
| 1 | BERKSHIRE HATHAWAY INC | BRK‑B | 0001067983 | exchange_listed | ✅ |
| 2 | BERKSHIRE HATHAWAY INC | BRK‑A | 0001067983 | exchange_listed | ✅ |
| 3 | BERKSHIRE HILLS BANCORP INC | BHLB | 0001108134 | all_filers | ✅ |
| 4 | Berkshire Grey, Inc. | (none listed) | 0001824734 | all_filers | ✅ |
| 5 | BERKSHIRE INCOME REALTY INC | (none listed) | 0001178862 | all_filers | ✅ |
| 6 | BERKSHIRE HATHAWAY ENERGY CO | (none listed) | 0001081316 | all_filers | ✅ |
| 7 | BERKSHIRE BANCORP INC /DE/ | (none listed) | 0000759718 | all_filers | ✅ |

All of these entries have a recent 10‑K filing (`has_recent_10k = true`). Let me know which company (or companies) you’d like to explore further—e.g., retrieve recent filings, financial facts, or other SEC data.
```

</details>

### BQ-02 — ✅ PASS
**Question:** I'm looking for companies related to 'General Electric'. What comes up?  
**Expected tools:** sec_edgar_search_companies  
**Tools fired:** sec_edgar_search_companies  

<details><summary>Agent response</summary>

```
Here are the companies that match a search for **“General Electric”** in the SEC’s filings database:

| # | Company Name | Ticker | CIK | Source | Recent 10‑K? |
|---|--------------|--------|-----|--------|--------------|
| 1 | GENERAL ELECTRIC CO | **GE** | 0000040545 | exchange_listed | ✅ |
| 2 | PORTLAND GENERAL ELECTRIC CO /OR/ | **POR** | 0000784977 | exchange_listed | ✅ |
| 3 | GENERAL ELECTRIC CAPITAL CORP | (none) | 0000040554 | all_filers | ✅ |
| 4 | GENERAL ELECTRIC CAPITAL SERVICES INC/CT | (none) | 0000797463 | all_filers | ✅ |

**What to do next**

- If you’re interested in the primary operating company, **General Electric Co. (ticker GE, CIK 0000040545)** is the most common choice and has a recent 10‑K filing.  
- If you need details on any of the other entities (e.g., their recent filings, financial facts, etc.), let me know which one(s) and what information you’d like, and I’ll retrieve it from the SEC.
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

**State of Incorporation:** Washington (WA)
```

</details>

### BQ-04 — ✅ PASS
**Question:** Tell me about Alphabet Inc. — what state is it incorporated in and what SIC code does it use?  
**Expected tools:** sec_edgar_resolve_company  
**Tools fired:** sec_edgar_resolve_company  

<details><summary>Agent response</summary>

```
**Alphabet Inc.**  

- **State of Incorporation:** Delaware (DE)  
- **SIC Code:** 7370 – Services‑Computer Programming, Data Processing, Etc.
```

</details>

### BQ-05 — ✅ PASS
**Question:** List the five most recent 10-K filings for Microsoft.  
**Expected tools:** sec_edgar_get_recent_filings  
**Tools fired:** sec_edgar_resolve_company, sec_edgar_get_recent_filings  

<details><summary>Agent response</summary>

```
**Microsoft Corp – Five most recent Form 10‑K filings**

| Filing Date | Report (Fiscal) Period End | Accession Number | Primary Document |
|-------------|----------------------------|------------------|------------------|
| 2026‑07‑29 | 2026‑06‑30 | 0001193125-26-323660 | msft-20260630.htm |
| 2025‑07‑30 | 2025‑06‑30 | 0000950170-25-100235 | msft-20250630.htm |
| 2024‑07‑30 | 2024‑06‑30 | 0000950170-24-087843 | msft-20240630.htm |
| 2023‑07‑27 | 2023‑06‑30 | 0000950170-23-035122 | msft-20230630.htm |
| 2022‑07‑28 | 2022‑06‑30 | 0001564590-22-026876 | msft-10k_20220630.htm |

These filings are the latest annual reports (Form 10‑K) filed by Microsoft Corp (CIK 0000789019).
```

</details>

### BQ-06 — ✅ PASS
**Question:** Show me the 10 most recent 10-Q filings for Johnson & Johnson (ticker: JNJ).  
**Expected tools:** sec_edgar_get_recent_filings  
**Tools fired:** sec_edgar_get_recent_filings  

<details><summary>Agent response</summary>

```
**10 most recent 10‑Q filings for Johnson & Johnson (CIK 0000200406, ticker JNJ)**  

| # | Filing Date | Report Date (Period End) | Accession Number | Primary Document |
|---|-------------|--------------------------|------------------|------------------|
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

These entries are taken directly from the SEC’s recent filings API.
```

</details>

### BQ-07 — ✅ PASS
**Question:** Show me the last 5 annual net income figures for Apple.  
**Expected tools:** sec_edgar_get_company_fact  
**Tools fired:** sec_edgar_resolve_company, sec_edgar_get_company_fact  

<details><summary>Agent response</summary>

```
**Apple Inc. – Net Income (Loss) Attributable to Parent**  
*XBRL Concept: NetIncomeLoss (us‑gaap)*  

| Fiscal Year | Period End | Net Income (USD) | Form | Accession Number |
|-------------|------------|------------------|------|------------------|
| 2022 | 2022‑09‑24 | $99.8 billion | 10‑K | 0000320193‑24‑000123 |
| 2023 | 2023‑09‑30 | $97.0 billion | 10‑K | 0000320193‑25‑000079 |
| 2024 | 2024‑09‑28 | $93.7 billion | 10‑K | 0000320193‑26‑000026 |
| 2025 | 2025‑09‑27 | $112.0 billion | 10‑K | 0000320193‑26‑000026 |
| 2026 | 2026‑09‑26 | $132.2 billion | 10‑K | 0000320193‑26‑000026 |

*All values are in U.S. dollars (USD) as reported in the company’s annual 10‑K filings.*
```

</details>

### BQ-08 — ✅ PASS
**Question:** What were Amazon's total assets for the last 4 fiscal years?  
**Expected tools:** sec_edgar_get_company_fact  
**Tools fired:** sec_edgar_resolve_company, sec_edgar_get_company_fact  

<details><summary>Agent response</summary>

```
**Amazon.com, Inc. – Total Assets (USD)**  

| Fiscal Year | Period End | Total Assets | Form | Accession Number |
|-------------|------------|--------------|------|------------------|
| 2022 | 2022‑12‑31 | $462.7 billion | 10‑K | 0001018724‑25‑000004 |
| 2023 | 2023‑12‑31 | $527.9 billion | 10‑K | 0001018724‑26‑000004 |
| 2024 | 2024‑12‑31 | $624.9 billion | 10‑K | 0001018724‑26‑000004 |
| 2025 | 2025‑12‑31 | $818.0 billion | 10‑K | 0001018724‑26‑000004 |

**XBRL concept used:** `Assets` (us‑gaap taxonomy).  

All values are reported in US dollars (USD) as disclosed in Amazon’s annual Form 10‑K filings.
```

</details>

### BQ-09 — ✅ PASS
**Question:** Show me Apple's quarterly revenue for the last 8 quarters.  
**Expected tools:** sec_edgar_get_quarterly_facts  
**Tools fired:** sec_edgar_resolve_company, sec_edgar_get_quarterly_facts  

<details><summary>Agent response</summary>

```
**Apple Inc. – Quarterly Revenue (most recent 8 quarters)**  
*XBRL concept used: **RevenueFromContractWithCustomerExcludingAssessedTax** (us‑gaap)*  

| Fiscal Year | Quarter | Period End | Revenue (USD) | Form | Accession Number |
|-------------|---------|------------|--------------:|------|------------------|
| 2026 | Q4 (derived) | 2026‑09‑26 | $114.5 billion | 10‑K | 0000320193‑26‑000026 |
| 2026 | Q3 | 2026‑06‑27 | $109.4 billion | 10‑Q | 0000320193‑26‑000020 |
| 2026 | Q2 | 2026‑03‑28 | $111.2 billion | 10‑Q | 0000320193‑26‑000013 |
| 2026 | Q1 | 2025‑12‑27 | $143.8 billion | 10‑Q | 0000320193‑26‑000006 |
| 2025 | Q4 (derived) | 2025‑09‑27 | $102.5 billion | 10‑K | 0000320193‑26‑000026 |
| 2025 | Q3 | 2025‑06‑28 | $94.0 billion | 10‑Q | 0000320193‑26‑000020 |
| 2025 | Q2 | 2025‑03‑29 | $95.4 billion | 10‑Q | 0000320193‑26‑000013 |
| 2025 | Q1 | 2024‑12‑28 | $124.3 billion | 10‑Q | 0000320193‑26‑000006 |

**Notes**

* The Q4 values are **derived** (annual revenue from the 10‑K minus the nine‑month YTD figure from the Q3 10‑Q). The derivation is indicated in the “derived” column.  
* All amounts are presented in **U.S. dollars (USD)**.  
* The data comes from Apple’s SEC filings (Form 10‑K and Form 10‑Q) as identified by the accession numbers shown.
```

</details>

### BQ-10 — ✅ PASS
**Question:** What was Microsoft's net income in each of the last 6 quarters?  
**Expected tools:** sec_edgar_get_quarterly_facts  
**Tools fired:** sec_edgar_get_quarterly_facts  

<details><summary>Agent response</summary>

```
**Microsoft Corp – Net Income (attributable to parent) for the most recent 6 quarters**

| Fiscal Quarter | Fiscal Year | Period End | Net Income (USD) | Form | Accession Number | Derived? |
|----------------|------------|------------|------------------|------|------------------|----------|
| Q1 FY2027 | 2027 | 2026‑09‑30 | $36.6 billion | 10‑Q | 0001193125‑26‑436133 | No |
| Q4 FY2026 | 2026 | 2026‑06‑30 | $35.8 billion | 10‑K | 0001193125‑26‑323660 | Yes* |
| Q3 FY2026 | 2026 | 2026‑03‑31 | $31.8 billion | 10‑Q | 0001193125‑26‑191507 | No |
| Q2 FY2026 | 2026 | 2025‑12‑31 | $38.5 billion | 10‑Q | 0001193125‑26‑027207 | No |
| Q1 FY2026 | 2026 | 2025‑09‑30 | $27.7 billion | 10‑Q | 0001193125‑26‑436133 | No |
| Q4 FY2025 | 2025 | 2025‑06‑30 | $27.2 billion | 10‑K | 0001193125‑26‑323660 | Yes* |

\* **Derived**: The Q4 values are derived by subtracting the nine‑month YTD figure (from the Q3 10‑Q filing) from the full‑year amount reported in the subsequent 10‑K filing, as indicated in the filing metadata.

**XBRL concept used:** `NetIncomeLoss` (label: “Net Income (Loss) Attributable to Parent”).
```

</details>

### BQ-11 — ✅ PASS
**Question:** What revenue-related XBRL concepts does Apple report in us-gaap?  
**Expected tools:** sec_edgar_list_concepts  
**Tools fired:** sec_edgar_list_concepts  

<details><summary>Agent response</summary>

```
**Apple Inc. (CIK 0000320193) – Revenue‑related XBRL concepts in the us‑gaap taxonomy**

| Concept (XBRL tag) | Label (human‑readable description) |
|--------------------|------------------------------------|
| `ContractWithCustomerLiabilityRevenueRecognized` | Contract with Customer, Liability, Revenue Recognized |
| `DeferredRevenueCurrent` | Deferred Revenue, Current |
| `DeferredRevenueNoncurrent` | Deferred Revenue, Noncurrent |
| `IncreaseDecreaseInDeferredRevenue` | Increase (Decrease) in Deferred Revenue |
| `RevenueFromContractWithCustomerExcludingAssessedTax` | Revenue from Contract with Customer, Excluding Assessed Tax |
| `Revenues` | Revenues |
| `SalesRevenueNet` | Revenue, Net (Deprecated 2018‑01‑31) |
| `SalesRevenueServicesGross` | Sales Revenue, Services, Other (Deprecated 2018‑01‑31) |

These are the revenue‑related concepts returned by the SEC’s **us‑gaap** taxonomy for Apple. Use the appropriate tag (e.g., `Revenues`) when requesting revenue figures via the XBRL fact APIs.
```

</details>

### BQ-12 — ✅ PASS
**Question:** I want to find debt-related financial concepts for Tesla. What us-gaap concepts are available?  
**Expected tools:** sec_edgar_list_concepts  
**Tools fired:** sec_edgar_list_concepts  

<details><summary>Agent response</summary>

```
**Debt‑related us‑gaap concepts reported by Tesla, Inc. (CIK 0001318605)**  

| Concept (XBRL tag) | Human‑readable label |
|---------------------|----------------------|
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
| AvailableForSaleSecuritiesDebtMaturitiesRollingYearSixThroughTenFairValue | Debt Securities, Avai...
```

</details>

### BQ-13 — ✅ PASS
**Question:** Compare the most recent annual net income for Apple, Microsoft, and Google.  
**Expected tools:** sec_edgar_compare_companies  
**Tools fired:** sec_edgar_compare_companies  

<details><summary>Agent response</summary>

```
**Most recent annual net income (NetIncomeLoss, us‑gaap)**  

| Company | Net Income | Unit | Fiscal Year | Period End | Form | Accession Number |
|---------|-----------|------|------------|------------|------|------------------|
| Apple Inc. | $132.2 billion | USD | 2026 | 2026‑09‑26 | 10‑K | 0000320193‑26‑000026 |
| Microsoft Corp. | $133.7 billion | USD | 2026 | 2026‑06‑30 | 10‑K | 0001193125‑26‑323660 |
| Alphabet Inc. (Google) | $132.2 billion | USD | 2025 | 2025‑12‑31 | 10‑K | 0001652044‑26‑000018 |

**Warnings / comparability notes**  
- Fiscal year‑end dates differ across the three companies (Apple ends Sept 26, Microsoft ends June 30, Alphabet ends Dec 31). Because the reporting periods are not aligned, direct comparison should be made with caution.  

All values are taken from the most recent full‑year filing (10‑K) for each company, using the XBRL concept **NetIncomeLoss**.
```

</details>

### BQ-14 — ✅ PASS
**Question:** Which company has more total assets — JPMorgan Chase (JPM) or Bank of America (BAC)? Use the most recent annual figures.  
**Expected tools:** sec_edgar_compare_companies  
**Tools fired:** sec_edgar_compare_companies  

<details><summary>Agent response</summary>

```
**Total assets (most recent annual figures, FY 2025)**  

| Company | Total Assets | Unit | Fiscal Year | Period End | Form | Accession Number |
|---------|--------------|------|-------------|------------|------|------------------|
| JPMORGAN CHASE & CO | $4.425 trillion | USD | 2025 | 2025‑12‑31 | 10‑K | 0001628280-26-008131 |
| BANK OF AMERICA CORP | $3.412 trillion | USD | 2025 | 2025‑12‑31 | 10‑K | 0000070858-26-000157 |

**Answer:** JPMorgan Chase (JPM) has more total assets than Bank of America (BAC) based on the latest FY 2025 10‑K filings.
```

</details>

### BQ-15 — ✅ PASS
**Question:** Which SEC filing reported Apple's most recent annual revenue? Give me the accession number and a link to the filing.  
**Expected tools:** sec_edgar_get_company_fact  
**Tools fired:** sec_edgar_resolve_company, sec_edgar_get_company_fact, sec_edgar_get_filing_metadata  

<details><summary>Agent response</summary>

```
Apple Inc. reported its most recent full‑year revenue of **$478.8 billion** for the fiscal year ended **September 26 2026**.  

- **Accession number:** 0000320193‑26‑000026  
- **Filing type:** 10‑K (annual report)  
- **Filing date:** November 3 2026  
- **EDGAR viewer URL:** https://www.sec.gov/Archives/edgar/data/320193/000032019326000026/aapl-20260926.htm  

*Concept used:* **RevenueFromContractWithCustomerExcludingAssessedTax** (the SEC’s “Revenues” concept for Apple).
```

</details>

### BQ-16 — ✅ PASS
**Question:** What form type and filing date corresponds to Microsoft's most recent annual net income figure?  
**Expected tools:** sec_edgar_get_company_fact  
**Tools fired:** sec_edgar_resolve_company, sec_edgar_get_company_fact, sec_edgar_get_filing_metadata  

<details><summary>Agent response</summary>

```
**Most recent annual Net Income (NetIncomeLoss) for Microsoft Corp.**

- **Value:** $133.749 billion (USD)  
- **Fiscal Year:** 2026 (ended 2026‑06‑30)  
- **Form Type:** 10‑K  
- **Filing Date:** 2026‑07‑29  
- **Accession Number:** 0001193125‑26‑323660  
- **EDGAR Viewer URL:** https://www.sec.gov/Archives/edgar/data/789019/000119312526323660/msft-20260630.htm  

*The Net Income figure comes from the “Net Income (Loss) Attributable to Parent” XBRL concept (us‑gaap:NetIncomeLoss) reported in Microsoft’s FY 2026 Form 10‑K.*
```

</details>

### BQ-17 — ✅ PASS
**Question:** I don't know the ticker — find companies with 'Pfizer' in the name, then show me the last 4 annual revenue figures for the main one.  
**Expected tools:** sec_edgar_search_companies, sec_edgar_get_company_fact  
**Tools fired:** sec_edgar_search_companies, sec_edgar_get_company_fact  

<details><summary>Agent response</summary>

```
**Company found**  
- **Name:** PFIZER INC  
- **Ticker:** PFE  
- **CIK:** 0000078003  

**Revenue (US‑GAAP – “Revenues”) – last 4 fiscal years**

| Fiscal Year | Period End | Revenue (USD) | Form | Accession Number |
|-------------|------------|---------------|------|------------------|
| 2022 | 2022‑12‑31 | $101.2 billion* | 10‑K | 0000078003‑25‑000054 |
| 2023 | 2023‑12‑31 | $59.6 billion* | 10‑K | 0000078003‑26‑000026 |
| 2024 | 2024‑12‑31 | $63.6 billion | 10‑K | 0000078003‑26‑000026 |
| 2025 | 2025‑12‑31 | $62.6 billion | 10‑K | 0000078003‑26‑000026 |

\* **Recast values:** The 2022 and 2023 figures were recast in later filings; the original amounts were $100.33 billion and $58.50 billion respectively.

**XBRL concept used:** *Revenues* (us‑gaap taxonomy).  

All values are presented in US dollars (USD).
```

</details>

### BQ-18 — ✅ PASS
**Question:** Search for companies with 'Exxon' in their name, resolve the main one, then list its 5 most recent 10-K filings.  
**Expected tools:** sec_edgar_search_companies, sec_edgar_get_recent_filings  
**Tools fired:** sec_edgar_search_companies, sec_edgar_resolve_company, sec_edgar_get_recent_filings  

<details><summary>Agent response</summary>

```
**Resolved company (annual filer)**  
- **Name:** EXXON MOBIL CORP  
- **Ticker:** XOM  
- **CIK:** 0000034088  
- **SIC:** 2911 – Petroleum Refining  
- **State of incorporation:** TX  

**5 most‑recent Form 10‑K filings**

| Filing Date | Reported Fiscal Year End | Accession Number | Primary Document |
|-------------|--------------------------|------------------|------------------|
| 2026‑02‑18 | 2025‑12‑31 | 0000034088‑26‑000045 | xom-20251231.htm |
| 2025‑02‑19 | 2024‑12‑31 | 0000034088‑25‑000010 | xom-20241231.htm |
| 2024‑02‑28 | 2023‑12‑31 | 0000034088‑24‑000018 | xom-20231231.htm |
| 2023‑02‑22 | 2022‑12‑31 | 0000034088‑23‑000020 | xom-20221231.htm |
| 2022‑02‑23 | 2021‑12‑31 | 0000034088‑22‑000011 | xom-20211231.htm |

These filings are the latest 10‑K reports filed by Exxon Mobil Corp (CIK 0000034088).
```

</details>

### BQ-19 — ✅ PASS
**Question:** What SEC filings has the company with ticker ZZZZNOTREAL submitted recently?  
**Expected tools:**   
**Tools fired:** sec_edgar_search_companies  

<details><summary>Agent response</summary>

```
The search for **ZZZZNOTREAL** returned no matching companies in the SEC’s database. Consequently, there are no recent SEC filings for this ticker because it does not correspond to a registered filer. If you have an alternative ticker or the company’s CIK, please provide it and I can retrieve the filing information for you.
```

</details>

### BQ-20 — ✅ PASS
**Question:** Show me Apple's quarterly EarningsPerShareBasicAndDiluted for the last 4 quarters.  
**Expected tools:** sec_edgar_get_quarterly_facts  
**Tools fired:** sec_edgar_resolve_company, sec_edgar_get_quarterly_facts  

<details><summary>Agent response</summary>

```
**Apple Inc. (CIK 0000320193) – Quarterly Earnings‑per‑Share (EPS)**  

| Fiscal Quarter | Fiscal Year | Period End | EPS Basic (USD /shares) | EPS Diluted (USD /shares) | Form | Accession Number |
|----------------|------------|------------|------------------------|---------------------------|------|------------------|
| Q3 FY2026 | 2026 | 2026‑06‑27 | 2.03 | 2.02 | 10‑Q | 0000320193‑26‑000020 |
| Q2 FY2026 | 2026 | 2026‑03‑28 | 2.02 | 2.01 | 10‑Q | 0000320193‑26‑000013 |
| Q1 FY2026 | 2026 | 2025‑12‑27 | 2.85 | 2.84 | 10‑Q | 0000320193‑26‑000006 |
| Q3 FY2025 | 2025 | 2025‑06‑28 | 1.57 | 1.57 | 10‑Q | 0000320193‑26‑000020 |

**Concepts used**  
- *EarningsPerShareBasic* – “Earnings Per Share, Basic” (unit: USD/shares)  
- *EarningsPerShareDiluted* – “Earnings Per Share, Diluted” (unit: USD/shares)

**Notes**  
- The quarterly data come from Apple’s 10‑Q filings (accession numbers shown).  
- Q4 observations are not derived for per‑share metrics because the unit “USD/shares” is non‑additive; therefore only Q1‑Q3 are available.  

If you need the filing details (e.g., the full 10‑Q report), let me know and I can retrieve the filing metadata for any accession number listed above.
```

</details>

### BQ-21 — ✅ PASS
**Question:** What is Apple's current stock price?  
**Expected tools:**   
**Tools fired:** *(none)*  

<details><summary>Agent response</summary>

```
I’m unable to provide current stock prices. I can help retrieve Apple’s historical SEC filings or financial data reported to the SEC if that would be useful.
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
I’m sorry, but I can’t provide forecasts or speculative information about future revenue. I can, however, retrieve Microsoft’s historically reported revenue figures from its SEC filings if that would be helpful.
```

</details>

---

## Tool Utilisation

| Tool | Expected in N Qs | Qs Fired | Fire Rate | Total Calls |
|---|---|---|---|---|
| `sec_edgar_compare_companies` | 2 | 2 | 100% | 2 |
| `sec_edgar_get_company_fact` | 5 | 5 | 100% | 5 |
| `sec_edgar_get_quarterly_facts` | 3 | 3 | 100% | 4 |
| `sec_edgar_get_recent_filings` | 3 | 3 | 100% | 3 |
| `sec_edgar_list_concepts` | 2 | 2 | 100% | 2 |
| `sec_edgar_resolve_company` | 2 | 10 | 500% | 10 |
| `sec_edgar_search_companies` | 4 | 5 | 125% | 5 |

---

## Results by Category

| Category | Questions | Pass | Partial | Fail |
|---|---|---|---|---|
| annual_facts | 2 | 2 | 0 | 0 |
| company_resolution | 2 | 2 | 0 | 0 |
| company_search | 2 | 2 | 0 | 0 |
| concept_discovery | 2 | 2 | 0 | 0 |
| cross_company_comparison | 2 | 2 | 0 | 0 |
| edge_cases | 2 | 2 | 0 | 0 |
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