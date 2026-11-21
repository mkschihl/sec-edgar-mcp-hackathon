"""SEC EDGAR Agent — Benchmark Question Set.

27 questions across 13 scenario categories covering all 11 tools.
Each question specifies:
  - id              : unique identifier (BQ-01 … BQ-23)
  - category        : scenario type
  - difficulty      : easy | medium | hard
  - question        : natural-language prompt sent to the agent
  - expected_tools  : tool(s) the agent must call for a correct answer
  - pass_criteria   : plain-English description of what a passing response contains
  - numeric_checks  : list of dicts with {description, threshold_pct} for numeric
                      validation, or None if no numeric constraints apply

Difficulty rubric:
  easy   — single tool, well-known ticker, unambiguous intent
  medium — two-tool chain, or requires the agent to handle a concept name issue
  hard   — three+ tool chain, cross-company comparison, or source attribution
"""

# Category mapping:
#   1  company_search          BQ-01, BQ-02
#   2  company_resolution      BQ-03, BQ-04
#   3  recent_filings          BQ-05, BQ-06
#   4  annual_facts            BQ-07, BQ-08
#   5  quarterly_facts         BQ-09, BQ-10
#   6  concept_discovery       BQ-11, BQ-12
#   7  cross_company_comparison BQ-13, BQ-14
#   8  filing_attribution      BQ-15, BQ-16
#   9  multi_step_discovery    BQ-17, BQ-18
#  10  edge_cases              BQ-19, BQ-20
#  11  out_of_scope            BQ-21, BQ-22, BQ-23
#  12  filing_text             BQ-24, BQ-25   ← new (sec_edgar_get_filing_text)
#  13  full_text_search        BQ-26, BQ-27   ← new (sec_edgar_full_text_search)

BENCHMARK_QUESTIONS = [
    # ------------------------------------------------------------------
    # Category 1 — Company search (sec_edgar_search_companies)
    # ------------------------------------------------------------------
    {
        "id": "BQ-01",
        "category": "company_search",
        "difficulty": "easy",
        "question": "Find all companies with 'Berkshire' in their name.",
        "expected_tools": ["sec_edgar_search_companies"],
        "pass_criteria": (
            "Response lists at least one match containing 'Berkshire'; "
            "BRK.A or BRK.B is present; each match includes a ticker and CIK."
        ),
        "numeric_checks": None,
    },
    {
        "id": "BQ-02",
        "category": "company_search",
        "difficulty": "easy",
        "question": "I'm looking for companies related to 'General Electric'. What comes up?",
        "expected_tools": ["sec_edgar_search_companies"],
        "pass_criteria": (
            "Response lists at least one match with 'General Electric' in the name; "
            "GE or GEV ticker is present."
        ),
        "numeric_checks": None,
    },
    # ------------------------------------------------------------------
    # Category 2 — Company resolution (sec_edgar_resolve_company)
    # ------------------------------------------------------------------
    {
        "id": "BQ-03",
        "category": "company_resolution",
        "difficulty": "easy",
        "question": "What is the SEC CIK number and industry classification for Microsoft?",
        "expected_tools": ["sec_edgar_resolve_company"],
        "pass_criteria": (
            "Response includes CIK 0000789019; mentions 'Microsoft'; "
            "includes a SIC code or industry description."
        ),
        "numeric_checks": None,
    },
    {
        "id": "BQ-04",
        "category": "company_resolution",
        "difficulty": "easy",
        "question": "Tell me about Alphabet Inc. — what state is it incorporated in and what SIC code does it use?",
        "expected_tools": ["sec_edgar_resolve_company"],
        "pass_criteria": (
            "Response includes Alphabet or Google; mentions state of incorporation (DE or CA); "
            "includes a SIC code."
        ),
        "numeric_checks": None,
    },
    # ------------------------------------------------------------------
    # Category 3 — Recent filings (sec_edgar_get_recent_filings)
    # ------------------------------------------------------------------
    {
        "id": "BQ-05",
        "category": "recent_filings",
        "difficulty": "easy",
        "question": "List the five most recent 10-K filings for Microsoft.",
        "expected_tools": ["sec_edgar_get_recent_filings"],
        "pass_criteria": (
            "Response lists up to 5 filings; all have form type 10-K; "
            "each includes a filing date and accession number."
        ),
        "numeric_checks": None,
    },
    {
        "id": "BQ-06",
        "category": "recent_filings",
        "difficulty": "easy",
        "question": "Show me the 10 most recent 10-Q filings for Johnson & Johnson (ticker: JNJ).",
        "expected_tools": ["sec_edgar_get_recent_filings"],
        "pass_criteria": (
            "Response lists up to 10 filings; all have form type 10-Q; "
            "includes filing dates."
        ),
        "numeric_checks": None,
    },
    # ------------------------------------------------------------------
    # Category 4 — Annual financial facts (sec_edgar_get_company_fact)
    # ------------------------------------------------------------------
    {
        "id": "BQ-07",
        "category": "annual_facts",
        "difficulty": "medium",
        "question": "Show me the last 5 annual net income figures for Apple.",
        "expected_tools": ["sec_edgar_get_company_fact"],
        "pass_criteria": (
            "Response presents at least 3 annual net income figures for Apple (AAPL); "
            "values are labelled with fiscal years; "
            "FY2024 (ended 2024-09-28) net income is $93.7B and "
            "FY2023 (ended 2023-09-30) net income is $97.0B. "
            "Additional fiscal years beyond FY2023/2024 are acceptable and common: "
            "FY2025 ended 2025-09-27 (~$112B) and FY2026 ended 2026-09-26 (~$132B) "
            "are both historical (period ends before 2026-11-18) and correct if present. "
            "No two distinct fiscal years may share the same reported value."
        ),
        "numeric_checks": {
            "must_include": [93.7e9, 97.0e9],
            "rel_tol": 0.02,
            "max_value": None,
        },
    },
    {
        "id": "BQ-08",
        "category": "annual_facts",
        "difficulty": "medium",
        "question": "What were Amazon's total assets for the last 4 fiscal years?",
        "expected_tools": ["sec_edgar_get_company_fact"],
        "pass_criteria": (
            "Response presents at least 3 annual total assets figures for Amazon (AMZN); "
            "values are in USD; fiscal years are identified; "
            "most recent figure is in the hundreds of billions USD range."
        ),
        "numeric_checks": None,
    },
    # ------------------------------------------------------------------
    # Category 5 — Quarterly facts (sec_edgar_get_quarterly_facts)
    # ------------------------------------------------------------------
    {
        "id": "BQ-09",
        "category": "quarterly_facts",
        "difficulty": "medium",
        "question": "Show me Apple's quarterly revenue for the last 8 quarters.",
        "expected_tools": ["sec_edgar_get_quarterly_facts"],
        "pass_criteria": (
            "Response presents individual quarterly revenue figures (not annual, not YTD); "
            "period labels like 'Q1 FY2025' or similar are present; "
            "at least 4 quarters returned; "
            "quarter ended 2026-06-27 = $109.4B and quarter ended 2026-03-28 = $111.2B. "
            "Holiday quarters (Q1, ending in late December) may legitimately exceed $130B; "
            "that is correct. Mark incorrect only if values appear to be year-to-date totals. "
            "Fiscal Q4 rows marked '(derived)' are computed as annual minus nine-month YTD; "
            "they are legitimate single-quarter values, not year-to-date totals, and are correct."
        ),
        "numeric_checks": {
            "must_include": [109.4e9, 111.2e9],
            "rel_tol": 0.02,
            "max_value": 200e9,
        },
    },
    {
        "id": "BQ-10",
        "category": "quarterly_facts",
        "difficulty": "medium",
        "question": "What was Microsoft's net income in each of the last 6 quarters?",
        "expected_tools": ["sec_edgar_get_quarterly_facts"],
        "pass_criteria": (
            "Response presents quarterly net income for Microsoft; "
            "quarter labels are present (Q1/Q2/Q3 or fiscal quarter names); "
            "at least 4 distinct quarters returned, each with a unique period end date; "
            "values in USD. "
            "Microsoft uses a fiscal year that starts in July — 'FY2027 Q1' label "
            "with period end 2026-09-30 is correct and historical, not a forecast. "
            "Values must be single-quarter (not year-to-date) amounts. "
            "Most recent quarter (Q1 FY2027, ended 2026-09-30) net income ≈ $36.6B; "
            "Q3 FY2026 (ended 2026-03-31) ≈ $31.8B; "
            "Q2 FY2026 (ended 2025-12-31) ≈ $38.5B; "
            "Q4 FY2026 (ended 2026-06-30) ≈ $35.8B (derived: annual minus nine-month YTD). "
            "Fiscal Q4 rows marked '(derived)' are computed as annual minus nine-month YTD; "
            "they are legitimate single-quarter values, not year-to-date totals, and are correct."
        ),
        "numeric_checks": {
            "must_include": [36.629e9, 31.778e9, 38.458e9, 35.766e9],
            "rel_tol": 0.005,
            "max_value": None,
        },
    },
    # ------------------------------------------------------------------
    # Category 6 — Concept discovery (sec_edgar_list_concepts)
    # ------------------------------------------------------------------
    {
        "id": "BQ-11",
        "category": "concept_discovery",
        "difficulty": "medium",
        "question": "What revenue-related XBRL concepts does Apple report in us-gaap?",
        "expected_tools": ["sec_edgar_list_concepts"],
        "pass_criteria": (
            "Response lists at least 2 XBRL concept names containing 'Revenue' or 'revenue'; "
            "includes human-readable labels alongside concept names."
        ),
        "numeric_checks": None,
    },
    {
        "id": "BQ-12",
        "category": "concept_discovery",
        "difficulty": "medium",
        "question": "I want to find debt-related financial concepts for Tesla. What us-gaap concepts are available?",
        "expected_tools": ["sec_edgar_list_concepts"],
        "pass_criteria": (
            "Response lists at least 2 debt-related XBRL concepts for Tesla (TSLA); "
            "concept names or labels contain 'Debt' or 'debt' or 'Liability'."
        ),
        "numeric_checks": None,
    },
    # ------------------------------------------------------------------
    # Category 7 — Cross-company comparison (sec_edgar_compare_companies)
    # ------------------------------------------------------------------
    {
        "id": "BQ-13",
        "category": "cross_company_comparison",
        "difficulty": "hard",
        "question": "Compare the most recent annual net income for Apple, Microsoft, and Google.",
        "expected_tools": ["sec_edgar_compare_companies"],
        "pass_criteria": (
            "Response presents a comparison with at least 2 of the 3 companies; "
            "values are in USD; fiscal years are stated; "
            "any fiscal year misalignment warnings are surfaced to the user."
        ),
        "numeric_checks": None,
    },
    {
        "id": "BQ-14",
        "category": "cross_company_comparison",
        "difficulty": "hard",
        "question": "Which company has more total assets — JPMorgan Chase (JPM) or Bank of America (BAC)? Use the most recent annual figures.",
        "expected_tools": ["sec_edgar_compare_companies"],
        "pass_criteria": (
            "Response compares total assets for JPM and BAC; "
            "clearly states which is larger; "
            "JPM total assets are approximately $4.42T USD (±0.5%) and "
            "BAC total assets are approximately $3.41T USD (±0.5%); "
            "includes fiscal year end dates."
        ),
        "numeric_checks": {
            "must_include": [4.4249e12, 3.411738e12],
            "rel_tol": 0.005,
            "max_value": None,
        },
    },
    # ------------------------------------------------------------------
    # Category 8 — Source filing attribution (sec_edgar_get_filing_metadata)
    # ------------------------------------------------------------------
    {
        "id": "BQ-15",
        "category": "filing_attribution",
        "difficulty": "hard",
        "question": "Which SEC filing reported Apple's most recent annual revenue? Give me the accession number and a link to the filing.",
        "expected_tools": ["sec_edgar_get_company_fact"],
        "optional_tools": ["sec_edgar_get_filing_metadata"],
        "pass_criteria": (
            "Response identifies the most recent annual revenue figure; "
            "states the revenue amount (~$478.8B for FY ended 2026-09-26); "
            "includes the accession number of the source 10-K; "
            "includes an edgar_viewer_url or direct link pointing to sec.gov; "
            "the link must be a sec.gov URL returned by a tool."
        ),
        "numeric_checks": {
            "must_include": [478.834e9],
            "rel_tol": 0.005,
            "max_value": None,
        },
    },
    {
        "id": "BQ-16",
        "category": "filing_attribution",
        "difficulty": "hard",
        "question": "What form type and filing date corresponds to Microsoft's most recent annual net income figure?",
        "expected_tools": ["sec_edgar_get_company_fact"],
        "optional_tools": ["sec_edgar_get_filing_metadata"],
        "pass_criteria": (
            "Response identifies the form type (10-K) and filing date for the "
            "source filing of Microsoft's most recent annual net income; "
            "states the net income amount (~$133.7B for FY ended 2026-06-30); "
            "includes the accession number."
        ),
        "numeric_checks": {
            "must_include": [133.749e9],
            "rel_tol": 0.005,
            "max_value": None,
        },
    },
    # ------------------------------------------------------------------
    # Category 9 — Multi-step: unknown company → facts
    # ------------------------------------------------------------------
    {
        "id": "BQ-17",
        "category": "multi_step_discovery",
        "difficulty": "hard",
        "question": "I don't know the ticker — find companies with 'Pfizer' in the name, then show me the last 4 annual revenue figures for the main one.",
        "expected_tools": ["sec_edgar_search_companies", "sec_edgar_get_company_fact"],
        "pass_criteria": (
            "Agent first searches for 'Pfizer' and identifies PFE; "
            "then retrieves at least 3 annual revenue figures for Pfizer (concept: Revenues); "
            "values in USD with fiscal years; "
            "FY2025 (ended 2025-12-31) revenue is approximately $62.6B; "
            "FY2024 (ended 2024-12-31) revenue is approximately $63.6B; "
            "FY2023 (ended 2023-12-31) revenue is approximately $59.6B (recast) or "
            "$58.5B (as originally filed); either value is acceptable provided it is "
            "labelled as FY2023. Do NOT accept $62.6B for FY2023 — that is the FY2025 "
            "value; reporting it for FY2023 is a year-mislabeling error. "
            "FY2022 (ended 2022-12-31) revenue is approximately $100.3B (original) or "
            "$101.2B (recast); either value is acceptable provided it is labelled as FY2022. "
            "The question asks for the LAST 4 annual figures, so the window may start from "
            "FY2022 or FY2021 depending on the most recent data available; FY2025 is "
            "historical (ended 2025-12-31 which is before today). "
            "Values should not be from the RevenueFromContractWithCustomer... concept, "
            "which reports different (incorrect) figures."
        ),
        "numeric_checks": {
            "must_include": [62.579e9, 63.627e9, 59.553e9],
            "rel_tol": 0.005,
            "max_value": None,
        },
    },
    {
        "id": "BQ-18",
        "category": "multi_step_discovery",
        "difficulty": "hard",
        "question": "Search for companies with 'Exxon' in their name, resolve the main one, then list its 5 most recent 10-K filings.",
        "expected_tools": ["sec_edgar_search_companies", "sec_edgar_get_recent_filings"],
        "pass_criteria": (
            "Agent searches for 'Exxon', identifies XOM; "
            "lists at least 3 recent 10-K filings with filing dates and accession numbers."
        ),
        "numeric_checks": None,
    },
    # ------------------------------------------------------------------
    # Category 10 — Edge cases & error handling
    # ------------------------------------------------------------------
    {
        "id": "BQ-19",
        "category": "edge_cases",
        "difficulty": "easy",
        "question": "What SEC filings has the company with ticker ZZZZNOTREAL submitted recently?",
        "expected_tools": [],
        "pass_criteria": (
            "Agent attempts the lookup and gracefully reports that the ticker was not found; "
            "does not fabricate a response; "
            "suggests using search_companies to find the right ticker."
        ),
        "numeric_checks": None,
    },
    {
        "id": "BQ-20",
        "category": "edge_cases",
        "difficulty": "medium",
        "question": "Show me Apple's quarterly EarningsPerShareBasicAndDiluted for the last 4 quarters.",
        "expected_tools": ["sec_edgar_get_quarterly_facts"],
        "pass_criteria": (
            "Agent retrieves quarterly EPS data for Apple; "
            "if the concept name is not found, the agent uses list_concepts or suggests a correction; "
            "if EPS values are returned, they are plausible quarterly EPS values for Apple "
            "(historically $1.00–$2.50/share for FY2022–FY2024, up to ~$3.00/share for FY2025/FY2026); "
            "response does not fabricate numbers."
        ),
        # EPS values are small; no must_include since the exact value varies by period.
        # Use max_value only to guard against clearly wrong magnitudes.
        "numeric_checks": {
            "must_include": [],
            "rel_tol": 0.05,
            "max_value": 10.0,  # EPS > $10/share would be clearly wrong for AAPL
        },
    },
    # ------------------------------------------------------------------
    # Category 11 — Out-of-scope questions (agent should refuse)
    # ------------------------------------------------------------------
    {
        "id": "BQ-21",
        "category": "out_of_scope",
        "difficulty": "easy",
        "question": "What is Apple's current stock price?",
        "expected_tools": [],
        "pass_criteria": (
            "Agent declines to answer or explains it cannot provide real-time stock prices; "
            "does not fabricate a price or use SEC tools to infer one; "
            "may suggest checking a financial data provider."
        ),
        "numeric_checks": None,
    },
    {
        "id": "BQ-22",
        "category": "out_of_scope",
        "difficulty": "easy",
        "question": "Should I buy Tesla stock right now? What's your recommendation?",
        "expected_tools": [],
        "pass_criteria": (
            "Agent declines to provide investment advice; "
            "does not use SEC tools to construct a buy/sell recommendation; "
            "a simple refusal is sufficient — the agent is not required to offer historical data."
        ),
        "numeric_checks": None,
    },
    {
        "id": "BQ-23",
        "category": "out_of_scope",
        "difficulty": "medium",
        "question": "What will Microsoft's revenue be next fiscal year?",
        "expected_tools": [],
        "pass_criteria": (
            "Agent declines to make a forward-looking forecast; "
            "does not fabricate a projected number; "
            "may offer to show historical revenue figures instead."
        ),
        "numeric_checks": None,
    },
    # ------------------------------------------------------------------
    # Category 12 — Filing text extraction (sec_edgar_get_filing_text)
    # ------------------------------------------------------------------
    {
        "id": "BQ-24",
        "category": "filing_text",
        "difficulty": "medium",
        "question": "Show me the Risk Factors section from Apple's most recent 10-K filing.",
        "expected_tools": ["sec_edgar_get_recent_filings", "sec_edgar_get_filing_text"],
        "pass_criteria": (
            "Agent retrieves a recent Apple 10-K accession number (via get_recent_filings "
            "or get_company_fact), then calls sec_edgar_get_filing_text with section='risk_factors'; "
            "response contains extracted plain text from the filing (not just metadata); "
            "text is at least a few sentences long and reads as risk-factor prose; "
            "response includes the document_url pointing to sec.gov; "
            "response does NOT fabricate risk factor content from memory."
        ),
        "numeric_checks": None,
    },
    {
        "id": "BQ-25",
        "category": "filing_text",
        "difficulty": "hard",
        "question": (
            "Read the MD&A (Management's Discussion and Analysis) section from "
            "Microsoft's most recent 10-K and summarise what it says about revenue growth."
        ),
        "expected_tools": ["sec_edgar_get_filing_text"],
        "optional_tools": ["sec_edgar_get_recent_filings", "sec_edgar_get_company_fact"],
        "pass_criteria": (
            "Agent calls sec_edgar_get_filing_text with section='mda' for a Microsoft 10-K; "
            "response contains or summarises actual extracted text about revenue growth "
            "(not fabricated); "
            "includes the document_url from the tool response; "
            "response is substantive (more than one sentence of content)."
        ),
        "numeric_checks": None,
    },
    # ------------------------------------------------------------------
    # Category 13 — Full-text keyword search (sec_edgar_full_text_search)
    # ------------------------------------------------------------------
    {
        "id": "BQ-26",
        "category": "full_text_search",
        "difficulty": "easy",
        "question": (
            "Which companies mentioned going concern in their 10-K filings "
            "filed in 2024? Show up to 5 results."
        ),
        "expected_tools": ["sec_edgar_full_text_search"],
        "pass_criteria": (
            "Agent calls sec_edgar_full_text_search with query containing 'going concern' "
            "and forms='10-K' (or similar) and a date range covering 2024; "
            "if results are returned, response presents at least 1 company with "
            "filing date and filing index URL or accession number, and results are real (not fabricated); "
            "if zero results are returned, agent clearly reports that and may suggest broadening the search; "
            "agent does NOT fabricate results when the tool returns zero matches."
        ),
        "numeric_checks": None,
    },
    {
        "id": "BQ-27",
        "category": "full_text_search",
        "difficulty": "medium",
        "question": (
            "Find Apple's 8-K filings from 2024 that mention the word 'dividend'. "
            "List up to 5 results with their filing dates."
        ),
        "expected_tools": ["sec_edgar_full_text_search"],
        "pass_criteria": (
            "Agent calls sec_edgar_full_text_search scoped to Apple (AAPL) with "
            "query='dividend', forms='8-K', and a date range covering 2024; "
            "response lists up to 5 matching 8-K filings with filing dates and "
            "accession numbers or filing index URLs; "
            "if no matching filings exist the agent clearly states that (not fabricates); "
            "results, if present, are Apple 8-K filings."
        ),
        "numeric_checks": None,
    },
    # ------------------------------------------------------------------
    # Category 14 — Company screening (sec_edgar_screen)
    # ------------------------------------------------------------------
    {
        "id": "BQ-28",
        "category": "screen",
        "difficulty": "easy",
        "question": (
            "Find the top 20 Nasdaq-listed prepackaged software companies (SIC code 7372)."
        ),
        "expected_tools": ["sec_edgar_screen"],
        "pass_criteria": (
            "Agent calls sec_edgar_screen with sic_code='7372' and exchange='Nasdaq' (or similar); "
            "response lists at least 5 companies with name, ticker, and CIK; "
            "results contain known Nasdaq software companies (e.g. MSFT, AAPL is not SIC 7372 — "
            "agent should report actual results from the tool, not fabricate); "
            "agent does NOT fabricate company names."
        ),
        "numeric_checks": None,
    },
    {
        "id": "BQ-29",
        "category": "screen",
        "difficulty": "medium",
        "question": (
            "List up to 20 pharmaceutical companies (SIC code 2836) incorporated in Delaware."
        ),
        "expected_tools": ["sec_edgar_screen"],
        "pass_criteria": (
            "Agent calls sec_edgar_screen with sic_code='2836' and state_of_incorporation='DE'; "
            "response lists all companies the tool returned (may be fewer than 5 — SEC data varies); "
            "results are drawn from the tool's response — agent does NOT fabricate company names; "
            "if the tool returns zero or very few results, agent clearly states that."
        ),
        "numeric_checks": None,
    },
    # ------------------------------------------------------------------
    # Category 15 — 8-K earnings press release (sec_edgar_get_earnings_release)
    # ------------------------------------------------------------------
    {
        "id": "BQ-30",
        "category": "earnings_release",
        "difficulty": "easy",
        "question": (
            "Show me Apple's most recent earnings press release. "
            "What were the reported quarterly revenue and diluted EPS?"
        ),
        "expected_tools": ["sec_edgar_get_earnings_release"],
        "pass_criteria": (
            "Agent calls sec_edgar_get_earnings_release with identifier='AAPL' (or '0000320193'); "
            "response includes the press_release_url; "
            "response states the reported quarterly revenue figure (in dollars); "
            "response states the diluted EPS figure (in dollars per share); "
            "figures come from the tool's extracted_figures or text — not fabricated."
        ),
        "numeric_checks": None,
    },
    {
        "id": "BQ-31",
        "category": "earnings_release",
        "difficulty": "medium",
        "question": (
            "What did NVIDIA announce in its most recent earnings press release? "
            "Specifically, what was the reported diluted EPS?"
        ),
        "expected_tools": ["sec_edgar_get_earnings_release"],
        "pass_criteria": (
            "Agent calls sec_edgar_get_earnings_release with identifier='NVDA' (or similar); "
            "response includes a diluted EPS figure extracted from the press release text; "
            "response includes the press_release_url; "
            "agent does NOT fabricate EPS if the tool fails to extract it — instead states "
            "it could not extract a clean figure and quotes the relevant text passage."
        ),
        "numeric_checks": None,
    },
    # ------------------------------------------------------------------
    # Category 16 — Synonym resolution (sec_edgar_resolve_synonym)
    # ------------------------------------------------------------------
    {
        "id": "BQ-32",
        "category": "synonym_resolution",
        "difficulty": "easy",
        "question": (
            "Who is 'Google' registered as with the SEC? "
            "What is their ticker symbol?"
        ),
        "expected_tools": ["sec_edgar_resolve_synonym"],
        "pass_criteria": (
            "Agent calls sec_edgar_resolve_synonym with input='Google' (or similar); "
            "response states the canonical SEC name 'Alphabet Inc.' (or Alphabet); "
            "response includes the ticker GOOGL (or GOOG); "
            "no SEC API calls are needed — this is a pure name lookup."
        ),
        "numeric_checks": None,
    },
    {
        "id": "BQ-33",
        "category": "synonym_resolution",
        "difficulty": "medium",
        "question": (
            "What SIC industry code is 'Meta' classified under with the SEC? "
            "What state are they incorporated in?"
        ),
        "expected_tools": ["sec_edgar_resolve_synonym", "sec_edgar_resolve_company"],
        "pass_criteria": (
            "Agent calls sec_edgar_resolve_synonym with input='Meta' to get the canonical "
            "name 'Meta Platforms, Inc.' and ticker META; "
            "agent then calls sec_edgar_resolve_company with identifier='META' (or the CIK); "
            "response states the SIC code (7370 or similar) and state of incorporation (Delaware/DE); "
            "agent does NOT fabricate the SIC code or state from memory."
        ),
        "numeric_checks": None,
    },
]

# Quick summary when run directly
if __name__ == "__main__":
    from collections import Counter
    cats = Counter(q["category"] for q in BENCHMARK_QUESTIONS)
    diffs = Counter(q["difficulty"] for q in BENCHMARK_QUESTIONS)
    all_tools = []
    for q in BENCHMARK_QUESTIONS:
        all_tools.extend(q["expected_tools"])
        all_tools.extend(q.get("optional_tools") or [])
    tool_counts = Counter(all_tools)
    with_numeric = sum(1 for q in BENCHMARK_QUESTIONS if q.get("numeric_checks"))

    print(f"Total questions: {len(BENCHMARK_QUESTIONS)}")
    print(f"With numeric_checks: {with_numeric}")
    print(f"\nBy category:")
    for cat, n in sorted(cats.items()):
        print(f"  {cat:<30} {n}")
    print(f"\nBy difficulty:")
    for d, n in sorted(diffs.items()):
        print(f"  {d:<10} {n}")
    print(f"\nTool coverage:")
    for tool, n in sorted(tool_counts.items()):
        print(f"  {tool:<50} {n} question(s)")
