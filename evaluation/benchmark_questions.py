"""SEC EDGAR Agent — Benchmark Question Set.

20 questions across 10 scenario categories covering all 8 tools.
Each question specifies:
  - id            : unique identifier (BQ-01 … BQ-20)
  - category      : scenario type
  - difficulty    : easy | medium | hard
  - question      : natural-language prompt sent to the agent
  - expected_tools: tool(s) the agent must call for a correct answer
  - pass_criteria : plain-English description of what a passing response contains

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
            "Response presents a table or list of at least 3 annual net income figures for Apple; "
            "values are in USD billions; each row includes a fiscal year and accession number."
        ),
    },
    {
        "id": "BQ-08",
        "category": "annual_facts",
        "difficulty": "medium",
        "question": "What were Amazon's total assets for the last 4 fiscal years?",
        "expected_tools": ["sec_edgar_get_company_fact"],
        "pass_criteria": (
            "Response presents at least 3 annual total assets figures for Amazon (AMZN); "
            "values are in USD; fiscal years are identified."
        ),
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
            "Response presents quarterly revenue figures (not annual); "
            "period labels like 'Q1 FY2025' or similar are present; "
            "at least 4 quarters returned; values in USD."
        ),
    },
    {
        "id": "BQ-10",
        "category": "quarterly_facts",
        "difficulty": "medium",
        "question": "What was Microsoft's net income in each of the last 6 quarters?",
        "expected_tools": ["sec_edgar_get_quarterly_facts"],
        "pass_criteria": (
            "Response presents quarterly net income for Microsoft; "
            "quarter labels are present (Q1/Q2/Q3/Q4); "
            "at least 4 quarters returned; values in USD."
        ),
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
            "Response presents a comparison table with at least 2 of the 3 companies; "
            "values are in USD; fiscal years are stated; "
            "any fiscal year misalignment warnings are surfaced to the user."
        ),
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
            "includes the values and fiscal year end dates; "
            "surfaces any comparability warnings."
        ),
    },
    # ------------------------------------------------------------------
    # Category 8 — Source filing attribution (sec_edgar_get_filing_metadata)
    # ------------------------------------------------------------------
    {
        "id": "BQ-15",
        "category": "filing_attribution",
        "difficulty": "hard",
        "question": "Which SEC filing reported Apple's most recent annual revenue? Give me the accession number and a link to the filing.",
        "expected_tools": ["sec_edgar_get_company_fact", "sec_edgar_get_filing_metadata"],
        "pass_criteria": (
            "Response identifies the most recent annual revenue figure; "
            "includes the accession number of the source 10-K; "
            "includes an edgar_viewer_url pointing to sec.gov."
        ),
    },
    {
        "id": "BQ-16",
        "category": "filing_attribution",
        "difficulty": "hard",
        "question": "What form type and filing date corresponds to Microsoft's most recent annual net income figure?",
        "expected_tools": ["sec_edgar_get_company_fact", "sec_edgar_get_filing_metadata"],
        "pass_criteria": (
            "Response identifies the form type (10-K) and filing date for the "
            "source filing of Microsoft's most recent annual net income; "
            "includes the accession number."
        ),
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
            "then retrieves at least 3 annual revenue figures for Pfizer; "
            "values in USD with fiscal years."
        ),
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
            "does not fabricate a response; suggests using search_companies to find the right ticker."
        ),
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
            "response does not fabricate numbers."
        ),
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

    print(f"Total questions: {len(BENCHMARK_QUESTIONS)}")
    print(f"\nBy category:")
    for cat, n in sorted(cats.items()):
        print(f"  {cat:<30} {n}")
    print(f"\nBy difficulty:")
    for d, n in sorted(diffs.items()):
        print(f"  {d:<10} {n}")
    print(f"\nTool coverage:")
    for tool, n in sorted(tool_counts.items()):
        print(f"  {tool:<50} {n} question(s)")
