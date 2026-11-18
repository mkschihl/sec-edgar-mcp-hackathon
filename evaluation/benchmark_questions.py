"""SEC EDGAR Agent — Benchmark Question Set.

23 questions across 11 scenario categories covering all 8 tools.
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
            "Additional fiscal years beyond FY2023/2024 are acceptable. "
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
            "that is correct. Mark incorrect only if values appear to be year-to-date totals."
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
            "at least 4 quarters returned; values in USD."
        ),
        "numeric_checks": None,
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
            "includes the accession number of the source 10-K; "
            "includes an edgar_viewer_url or direct link pointing to sec.gov; "
            "the link must be a sec.gov URL returned by a tool."
        ),
        "numeric_checks": None,
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
            "includes the accession number."
        ),
        "numeric_checks": None,
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
            "FY2024 (ended 2024-12-31) revenue is approximately $63.6B; "
            "FY2023 (ended 2023-12-31) revenue is approximately $62.6B; "
            "FY2023 may show a recast note — the ORIGINAL filing reported $58.5B, "
            "but the recast value is $59.6B; either value is acceptable provided it is "
            "labelled as FY2023. "
            "FY2022 (ended 2022-12-31) revenue is approximately $100.3B. "
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
        "expected_tools": ["sec_edgar_get_recent_filings"],
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
            "if EPS values are returned, they are in the range $1.0–$2.5 per share; "
            "response does not fabricate numbers."
        ),
        # EPS values are small ($1–$2.50/share); no must_include since the exact
        # value varies. Use max_value only to guard against clearly wrong magnitudes.
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
            "may note that it can retrieve historical financial facts but not advise on trading."
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
]

# Quick summary when run directly
if __name__ == "__main__":
    from collections import Counter
    cats = Counter(q["category"] for q in BENCHMARK_QUESTIONS)
    diffs = Counter(q["difficulty"] for q in BENCHMARK_QUESTIONS)
    all_tools = []
    for q in BENCHMARK_QUESTIONS:
        all_tools.extend(q["expected_tools"])
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
