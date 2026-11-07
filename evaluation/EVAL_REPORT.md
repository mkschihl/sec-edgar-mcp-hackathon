# SEC EDGAR Agent — Evaluation Report

**Agent:** `sec_edgar_agent`  
**Environment:** `gsa-hackathon` (IBM Cloud Toronto)  
**Run date:** 2026-11-07 18:33  
**Duration:** 557s for 20 questions  

---

## Summary

| Metric | Value |
|---|---|
| Total questions | 20 |
| ✅ Pass | 20 (100%) |
| ⚠️ Partial | 0 (0%) |
| ❌ Fail | 0 (0%) |

---

## Results by Question

| ID | Diff | Category | Score | Expected Tools | Tools Fired | Notes |
|---|---|---|---|---|---|---|
| BQ-01 | 🟢 easy | company_search | ✅ pass | `search_companies` | `search_companies` | All expected tools fired. |
| BQ-02 | 🟢 easy | company_search | ✅ pass | `search_companies` | `search_companies` | All expected tools fired. |
| BQ-03 | 🟢 easy | company_resolution | ✅ pass | `resolve_company` | `resolve_company` | All expected tools fired. |
| BQ-04 | 🟢 easy | company_resolution | ✅ pass | `resolve_company` | `resolve_company` | All expected tools fired. |
| BQ-05 | 🟢 easy | recent_filings | ✅ pass | `get_recent_filings` | `get_recent_filings` | All expected tools fired. |
| BQ-06 | 🟢 easy | recent_filings | ✅ pass | `get_recent_filings` | `get_recent_filings` | All expected tools fired. |
| BQ-07 | 🟡 medium | annual_facts | ✅ pass | `get_company_fact` | `get_company_fact`, `resolve_company` | All expected tools fired. |
| BQ-08 | 🟡 medium | annual_facts | ✅ pass | `get_company_fact` | `get_company_fact`, `resolve_company` | All expected tools fired. |
| BQ-09 | 🟡 medium | quarterly_facts | ✅ pass | `get_quarterly_facts` | `get_quarterly_facts` | All expected tools fired. |
| BQ-10 | 🟡 medium | quarterly_facts | ✅ pass | `get_quarterly_facts` | `resolve_company`, `get_quarterly_facts` | All expected tools fired. |
| BQ-11 | 🟡 medium | concept_discovery | ✅ pass | `list_concepts` | `list_concepts` | All expected tools fired. |
| BQ-12 | 🟡 medium | concept_discovery | ✅ pass | `list_concepts` | `get_company_fact`, `list_concepts`, `compare_companies` | All expected tools fired. |
| BQ-13 | 🔴 hard | cross_company_comparison | ✅ pass | `compare_companies` | `compare_companies` | All expected tools fired. |
| BQ-14 | 🔴 hard | cross_company_comparison | ✅ pass | `compare_companies` | `compare_companies` | All expected tools fired. |
| BQ-15 | 🔴 hard | filing_attribution | ✅ pass | `get_company_fact`, `get_filing_metadata` | `get_company_fact`, `get_filing_metadata` | All expected tools fired. |
| BQ-16 | 🔴 hard | filing_attribution | ✅ pass | `get_company_fact`, `get_filing_metadata` | `get_company_fact`, `resolve_company`, `get_filing_metadata` | All expected tools fired. |
| BQ-17 | 🔴 hard | multi_step_discovery | ✅ pass | `search_companies`, `get_company_fact` | `get_company_fact`, `search_companies` | All expected tools fired. |
| BQ-18 | 🔴 hard | multi_step_discovery | ✅ pass | `search_companies`, `get_recent_filings` | `search_companies`, `resolve_company`, `get_recent_filings` | All expected tools fired. |
| BQ-19 | 🟢 easy | edge_cases | ✅ pass | `get_recent_filings` | `get_recent_filings` | All expected tools fired. |
| BQ-20 | 🟡 medium | edge_cases | ✅ pass | `get_quarterly_facts` | `resolve_company`, `get_quarterly_facts` | All expected tools fired. |

---

## Agent Responses

### BQ-01 — ✅ PASS
**Question:** Find all companies with 'Berkshire' in their name.  
**Expected tools:** sec_edgar_search_companies  
**Tools fired:** sec_edgar_search_companies  

<details><summary>Agent response</summary>

```
Here are the companies that contain “Berkshire” in their name (limited to the first 10 matches):

| CIK        | Company Name                | Ticker |
|------------|----------------------------|--------|
| 0001067983 | BERKSHIRE HATHAWAY INC      | BRK‑B |
| 0001067983 | BERKSHIRE HATHAWAY INC      | BRK‑A |

Both tickers refer to the two classes of Berkshire Hathaway’s common stock. Let me know which one (or both) you’d like to explore further!
```

</details>

### BQ-02 — ✅ PASS
**Question:** I'm looking for companies related to 'General Electric'. What comes up?  
**Expected tools:** sec_edgar_search_companies  
**Tools fired:** sec_edgar_search_companies  

<details><summary>Agent response</summary>

```
Here are the top matches for a search on “General Electric”:

| Ticker | CIK | Company |
|--------|-----|---------|
| **GE** | 0000040545 | General Electric Co |
| **POR** | 0000784977 | Portland General Electric Co (OR) |

Let me know which company you’d like to explore further (or if you’d like details on a different match).
```

</details>

### BQ-03 — ✅ PASS
**Question:** What is the SEC CIK number and industry classification for Microsoft?  
**Expected tools:** sec_edgar_resolve_company  
**Tools fired:** sec_edgar_resolve_company  

<details><summary>Agent response</summary>

```
**Microsoft Corporation (ticker MSFT)**  

- **SEC CIK:** 0000789019  
- **Industry classification (SIC):** **7372 – Services‑Prepackaged Software** (Software publishing and services)
```

</details>

### BQ-04 — ✅ PASS
**Question:** Tell me about Alphabet Inc. — what state is it incorporated in and what SIC code does it use?  
**Expected tools:** sec_edgar_resolve_company  
**Tools fired:** sec_edgar_resolve_company  

<details><summary>Agent response</summary>

```
Alphabet Inc. is incorporated in the state of **Delaware (DE)** and reports the **SIC code 7370** (Services‑Computer Programming, Data Processing, Etc.).
```

</details>

### BQ-05 — ✅ PASS
**Question:** List the five most recent 10-K filings for Microsoft.  
**Expected tools:** sec_edgar_get_recent_filings  
**Tools fired:** sec_edgar_get_recent_filings  

<details><summary>Agent response</summary>

```
**Microsoft Corp – Five most recent Form 10‑K filings**

| # | Filing Date | Report (Period End) | Accession Number | Form | Primary Document |
|---|-------------|---------------------|------------------|------|------------------|
| 1 | 2026‑07‑29 | 2026‑06‑30 | 0001193125‑26‑323660 | 10‑K | msft‑20260630.htm |
| 2 | 2025‑07‑30 | 2025‑06‑30 | 0000950170‑25‑100235 | 10‑K | msft‑20250630.htm |
| 3 | 2024‑07‑30 | 2024‑06‑30 | 0000950170‑24‑087843 | 10‑K | msft‑20240630.htm |
| 4 | 2023‑07‑27 | 2023‑06‑30 | 0000950170‑23‑035122 | 10‑K | msft‑20230630.htm |
| 5 | 2022‑07‑28 | 2022‑06‑30 | 0001564590‑22‑026876 | 10‑K | msft‑10k_20220630.htm |

These are the five latest annual reports (Form 10‑K) filed by Microsoft Corp, identified by their accession numbers and primary document filenames. If you need more details or want to view a specific filing, let me know!
```

</details>

### BQ-06 — ✅ PASS
**Question:** Show me the 10 most recent 10-Q filings for Johnson & Johnson (ticker: JNJ).  
**Expected tools:** sec_edgar_get_recent_filings  
**Tools fired:** sec_edgar_get_recent_filings  

<details><summary>Agent response</summary>

```
**Johnson & Johnson (ticker JNJ) – 10 most recent Form 10‑Q filings**

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

These filings are the most recent 10‑Q reports filed by Johnson & Johnson, listed from newest to oldest. If you need the full filing URLs, details about a specific filing, or additional filing types, just let me know!
```

</details>

### BQ-07 — ✅ PASS
**Question:** Show me the last 5 annual net income figures for Apple.  
**Expected tools:** sec_edgar_get_company_fact  
**Tools fired:** sec_edgar_get_company_fact, sec_edgar_resolve_company  

<details><summary>Agent response</summary>

```
**Apple Inc. – Net Income (annual, FY) – last 5 years**

| Fiscal Year (FY) | Net Income (USD) | Form | Accession Number |
|------------------|------------------|------|------------------|
| 2022 | $99.8 billion | 10‑K | 0000320193‑22‑000108 |
| 2023 | $99.8 billion | 10‑K | 0000320193‑23‑000106 |
| 2024 | $96.7 billion | 10‑K | 0000320193‑24‑000123 |
| 2025 | $112.0 billion | 10‑K | 0000320193‑25‑000079 |
| 2026 | $132.2 billion | 10‑K | 0000320193‑26‑000026 |

*All values are taken from the “NetIncomeLoss” XBRL fact (us‑gaap) and represent the net income attributable to Apple’s parent for the full fiscal year. The figures are shown in US dollars.*
```

</details>

### BQ-08 — ✅ PASS
**Question:** What were Amazon's total assets for the last 4 fiscal years?  
**Expected tools:** sec_edgar_get_company_fact  
**Tools fired:** sec_edgar_get_company_fact, sec_edgar_resolve_company  

<details><summary>Agent response</summary>

```
**Amazon.com, Inc. – Total Assets (last 4 fiscal years)**  

| Fiscal Year (ended) | Total Assets | Form | Accession Number |
|---------------------|--------------|------|------------------|
| 2025 (12‑31‑2025) | **$818.0 billion** | 10‑K | 0001018724‑26‑000004 |
| 2024 (12‑31‑2024) | **$624.9 billion** | 10‑K | 0001018724‑25‑000004 |
| 2023 (12‑31‑2023) | **$527.9 billion** | 10‑K | 0001018724‑24‑000008 |
| 2022 (12‑31‑2022) | **$462.7 billion** | 10‑K | 0001018724‑23‑000004 |

*All amounts are reported in U.S. dollars (USD) as shown in the company’s balance‑sheet filings (Form 10‑K).*
```

</details>

### BQ-09 — ✅ PASS
**Question:** Show me Apple's quarterly revenue for the last 8 quarters.  
**Expected tools:** sec_edgar_get_quarterly_facts  
**Tools fired:** sec_edgar_get_quarterly_facts  

<details><summary>Agent response</summary>

```
**Apple Inc. – Quarterly Revenue (last 8 quarters)**  
*(concept: RevenueFromContractWithCustomerExcludingAssessedTax, unit USD)*  

| Period (Fiscal) | Quarter | Revenue | Form | Accession No. | Filing Date* |
|-----------------|---------|----------|------|---------------|--------------|
| FY 2026 | Q3 (ended Jun 27 2026) | $364.4 billion | 10‑Q | 0000320193‑26‑000020 | 2026‑08‑03 |
| FY 2026 | Q2 (ended Mar 28 2026) | $254.9 billion | 10‑Q | 0000320193‑26‑000013 | 2026‑05‑05 |
| FY 2026 | Q1 (ended Dec 27 2025) | $143.8 billion | 10‑Q | 0000320193‑26‑000006 | 2026‑02‑05 |
| FY 2025 | Q3 (ended Jun 28 2025) | $313.7 billion | 10‑Q | 0000320193‑25‑000073 | 2025‑08‑04 |
| FY 2025 | Q3 (ended Jun 28 2025) – alternate series | $94.0 billion | 10‑Q | 0000320193‑25‑000073 | 2025‑08‑04 |
| FY 2025 | Q2 (ended Mar 29 2025) | *data not returned in the last 8 observations* | – | – | – |
| FY 2025 | Q1 (ended Dec 28 2024) | *data not returned in the last 8 observations* | – | – | – |
| FY 2024 | Q4 (ended Sep 28 2024) | *data not returned in the last 8 observations* | – | – | – |

\* Filing dates are taken from the filing’s metadata (10‑Q) associated with each accession number.

**Notes**

* The SEC XBRL data provides two values for Q3 FY2025 (one large, one much smaller). Both are shown; the larger figure ($313.7 B) matches Apple’s reported quarterly revenue for that period.  
* Quarterly observations are limited to what the SEC’s company‑facts endpoint currently returns; the most recent eight distinct quarters are displayed.  
* If you need the missing quarters (Q2 FY2025, Q1 FY2025, Q4 FY2024, etc.) or prefer the annual‑only “Revenues” concept, let me know and I can retrieve the annual series or explore other concepts.
```

</details>

### BQ-10 — ✅ PASS
**Question:** What was Microsoft's net income in each of the last 6 quarters?  
**Expected tools:** sec_edgar_get_quarterly_facts  
**Tools fired:** sec_edgar_resolve_company, sec_edgar_get_quarterly_facts  

<details><summary>Agent response</summary>

```
**Microsoft Corp – Net Income (attributable to parent) for the most recent quarters**

| Fiscal Quarter (Period) | Fiscal Year | Net Income | Form | Accession # |
|--------------------------|------------|------------|------|-------------|
| Q1 FY 2027 | 2027 | **$36.6 billion** | 10‑Q | 0001193125‑26‑436133 |
| Q3 FY 2026 | 2026 | **$31.8 billion** | 10‑Q | 0001193125‑26‑191507 |
| Q2 FY 2026 | 2026 | **$38.5 billion** | 10‑Q | 0001193125‑26‑027207 |
| Q1 FY 2026 | 2026 | **$27.7 billion** | 10‑Q | 0001193125‑25‑256321 |
| Q3 FY 2025* | 2025 | **$97.98 billion** (reported in the same filing as Q3 FY 2026) | 10‑Q | 0001193125‑26‑191507 |
| Q2 FY 2025* | 2025 | **$66.21 billion** (reported in the same filing as Q2 FY 2026) | 10‑Q | 0001193125‑26‑027207 |

\* The SEC’s XBRL data sometimes includes both the current‑year and prior‑year figures within the same filing. Those prior‑year values are shown above for completeness, but the most recent six *distinct* quarters are Q1 FY 2027, Q3 FY 2026, Q2 FY 2026, Q1 FY 2026, and the prior‑year counterparts for Q3 FY 2025 and Q2 FY 2025.

All amounts are presented in **U.S. dollars (USD)** and are taken directly from the company’s 10‑Q filings via the SEC’s XBRL “NetIncomeLoss” fact.
```

</details>

### BQ-11 — ✅ PASS
**Question:** What revenue-related XBRL concepts does Apple report in us-gaap?  
**Expected tools:** sec_edgar_list_concepts  
**Tools fired:** sec_edgar_list_concepts  

<details><summary>Agent response</summary>

```
Apple Inc. (CIK 0000320193) reports the following revenue‑related XBRL concepts in the **us‑gaap** taxonomy:

| XBRL Concept | Human‑Readable Label |
|--------------|----------------------|
| **RevenueFromContractWithCustomerExcludingAssessedTax** | Revenue from Contract with Customer, Excluding Assessed Tax |
| **Revenues** | Revenues |
| **SalesRevenueNet** | Revenue, Net (Deprecated 2018‑01‑31) |
| **SalesRevenueServicesGross** | Sales Revenue, Services, Other (Deprecated 2018‑01‑31) |
| **ContractWithCustomerLiabilityRevenueRecognized** | Contract with Customer, Liability, Revenue Recognized |
| **DeferredRevenueCurrent** | Deferred Revenue, Current |
| **DeferredRevenueNoncurrent** | Deferred Revenue, Noncurrent |
| **IncreaseDecreaseInDeferredRevenue** | Increase (Decrease) in Deferred Revenue |

These are the concepts that match a “revenue” search for Apple in the us‑gaap taxonomy. If you need data for any of these concepts (e.g., actual revenue amounts) just let me know which one(s) and whether you want annual or quarterly figures.
```

</details>

### BQ-12 — ✅ PASS
**Question:** I want to find debt-related financial concepts for Tesla. What us-gaap concepts are available?  
**Expected tools:** sec_edgar_list_concepts  
**Tools fired:** sec_edgar_get_company_fact, sec_edgar_list_concepts, sec_edgar_compare_companies  

<details><summary>Agent response</summary>

```
Here are the **debt‑related us‑gaap concepts** that Tesla, Inc. reports in its XBRL filings (the list is limited to the first 20 matches for brevity; Tesla has 72 matches in total).

| Concept (XBRL tag) | Human‑readable label |
|--------------------|----------------------|
| **AdjustmentsToAdditionalPaidInCapitalEquityComponentOfConvertibleDebt** | Adjustments to Additional Paid in Capital, Equity Component of Convertible Debt |
| **AmortizationOfDebtDiscountPremium** | Amortization of Debt Discount (Premium) |
| **AmortizationOfFinancingCosts** | Amortization of Debt Issuance Costs |
| **AmortizationOfFinancingCostsAndDiscounts** | Amortization of Debt Issuance Costs and Discounts |
| **AvailableForSaleDebtSecuritiesAccumulatedGrossUnrealizedGainBeforeTax** | Debt Securities, Available‑for‑sale, Accumulated Gross Unrealized Gain, before Tax |
| **AvailableForSaleDebtSecuritiesAccumulatedGrossUnrealizedLossBeforeTax** | Debt Securities, Available‑for‑sale, Accumulated Gross Unrealized Loss, before Tax |
| **AvailableForSaleDebtSecuritiesAmortizedCostBasis** | Debt Securities, Available‑for‑sale, Amortized Cost |
| **AvailableForSaleDebtSecuritiesGrossUnrealizedGain** | Debt Securities, Available‑for‑sale, Unrealized Gain |
| **AvailableForSaleDebtSecuritiesGrossUnrealizedLoss** | Debt Securities, Available‑for‑sale, Unrealized Loss |
| **AvailableForSaleSecuritiesDebtMaturitiesNextRollingTwelveMonthsAmortizedCostBasis** | Debt Securities, Available‑for‑sale, Maturity, Rolling within One Year, Amortized Cost |
| **AvailableForSaleSecuritiesDebtMaturitiesNextRollingTwelveMonthsFairValue** | Debt Securities, Available‑for‑sale, Maturity, Rolling within One Year, Fair Value |
| **AvailableForSaleSecuritiesDebtMaturitiesRollingAfterYearTenAmortizedCostBasis** | Debt Securities, Available‑for‑sale, Maturity, Rolling after 10 Years, Amortized Cost |
| **AvailableForSaleSecuritiesDebtMaturitiesRollingYearSixThroughTenAmortizedCostBasis** | Debt Securities, Available‑for‑sa...
```

</details>

### BQ-13 — ✅ PASS
**Question:** Compare the most recent annual net income for Apple, Microsoft, and Google.  
**Expected tools:** sec_edgar_compare_companies  
**Tools fired:** sec_edgar_compare_companies  

<details><summary>Agent response</summary>

```
**Most‑recent annual net income (USD)**  

| Company | Net Income | Fiscal‑Year End | Form | Accession # |
|---------|------------|----------------|------|-------------|
| Apple Inc. (AAPL) | **$132.2 billion** | 2026‑09‑26 | 10‑K | 0000320193‑26‑000026 |
| Microsoft Corp. (MSFT) | **$133.7 billion** | 2026‑06‑30 | 10‑K | 0001193125‑26‑323660 |
| Alphabet Inc. (GOOGL) | **$132.2 billion** | 2025‑12‑31 | 10‑K | 0001652044‑26‑000018 |

**Warnings about comparability**

- The fiscal year‑ends differ across the three companies (Apple ends Sept 26, Microsoft ends June 30, Alphabet ends Dec 31). Because the reporting periods are not aligned, direct year‑over‑year comparison may be misleading.  
- All values are reported in U.S. dollars (USD) and come from each company’s most recent Form 10‑K filing.

If you need the filing details (e.g., filing date, report date, or a direct EDGAR link), let me know and I can retrieve the filing metadata for any accession number.
```

</details>

### BQ-14 — ✅ PASS
**Question:** Which company has more total assets — JPMorgan Chase (JPM) or Bank of America (BAC)? Use the most recent annual figures.  
**Expected tools:** sec_edgar_compare_companies  
**Tools fired:** sec_edgar_compare_companies  

<details><summary>Agent response</summary>

```
**Total assets (most recent full‑year figures)**  

| Company | Total Assets | Fiscal Year End | Form | Accession Number |
|---------|--------------|----------------|------|------------------|
| JPMorgan Chase & Co. (JPM) | **$4.42 trillion** | 2025‑12‑31 | 10‑K | 0001628280‑26‑008131 |
| Bank of America Corp. (BAC) | **$3.41 trillion** | 2025‑12‑31 | 10‑K | 0000070858‑26‑000157 |

**Conclusion:** JPMorgan Chase (JPM) reports higher total assets than Bank of America (BAC) in the most recent annual filing.
```

</details>

### BQ-15 — ✅ PASS
**Question:** Which SEC filing reported Apple's most recent annual revenue? Give me the accession number and a link to the filing.  
**Expected tools:** sec_edgar_get_company_fact, sec_edgar_get_filing_metadata  
**Tools fired:** sec_edgar_get_company_fact, sec_edgar_get_filing_metadata  

<details><summary>Agent response</summary>

```
Apple Inc.’s most recent annual revenue figure (FY 2026) appears in its 2026 Form 10‑K filing.

**Accession number:** `0000320193-26-000026`  
**Filing link:** [SEC EDGAR viewer – 10‑K (2026‑09‑26)](https://www.sec.gov/Archives/edgar/data/320193/000032019326000026/aapl-20260926.htm)

*Form type:* 10‑K  
*Filing date:* November 3 2026  
*Report (period end) date:* September 26 2026  

This filing contains the “Revenue from Contract with Customer, Excluding Assessed Tax” fact of **$478.8 billion** for FY 2026.
```

</details>

### BQ-16 — ✅ PASS
**Question:** What form type and filing date corresponds to Microsoft's most recent annual net income figure?  
**Expected tools:** sec_edgar_get_company_fact, sec_edgar_get_filing_metadata  
**Tools fired:** sec_edgar_get_company_fact, sec_edgar_resolve_company, sec_edgar_get_filing_metadata  

<details><summary>Agent response</summary>

```
Microsoft’s most recent **annual** Net Income figure comes from its FY 2026 10‑K filing:

| Concept | Form | Filing Date | Reporting Period (Period End) |
|---------|------|-------------|--------------------------------|
| Net Income (NetIncomeLoss) | **10‑K** | **July 29 2026** | **June 30 2026** (FY 2026) |

The filing’s accession number is **0001193125‑26‑323660** and can be viewed here: https://www.sec.gov/Archives/edgar/data/789019/000119312526323660/msft-20260630.htm.
```

</details>

### BQ-17 — ✅ PASS
**Question:** I don't know the ticker — find companies with 'Pfizer' in the name, then show me the last 4 annual revenue figures for the main one.  
**Expected tools:** sec_edgar_search_companies, sec_edgar_get_company_fact  
**Tools fired:** sec_edgar_get_company_fact, sec_edgar_search_companies  

<details><summary>Agent response</summary>

```
**Pfizer Inc. (ticker PFE) – Recent Annual Revenue**

| Fiscal Year (ended) | Revenue (USD) | Form | Accession # |
|---------------------|---------------|------|--------------|
| 2025‑12‑31 | $62.6 billion | 10‑K | 0000078003‑26‑000026 |
| 2024‑12‑31 | $63.6 billion | 10‑K | 0000078003‑25‑000054 |
| 2023‑12‑31 | $58.5 billion | 10‑K | 0000078003‑24‑000039 |
| 2022‑12‑31 | $100.3 billion | 10‑K | 0000078003‑23‑000024 |

*Figures are taken from the “Revenues” XBRL concept (us‑gaap) reported in Pfizer’s annual 10‑K filings. All values are expressed in U.S. dollars.*
```

</details>

### BQ-18 — ✅ PASS
**Question:** Search for companies with 'Exxon' in their name, resolve the main one, then list its 5 most recent 10-K filings.  
**Expected tools:** sec_edgar_search_companies, sec_edgar_get_recent_filings  
**Tools fired:** sec_edgar_search_companies, sec_edgar_resolve_company, sec_edgar_get_recent_filings  

<details><summary>Agent response</summary>

```
**Search results for “Exxon”**

| Ticker | CIK | Company |
|--------|-----|---------|
| **XOM** | 0002115436 | ExxonMobil Holdings Corp |

**Resolved company:** ExxonMobil Holdings Corp (ticker **XOM**, CIK 0002115436).

**Recent 10‑K filings**

I queried the SEC’s recent‑filings endpoint for 10‑K reports for XOM and retrieved the latest 100 filings. None of those filings are 10‑K forms—the most recent 10‑K for ExxonMobil was filed before the window covered by the API’s “recent” endpoint.

**What this means**

- The SEC’s “recent filings” feed (up to the most recent 100 submissions) does not include a 10‑K for ExxonMobil at this time.
- To obtain the latest 10‑K you would need to query the full filing history (e.g., via the SEC’s Company Facts or Submissions API) or specify a date range that goes back further than the most‑recent 100 filings.

Let me know if you’d like me to retrieve the full filing history for XOM to locate its most recent 10‑K, or if there’s anything else you’d like to explore.
```

</details>

### BQ-19 — ✅ PASS
**Question:** What SEC filings has the company with ticker ZZZZNOTREAL submitted recently?  
**Expected tools:** sec_edgar_get_recent_filings  
**Tools fired:** sec_edgar_get_recent_filings  

<details><summary>Agent response</summary>

```
I’m sorry—I couldn’t locate a company with the ticker **ZZZZNOTREAL** in the SEC’s database. If you’re unsure of the exact ticker, please provide the company’s name (or a partial name), and I can search for the correct ticker or CIK before retrieving its recent filings.
```

</details>

### BQ-20 — ✅ PASS
**Question:** Show me Apple's quarterly EarningsPerShareBasicAndDiluted for the last 4 quarters.  
**Expected tools:** sec_edgar_get_quarterly_facts  
**Tools fired:** sec_edgar_resolve_company, sec_edgar_get_quarterly_facts  

<details><summary>Agent response</summary>

```
**Apple Inc. (ticker AAPL) – Quarterly Earnings‑per‑Share (basic & diluted)**  

| Fiscal Quarter | Period End | Basic EPS (USD per share) | Diluted EPS (USD per share) | Form (source) | Accession No. |
|----------------|------------|---------------------------|-----------------------------|---------------|---------------|
| Q3 FY 2026 | 27 Jun 2026 | **$6.91** | **$6.88** | 10‑Q | 0000320193‑26‑000020 |
| Q2 FY 2026 | 28 Mar 2026 | **$4.87** | **$4.85** | 10‑Q | 0000320193‑26‑000013 |
| Q1 FY 2026 | – (not available in the most recent 4‑quarter pull) | – | – | – | – |
| Q4 FY 2025 | – (not available in the most recent 4‑quarter pull) | – | – | – | – |

**Notes**

* The SEC’s quarterly XBRL data returned only two quarters (Q3 FY 2026 and Q2 FY 2026) within the most‑recent‑4‑quarter request. Earlier quarters are not yet available via the `sec_edgar_get_quarterly_facts` endpoint (or are older than the limit you asked for).  
* Values are expressed in **U.S. dollars per share** (the unit reported is `USD/shares`).  
* Each observation’s `accn` (accession number) links to the exact filing; you can view the filing with the SEC EDGAR viewer by using that accession number.  

If you need the missing quarters (Q1 FY 2026, Q4 FY 2025) or additional detail, let me know and I can retrieve the older filings or expand the observation limit.
```

</details>

---

## Tool Utilisation

| Tool | Expected in N Qs | Times Fired | Fire Rate |
|---|---|---|---|
| `sec_edgar_compare_companies` | 2 | 3 | 150% |
| `sec_edgar_get_company_fact` | 5 | 6 | 120% |
| `sec_edgar_get_filing_metadata` | 2 | 2 | 100% |
| `sec_edgar_get_quarterly_facts` | 3 | 3 | 100% |
| `sec_edgar_get_recent_filings` | 4 | 4 | 100% |
| `sec_edgar_list_concepts` | 2 | 2 | 100% |
| `sec_edgar_resolve_company` | 2 | 8 | 400% |
| `sec_edgar_search_companies` | 4 | 4 | 100% |

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