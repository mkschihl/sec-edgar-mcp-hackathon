"""Build the sec-edgar-eval-* Phoenix dataset CSV from the benchmark questions.

The default target is sec-edgar-eval-2, which fixes the numeric_checks schema
so the numeric judge uses the new {must_include, rel_tol, max_value} format
instead of the old list-of-dicts.

Usage (from eval/phoenix/):
    python build_dataset.py                                   # → sec-edgar-eval-2
    python build_dataset.py --dry-run                         # validate only
    python build_dataset.py --output-dir datasets/sec-edgar-eval-2/examples
    python build_dataset.py --dataset-name sec-edgar-eval-1   # legacy compat

Output:
    datasets/sec-edgar-eval-2/examples/sec-edgar-eval-2.csv

The CSV has columns: query, responses, metadata
  - query    : the natural-language question (input)
  - responses: ground-truth reference answer string (output / expected)
  - metadata : JSON string with numeric_checks, category, difficulty
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
EVAL_PHOENIX_DIR = Path(__file__).resolve().parent
EVAL_DIR         = EVAL_PHOENIX_DIR.parent.parent / "evaluation"
_DEFAULT_DATASET = "sec-edgar-eval-2"
DEFAULT_OUT_DIR  = EVAL_PHOENIX_DIR / "datasets" / _DEFAULT_DATASET / "examples"
OUTPUT_CSV_NAME  = f"{_DEFAULT_DATASET}.csv"

sys.path.insert(0, str(EVAL_DIR))
from benchmark_questions import BENCHMARK_QUESTIONS  # noqa: E402


# ---------------------------------------------------------------------------
# Reference answers for each question
#
# These are the minimum-sufficient ground-truth answers used by the
# correctness judge. Keep them concise but specific enough to distinguish
# a correct response from a vague or incorrect one.
# ---------------------------------------------------------------------------
_REFERENCE_ANSWERS: dict[str, str] = {
    "BQ-01": (
        "At least one result with 'Berkshire' in the name should be returned. "
        "Berkshire Hathaway (ticker BRK.A or BRK.B) must appear. "
        "Each result includes a CIK and ticker."
    ),
    "BQ-02": (
        "At least one result with 'General Electric' in the name should be returned. "
        "GE (General Electric Company) or GEV (GE Vernova) must appear."
    ),
    "BQ-03": (
        "Microsoft's CIK is 0000789019. "
        "Its SIC code is 7372 (Prepackaged Software). "
        "It is incorporated in Washington state."
    ),
    "BQ-04": (
        "Alphabet Inc. (Google) is incorporated in Delaware. "
        "Its SIC code is 7370 (Services-Computer Integrated Systems Design). "
        "The ticker is GOOGL or GOOG."
    ),
    "BQ-05": (
        "Up to 5 Microsoft 10-K filings should be listed with filing dates "
        "and accession numbers. All form types must be 10-K. "
        "Filing dates may be in 2026 or later — these are real historical filings "
        "that have already been submitted to the SEC and are correct if present."
    ),
    "BQ-06": (
        "Up to 10 Johnson & Johnson (JNJ) 10-Q filings should be listed "
        "with filing dates. All form types must be 10-Q."
    ),
    "BQ-07": (
        "Apple (AAPL) annual net income for at least 3 recent fiscal years. "
        "FY2024 (ended Sep 2024): approximately $93.7B USD. "
        "FY2023 (ended Sep 2023): approximately $96.0B USD. "
        "FY2022 (ended Sep 2022): approximately $99.8B USD. "
        "Each row should include a fiscal year label. "
        "FY2025 (ended Sep 2025) net income ~$112B and "
        "FY2026 (ended Sep 2026) net income ~$132B are also historical "
        "(period ends before today) and are correct if present."
    ),
    "BQ-08": (
        "Amazon (AMZN) total assets for at least 3 recent fiscal years. "
        "Values are in hundreds of billions USD. "
        "FY2023 total assets were approximately $527B USD. "
        "FY2024 total assets were approximately $624B USD. "
        "FY2025 total assets are also historical (period ended before today) and correct if present. "
        "Do NOT penalise values that appear large — Amazon total assets grew significantly in 2024–2025."
    ),
    "BQ-09": (
        "Apple quarterly revenue for at least 4 recent quarters. "
        "Individual quarters range from approximately $85B to $130B USD. "
        "Quarter labels (e.g. Q1 FY2025, Q2 FY2025) should be present."
    ),
    "BQ-10": (
        "Microsoft quarterly net income for at least 4 recent quarters. "
        "Values are in billions USD. "
        "Quarter labels should be present."
    ),
    "BQ-11": (
        "At least 2 XBRL revenue concepts for Apple in us-gaap taxonomy. "
        "Concepts should include names like 'RevenueFromContractWithCustomerExcludingAssessedTax' "
        "or 'Revenues'. Human-readable labels should accompany concept names."
    ),
    "BQ-12": (
        "At least 2 XBRL debt-related concepts for Tesla (TSLA) in us-gaap taxonomy. "
        "Concepts should contain 'Debt' or 'Liability' in their name or label."
    ),
    "BQ-13": (
        "Comparison of most recent annual net income for at least 2 of: "
        "Apple (AAPL), Microsoft (MSFT), Alphabet (GOOGL). "
        "Values in USD with fiscal year labels. "
        "Fiscal year misalignment warnings should be noted if applicable. "
        "FY2025 and FY2026 figures are historical (period ends before today) "
        "and are correct if the agent returns them as the most recent values. "
        "Apple FY2026 net income ~$132B (ended Sep 26 2026) is correct. "
        "Microsoft FY2026 net income ~$133.7B (ended Jun 30 2026) is correct. "
        "Alphabet FY2025 net income ~$132B (ended Dec 31 2025) is correct. "
        "Do NOT flag these as out-of-scope — all period ends are before today."
    ),
    "BQ-14": (
        "JPMorgan Chase (JPM) has more total assets than Bank of America (BAC). "
        "JPM total assets: approximately $4.0 trillion USD (most recent annual). "
        "BAC total assets: approximately $3.3 trillion USD (most recent annual). "
        "Fiscal year end dates should be included. "
        "FY2025 and FY2026 figures from these banks are historical — their period "
        "ends have already passed and they are correct if present. "
        "Do NOT flag the response as out-of-scope for returning recent historical data."
    ),
    "BQ-15": (
        "The most recent Apple annual revenue is from a 10-K filing. "
        "The revenue figure is approximately $478.8 billion for the fiscal year "
        "ended September 2026 (accession 0000320193-26-000026). "
        "Response includes the accession number of that 10-K. "
        "Response includes a link or URL to sec.gov or the EDGAR viewer. "
        "Date formats like 'September 26 2026' and '2026-09-26' are equivalent — "
        "do NOT fail on date formatting differences."
    ),
    "BQ-16": (
        "The most recent Microsoft annual net income is from a 10-K filing. "
        "Response includes the form type (10-K), filing date, and accession number."
    ),
    "BQ-17": (
        "Agent searches for 'Pfizer' and identifies Pfizer Inc. (PFE). "
        "At least 3 annual revenue figures for Pfizer are returned. "
        "FY2025 (ended 2025-12-31) revenue: approximately $62.6B USD. "
        "FY2024 (ended 2024-12-31) revenue: approximately $63.6B USD. "
        "FY2023 (ended 2023-12-31) revenue: approximately $58.5B–$59.6B USD. "
        "FY2022 (ended 2022-12-31) revenue: approximately $100.3B USD (COVID-related peak). "
        "FY2025 is historical (ended before today) and correct if present. "
        "Values include fiscal year labels."
    ),
    "BQ-18": (
        "Agent searches for 'Exxon' and identifies Exxon Mobil Corporation (XOM). "
        "At least 3 recent 10-K filings are listed with filing dates and accession numbers."
    ),
    "BQ-19": (
        "Agent reports that ticker ZZZZNOTREAL was not found in the SEC database. "
        "No filing data is fabricated. "
        "Agent suggests using sec_edgar_search_companies to find the correct ticker."
    ),
    "BQ-20": (
        "Agent attempts to retrieve quarterly EPS data for Apple. "
        "If EarningsPerShareBasicAndDiluted is not found, agent suggests using "
        "sec_edgar_list_concepts to find the correct concept name. "
        "If EPS values are returned, typical range is $1.00–$2.50 per share for "
        "FY2024 quarters; FY2025/FY2026 quarters may be higher (e.g. $2.85 for "
        "Q1 FY2026) and are correct if present — do not penalise values above $2.50 "
        "for recent historical quarters. No numbers are fabricated."
    ),
    "BQ-21": (
        "Agent declines to provide Apple's current stock price, explaining it only "
        "has access to historical SEC filing data, not real-time market data. "
        "No stock price is fabricated."
    ),
    "BQ-22": (
        "Agent declines to provide investment advice about Tesla stock. "
        "Agent does not use SEC tools to construct a buy/sell recommendation. "
        "It is NOT required for the agent to offer historical financial facts — "
        "a simple, polite refusal is fully correct. "
        "Do not penalise the agent for not volunteering to show SEC data."
    ),
    "BQ-23": (
        "Agent declines to forecast Microsoft's future revenue, explaining it cannot "
        "make forward-looking projections. "
        "Agent may offer to show historical revenue figures instead."
    ),
    "BQ-24": (
        "Agent calls sec_edgar_get_filing_text for Apple's most recent 10-K "
        "with section='risk_factors'. "
        "Response contains extracted plain text from the filing — multi-sentence prose "
        "describing Apple's business risks (e.g. competition, supply chain, regulation). "
        "Response includes a document_url pointing to sec.gov. "
        "Content is NOT fabricated from memory."
    ),
    "BQ-25": (
        "Agent calls sec_edgar_get_filing_text for Microsoft's most recent 10-K "
        "with section='mda'. "
        "Response summarises or quotes actual MD&A text about revenue growth. "
        "Response includes a document_url pointing to sec.gov. "
        "Content is NOT fabricated from memory."
    ),
    "BQ-26": (
        "Agent calls sec_edgar_full_text_search with query='going concern' "
        "restricted to 10-K form type and 2024 date range. "
        "If results are returned, response lists at least 1 company with filing date "
        "and filing index URL or accession number; results are real (not fabricated). "
        "If zero results returned, agent clearly states that and may offer to broaden "
        "the search — this is also a correct response."
    ),
    "BQ-27": (
        "Agent calls sec_edgar_full_text_search scoped to Apple (AAPL) with "
        "query='dividend' and forms='8-K' in 2024. "
        "If results exist, response lists up to 5 Apple 8-K filings with filing dates. "
        "If no results, agent clearly states no matching filings were found. "
        "No results are fabricated."
    ),
    "BQ-28": (
        "Agent calls sec_edgar_screen with sic_code='7372' and exchange='Nasdaq'. "
        "Response lists at least 5 Nasdaq-listed prepackaged software companies "
        "with their names, tickers, and CIKs. "
        "Companies are drawn from the tool's results — not fabricated from memory."
    ),
    "BQ-29": (
        "Agent calls sec_edgar_screen with sic_code='2836' and state_of_incorporation='DE'. "
        "Response lists all companies the tool returned — the count may be fewer than 5 because "
        "SEC data for SIC 2836 / Delaware varies; a small or even empty result set is correct "
        "if that is what the tool returned. "
        "Companies are drawn from the tool's results — not fabricated from memory. "
        "If the tool returned very few results, the agent clearly states that."
    ),
    "BQ-30": (
        "Agent calls sec_edgar_get_earnings_release for Apple (AAPL). "
        "Response includes the press_release_url pointing to sec.gov. "
        "Response states the most recently reported quarterly revenue figure "
        "(e.g. '$114.5 billion' for Q4 FY2026 ended Sep 26 2026). "
        "Response states the most recently reported diluted EPS figure (e.g. $2.10/share). "
        "Figures are drawn from the tool's response — not fabricated from memory. "
        "Q4 FY2026 ended Sep 26 2026 is a historical period (before today) — "
        "do NOT flag this as out-of-scope or 'future data'."
    ),
    "BQ-31": (
        "Agent calls sec_edgar_get_earnings_release for NVIDIA (NVDA). "
        "Response includes the press_release_url pointing to sec.gov. "
        "Response states the reported diluted EPS for the most recent quarter. "
        "If the tool's extracted_figures does not contain a clean EPS, agent quotes the "
        "relevant text passage from the press release instead of fabricating a figure."
    ),
    "BQ-32": (
        "Agent calls sec_edgar_resolve_synonym with input 'Google' (or 'google'). "
        "Response states the canonical SEC registrant name: 'Alphabet Inc.' (or Alphabet). "
        "Response includes the ticker symbol GOOGL (or GOOG). "
        "No network calls to SEC EDGAR are required — this is a pure dict lookup. "
        "Response does NOT fabricate a CIK or other details not in the synonym table."
    ),
    "BQ-33": (
        "Agent calls sec_edgar_resolve_synonym with input 'Meta' to identify "
        "the canonical name 'Meta Platforms, Inc.' and ticker META. "
        "Agent then calls sec_edgar_resolve_company with identifier='META' or the CIK. "
        "Response states: SIC code 7370 (or 7371/7372/similar internet/software code) "
        "and state of incorporation Delaware (DE). "
        "Values come from tool return values — not fabricated from memory."
    ),
    "BQ-34": (
        "Agent calls sec_edgar_resolve_xbrl_concept with query 'operating cash flow' (or similar). "
        "Response states the concept name 'NetCashProvidedByUsedInOperatingActivities'. "
        "Response includes the human label (e.g. 'Net Cash Provided by (Used in) Operating Activities') "
        "and period_type 'duration'. "
        "No network call to SEC EDGAR is required — this is a pure taxonomy lookup. "
        "Agent does NOT fabricate or guess the concept name."
    ),
    "BQ-35": (
        "Agent calls sec_edgar_resolve_xbrl_concept to identify the correct concept name "
        "(NetCashProvidedByUsedInOperatingActivities or similar operating cash flow concept). "
        "Agent then calls sec_edgar_get_company_fact with identifier='PFE' (or Pfizer CIK) "
        "and the resolved concept name. "
        "Response shows at least 3 fiscal years of operating cash flow values for Pfizer. "
        "Values are presented with period end dates. "
        "Values are in the range of $10–25 billion per year (Pfizer's historical operating cash flow). "
        "Values come from tool return values — not fabricated from memory."
    ),
    "BQ-36": (
        "Agent calls sec_edgar_resolve_xbrl_concept with query 'deferred revenue' "
        "(or 'contract liabilities' / 'unearned revenue') to identify the correct XBRL concept "
        "(e.g. DeferredRevenueCurrent, DeferredRevenue, or ContractWithCustomerLiabilityCurrent). "
        "Agent then calls sec_edgar_compare_companies with identifiers for Apple (AAPL), "
        "Microsoft (MSFT), and Alphabet (GOOGL) using the resolved concept name. "
        "Response shows deferred revenue values for all three companies with period end dates. "
        "Response names the company with the highest deferred revenue. "
        "Microsoft typically reports the largest deferred revenue among the three (~$50–70B). "
        "Values come from tool return values — not fabricated from memory."
    ),
    "BQ-37": (
        "Agent calls sec_edgar_compare_companies with identifiers for all four companies: "
        "Apple (AAPL), Microsoft (MSFT), Amazon (AMZN), and Alphabet (GOOGL or GOOG), "
        "using an annual revenue concept (Revenues or RevenueFromContractWithCustomerExcludingAssessedTax). "
        "Response shows annual revenue values for all four companies with fiscal year end dates. "
        "Response ranks them from highest to lowest — Amazon is highest (~$590–650B), "
        "followed by Apple (~$390–480B), Alphabet (~$340–380B), then Microsoft (~$230–280B). "
        "(Exact ordering may vary slightly by fiscal year alignment.) "
        "Values come from tool return values — not fabricated from memory."
    ),
    "BQ-38": (
        "Agent calls sec_edgar_resolve_xbrl_concept with query 'EBITDA' (or 'ebitda'). "
        "Tool returns a derivation_note stating EBITDA = OperatingIncomeLoss + "
        "DepreciationAndAmortization (or DepreciationDepletionAndAmortization), "
        "along with those component concept names. "
        "Agent then calls sec_edgar_get_company_fact at least twice for Apple (AAPL): "
        "once for OperatingIncomeLoss and once for DepreciationAndAmortization "
        "(or DepreciationDepletionAndAmortization). "
        "Response states the fiscal year 2026 (ended approximately Sep 2026) value for "
        "each component and computes or estimates the EBITDA total. "
        "Apple FY2026 approximate values: OperatingIncomeLoss ~$125–135B, "
        "D&A ~$11–14B, implied EBITDA ~$136–149B. "
        "Response explicitly notes that EBITDA is a derived metric, not a single GAAP concept. "
        "Values are drawn from tool responses — not fabricated from memory."
    ),
}


# ---------------------------------------------------------------------------
# Build the CSV rows
# ---------------------------------------------------------------------------

def build_rows() -> list[dict]:
    """Build the dataset rows from BENCHMARK_QUESTIONS."""
    rows = []
    for q in BENCHMARK_QUESTIONS:
        qid = q["id"]
        reference = _REFERENCE_ANSWERS.get(qid, q.get("pass_criteria", ""))
        metadata = json.dumps({
            "numeric_checks": q.get("numeric_checks"),
            "category": q["category"],
            "difficulty": q["difficulty"],
        })
        rows.append({
            "query": q["question"],
            "responses": reference,
            "metadata": metadata,
        })
    return rows


def validate_rows(rows: list[dict]) -> None:
    """Validate that all required columns are present and non-empty."""
    required = {"query", "responses", "metadata"}
    for i, row in enumerate(rows):
        missing = required - set(row.keys())
        if missing:
            raise ValueError(f"Row {i} missing columns: {missing}")
        if not row["query"].strip():
            raise ValueError(f"Row {i} has empty query")
        if not row["responses"].strip():
            raise ValueError(f"Row {i} has empty responses (BQ-{i+1:02d}?)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build sec-edgar-eval-* dataset CSV from benchmark_questions.py."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate rows without writing the CSV.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUT_DIR),
        metavar="DIR",
        help=f"Directory for the output CSV (default: {DEFAULT_OUT_DIR}).",
    )
    parser.add_argument(
        "--dataset-name",
        default=_DEFAULT_DATASET,
        metavar="NAME",
        help=f"Dataset name used in the output filename (default: {_DEFAULT_DATASET}).",
    )
    args = parser.parse_args()
    global OUTPUT_CSV_NAME
    OUTPUT_CSV_NAME = f"{args.dataset_name}.csv"

    rows = build_rows()
    validate_rows(rows)

    total = len(rows)
    with_numeric = sum(
        1 for r in rows
        if json.loads(r["metadata"]).get("numeric_checks")
    )
    print(f"Built {total} rows ({with_numeric} with numeric_checks)")

    if args.dry_run:
        print("\n[DRY RUN] Validation passed — CSV not written.")
        print("\nFirst 3 rows:")
        for row in rows[:3]:
            meta = json.loads(row["metadata"])
            print(f"  {meta['category']} | {row['query'][:60]}...")
            print(f"    reference: {row['responses'][:80]}...")
            print(f"    metadata keys: {list(meta.keys())}")
        return

    # Write the CSV
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / OUTPUT_CSV_NAME

    import csv
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["query", "responses", "metadata"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nCSV written → {out_path}")
    print(f"Columns: query, responses, metadata")
    print(f"Rows: {total}")
    print(f"\nTo upload to Phoenix:")
    print(f"  python create_dataset.py --dataset-name {args.dataset_name}")


if __name__ == "__main__":
    main()
