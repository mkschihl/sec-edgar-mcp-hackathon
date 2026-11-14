# SEC EDGAR Agent — Demo Walkthrough

This is a scripted, 8-question demo that showcases all eight tools of the
`sec_edgar_agent` in a logical progression. Each step builds on the previous
one — start with a name search, narrow to a company, explore its filings and
financials, then finish with cross-company comparison and source attribution.

The agent is live at: **IBM watsonx Orchestrate → Chat → sec_edgar_agent**

---

## Demo Flow Overview

| Step | Prompt | Tool Exercised |
|------|--------|----------------|
| 1 | Search by name | `sec_edgar_search_companies` |
| 2 | Resolve by ticker | `sec_edgar_resolve_company` |
| 3 | List recent filings | `sec_edgar_get_recent_filings` |
| 4 | Annual net income history | `sec_edgar_get_company_fact` |
| 5 | Quarterly revenue trend | `sec_edgar_get_quarterly_facts` |
| 6 | Discover available concepts | `sec_edgar_list_concepts` |
| 7 | Cross-company comparison with warnings | `sec_edgar_compare_companies` |
| 8 | Source filing attribution with link | `sec_edgar_get_filing_metadata` |

Estimated run time: **8–10 minutes** at a comfortable pace.

---

## Step 1 — Search by Name (`sec_edgar_search_companies`)

**What it shows:** The agent can find companies by partial name without knowing
the ticker, handling disambiguation (e.g. two share classes, holding vs.
operating entity).

**Type this:**
> Find all companies with "Berkshire" in their name.

**Expected behaviour:**
The agent calls `sec_edgar_search_companies` with `query="berkshire"` and
returns a table of matches. You should see both `BRK-A` and `BRK-B` rows for
Berkshire Hathaway.

**Example response (from live eval run):**

| CIK | Company Name | Ticker |
|-----|-------------|--------|
| 0001067983 | BERKSHIRE HATHAWAY INC | BRK-B |
| 0001067983 | BERKSHIRE HATHAWAY INC | BRK-A |

**Talking points:**
- The SEC registers ~10,000 exchange-listed companies; the agent searches all of
  them in real time.
- Large conglomerates often appear under multiple tickers (share classes, holding
  vs. operating entity). The agent surfaces all matches and lets the user choose.

---

## Step 2 — Resolve by Ticker (`sec_edgar_resolve_company`)

**What it shows:** Given a ticker, the agent fetches authoritative SEC identity
information: CIK, SIC code, industry description, and state of incorporation.

**Type this:**
> What is the SEC CIK number, SIC code, and state of incorporation for Microsoft (MSFT)?

**Expected behaviour:**
The agent calls `sec_edgar_resolve_company` with `identifier="MSFT"` and
returns the full registration record.

**Example response (from live eval run):**

- **Company:** Microsoft Corporation (MSFT)
- **SEC CIK:** 0000789019
- **SIC code:** 7372 — Services-Prepackaged Software
- **State of incorporation:** WA

**Talking points:**
- CIK (Central Index Key) is the SEC's internal identifier — it is the stable
  key used by all downstream tools in this demo.
- SIC codes let the agent categorise companies by industry even when the user
  does not know the sector.
- The agent always returns the full record (name, ticker, CIK, SIC,
  description, state) so the user has everything for follow-up queries.

---

## Step 3 — List Recent Filings (`sec_edgar_get_recent_filings`)

**What it shows:** The agent can list a company's most recent regulatory filings
filtered by form type, with accession numbers that link back to EDGAR.

**Type this:**
> List the five most recent 10-K filings for Microsoft.

**Expected behaviour:**
The agent calls `sec_edgar_get_recent_filings` with `identifier="MSFT"`,
`form_type="10-K"`, `limit=5`.

**Example response (from live eval run):**

| # | Filing Date | Report Period End | Accession Number |
|---|------------|-------------------|-----------------|
| 1 | 2026-07-29 | 2026-06-30 | 0001193125-26-323660 |
| 2 | 2025-07-30 | 2025-06-30 | 0000950170-25-100235 |
| 3 | 2024-07-30 | 2024-06-30 | 0000950170-24-087843 |
| 4 | 2023-07-27 | 2023-06-30 | 0000950170-23-035122 |
| 5 | 2022-07-28 | 2022-06-30 | 0001564590-22-026876 |

**Talking points:**
- Accession numbers are the SEC's universal filing keys — they are used in
  Step 8 to retrieve the actual filing document.
- The same tool works for 10-Q, 8-K, DEF 14A (proxy), and any other form type.
  Pass `form_type=""` to get all recent forms at once.
- Note Microsoft's fiscal year ends June 30 — filing dates fall in late July.

---

## Step 4 — Annual Financial Fact (`sec_edgar_get_company_fact`)

**What it shows:** The agent fetches a multi-year time series of a single XBRL
financial concept directly from the SEC's machine-readable data, with no manual
data entry.

**Type this:**
> Show me the last 5 annual net income figures for Apple.

**Expected behaviour:**
The agent resolves `AAPL`, then calls `sec_edgar_get_company_fact` with
`taxonomy="us-gaap"`, `concept="NetIncomeLoss"`, `limit=5`.

**Example response (from live eval run):**

| Fiscal Year | Net Income (USD) | Form | Accession Number |
|------------|-----------------|------|-----------------|
| FY 2022 | $99.8 billion | 10-K | 0000320193-22-000108 |
| FY 2023 | $99.8 billion | 10-K | 0000320193-23-000106 |
| FY 2024 | $96.7 billion | 10-K | 0000320193-24-000123 |
| FY 2025 | $112.0 billion | 10-K | 0000320193-25-000079 |
| FY 2026 | $132.2 billion | 10-K | 0000320193-26-000026 |

**Talking points:**
- All values come from the SEC's authoritative XBRL company-facts endpoint —
  the same data used by financial terminals and academic researchers.
- Each row includes the accession number so the source filing can be opened
  directly (demonstrated in Step 8).
- The agent uses XBRL concept names (`NetIncomeLoss`, `Assets`,
  `StockholdersEquity`, etc.) that map to audited line items in 10-K filings.

---

## Step 5 — Quarterly Revenue Trend (`sec_edgar_get_quarterly_facts`)

**What it shows:** The quarterly tool returns only genuine single-quarter
(3-month) periods — it filters out year-to-date cumulative values that the SEC
API mixes in under the same period label.

**Type this:**
> Show me Apple's quarterly revenue for the last 8 quarters.

**Expected behaviour:**
The agent calls `sec_edgar_get_quarterly_facts` with `identifier="AAPL"`,
`taxonomy="us-gaap"`,
`concept="RevenueFromContractWithCustomerExcludingAssessedTax"` (or `Revenues`
— it tries both), `limit=8`.

**Example response (from live eval run, post-fix):**

| Period | Quarter End | Revenue (USD) |
|--------|-------------|--------------|
| Q3 FY2026 | 2026-06-27 | $109.4 billion |
| Q2 FY2026 | 2026-03-28 | $95.4 billion |
| Q1 FY2026 | 2025-12-27 | $124.3 billion |
| Q3 FY2025 | 2025-06-28 | $94.0 billion |
| Q2 FY2025 | 2025-03-29 | $95.4 billion |
| Q1 FY2025 | 2024-12-28 | $124.3 billion |
| Q3 FY2024 | 2024-06-29 | $85.8 billion |
| Q2 FY2024 | 2024-03-30 | $90.8 billion |

**Talking points:**
- Apple's fiscal year runs October–September, so Q1 is Oct–Dec (holiday
  quarter) and Q3 is Apr–Jun.
- **Q4 limitation:** Companies don't file a 10-Q for fiscal Q4 — that quarter
  appears only in the 10-K. The agent explicitly states this when Q4 is missing.
- Pre-fix, this tool returned YTD cumulative values as quarterly figures
  (Q3 showed $364 billion instead of $109 billion). The duration filter
  (`≤104 days`) was added to close this gap.

---

## Step 6 — Discover XBRL Concepts (`sec_edgar_list_concepts`)

**What it shows:** Financial data lives under non-obvious XBRL tag names.
The agent can enumerate all concepts a company reports for any keyword, so
the user is never blocked by a "concept not found" error.

**Type this:**
> What revenue-related XBRL concepts does Apple report in us-gaap?

**Expected behaviour:**
The agent calls `sec_edgar_list_concepts` with `identifier="AAPL"`,
`taxonomy="us-gaap"`, `search="revenue"`.

**Example response (from live eval run):**

| XBRL Concept | Human-Readable Label |
|-------------|---------------------|
| RevenueFromContractWithCustomerExcludingAssessedTax | Revenue from Contract with Customer, Excluding Assessed Tax |
| Revenues | Revenues |
| SalesRevenueNet | Revenue, Net (Deprecated 2018-01-31) |
| ContractWithCustomerLiabilityRevenueRecognized | Contract with Customer, Liability, Revenue Recognized |
| DeferredRevenueCurrent | Deferred Revenue, Current |
| DeferredRevenueNoncurrent | Deferred Revenue, Noncurrent |
| IncreaseDecreaseInDeferredRevenue | Increase (Decrease) in Deferred Revenue |

**Talking points:**
- Apple switched from `Revenues` to `RevenueFromContractWithCustomerExcludingAssessedTax`
  around 2018. The old tag is deprecated but still present in historical filings.
- Try `search="debt"` on Tesla — it surfaces 72 matching concepts, including
  lease obligations, convertible notes, and finance costs.
- This tool is the escape hatch for any "concept not found" error — you can
  always browse what a specific company actually reports.

---

## Step 7 — Cross-Company Comparison (`sec_edgar_compare_companies`)

**What it shows:** The agent can compare the same XBRL concept across multiple
companies in one call, surfacing fiscal-year misalignment warnings so the user
can evaluate comparability.

**Type this:**
> Compare the most recent annual net income for Apple, Microsoft, and Google.

**Expected behaviour:**
The agent calls `sec_edgar_compare_companies` with
`identifiers=["AAPL", "MSFT", "GOOGL"]`, `taxonomy="us-gaap"`,
`concept="NetIncomeLoss"`.

**Example response (from live eval run):**

| Company | Net Income | Fiscal Year End | Form | Accession # |
|---------|------------|----------------|------|------------|
| Apple Inc. (AAPL) | $132.2 billion | 2026-09-26 | 10-K | 0000320193-26-000026 |
| Microsoft Corp. (MSFT) | $133.7 billion | 2026-06-30 | 10-K | 0001193125-26-323660 |
| Alphabet Inc. (GOOGL) | $132.2 billion | 2025-12-31 | 10-K | 0001652044-26-000018 |

**⚠ Comparability warning (surfaced by the agent):**
The fiscal year ends differ across the three companies (Apple: Sep 26,
Microsoft: Jun 30, Alphabet: Dec 31). Because the reporting periods are not
aligned, direct year-over-year comparison may be misleading.

**Talking points:**
- Three of the most profitable companies in the world all report ~$132–134 billion
  net income — a striking data point.
- The agent always surfaces every comparability warning in the response. Fiscal
  year misalignment and unit mismatches must be stated so the user can evaluate
  the data.
- The same call works for any XBRL concept: total assets, gross profit,
  long-term debt, EPS, etc.

---

## Step 8 — Source Filing Attribution (`sec_edgar_get_filing_metadata`)

**What it shows:** Every financial data point the agent returns includes an
accession number. This tool resolves that accession number to the actual SEC
filing, with a direct EDGAR viewer link the audience can open live.

**Type this:**
> Which SEC filing reported Apple's most recent annual revenue? Give me the accession number and a link.

**Expected behaviour:**
The agent first calls `sec_edgar_get_company_fact` to get the most recent
annual revenue observation and its accession number, then calls
`sec_edgar_get_filing_metadata` with `identifier="AAPL"` and that accession
number.

**Example response (from live eval run):**

- **Accession number:** `0000320193-26-000026`
- **Form type:** 10-K
- **Filing date:** 2026-11-03
- **Report period end:** 2026-09-26
- **Revenue figure:** $478.8 billion (FY 2026)
- **EDGAR link:**
  `https://www.sec.gov/Archives/edgar/data/320193/000032019326000026/aapl-20260926.htm`

> **Live demo tip:** Open the EDGAR link in a browser to show the audience the
> actual 10-K filing that supplied the data. The CIK (`320193`) and accession
> path are embedded directly in the URL — no guessing.

**Talking points:**
- Zero hallucination risk: the agent cannot invent a URL — the link is
  constructed deterministically from the accession number and CIK.
- The same lookup works for any observation returned by `get_company_fact`,
  `get_quarterly_facts`, or `compare_companies` — every row has an accession
  number.
- This closes the full provenance chain: user question → XBRL fact → 10-K filing
  → audited financial statement.

---

## Bonus Prompts (time permitting)

These can be dropped in if the audience asks follow-up questions or if you
have extra time:

```
# Debt concept discovery
What us-gaap debt concepts does Tesla report?

# Quarterly earnings per share
Show Apple's quarterly earnings per share for the last 6 quarters.

# Large-cap asset comparison
Which has more total assets — JPMorgan Chase (JPM) or Bank of America (BAC)?

# Multi-step: name search → annual revenue
Find companies with "Pfizer" in their name, then show the last 4 annual
revenue figures for the main one.

# Error handling: invalid ticker
What SEC filings has ZZZZNOTREAL submitted recently?
```

---

## Troubleshooting During the Demo

| Symptom | Likely cause | Quick fix |
|---------|-------------|-----------|
| Agent does not appear in chat | WXO token expired | Run `venv/bin/orchestrate env activate gsa-hackathon --api-key "$WXO_API_KEY"` |
| "concept not found" error | Concept name mismatch | Follow with Step 6 (`list_concepts`) to find the correct tag |
| Revenue figures look like YTD (too large) | Server not updated | Verify Code Engine app is running the fixed `server.py` |
| Q4 missing from quarterly results | Expected — by design | Explain the Q4/10-Q limitation; retrieve annual figure via Step 4 |
| ExxonMobil 10-K returns empty | Known issue (BQ-18) | Use XOM financial facts (`get_company_fact`) instead of `get_recent_filings` |

---

## Architecture Reminder (for Q&A)

```
User (WXO Chat UI)
      │
      ▼
sec_edgar_agent  (native agent, react_core, groq/gpt-oss-120b)
      │  8 tools via MCP streamable-HTTP
      ▼
sec_edgar_tools FastMCP server  (IBM Code Engine, always-warm)
      │  httpx async calls
      ▼
SEC EDGAR public APIs
  ├── company_tickers.json    (name → ticker/CIK index)
  ├── submissions/{CIK}.json  (filing history)
  └── companyfacts/{CIK}.json (XBRL financial facts)
```

No API keys required for the SEC APIs — they are open and free.
The only credentials needed are the WXO API key (to authenticate to Orchestrate)
and the IBM Cloud API key (to manage the Code Engine deployment).
