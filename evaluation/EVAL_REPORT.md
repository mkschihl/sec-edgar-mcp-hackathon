# SEC EDGAR Agent — Evaluation Report

**Agent:** `sec_edgar_agent`  
**Environment:** `gsa-hackathon` (IBM Cloud Toronto)  
**Run date:** 2026-11-18 03:45  
**Duration:** 35s for 3 questions  

---

## Summary

| Metric | Value |
|---|---|
| Total questions | 3 |
| ✅ Pass | 2 (67%) |
| ⚠️ Partial | 1 (33%) |
| ❌ Fail | 0 (0%) |

---

## Results by Question

| ID | Diff | Category | Score | Expected Tools | Tools Fired | Notes |
|---|---|---|---|---|---|---|
| BQ-09 | 🟡 medium | quarterly_facts | ✅ pass | `get_quarterly_facts` | `get_quarterly_facts` | All expected tools fired. |
| BQ-15 | 🔴 hard | filing_attribution | ⚠️ partial | `get_company_fact`, `get_filing_metadata` | `resolve_company`, `get_company_fact` | Some tools fired. Missing: ['sec_edgar_get_filing_metadata']. |
| BQ-17 | 🔴 hard | multi_step_discovery | ✅ pass | `search_companies`, `get_company_fact` | `search_companies`, `get_company_fact` | All expected tools fired. |

---

## Agent Responses

### BQ-09 — ✅ PASS
**Question:** Show me Apple's quarterly revenue for the last 8 quarters.  
**Expected tools:** sec_edgar_get_quarterly_facts  
**Tools fired:** sec_edgar_get_quarterly_facts  

<details><summary>Agent response</summary>

```
**Apple Inc. – Quarterly Revenue (most recent 8 quarters)**  

| Fiscal Year | Quarter | Period End | Revenue (USD) | Form | Accession Number |
|------------|---------|------------|---------------|------|------------------|
| 2026 | Q3 | 2026‑06‑27 | $109.4 billion | 10‑Q | 0000320193‑26‑000020 |
| 2026 | Q2 | 2026‑03‑28 | $111.2 billion | 10‑Q | 0000320193‑26‑000013 |
| 2026 | Q1 | 2025‑12‑27 | $143.8 billion | 10‑Q | 0000320193‑26‑000006 |
| 2025 | Q3 | 2025‑06‑28 | $94.0 billion | 10‑Q | 0000320193‑26‑000020 |
| 2025 | Q2 | 2025‑03‑29 | $95.4 billion | 10‑Q | 0000320193‑26‑000013 |
| 2025 | Q1 | 2024‑12‑28 | $124.3 billion | 10‑Q | 0000320193‑26‑000006 |
| 2024 | Q3 | 2024‑06‑29 | $85.8 billion | 10‑Q | 0000320193‑25‑000073 |
| 2024 | Q2 | 2024‑03‑30 | $90.8 billion | 10‑Q | 0000320193‑25‑000057 |

**XBRL Concept Used:** `RevenueFromContractWithCustomerExcludingAssessedTax` (the SEC’s most recent quarterly revenue concept; requested “Revenues” was mapped to this tag).

*All values are in U.S. dollars (USD) as reported in the respective 10‑Q filings.*
```

</details>

### BQ-15 — ⚠️ PARTIAL
**Question:** Which SEC filing reported Apple's most recent annual revenue? Give me the accession number and a link to the filing.  
**Expected tools:** sec_edgar_get_company_fact, sec_edgar_get_filing_metadata  
**Tools fired:** sec_edgar_resolve_company, sec_edgar_get_company_fact  

<details><summary>Agent response</summary>

```
**Apple Inc. – Most recent annual revenue**

| Fiscal Year | Period End | Revenue (USD) | Form | Accession Number |
|-------------|------------|--------------|------|------------------|
| 2026 | 2026‑09‑26 | $478.8 billion | 10‑K | **0000320193‑26‑000026** |

**Link to the filing**  
The revenue figure comes from Apple’s 2026 Form 10‑K filing, which can be viewed at:

https://www.sec.gov/Archives/edgar/data/320193/0000320193-26-000026.txt

(SEC EDGAR viewer URL format: `https://www.sec.gov/Archives/edgar/data/{CIK}/{accession_number}.txt`)

**XBRL concept used**: `RevenueFromContractWithCustomerExcludingAssessedTax` (the SEC returned this concept when “Revenues” was requested, as it contains the most recent annual revenue data).
```

</details>

### BQ-17 — ✅ PASS
**Question:** I don't know the ticker — find companies with 'Pfizer' in the name, then show me the last 4 annual revenue figures for the main one.  
**Expected tools:** sec_edgar_search_companies, sec_edgar_get_company_fact  
**Tools fired:** sec_edgar_search_companies, sec_edgar_get_company_fact  

<details><summary>Agent response</summary>

```
**Pfizer Inc. (CIK 0000078003, ticker PFE)** – Annual Revenue  

| Fiscal Year | Period End | Revenue (USD) | Form | Accession Number | Note |
|-------------|------------|---------------|------|------------------|------|
| 2022 | 2022‑12‑31 | **$101.2 billion** (recast; originally $100.3 billion) | 10‑K | 0000078003‑25‑000054 | Recast in later filing |
| 2023 | 2023‑12‑31 | **$59.6 billion** (recast; originally $58.5 billion) | 10‑K | 0000078003‑26‑000026 | Recast in later filing |
| 2024 | 2024‑12‑31 | **$63.6 billion** | 10‑K | 0000078003‑26‑000026 | – |
| 2025 | 2025‑12‑31 | **$62.6 billion** | 10‑K | 0000078003‑26‑000026 | – |

*Concept used:* **Revenues** (us‑gaap). Values are shown in US dollars. Recast notes indicate the figure was adjusted in a later filing; the original amount is provided for reference.
```

</details>

---

## Tool Utilisation

| Tool | Expected in N Qs | Qs Fired | Fire Rate | Total Calls |
|---|---|---|---|---|
| `sec_edgar_get_company_fact` | 2 | 2 | 100% | 2 |
| `sec_edgar_get_filing_metadata` | 1 | 0 | 0% | 0 |
| `sec_edgar_get_quarterly_facts` | 1 | 1 | 100% | 1 |
| `sec_edgar_search_companies` | 1 | 1 | 100% | 1 |

---

## Results by Category

| Category | Questions | Pass | Partial | Fail |
|---|---|---|---|---|
| filing_attribution | 1 | 0 | 1 | 0 |
| multi_step_discovery | 1 | 1 | 0 | 0 |
| quarterly_facts | 1 | 1 | 0 | 0 |

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