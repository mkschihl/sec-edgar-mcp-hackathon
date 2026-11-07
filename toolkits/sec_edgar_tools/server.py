"""SEC EDGAR MCP Toolkit — stdio transport.

Eight tools exposed to watsonx Orchestrate:
  - sec_edgar_search_companies      : search exchange-listed companies by partial name
  - sec_edgar_resolve_company       : resolve ticker or CIK to canonical company info
  - sec_edgar_get_recent_filings    : recent filing history with optional form-type filter
  - sec_edgar_get_company_fact      : XBRL concept time series for one company
  - sec_edgar_compare_companies     : compare one XBRL concept across multiple companies
  - sec_edgar_get_filing_metadata   : filing doc list and EDGAR URL for an accession number
  - sec_edgar_list_concepts         : discover available XBRL concepts for a company
  - sec_edgar_get_quarterly_facts   : quarterly XBRL observations (Q1/Q2/Q3/Q4) for one company

Orchestrate starts this file as a subprocess and communicates over stdin/stdout.
SEC APIs require no API key. Rate limit: 10 req/s per IP.
"""

from __future__ import annotations

import asyncio
from datetime import date, datetime
from typing import Annotated

import httpx
from fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Module-level constants and shared state
# ---------------------------------------------------------------------------

SEC_USER_AGENT = "Michael Schihl schihlm@sec.gov"

# In-memory cache: populated once per process lifetime on first call that
# needs it. Keys are uppercase tickers; values are raw SEC dict entries
# with keys: cik_str, ticker, title.
_TICKER_CACHE: dict[str, dict] = {}

# Secondary index keyed by zero-padded 10-digit CIK string
_CIK_CACHE: dict[str, dict] = {}

mcp = FastMCP(
    "sec_edgar_tools",
    instructions=(
        "SEC EDGAR toolkit with eight tools for authoritative SEC filing data.\n\n"
        "TOOL SELECTION GUIDE:\n"
        "- Find companies by partial name → sec_edgar_search_companies\n"
        "- Resolve a ticker or CIK to canonical info → sec_edgar_resolve_company\n"
        "- List recent 10-K/10-Q/8-K filings → sec_edgar_get_recent_filings\n"
        "- Fetch an XBRL annual concept time series → sec_edgar_get_company_fact\n"
        "- Fetch quarterly (Q1/Q2/Q3/Q4) observations → sec_edgar_get_quarterly_facts\n"
        "- Compare a concept across multiple companies → sec_edgar_compare_companies\n"
        "- Look up a specific filing by accession number → sec_edgar_get_filing_metadata\n"
        "- Discover what XBRL concepts a company reports → sec_edgar_list_concepts\n\n"
        "No authentication required. All tools return dicts; errors include "
        "an 'error' key and a 'hint' key with recovery guidance."
    ),
)

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _make_headers() -> dict[str, str]:
    return {"User-Agent": SEC_USER_AGENT, "Accept": "application/json"}


# Lazy process-level HTTP client — created on first use, reused for all
# subsequent calls within the same MCP server process.  Creating a new
# AsyncClient for every tool call incurs a fresh TCP/TLS handshake; reusing
# one client keeps connections warm across consecutive requests.
_http_client: httpx.AsyncClient | None = None


def _get_client() -> httpx.AsyncClient:
    """Return the process-level shared AsyncClient, creating it if needed."""
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(timeout=20.0, follow_redirects=False)
    return _http_client


async def _ensure_ticker_cache(client: httpx.AsyncClient) -> None:
    """Fetch company_tickers.json and populate _TICKER_CACHE / _CIK_CACHE if empty."""
    global _TICKER_CACHE, _CIK_CACHE
    if _TICKER_CACHE:
        return
    resp = await client.get(
        "https://www.sec.gov/files/company_tickers.json",
        headers=_make_headers(),
    )
    resp.raise_for_status()
    data = resp.json()
    for entry in data.values():
        ticker = entry["ticker"].upper()
        padded_cik = f"{int(entry['cik_str']):010d}"
        record = {
            "ticker": ticker,
            "cik_str": padded_cik,
            "title": entry["title"],
        }
        _TICKER_CACHE[ticker] = record
        _CIK_CACHE[padded_cik] = record


async def _resolve_identifier(identifier: str) -> tuple[str, str] | dict:
    """Resolve a ticker or CIK string to (padded_cik, ticker).

    Returns an error dict if the identifier cannot be resolved.
    The ticker cache is warmed as a side-effect on the first call.
    """
    client = _get_client()
    await _ensure_ticker_cache(client)
    id_clean = identifier.strip()
    if id_clean.isdigit():
        padded_cik = f"{int(id_clean):010d}"
        record = _CIK_CACHE.get(padded_cik)
        ticker = record["ticker"] if record else id_clean
        return padded_cik, ticker
    record = _TICKER_CACHE.get(id_clean.upper())
    if record is None:
        return {
            "error": f"'{identifier}' not found in the SEC exchange-listed company database.",
            "hint": "Check the ticker spelling or use sec_edgar_search_companies to find the correct identifier.",
        }
    return record["cik_str"], record["ticker"]


# Cache for submissions JSON (filing history) keyed by padded CIK.
# Avoids redundant HTTP round-trips when multiple tools query the same company
# in the same agent turn (e.g. get_recent_filings then get_filing_metadata).
_SUBMISSION_CACHE: dict[str, dict] = {}


async def _fetch_submission(cik: str) -> dict:
    """Fetch and cache the submissions JSON for a company by padded CIK."""
    if cik not in _SUBMISSION_CACHE:
        client = _get_client()
        resp = await client.get(
            f"https://data.sec.gov/submissions/CIK{cik}.json",
            headers=_make_headers(),
        )
        resp.raise_for_status()
        _SUBMISSION_CACHE[cik] = resp.json()
    return _SUBMISSION_CACHE[cik]


def _normalize_accession(raw: str) -> str:
    """Normalize an accession number to dashed format XXXXXXXXXX-YY-ZZZZZZ."""
    clean = raw.replace("-", "").strip()
    if len(clean) != 18:
        return raw  # pass through unmodified; caller will handle the error
    return f"{clean[:10]}-{clean[10:12]}-{clean[12:]}"


def _accession_to_path(accession_dashed: str) -> str:
    """Convert '0000320193-24-000123' → '000032019324000123' (path segment form)."""
    return accession_dashed.replace("-", "")


def _days_between(date_str_a: str, date_str_b: str) -> int:
    """Return absolute day difference between two ISO date strings."""
    try:
        a = datetime.strptime(date_str_a, "%Y-%m-%d").date()
        b = datetime.strptime(date_str_b, "%Y-%m-%d").date()
        return abs((a - b).days)
    except ValueError:
        return 0


def _check_comparability(results: list[dict], warnings: list[str]) -> None:
    """Append comparability warnings to the warnings list in-place.

    Checks for unit mismatches and fiscal-year-end misalignment (> 45 days).
    Extracted into a helper to isolate the logic and keep compare_companies readable.
    """
    if len(results) < 2:
        return
    units_seen = {r["unit"] for r in results}
    if len(units_seen) > 1:
        unit_list = ", ".join(f"{r['ticker']}={r['unit']}" for r in results)
        warnings.append(
            f"Unit mismatch — companies report in different units: {unit_list}. "
            "Values are not directly comparable."
        )
    for i in range(len(results)):
        for j in range(i + 1, len(results)):
            a, b = results[i], results[j]
            if a["period_end"] and b["period_end"]:
                days = _days_between(a["period_end"], b["period_end"])
                if days > 45:
                    warnings.append(
                        f"Fiscal year ends differ: {a['ticker']} ends {a['period_end']}, "
                        f"{b['ticker']} ends {b['period_end']} "
                        f"({days} days apart — not calendar-year aligned)."
                    )


# ---------------------------------------------------------------------------
# Tool 1 — Search companies by partial name
# ---------------------------------------------------------------------------

@mcp.tool(
    name="sec_edgar_search_companies",
    annotations={
        "title": "Search SEC Companies by Name",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def sec_edgar_search_companies(
    query: Annotated[str, "Partial company name to search for, e.g. 'apple', 'berkshire', 'general electric'. Case-insensitive substring match."],
    limit: Annotated[int, "Maximum number of matches to return. Default 10, max 50."] = 10,
) -> dict:
    """Search SEC-registered exchange-listed companies by partial name.

    Searches the SEC's company_tickers.json (covers ~10,000 exchange-listed
    companies). Performs a case-insensitive substring match on the company
    title. The ticker cache is populated on the first call and reused for
    all subsequent calls in the same process.

    Returns a dict with keys: query, match_count, matches (list of
    ticker/cik/name). On failure returns {"error": "...", "hint": "..."}.
    """
    query = query.strip()
    if not query:
        return {"error": "query must not be empty.", "hint": "Provide a partial company name such as 'apple' or 'berkshire'."}
    limit = max(1, min(limit, 50))
    try:
        await _ensure_ticker_cache(_get_client())
        query_lower = query.lower()
        matches = [
            {"ticker": v["ticker"], "cik": v["cik_str"], "name": v["title"]}
            for v in _TICKER_CACHE.values()
            if query_lower in v["title"].lower()
        ]
        matches = matches[:limit]
        return {"query": query, "match_count": len(matches), "matches": matches}
    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        return {"error": str(exc), "hint": "Could not fetch company list from SEC. Try again shortly."}


# ---------------------------------------------------------------------------
# Tool 2 — Resolve company ticker or CIK
# ---------------------------------------------------------------------------

@mcp.tool(
    name="sec_edgar_resolve_company",
    annotations={
        "title": "Resolve SEC Company",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def sec_edgar_resolve_company(
    identifier: Annotated[str, "Ticker symbol (e.g. 'AAPL') or numeric CIK string (e.g. '320193' or '0000320193')."],
) -> dict:
    """Resolve a company ticker symbol or CIK to canonical SEC company info.

    Looks up the company in the SEC's exchange-listed ticker file, then fetches
    the full submission metadata to return SIC code, industry description, and
    state of incorporation.

    Returns a dict with keys: cik, name, ticker, sic, sic_description,
    state_of_incorporation. On failure returns {"error": "...", "hint": "..."}.
    """
    identifier = identifier.strip()
    if not identifier:
        return {"error": "identifier must not be empty.", "hint": "Provide a ticker like 'AAPL' or a numeric CIK."}
    try:
        resolved = await _resolve_identifier(identifier)
        if isinstance(resolved, dict):
            return resolved
        padded_cik, ticker = resolved
        sub = await _fetch_submission(padded_cik)

        return {
            "cik": padded_cik,
            "name": sub.get("name", identifier),
            "ticker": ticker,
            "sic": sub.get("sic", ""),
            "sic_description": sub.get("sicDescription", ""),
            "state_of_incorporation": sub.get("stateOfIncorporation", ""),
        }
    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        return {"error": str(exc), "hint": "Check the identifier and try again. The SEC API may be temporarily unavailable."}


# ---------------------------------------------------------------------------
# Tool 3 — Get recent filings
# ---------------------------------------------------------------------------

@mcp.tool(
    name="sec_edgar_get_recent_filings",
    annotations={
        "title": "Get Recent SEC Filings",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def sec_edgar_get_recent_filings(
    identifier: Annotated[str, "Ticker symbol or CIK."],
    form_type: Annotated[str, "Form type filter, e.g. '10-K', '10-Q', '8-K'. Use empty string or 'all' to return all form types."] = "",
    limit: Annotated[int, "Maximum number of filings to return. Default 10, max 50."] = 10,
) -> dict:
    """Return recent SEC filings for a company, optionally filtered by form type.

    Fetches the submission history from data.sec.gov. When form_type is empty
    or 'all', returns all recent form types. Results are ordered most-recent
    first.

    Returns a dict with keys: company, cik, form_type_filter, filings (list).
    Each filing has: form, filing_date, report_date, accession_number,
    primary_document. On failure returns {"error": "...", "hint": "..."}.
    """
    limit = max(1, min(limit, 50))
    form_filter = "" if form_type.strip().lower() in ("", "all") else form_type.strip().upper()
    try:
        resolved = await _resolve_identifier(identifier)
        if isinstance(resolved, dict):
            return resolved
        padded_cik, _ = resolved

        sub = await _fetch_submission(padded_cik)
        company_name = sub.get("name", identifier)
        recent = sub.get("filings", {}).get("recent", {})
        forms = recent.get("form", [])
        filing_dates = recent.get("filingDate", [])
        report_dates = recent.get("reportDate", [])
        accessions = recent.get("accessionNumber", [])
        primary_docs = recent.get("primaryDocument", [])

        filings = []
        for form, fd, rd, acc, pdoc in zip(forms, filing_dates, report_dates, accessions, primary_docs):
            if form_filter and form.upper() != form_filter:
                continue
            filings.append({
                "form": form,
                "filing_date": fd,
                "report_date": rd,
                "accession_number": acc,
                "primary_document": pdoc,
            })
            if len(filings) >= limit:
                break

        return {
            "company": company_name,
            "cik": padded_cik,
            "form_type_filter": form_filter or "all",
            "filings": filings,
        }
    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        return {"error": str(exc), "hint": "Check the identifier and try again. The SEC API may be temporarily unavailable."}


# ---------------------------------------------------------------------------
# Tool 4 — Get company XBRL fact time series
# ---------------------------------------------------------------------------

@mcp.tool(
    name="sec_edgar_get_company_fact",
    annotations={
        "title": "Get XBRL Company Fact",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def sec_edgar_get_company_fact(
    identifier: Annotated[str, "Ticker symbol or CIK."],
    taxonomy: Annotated[str, "XBRL taxonomy, e.g. 'us-gaap' or 'dei'."],
    concept: Annotated[str, "XBRL concept tag, e.g. 'Revenues', 'NetIncomeLoss', 'Assets'."],
    limit: Annotated[int, "Maximum observations per unit type to return. Use 0 for all. Default 8."] = 8,
) -> dict:
    """Return the XBRL fact time series for a single concept and company.

    Fetches all XBRL-tagged values for the given taxonomy/concept from the
    SEC companyfacts endpoint. Returns all unit types as separate lists under
    a 'units' dict (e.g. {'USD': [...], 'shares': [...]}). When limit > 0,
    each list is trimmed to the last N entries (most recent last).

    Returns a dict with keys: company, cik, taxonomy, concept, label,
    description, units. On failure returns {"error": "...", "hint": "..."}.
    """
    try:
        resolved = await _resolve_identifier(identifier)
        if isinstance(resolved, dict):
            return resolved
        padded_cik, _ = resolved

        client = _get_client()
        resp = await client.get(
            f"https://data.sec.gov/api/xbrl/companyfacts/CIK{padded_cik}.json",
            headers=_make_headers(),
        )
        resp.raise_for_status()
        facts = resp.json()

        company_name = facts.get("entityName", identifier)
        taxonomy_data = facts.get("facts", {}).get(taxonomy)
        if taxonomy_data is None:
            available = list(facts.get("facts", {}).keys())
            return {
                "error": f"Taxonomy '{taxonomy}' not found for {company_name}.",
                "hint": f"Available taxonomies: {available}. Common values: 'us-gaap', 'dei'.",
            }

        concept_data = taxonomy_data.get(concept)
        if concept_data is None:
            sample = list(taxonomy_data.keys())[:10]
            return {
                "error": f"Concept '{concept}' not found in taxonomy '{taxonomy}' for {company_name}.",
                "hint": f"Sample available concepts (first 10): {sample}. Check spelling and capitalisation.",
            }

        label = concept_data.get("label", concept)
        description = concept_data.get("description", "")
        raw_units = concept_data.get("units", {})

        units_out: dict[str, list] = {
            unit_label: (list(obs)[-limit:] if limit > 0 else list(obs))
            for unit_label, obs in raw_units.items()
        }

        return {
            "company": company_name,
            "cik": padded_cik,
            "taxonomy": taxonomy,
            "concept": concept,
            "label": label,
            "description": description,
            "units": units_out,
        }
    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        return {"error": str(exc), "hint": "Check the identifier and concept, and try again."}


# ---------------------------------------------------------------------------
# Tool 5 — Compare XBRL concept across companies
# ---------------------------------------------------------------------------

@mcp.tool(
    name="sec_edgar_compare_companies",
    annotations={
        "title": "Compare XBRL Concept Across Companies",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def sec_edgar_compare_companies(
    identifiers: Annotated[list[str], "List of ticker symbols or CIKs to compare, e.g. ['AAPL', 'MSFT', 'GOOGL']."],
    taxonomy: Annotated[str, "XBRL taxonomy, e.g. 'us-gaap'."],
    concept: Annotated[str, "XBRL concept tag, e.g. 'Revenues', 'NetIncomeLoss'."],
) -> dict:
    """Compare one XBRL financial concept across multiple companies.

    For each company, finds the most recent full-year (FY) observation under
    the most prevalent unit type. Emits warnings when fiscal year ends differ
    by more than 45 days across companies, or when unit types are inconsistent.
    Companies are fetched sequentially with a small delay to respect the SEC
    10 req/s rate limit.

    Returns a dict with keys: concept, taxonomy, results (list), warnings (list).
    Each result has: company, cik, ticker, value, unit, period_end, fiscal_year,
    accession_number, form. On failure returns {"error": "...", "hint": "..."}.
    """
    if not identifiers:
        return {"error": "identifiers must be a non-empty list.", "hint": "Provide at least one ticker or CIK."}

    results = []
    warnings: list[str] = []

    try:
        client = _get_client()
        for idx, identifier in enumerate(identifiers):
            if idx > 0:
                await asyncio.sleep(0.12)  # respect SEC 10 req/s limit

            resolved = await _resolve_identifier(identifier)
            if isinstance(resolved, dict):
                warnings.append(f"'{identifier}' not found in the SEC database — skipped.")
                continue
            padded_cik, ticker = resolved

            try:
                resp = await client.get(
                    f"https://data.sec.gov/api/xbrl/companyfacts/CIK{padded_cik}.json",
                    headers=_make_headers(),
                )
                resp.raise_for_status()
                facts = resp.json()
            except (httpx.HTTPStatusError, httpx.RequestError) as exc:
                warnings.append(f"Could not fetch facts for '{identifier}': {exc} — skipped.")
                continue

            company_name = facts.get("entityName", identifier)
            concept_data = (
                facts.get("facts", {})
                .get(taxonomy, {})
                .get(concept)
            )
            if concept_data is None:
                warnings.append(f"{company_name}: concept '{taxonomy}/{concept}' not found — skipped.")
                continue

            raw_units = concept_data.get("units", {})

            # Pick the unit with the most observations
            best_unit = max(raw_units.keys(), key=lambda u: len(raw_units[u]), default=None)
            if best_unit is None:
                warnings.append(f"{company_name}: no unit data for '{concept}' — skipped.")
                continue

            observations = raw_units[best_unit]

            # Find the most recent full-year (fp == "FY") observation
            fy_obs = [o for o in observations if o.get("fp") == "FY" and o.get("form", "").startswith("10-")]
            if not fy_obs:
                # Fall back to any FY observation
                fy_obs = [o for o in observations if o.get("fp") == "FY"]
            if not fy_obs:
                warnings.append(f"{company_name}: no full-year (FY) observations found for '{concept}' — using most recent available.")
                fy_obs = observations

            latest = next(reversed(fy_obs))
            results.append({
                "company": company_name,
                "cik": padded_cik,
                "ticker": ticker,
                "value": latest.get("val"),
                "unit": best_unit,
                "period_end": latest.get("end", ""),
                "fiscal_year": latest.get("fy"),
                "accession_number": latest.get("accn", ""),
                "form": latest.get("form", ""),
            })

    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        return {"error": str(exc), "hint": "A network error occurred. Check identifiers and try again."}

    # --- Post-collection comparability checks ---
    _check_comparability(results, warnings)

    return {
        "concept": concept,
        "taxonomy": taxonomy,
        "results": results,
        "warnings": warnings,
    }


# ---------------------------------------------------------------------------
# Tool 6 — Get filing metadata by accession number
# ---------------------------------------------------------------------------

@mcp.tool(
    name="sec_edgar_get_filing_metadata",
    annotations={
        "title": "Get SEC Filing Metadata",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def sec_edgar_get_filing_metadata(
    identifier: Annotated[str, "Ticker symbol or CIK."],
    accession_number: Annotated[str, "Accession number, e.g. '0000320193-24-000123' or '000032019324000123' (dashes optional)."],
) -> dict:
    """Return metadata for a specific SEC filing identified by its accession number.

    Answers the question 'which filing supplied this number?' by looking up
    the accession number in the company's submission history and returning
    the form type, dates, primary document filename, and a direct EDGAR
    viewer URL.

    Returns a dict with keys: company, cik, accession_number, form,
    filing_date, report_date, primary_document, edgar_viewer_url.
    On failure returns {"error": "...", "hint": "..."}.
    """
    try:
        resolved = await _resolve_identifier(identifier)
        if isinstance(resolved, dict):
            return resolved
        padded_cik, _ = resolved

        sub = await _fetch_submission(padded_cik)
        company_name = sub.get("name", identifier)
        accession_dashed = _normalize_accession(accession_number.strip())
        accession_path = _accession_to_path(accession_dashed)

        recent = sub.get("filings", {}).get("recent", {})
        accessions = recent.get("accessionNumber", [])

        # Build a dict for O(1) lookup: normalised accession → list index
        accession_index = {
            _normalize_accession(acc): i for i, acc in enumerate(accessions)
        }
        idx = accession_index.get(accession_dashed)

        if idx is None:
            return {
                "error": f"Accession number '{accession_dashed}' not found in recent filings for {company_name}.",
                "hint": "Verify the accession number. Very old filings may not appear in the recent submissions list.",
            }

        forms = recent.get("form", [])
        filing_dates = recent.get("filingDate", [])
        report_dates = recent.get("reportDate", [])
        primary_docs = recent.get("primaryDocument", [])

        form = forms[idx] if idx < len(forms) else ""
        filing_date = filing_dates[idx] if idx < len(filing_dates) else ""
        report_date = report_dates[idx] if idx < len(report_dates) else ""
        primary_doc = primary_docs[idx] if idx < len(primary_docs) else ""

        # Numeric CIK (no leading zeros) is used in the EDGAR archive path
        numeric_cik = str(int(padded_cik))
        edgar_url = (
            f"https://www.sec.gov/Archives/edgar/data/{numeric_cik}/{accession_path}/{primary_doc}"
            if primary_doc else
            f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={padded_cik}&type={form}"
        )

        return {
            "company": company_name,
            "cik": padded_cik,
            "accession_number": accession_dashed,
            "form": form,
            "filing_date": filing_date,
            "report_date": report_date,
            "primary_document": primary_doc,
            "edgar_viewer_url": edgar_url,
        }
    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        return {"error": str(exc), "hint": "Check the identifier and accession number and try again."}


# ---------------------------------------------------------------------------
# Tool 7 — Discover available XBRL concepts for a company
# ---------------------------------------------------------------------------

@mcp.tool(
    name="sec_edgar_list_concepts",
    annotations={
        "title": "List XBRL Concepts for a Company",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def sec_edgar_list_concepts(
    identifier: Annotated[str, "Ticker symbol or CIK."],
    taxonomy: Annotated[str, "XBRL taxonomy to search. Default 'us-gaap'. Also common: 'dei'."] = "us-gaap",
    search: Annotated[str, "Optional substring filter on concept name or label, e.g. 'revenue', 'income', 'asset'. Case-insensitive. Leave empty to list all."] = "",
    limit: Annotated[int, "Maximum number of concepts to return. Default 50, max 200."] = 50,
) -> dict:
    """Discover what XBRL financial concepts a company reports under a given taxonomy.

    Fetches all available concept tags and their human-readable labels from the
    SEC companyfacts endpoint. Use the optional search parameter to filter by
    keyword (e.g. 'revenue' finds all revenue-related concepts). Results are
    sorted alphabetically by concept name.

    This tool is essential when a concept name is unknown or a prior tool call
    returned a 'concept not found' error — use it to find the correct XBRL tag.

    Returns a dict with keys: company, cik, taxonomy, search, total_matches,
    concepts (list of {concept, label}). On failure returns {"error": "...", "hint": "..."}.
    """
    limit = max(1, min(limit, 200))
    try:
        resolved = await _resolve_identifier(identifier)
        if isinstance(resolved, dict):
            return resolved
        padded_cik, _ = resolved

        client = _get_client()
        resp = await client.get(
            f"https://data.sec.gov/api/xbrl/companyfacts/CIK{padded_cik}.json",
            headers=_make_headers(),
        )
        resp.raise_for_status()
        facts = resp.json()

        company_name = facts.get("entityName", identifier)
        taxonomy_data = facts.get("facts", {}).get(taxonomy)
        if taxonomy_data is None:
            available = list(facts.get("facts", {}).keys())
            return {
                "error": f"Taxonomy '{taxonomy}' not found for {company_name}.",
                "hint": f"Available taxonomies: {available}. Common values: 'us-gaap', 'dei'.",
            }

        search_lower = search.strip().lower()
        concepts = []
        for concept_name, concept_data in taxonomy_data.items():
            # Some SEC entries have null labels — fall back to concept name
            label = concept_data.get("label") or concept_name
            if search_lower and (
                search_lower not in concept_name.lower()
                and search_lower not in label.lower()
            ):
                continue
            concepts.append({"concept": concept_name, "label": label})

        concepts.sort(key=lambda c: c["concept"])
        total_matches = len(concepts)
        concepts = concepts[:limit]

        return {
            "company": company_name,
            "cik": padded_cik,
            "taxonomy": taxonomy,
            "search": search.strip(),
            "total_matches": total_matches,
            "concepts": concepts,
        }
    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        return {"error": str(exc), "hint": "Check the identifier and try again."}


# ---------------------------------------------------------------------------
# Tool 8 — Quarterly XBRL observations (Q1/Q2/Q3/Q4)
# ---------------------------------------------------------------------------

@mcp.tool(
    name="sec_edgar_get_quarterly_facts",
    annotations={
        "title": "Get Quarterly XBRL Facts",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def sec_edgar_get_quarterly_facts(
    identifier: Annotated[str, "Ticker symbol or CIK."],
    taxonomy: Annotated[str, "XBRL taxonomy, e.g. 'us-gaap'."],
    concept: Annotated[str, "XBRL concept tag, e.g. 'Revenues', 'NetIncomeLoss'."],
    limit: Annotated[int, "Number of quarterly observations to return, most recent first. Default 8, max 40."] = 8,
) -> dict:
    """Return quarterly (Q1/Q2/Q3/Q4) XBRL observations for a single concept and company.

    Filters to observations where the fiscal period (fp) is Q1, Q2, Q3, or Q4
    and the source form is a 10-Q filing. Results are returned most-recent-first.
    Each observation includes a human-readable period_label (e.g. 'Q3 FY2025').

    Use this tool when the user asks about quarterly trends, specific quarters,
    or wants to compare quarters. For annual (full-year) data, use
    sec_edgar_get_company_fact instead.

    Returns a dict with keys: company, cik, taxonomy, concept, unit, label,
    observations (list), note. On failure returns {"error": "...", "hint": "..."}.
    """
    limit = max(1, min(limit, 40))
    try:
        resolved = await _resolve_identifier(identifier)
        if isinstance(resolved, dict):
            return resolved
        padded_cik, _ = resolved

        client = _get_client()
        resp = await client.get(
            f"https://data.sec.gov/api/xbrl/companyfacts/CIK{padded_cik}.json",
            headers=_make_headers(),
        )
        resp.raise_for_status()
        facts = resp.json()

        company_name = facts.get("entityName", identifier)
        taxonomy_data = facts.get("facts", {}).get(taxonomy)
        if taxonomy_data is None:
            available = list(facts.get("facts", {}).keys())
            return {
                "error": f"Taxonomy '{taxonomy}' not found for {company_name}.",
                "hint": f"Available taxonomies: {available}.",
            }

        concept_data = taxonomy_data.get(concept)
        if concept_data is None:
            sample = list(taxonomy_data.keys())[:10]
            return {
                "error": f"Concept '{concept}' not found in taxonomy '{taxonomy}' for {company_name}.",
                "hint": f"Sample available concepts (first 10): {sample}. Use sec_edgar_list_concepts to search.",
            }

        label = concept_data.get("label", concept)
        raw_units = concept_data.get("units", {})

        # Pick the unit with the most observations (same logic as compare_companies)
        best_unit = max(raw_units.keys(), key=lambda u: len(raw_units[u]), default=None)
        if best_unit is None:
            return {
                "error": f"No unit data found for concept '{concept}' for {company_name}.",
                "hint": "The concept may exist but have no numeric observations.",
            }

        all_obs = raw_units[best_unit]

        # Filter to quarterly observations from 10-Q filings
        quarterly_fps = {"Q1", "Q2", "Q3", "Q4"}
        quarterly_obs = [
            o for o in all_obs
            if o.get("fp") in quarterly_fps and o.get("form", "").startswith("10-Q")
        ]

        # Sort most-recent first by period end date
        quarterly_obs.sort(key=lambda o: o.get("end", ""), reverse=True)

        note = ""
        if len(quarterly_obs) == 0:
            # Fall back to any quarterly fp even if not from 10-Q
            quarterly_obs = [o for o in all_obs if o.get("fp") in quarterly_fps]
            quarterly_obs.sort(key=lambda o: o.get("end", ""), reverse=True)
            if quarterly_obs:
                note = "Quarterly data sourced from non-10-Q filings (e.g. 10-K restated quarters)."
            else:
                return {
                    "error": f"No quarterly (Q1/Q2/Q3/Q4) observations found for '{concept}' for {company_name}.",
                    "hint": "This concept may only be reported annually. Use sec_edgar_get_company_fact for annual data.",
                }
        elif len(quarterly_obs) < limit:
            note = f"Only {len(quarterly_obs)} quarterly observations available; fewer than the requested {limit}."

        # Slice and annotate with human-readable period label
        sliced = quarterly_obs[:limit]
        observations = []
        for o in sliced:
            fp = o.get("fp", "")
            fy = o.get("fy")
            period_label = f"{fp} FY{fy}" if fp and fy else fp
            observations.append({
                "period_label": period_label,
                "end": o.get("end", ""),
                "val": o.get("val"),
                "form": o.get("form", ""),
                "accn": o.get("accn", ""),
                "fy": fy,
                "fp": fp,
            })

        return {
            "company": company_name,
            "cik": padded_cik,
            "taxonomy": taxonomy,
            "concept": concept,
            "unit": best_unit,
            "label": label,
            "observations": observations,
            "note": note,
        }
    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        return {"error": str(exc), "hint": "Check the identifier and concept, and try again."}


if __name__ == "__main__":
    mcp.run(transport="stdio")
