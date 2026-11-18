# SEC EDGAR Agent — Evaluation Report

**Agent:** `sec_edgar_agent`  
**Environment:** `gsa-hackathon` (IBM Cloud Toronto)  
**Run date:** 2026-11-18 02:19  
**Duration:** 86s for 7 questions  

---

## Summary

| Metric | Value |
|---|---|
| Total questions | 7 |
| ✅ Pass | 7 (100%) |
| ⚠️ Partial | 0 (0%) |
| ❌ Fail | 0 (0%) |

---

## Results by Question

| ID | Diff | Category | Score | Expected Tools | Tools Fired | Notes |
|---|---|---|---|---|---|---|
| BQ-07 | 🟡 medium | annual_facts | ✅ pass | `get_company_fact` | `resolve_company`, `get_company_fact` | All expected tools fired. |
| BQ-09 | 🟡 medium | quarterly_facts | ✅ pass | `get_quarterly_facts` | `resolve_company`, `get_quarterly_facts` | All expected tools fired. |
| BQ-10 | 🟡 medium | quarterly_facts | ✅ pass | `get_quarterly_facts` | `resolve_company`, `get_quarterly_facts` | All expected tools fired. |
| BQ-14 | 🔴 hard | cross_company_comparison | ✅ pass | `compare_companies` | `compare_companies` | All expected tools fired. |
| BQ-17 | 🔴 hard | multi_step_discovery | ✅ pass | `search_companies`, `get_company_fact` | `search_companies`, `get_company_fact` | All expected tools fired. |
| BQ-18 | 🔴 hard | multi_step_discovery | ✅ pass | `search_companies`, `get_recent_filings` | `search_companies`, `resolve_company`, `get_recent_filings` | All expected tools fired. |
| BQ-20 | 🟡 medium | edge_cases | ✅ pass | `get_quarterly_facts` | `resolve_company`, `get_quarterly_facts` | All expected tools fired. |

---

## Agent Responses

### BQ-07 — ✅ PASS
**Question:** Show me the last 5 annual net income figures for Apple.  
**Expected tools:** sec_edgar_get_company_fact  
**Tools fired:** sec_edgar_resolve_company, sec_edgar_get_company_fact  

<details><summary>Agent response</summary>

```
**Apple Inc. – Net Income (NetIncomeLoss)**  
*XBRL concept: `NetIncomeLoss` (us‑gaap)*  

| Fiscal Year | Period End | Net Income (USD) | Form | Accession Number |
|-------------|------------|------------------|------|-------------------|
| 2022 | 2022‑09‑24 | $99.8 billion | 10‑K | 0000320193‑24‑000123 |
| 2023 | 2023‑09‑30 | $97.0 billion | 10‑K | 0000320193‑25‑000079 |
| 2024 | 2024‑09‑28 | $93.7 billion | 10‑K | 0000320193‑26‑000026 |
| 2025 | 2025‑09‑27 | $112.0 billion | 10‑K | 0000320193‑26‑000026 |
| 2026 | 2026‑09‑26 | $132.2 billion | 10‑K | 0000320193‑26‑000026 |

*All values are presented in U.S. dollars (USD). The data come from Apple’s annual Form 10‑K filings as reported in the SEC’s XBRL filings.*
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

| Fiscal Quarter | Fiscal Year | Period End | Revenue (USD) | Form | Accession Number |
|----------------|------------|------------|----------------|------|-------------------|
| Q3 | 2026 | 2026‑06‑27 | $109.4 billion | 10‑Q | 0000320193‑26‑000020 |
| Q2 | 2026 | 2026‑03‑28 | $111.2 billion | 10‑Q | 0000320193‑26‑000013 |
| Q1 | 2026 | 2025‑12‑27 | $143.8 billion | 10‑Q | 0000320193‑26‑000006 |
| Q3 | 2025 | 2025‑06‑28 | $94.0 billion | 10‑Q | 0000320193‑26‑000020 |
| Q2 | 2025 | 2025‑03‑29 | $95.4 billion | 10‑Q | 0000320193‑26‑000013 |
| Q1 | 2025 | 2024‑12‑28 | $124.3 billion | 10‑Q | 0000320193‑26‑000006 |
| Q3 | 2024 | 2024‑06‑29 | $85.8 billion | 10‑Q | 0000320193‑25‑000073 |
| Q2 | 2024 | 2024‑03‑30 | $90.8 billion | 10‑Q | 0000320193‑25‑000057 |

**Notes**

* The data come from Apple’s 10‑Q filings (quarterly reports).  
* Q4 figures are not included in the quarterly‑facts endpoint because they are reported in the annual 10‑K (or occasional 8‑K), not in a separate 10‑Q. If you need the Q4 (full‑year) revenue, let me know and I can retrieve the annual figure via the company‑fact call.
```

</details>

### BQ-10 — ✅ PASS
**Question:** What was Microsoft's net income in each of the last 6 quarters?  
**Expected tools:** sec_edgar_get_quarterly_facts  
**Tools fired:** sec_edgar_resolve_company, sec_edgar_get_quarterly_facts  

<details><summary>Agent response</summary>

```
**Microsoft Corp – Net Income (attributable to parent) for the most recent 6 quarters**  

| Fiscal Quarter | Fiscal Year | Period End | Net Income (USD) | Form | Accession Number |
|----------------|------------|------------|------------------|------|------------------|
| Q1 FY2027 | 2027 | 2026‑09‑30 | $36.63 billion | 10‑Q | 0001193125‑26‑436133 |
| Q3 FY2026 | 2026 | 2026‑03‑31 | $31.78 billion | 10‑Q | 0001193125‑26‑191507 |
| Q2 FY2026 | 2026 | 2025‑12‑31 | $38.46 billion | 10‑Q | 0001193125‑26‑027207 |
| Q1 FY2026 | 2026 | 2025‑09‑30 | $27.75 billion | 10‑Q | 0001193125‑26‑436133 |
| Q3 FY2025 | 2025 | 2025‑03‑31 | $25.82 billion | 10‑Q | 0001193125‑26‑191507 |
| Q2 FY2025 | 2025 | 2024‑12‑31 | $24.11 billion | 10‑Q | 0001193125‑26‑027207 |

**Concept used:** `NetIncomeLoss` (XBRL label “Net Income (Loss) Attributable to Parent”).  

All values are expressed in **U.S. dollars (USD)** and come from the company’s 10‑Q filings. The period end dates reflect the actual quarter‑end dates, not the filing date.
```

</details>

### BQ-14 — ✅ PASS
**Question:** Which company has more total assets — JPMorgan Chase (JPM) or Bank of America (BAC)? Use the most recent annual figures.  
**Expected tools:** sec_edgar_compare_companies  
**Tools fired:** sec_edgar_compare_companies  

<details><summary>Agent response</summary>

```
**Total assets (most recent annual figures, FY 2025)**  

| Company | Fiscal Year | Period End | Total Assets | Unit | Form | Accession Number |
|---------|------------|------------|--------------|------|------|------------------|
| JPMorgan Chase & Co. | 2025 | 2025‑12‑31 | **$4.425 trillion** | USD | 10‑K | 0001628280‑26‑008131 |
| Bank of America Corp. | 2025 | 2025‑12‑31 | **$3.412 trillion** | USD | 10‑K | 0000070858‑26‑000157 |

**Result:** JPMorgan Chase has more total assets than Bank of America.
```

</details>

### BQ-17 — ✅ PASS
**Question:** I don't know the ticker — find companies with 'Pfizer' in the name, then show me the last 4 annual revenue figures for the main one.  
**Expected tools:** sec_edgar_search_companies, sec_edgar_get_company_fact  
**Tools fired:** sec_edgar_search_companies, sec_edgar_get_company_fact  

<details><summary>Agent response</summary>

```
**Company identified:** PFIZER INC (ticker PFE, CIK 0000078003) – the primary operating company with recent 10‑K filings.

**Revenue data source:** XBRL concept **RevenueFromContractWithCustomerExcludingAssessedTax** (us‑gaap taxonomy).  

| Fiscal Year | Period End | Revenue (USD) | Form | Accession Number | Note |
|------------|------------|----------------|------|------------------|------|
| 2020 | 2020‑12‑31 | $41.65 billion | 10‑K | 0000078003-22-000027 | Recast; originally filed $41.91 billion |
| 2021 | 2021‑12‑31 | $73.64 billion | 10‑K | 0000078003-24-000039 | Recast; originally filed $81.29 billion |
| 2022 | 2022‑12‑31 | $91.79 billion | 10‑K | 0000078003-24-000039 | – |
| 2023 | 2023‑12‑31 | $50.91 billion | 10‑K | 0000078003-24-000039 | – |

**Explanation**

- The SEC filings show that Pfizer’s revenue reporting switched to the “Revenue from Contract with Customer, Excluding Assessed Tax” concept after 2018.  
- For 2020 and 2021 the values were *recast* in later filings; the original amounts are shown in the “as_originally_filed” field.  
- The most recent four fiscal‑year observations (2020‑2023) are presented above, sorted by fiscal year.  

If you need the underlying filings or want to view a different revenue concept (e.g., “Revenues”), let me know and I can retrieve that information as well.
```

</details>

### BQ-18 — ✅ PASS
**Question:** Search for companies with 'Exxon' in their name, resolve the main one, then list its 5 most recent 10-K filings.  
**Expected tools:** sec_edgar_search_companies, sec_edgar_get_recent_filings  
**Tools fired:** sec_edgar_search_companies, sec_edgar_resolve_company, sec_edgar_get_recent_filings  

<details><summary>Agent response</summary>

```
**Resolved Company (primary operating entity)**  
- **Name:** EXXON MOBIL CORP  
- **Ticker:** XOM  
- **CIK:** 0000034088  
- **SIC:** 2911 – Petroleum Refining  
- **State of Incorporation:** TX  

*Note:* The ticker “XOM” also matches a newer holding company (ExxonMobil Holdings Corp, CIK 0002115436) that currently has no 10‑K filings. The filings below are from the operating company **EXXON MOBIL CORP**, which has recent 10‑K reports.

### 5 Most Recent Form 10‑K Filings

| Filing Date | Report (Fiscal) Year End | Accession Number | Primary Document |
|-------------|---------------------------|------------------|------------------|
| 2026‑02‑18 | 2025‑12‑31 | 0000034088-26-000045 | xom-20251231.htm |
| 2025‑02‑19 | 2024‑12‑31 | 0000034088-25-000010 | xom-20241231.htm |
| 2024‑02‑28 | 2023‑12‑31 | 0000034088-24-000018 | xom-20231231.htm |
| 2023‑02‑22 | 2022‑12‑31 | 0000034088-23-000020 | xom-20221231.htm |
| 2022‑02‑23 | 2021‑12‑31 | 0000034088-22-000011 | xom-20211231.htm |

These filings are the most recent annual reports (Form 10‑K) filed by Exxon Mobil Corp. If you need the full documents, you can retrieve them via the SEC EDGAR viewer using the accession numbers listed.
```

</details>

### BQ-20 — ✅ PASS
**Question:** Show me Apple's quarterly EarningsPerShareBasicAndDiluted for the last 4 quarters.  
**Expected tools:** sec_edgar_get_quarterly_facts  
**Tools fired:** sec_edgar_resolve_company, sec_edgar_get_quarterly_facts  

<details><summary>Agent response</summary>

```
**Apple Inc. (CIK 0000320193) – Quarterly EPS (Basic & Diluted)**  

| Fiscal Quarter | Fiscal Year | Period End | EPS Basic (USD / share) | EPS Diluted (USD / share) | Form | Accession Number |
|----------------|------------|------------|------------------------|---------------------------|------|-------------------|
| Q3 FY2026 | 2026 | 2026‑06‑27 | 2.03 | 2.02 | 10‑Q | 0000320193‑26‑000020 |
| Q2 FY2026 | 2026 | 2026‑03‑28 | 2.02 | 2.01 | 10‑Q | 0000320193‑26‑000013 |
| Q1 FY2026 | 2026 | 2025‑12‑27 | 2.85 | 2.84 | 10‑Q | 0000320193‑26‑000006 |
| Q3 FY2025 | 2025 | 2025‑06‑28 | 1.57 | 1.57 | 10‑Q | 0000320193‑26‑000020 |

**Notes**

* The data come from the XBRL concepts **EarningsPerShareBasic** and **EarningsPerShareDiluted** (unit: USD / share).  
* Quarterly figures are taken from the most recent 10‑Q filings; Q4 figures are not included because they are reported in the annual 10‑K, not in a 10‑Q.  
* All values are as reported by Apple; no recasting was required.
```

</details>

---

## Tool Utilisation

| Tool | Expected in N Qs | Qs Fired | Fire Rate | Total Calls |
|---|---|---|---|---|
| `sec_edgar_compare_companies` | 1 | 1 | 100% | 1 |
| `sec_edgar_get_company_fact` | 2 | 2 | 100% | 2 |
| `sec_edgar_get_quarterly_facts` | 3 | 3 | 100% | 4 |
| `sec_edgar_get_recent_filings` | 1 | 1 | 100% | 1 |
| `sec_edgar_search_companies` | 2 | 2 | 100% | 2 |

---

## Results by Category

| Category | Questions | Pass | Partial | Fail |
|---|---|---|---|---|
| annual_facts | 1 | 1 | 0 | 0 |
| cross_company_comparison | 1 | 1 | 0 | 0 |
| edge_cases | 1 | 1 | 0 | 0 |
| multi_step_discovery | 2 | 2 | 0 | 0 |
| quarterly_facts | 2 | 2 | 0 | 0 |

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