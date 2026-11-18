"""SEC EDGAR MCP Toolkit — stdio transport.

Eight tools exposed to watsonx Orchestrate:
  - sec_edgar_search_companies      : search all SEC-registered companies by partial name
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
import re
from datetime import date, datetime
from typing import Annotated
from urllib.parse import quote as _url_quote

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

# Revenue concept candidates, in fallback priority order.
# When the requested concept is any of these, all candidates present in the
# company's facts are evaluated; the one whose most-recent period_end is
# newest wins (broader total).  Ties broken by larger value at that date.
REVENUE_CANDIDATES = [
    "Revenues",
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "SalesRevenueNet",
    "RevenueFromContractWithCustomerIncludingAssessedTax",
]

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
#
# trust_env=False: prevents httpx from picking up HTTP_PROXY / HTTPS_PROXY
# environment variables injected by container runtimes (e.g. Code Engine,
# corporate proxies).  The SEC public APIs require direct outbound access;
# routing through a proxy breaks them.
#
# follow_redirects=True: SEC APIs occasionally redirect http:// → https://
# or move endpoints; following silently is correct here.
_http_client: httpx.AsyncClient | None = None
_http_client_loop: asyncio.AbstractEventLoop | None = None


def _get_client() -> httpx.AsyncClient:
    """Return a shared AsyncClient bound to the current running event loop.

    When a script calls asyncio.run() multiple times (e.g. in tests), each call
    creates a new event loop and closes the previous one.  An AsyncClient created
    on the first loop raises "Event loop is closed" on the second loop.  We detect
    this by storing the loop the client was created on and rebuilding the client
    whenever the current loop differs or the stored loop is closed.

    Production servers run a single persistent loop, so this check is effectively
    free there (one pointer comparison per call).
    """
    global _http_client, _http_client_loop
    try:
        current_loop = asyncio.get_running_loop()
    except RuntimeError:
        current_loop = None
    # Rebuild if: no client yet, loop mismatch, or stored loop has been closed.
    if (
        _http_client is None
        or _http_client_loop is None
        or _http_client_loop is not current_loop
        or (_http_client_loop is not None and _http_client_loop.is_closed())
    ):
        _http_client = httpx.AsyncClient(
            timeout=20.0,
            follow_redirects=True,
            trust_env=False,
        )
        _http_client_loop = current_loop
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


# ---------------------------------------------------------------------------
# EFTS all-filers name search
# ---------------------------------------------------------------------------

_DISPLAY_NAME_PATTERN = re.compile(
    r"^(.*?)\s*(?:\(([^()]+)\)\s+)?\(CIK\s+(\d+)\)\s*$"
)


def _parse_display_name(raw: str) -> dict | None:
    """Parse an EFTS display_name string into {name, ticker, cik}.

    Display names look like:
        "EXXON MOBIL CORP  (XOM)  (CIK 0000034088)"
        "UNITED PETROLEUM CORP  (CIK 0000082925)"
        "GLOBAL PARTNERS LP  (GLP, GLP-PB)  (CIK 0001323468)"
    """
    m = _DISPLAY_NAME_PATTERN.match(raw.strip())
    if not m:
        return None
    name = m.group(1).strip()
    tickers_raw = m.group(2) or ""
    # Keep only plain ticker tokens (letters/digits/hyphens, no spaces)
    tickers = [t.strip() for t in tickers_raw.split(",") if re.match(r"^[A-Z0-9\-]+$", t.strip())]
    primary_ticker = tickers[0] if tickers else ""
    cik = f"{int(m.group(3)):010d}"
    return {"name": name, "ticker": primary_ticker, "cik": cik}


# Sentinel returned by _search_all_filers when the EFTS call fails entirely,
# so the caller can surface a warning without treating it as an empty result.
_EFTS_UNAVAILABLE = object()


async def _search_all_filers(
    query: str, limit: int, client: httpx.AsyncClient
) -> list[dict] | object:
    """Search ALL SEC-registered filers by company name using the EDGAR full-text
    search index, filtered to entities that have filed a 10-K in the last 730 days.

    This covers companies like EXXON MOBIL CORP whose operating entity is not
    in company_tickers.json (exchange-listed only) because the ticker is registered
    to a holding company shell.

    Returns a list of {name, ticker, cik, source} dicts on success, or the
    module-level sentinel _EFTS_UNAVAILABLE if the HTTP call fails entirely.
    """
    from datetime import timedelta
    startdt = (date.today() - timedelta(days=730)).isoformat()
    encoded = _url_quote(f'"{query}"')
    url = (
        f"https://efts.sec.gov/LATEST/search-index"
        f"?q={encoded}&forms=10-K&dateRange=custom&startdt={startdt}"
    )
    try:
        resp = await client.get(url, headers=_make_headers(), timeout=10.0)
        resp.raise_for_status()
    except (httpx.HTTPStatusError, httpx.RequestError):
        return _EFTS_UNAVAILABLE

    hits = resp.json().get("hits", {}).get("hits", [])
    seen: dict[str, dict] = {}
    query_lower = query.lower()
    for hit in hits:
        src = hit.get("_source", {})
        for cik, raw_name in zip(src.get("ciks", []), src.get("display_names", [])):
            if cik in seen:
                continue
            parsed = _parse_display_name(raw_name)
            if parsed is None:
                continue
            # Only keep names that contain the query as a substring
            if query_lower not in parsed["name"].lower():
                continue
            seen[cik] = {**parsed, "source": "all_filers"}
            if len(seen) >= limit:
                break
        if len(seen) >= limit:
            break

    return list(seen.values())


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


def _fiscal_year_for(end: str, fye_mmdd: str | None) -> int:
    """Fiscal year a period belongs to, using the company's fiscalYearEnd ("MMDD")
    from the submissions JSON.  Handles 52/53-week years (±7 days)."""
    from datetime import timedelta
    e = datetime.strptime(end, "%Y-%m-%d").date()
    if not fye_mmdd or len(fye_mmdd) != 4:
        return e.year
    mm, dd = int(fye_mmdd[:2]), int(fye_mmdd[2:])
    dd = min(dd, 28) if mm == 2 else dd
    this_fye = date(e.year, mm, dd)
    prev_fye = date(e.year - 1, mm, dd)
    if e <= prev_fye + timedelta(days=7):
        return e.year - 1
    if e > this_fye + timedelta(days=7):
        return e.year + 1
    return e.year


def _duration_days(o: dict) -> int | None:
    """Return (end - start).days for a flow observation, or None for instant facts."""
    start = o.get("start")
    end = o.get("end")
    if not start or not end:
        return None
    try:
        s = datetime.strptime(start, "%Y-%m-%d").date()
        e = datetime.strptime(end, "%Y-%m-%d").date()
        return (e - s).days
    except ValueError:
        return None


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
        "openWorldHint": True,
    },
)
async def sec_edgar_search_companies(
    query: Annotated[str, "Partial company name to search for, e.g. 'apple', 'berkshire', 'general electric'. Case-insensitive substring match."],
    limit: Annotated[int, "Maximum number of matches to return. Default 10, max 50."] = 10,
) -> dict:
    """Search SEC-registered companies by partial name.

    Two-pass search run concurrently:
    1. Primary: searches company_tickers.json (~10,000 exchange-listed companies).
    2. All-filers: queries the EDGAR full-text search index filtered to companies
       that have filed a 10-K in the last 730 days. This surfaces operating entities
       whose ticker is registered to a holding-company shell and therefore absent from
       the exchange-listed file (e.g. EXXON MOBIL CORP).

    Each match includes:
      source         — "exchange_listed" or "all_filers"
      has_recent_10k — true if the entity has a 10-K in the last 730 days

    Results are sorted so has_recent_10k == true comes first, then by original order.
    At least max(limit, 5) matches are returned, so a limit=1 call never hides the
    operating company behind a holding shell.

    If the all-filers EFTS search is temporarily unavailable, the response includes a
    "warnings" list noting the degraded state.

    After choosing a company from search results, pass its CIK (not ticker) to other
    tools — some tickers map to a holding entity rather than the operating company.

    Returns a dict with keys: query, match_count, matches, warnings.
    On failure returns {"error": "...", "hint": "..."}.
    """
    query = query.strip()
    if not query:
        return {"error": "query must not be empty.", "hint": "Provide a partial company name such as 'apple' or 'berkshire'."}
    limit = max(1, min(limit, 50))
    effective_limit = max(limit, 5)
    client = _get_client()
    warnings: list[str] = []
    try:
        # Warm the ticker cache, then run both passes concurrently.
        await _ensure_ticker_cache(client)
        query_lower = query.lower()
        primary_all = [
            {"ticker": v["ticker"], "cik": v["cik_str"], "name": v["title"], "source": "exchange_listed"}
            for v in _TICKER_CACHE.values()
            if query_lower in v["title"].lower()
        ]

        # Run the all-filers search concurrently with building primary list (already done above).
        fallback_result = await _search_all_filers(query, effective_limit, client)

        efts_failed = fallback_result is _EFTS_UNAVAILABLE
        if efts_failed:
            warnings.append(
                "Full-filer search unavailable; results may omit operating entities."
            )
            fallback: list[dict] = []
        else:
            fallback = fallback_result  # type: ignore[assignment]

        # Build a set of CIKs that have a recent 10-K (from the all-filers results).
        recent_10k_ciks = {m["cik"] for m in fallback}

        # Annotate primary matches with has_recent_10k.
        for m in primary_all:
            m["has_recent_10k"] = m["cik"] in recent_10k_ciks

        # Annotate all-filers matches (always has_recent_10k by definition).
        for m in fallback:
            m["has_recent_10k"] = True

        # Merge: primary first, then fallback entries not already in primary.
        primary_ciks = {m["cik"] for m in primary_all}
        extra = [m for m in fallback if m["cik"] not in primary_ciks]
        merged = primary_all + extra

        # Sort: has_recent_10k == True first, preserve original order within each tier.
        merged.sort(key=lambda m: (0 if m["has_recent_10k"] else 1))

        matches = merged[:effective_limit]
        return {
            "query": query,
            "match_count": len(matches),
            "matches": matches,
            "warnings": warnings,
        }
    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        return {"error": str(exc), "hint": "Could not fetch company list from SEC. Try again shortly."}
    except Exception as exc:
        return {"error": f"Unexpected error: {type(exc).__name__}: {exc}",
                "hint": "Report this to the toolkit maintainer; do not retry with the same arguments."}


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
    identifier: Annotated[str, "Accepts a ticker or CIK. After choosing a company from search results, pass its CIK, because some tickers map to a holding entity. E.g. 'AAPL' or '0000320193'."],
) -> dict:
    """Resolve a company ticker symbol or CIK to canonical SEC company info.

    Looks up the company in the SEC's exchange-listed ticker file, then fetches
    the full submission metadata to return SIC code, industry description, state
    of incorporation, and recent filing activity.

    New fields:
      latest_10k_date  — most recent 10-K filingDate, or null
      latest_10q_date  — most recent 10-Q filingDate, or null
      is_active_filer  — true if either date is within the last 730 days

    If is_active_filer is false, a "warning" key is added advising the caller to
    search for the operating entity by legal name and use the CIK of the match
    where has_recent_10k is true.

    Returns a dict with keys: cik, name, ticker, sic, sic_description,
    state_of_incorporation, latest_10k_date, latest_10q_date, is_active_filer.
    On failure returns {"error": "...", "hint": "..."}.
    """
    from datetime import timedelta
    identifier = identifier.strip()
    if not identifier:
        return {"error": "identifier must not be empty.", "hint": "Provide a ticker like 'AAPL' or a numeric CIK."}
    try:
        resolved = await _resolve_identifier(identifier)
        if isinstance(resolved, dict):
            return resolved
        padded_cik, ticker = resolved
        sub = await _fetch_submission(padded_cik)

        # Scan recent filings for latest 10-K and 10-Q dates.
        recent = sub.get("filings", {}).get("recent", {})
        forms = recent.get("form", [])
        filing_dates = recent.get("filingDate", [])
        latest_10k: str | None = None
        latest_10q: str | None = None
        for form, fd in zip(forms, filing_dates):
            if form.upper() == "10-K" and latest_10k is None:
                latest_10k = fd
            elif form.upper() == "10-Q" and latest_10q is None:
                latest_10q = fd
            if latest_10k and latest_10q:
                break

        cutoff = (date.today() - timedelta(days=730)).isoformat()
        is_active = bool(
            (latest_10k and latest_10k >= cutoff)
            or (latest_10q and latest_10q >= cutoff)
        )

        result: dict = {
            "cik": padded_cik,
            "name": sub.get("name", identifier),
            "ticker": ticker,
            "sic": sub.get("sic", ""),
            "sic_description": sub.get("sicDescription", ""),
            "state_of_incorporation": sub.get("stateOfIncorporation", ""),
            "latest_10k_date": latest_10k,
            "latest_10q_date": latest_10q,
            "is_active_filer": is_active,
        }
        if not is_active:
            result["warning"] = (
                "This entity has no recent 10-K/10-Q. It may be a holding shell. "
                "Call sec_edgar_search_companies with the full legal company name and "
                "use the CIK of the match where has_recent_10k is true."
            )
        elif latest_10k is None and latest_10q is not None and latest_10q >= cutoff:
            result["warning"] = (
                "This entity files quarterly reports but has no 10-K yet (possibly a "
                "newly formed holding company). For annual reports, check search results "
                "for a related entity where has_recent_10k is true."
            )
        return result
    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        return {"error": str(exc), "hint": "Check the identifier and try again. The SEC API may be temporarily unavailable."}
    except Exception as exc:
        return {"error": f"Unexpected error: {type(exc).__name__}: {exc}",
                "hint": "Report this to the toolkit maintainer; do not retry with the same arguments."}


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
    identifier: Annotated[str, "Accepts a ticker or CIK. After choosing a company from search results, pass its CIK, because some tickers map to a holding entity."],
    form_type: Annotated[str, "Form type filter, e.g. '10-K', '10-Q', '8-K'. Use empty string or 'all' to return all form types."] = "",
    limit: Annotated[int, "Maximum number of filings to return. Default 10, max 50."] = 10,
) -> dict:
    """Return recent SEC filings for a company, optionally filtered by form type.

    Fetches the submission history from data.sec.gov. When form_type is empty
    or 'all', returns all recent form types. Results are ordered most-recent
    first.

    When form_type is '10-K' or '10-Q' and no filings are found, adds a
    "warning" key advising the caller to verify that the correct operating-entity
    CIK was used (not a holding-company shell).

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

        result: dict = {
            "company": company_name,
            "cik": padded_cik,
            "form_type_filter": form_filter or "all",
            "filings": filings,
        }
        # Warn when a 10-K/10-Q filter returns nothing — likely a holding-shell CIK.
        if not filings and form_filter in ("10-K", "10-Q"):
            result["warning"] = (
                "This entity has no recent 10-K/10-Q. It may be a holding shell. "
                "Call sec_edgar_search_companies with the full legal company name and "
                "use the CIK of the match where has_recent_10k is true."
            )
        return result
    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        return {"error": str(exc), "hint": "Check the identifier and try again. The SEC API may be temporarily unavailable."}
    except Exception as exc:
        return {"error": f"Unexpected error: {type(exc).__name__}: {exc}",
                "hint": "Report this to the toolkit maintainer; do not retry with the same arguments."}


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
    identifier: Annotated[str, "Accepts a ticker or CIK. After choosing a company from search results, pass its CIK, because some tickers map to a holding entity."],
    taxonomy: Annotated[str, "XBRL taxonomy, e.g. 'us-gaap' or 'dei'."],
    concept: Annotated[str, "XBRL concept tag, e.g. 'Revenues', 'NetIncomeLoss', 'Assets'."],
    limit: Annotated[int, "Maximum observations per unit type to return. Use 0 for all. Default 8."] = 8,
) -> dict:
    """Return the XBRL fact time series for a single concept and company.

    Fetches all full-year (FY) XBRL-tagged values for the given taxonomy/concept
    from the SEC companyfacts endpoint. Returns all unit types as separate lists
    under a 'units' dict (e.g. {'USD': [...], 'shares': [...]}).  When limit > 0,
    each list is trimmed to the last N entries (most recent last).

    Each row is one fiscal year. Label rows with fiscal_year / fiscal_year_end.
    filing_fiscal_year is the fiscal year of the filing that supplied the value
    and must NOT be used as the period label.  If recast is true, the value was
    revised in a later filing; as_originally_filed shows the first value.

    Each row also includes filing_index_url — the deterministic EDGAR archive
    index page for that filing (no extra HTTP call needed):
      https://www.sec.gov/Archives/edgar/data/<cik>/<accession_no_dashes>/

    Non-FY observations (Q1/Q2/Q3) are excluded; use sec_edgar_get_quarterly_facts
    for quarterly data.

    Returns a dict with keys: company, cik, taxonomy, concept, label,
    description, units. On failure returns {"error": "...", "hint": "..."}.
    """
    try:
        resolved = await _resolve_identifier(identifier)
        if isinstance(resolved, dict):
            return resolved
        padded_cik, _ = resolved

        client = _get_client()
        # Fetch submission and companyfacts concurrently to reduce latency.
        sub, resp = await asyncio.gather(
            _fetch_submission(padded_cik),
            client.get(
                f"https://data.sec.gov/api/xbrl/companyfacts/CIK{padded_cik}.json",
                headers=_make_headers(),
            ),
        )
        resp.raise_for_status()
        facts = resp.json()
        fye_mmdd: str | None = sub.get("fiscalYearEnd")

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

        def _dedup_fy(obs_list: list) -> list:
            """Keep only fp=='FY' observations with annual duration (350-380 days)
            or no start (instant/balance-sheet facts).  Group by 'end' date;
            within each group pick latest 'filed' as the winner; record the
            earliest-filed value as as_originally_filed and flag recast if different.
            Returns rows with renamed/additional keys; no raw 'fy' key."""
            # Pass 1: collect FY observations that satisfy duration filter
            candidates: list[dict] = []
            for o in obs_list:
                if o.get("fp") != "FY":
                    continue
                dur = _duration_days(o)
                if dur is not None and not (350 <= dur <= 380):
                    continue
                candidates.append(o)

            # Pass 2: group by end date; track winner (latest filed) and
            # earliest filed value (as_originally_filed)
            groups: dict[str, dict] = {}   # end → {"winner": o, "first_val": val, "first_filed": filed}
            for o in candidates:
                end = o.get("end", "")
                filed = o.get("filed", "")
                val = o.get("val")
                if end not in groups:
                    groups[end] = {"winner": o, "first_val": val, "first_filed": filed}
                else:
                    g = groups[end]
                    # update winner if this filing is later
                    if filed > g["winner"].get("filed", ""):
                        g["winner"] = o
                    # update earliest if this filing is earlier
                    if filed < g["first_filed"]:
                        g["first_val"] = val
                        g["first_filed"] = filed

            # Pass 3: build output rows
            rows: list[dict] = []
            for end, g in sorted(groups.items()):
                o = g["winner"]
                orig_val = g["first_val"]
                winner_val = o.get("val")
                try:
                    fy = _fiscal_year_for(end, fye_mmdd)
                except Exception:
                    fy = o.get("fy") or datetime.strptime(end, "%Y-%m-%d").year
                accn = o.get("accn", "")
                rows.append({
                    "fiscal_year": fy,
                    "fiscal_year_end": end,
                    "period_start": o.get("start") or None,
                    "value": winner_val,
                    "as_originally_filed": orig_val,
                    "recast": winner_val != orig_val,
                    "form": o.get("form", ""),
                    "filed": o.get("filed", ""),
                    "accession_number": accn,
                    "filing_index_url": (
                        f"https://www.sec.gov/Archives/edgar/data/"
                        f"{int(padded_cik)}/{accn.replace('-', '')}/"
                        if accn else ""
                    ),
                    "filing_fiscal_year": o.get("fy"),
                })
            return rows

        # If the requested concept is a revenue candidate, evaluate all
        # candidates present in this company's facts and pick the one whose
        # most-recent FY period_end is newest (ties → larger value).
        effective_concept = concept
        concept_note: str | None = None
        if concept in REVENUE_CANDIDATES:
            best_cname: str | None = None
            best_end: str = ""
            best_val: float | int | None = None
            for cname in REVENUE_CANDIDATES:
                cdata = taxonomy_data.get(cname)
                if cdata is None:
                    continue
                for unit_obs in cdata.get("units", {}).values():
                    for o in unit_obs:
                        if o.get("fp") != "FY":
                            continue
                        dur = _duration_days(o)
                        if dur is not None and not (350 <= dur <= 380):
                            continue
                        end = o.get("end", "")
                        val = o.get("val")
                        if end > best_end or (
                            end == best_end
                            and val is not None
                            and (best_val is None or val > best_val)
                        ):
                            best_end = end
                            best_val = val
                            best_cname = cname
            if best_cname and best_cname != concept:
                effective_concept = best_cname
                new_data = taxonomy_data[best_cname]
                label = new_data.get("label", best_cname)
                description = new_data.get("description", "")
                raw_units = new_data.get("units", {})
                concept_note = (
                    f"Requested '{concept}' but '{best_cname}' has more recent data "
                    f"(most recent period_end {best_end}); using '{best_cname}'."
                )

        units_out: dict[str, list] = {}
        for unit_label, obs in raw_units.items():
            cleaned = _dedup_fy(list(obs))
            units_out[unit_label] = cleaned[-limit:] if limit > 0 else cleaned

        result_dict: dict = {
            "company": company_name,
            "cik": padded_cik,
            "taxonomy": taxonomy,
            "concept": effective_concept,
            "label": label,
            "description": description,
            "units": units_out,
        }
        if concept_note:
            result_dict["concept_note"] = concept_note
        return result_dict
    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        return {"error": str(exc), "hint": "Check the identifier and concept, and try again."}
    except Exception as exc:
        return {"error": f"Unexpected error: {type(exc).__name__}: {exc}",
                "hint": "Report this to the toolkit maintainer; do not retry with the same arguments."}


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

    Each result row includes filing_index_url — the deterministic EDGAR archive
    index page for that filing (no extra HTTP call needed):
      https://www.sec.gov/Archives/edgar/data/<cik>/<accession_no_dashes>/

    Returns a dict with keys: concept, taxonomy, results (list), warnings (list).
    Each result has: company, cik, ticker, concept, value, unit, period_end,
    fiscal_year, accession_number, filing_index_url, form.
    On failure returns {"error": "...", "hint": "..."}.
    """
    if not identifiers:
        return {"error": "identifiers must be a non-empty list.", "hint": "Provide at least one ticker or CIK."}

    results = []
    warnings: list[str] = []

    try:
        client = _get_client()
        today = date.today()
        for idx, identifier in enumerate(identifiers):
            if idx > 0:
                await asyncio.sleep(0.12)  # respect SEC 10 req/s limit

            resolved = await _resolve_identifier(identifier)
            if isinstance(resolved, dict):
                warnings.append(f"'{identifier}' not found in the SEC database — skipped.")
                continue
            padded_cik, ticker = resolved

            try:
                sub = await _fetch_submission(padded_cik)
                resp = await client.get(
                    f"https://data.sec.gov/api/xbrl/companyfacts/CIK{padded_cik}.json",
                    headers=_make_headers(),
                )
                resp.raise_for_status()
                facts = resp.json()
            except (httpx.HTTPStatusError, httpx.RequestError) as exc:
                warnings.append(f"Could not fetch facts for '{identifier}': {exc} — skipped.")
                continue

            # Prefer canonical name from submissions JSON over entityName
            company_name = sub.get("name") or facts.get("entityName", identifier)
            fye_mmdd: str | None = sub.get("fiscalYearEnd")

            taxonomy_data = facts.get("facts", {}).get(taxonomy, {})
            concept_data = taxonomy_data.get(concept)
            if concept_data is None and concept not in REVENUE_CANDIDATES:
                warnings.append(f"{company_name}: concept '{taxonomy}/{concept}' not found — skipped.")
                continue

            # Revenue-candidate selection: pick the candidate whose most-recent
            # FY period_end is newest; ties → larger value.
            effective_concept_cc = concept
            concept_note_cc: str | None = None
            if concept in REVENUE_CANDIDATES:
                best_cname_cc: str | None = None
                best_end_cc: str = ""
                best_val_cc: float | int | None = None
                for cname in REVENUE_CANDIDATES:
                    cdata = taxonomy_data.get(cname)
                    if cdata is None:
                        continue
                    for unit_obs in cdata.get("units", {}).values():
                        for o in unit_obs:
                            if o.get("fp") != "FY":
                                continue
                            dur = _duration_days(o)
                            if dur is not None and not (350 <= dur <= 380):
                                continue
                            end = o.get("end", "")
                            val = o.get("val")
                            if end > best_end_cc or (
                                end == best_end_cc
                                and val is not None
                                and (best_val_cc is None or val > best_val_cc)
                            ):
                                best_end_cc = end
                                best_val_cc = val
                                best_cname_cc = cname
                if best_cname_cc is None:
                    warnings.append(f"{company_name}: no revenue concept found — skipped.")
                    continue
                if best_cname_cc != concept:
                    concept_note_cc = (
                        f"Requested '{concept}' but '{best_cname_cc}' has more recent data "
                        f"(period_end {best_end_cc}); using '{best_cname_cc}'."
                    )
                effective_concept_cc = best_cname_cc
                concept_data = taxonomy_data[best_cname_cc]

            raw_units = concept_data.get("units", {})

            # Pick the unit with the most observations
            best_unit = max(raw_units.keys(), key=lambda u: len(raw_units[u]), default=None)
            if best_unit is None:
                warnings.append(f"{company_name}: no unit data for '{effective_concept_cc}' — skipped.")
                continue

            observations = raw_units[best_unit]

            # Filter to FY observations with annual duration or instant (no start)
            fy_obs = []
            for o in observations:
                if o.get("fp") != "FY":
                    continue
                dur = _duration_days(o)
                if dur is not None and not (350 <= dur <= 380):
                    continue
                fy_obs.append(o)

            if not fy_obs:
                warnings.append(f"{company_name}: no full-year (FY) annual observations found for '{effective_concept_cc}' — skipped.")
                continue

            # Pick the observation with the maximum period end date; break ties by latest filed
            best = max(fy_obs, key=lambda o: (o.get("end", ""), o.get("filed", "")))

            period_end = best.get("end", "")
            try:
                fiscal_year = _fiscal_year_for(period_end, fye_mmdd)
            except Exception:
                fiscal_year = best.get("fy")

            # Staleness warning: period_end more than 548 days before today
            if period_end:
                try:
                    pe_date = datetime.strptime(period_end, "%Y-%m-%d").date()
                    if (today - pe_date).days > 548:
                        warnings.append(
                            f"{ticker}: most recent value for {effective_concept_cc} is from "
                            f"{period_end}; the company may report this metric under "
                            "a different concept."
                        )
                except ValueError:
                    pass

            accn_cc = best.get("accn", "")
            row: dict = {
                "company": company_name,
                "cik": padded_cik,
                "ticker": ticker,
                "concept": effective_concept_cc,
                "value": best.get("val"),
                "unit": best_unit,
                "period_end": period_end,
                "fiscal_year": fiscal_year,
                "filing_fiscal_year": best.get("fy"),
                "accession_number": accn_cc,
                "filing_index_url": (
                    f"https://www.sec.gov/Archives/edgar/data/"
                    f"{int(padded_cik)}/{accn_cc.replace('-', '')}/"
                    if accn_cc else ""
                ),
                "form": best.get("form", ""),
            }
            if concept_note_cc:
                row["concept_note"] = concept_note_cc
            results.append(row)

    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        return {"error": str(exc), "hint": "A network error occurred. Check identifiers and try again."}
    except Exception as exc:
        return {"error": f"Unexpected error: {type(exc).__name__}: {exc}",
                "hint": "Report this to the toolkit maintainer; do not retry with the same arguments."}

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
    identifier: Annotated[str, "Accepts a ticker or CIK. After choosing a company from search results, pass its CIK, because some tickers map to a holding entity."],
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
        filing_index_url = (
            f"https://www.sec.gov/Archives/edgar/data/{numeric_cik}"
            f"/{accession_dashed.replace('-', '')}/"
        )
        edgar_url = (
            f"https://www.sec.gov/Archives/edgar/data/{numeric_cik}/{accession_path}/{primary_doc}"
            if primary_doc else
            filing_index_url
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
    except Exception as exc:
        return {"error": f"Unexpected error: {type(exc).__name__}: {exc}",
                "hint": "Report this to the toolkit maintainer; do not retry with the same arguments."}


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
    identifier: Annotated[str, "Accepts a ticker or CIK. After choosing a company from search results, pass its CIK, because some tickers map to a holding entity."],
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
    except Exception as exc:
        return {"error": f"Unexpected error: {type(exc).__name__}: {exc}",
                "hint": "Report this to the toolkit maintainer; do not retry with the same arguments."}


# ---------------------------------------------------------------------------
# Tool 8 — Quarterly XBRL observations (Q1/Q2/Q3)
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
    identifier: Annotated[str, "Accepts a ticker or CIK. After choosing a company from search results, pass its CIK, because some tickers map to a holding entity."],
    taxonomy: Annotated[str, "XBRL taxonomy, e.g. 'us-gaap'."],
    concept: Annotated[str, "XBRL concept tag, e.g. 'Revenues', 'NetIncomeLoss'."],
    limit: Annotated[int, "Number of quarterly observations to return, most recent first. Default 8, max 40."] = 8,
) -> dict:
    """Return quarterly (Q1/Q2/Q3) XBRL observations for a single concept and company.

    IMPORTANT: This tool returns Q1, Q2, and Q3 only.  Q4 figures are NOT available
    here because companies do not file a 10-Q for Q4; Q4 data appears only in the
    annual 10-K or an earnings 8-K.  Use sec_edgar_get_company_fact for full-year (FY)
    annual figures.

    Filters to 10-Q observations with a single-quarter duration of 80–100 days.
    This eliminates year-to-date (YTD) cumulative values (e.g. a nine-month total
    tagged fp=Q3 would exceed the duration window and is excluded).

    Revenue concept auto-retry: if concept='Revenues' returns zero quarterly
    observations, the tool automatically retries with
    'RevenueFromContractWithCustomerExcludingAssessedTax' (the concept Apple and
    many other companies switched to after 2018). The result includes a 'concept'
    field showing which concept name was actually used.

    Each observation key reference:
      fiscal_quarter  — the SEC fp value (Q1/Q2/Q3)
      fiscal_year     — derived from the period end date (not the filing year)
      period_label    — human-readable, e.g. "Q3 FY2024"
      period_start / period_end — ISO dates bounding the quarter
      value           — the numeric fact value
      accession_number, filing_fiscal_year — filing provenance (do NOT use
        filing_fiscal_year as the period label)

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
        # Fetch submission and companyfacts concurrently to reduce latency.
        sub, resp = await asyncio.gather(
            _fetch_submission(padded_cik),
            client.get(
                f"https://data.sec.gov/api/xbrl/companyfacts/CIK{padded_cik}.json",
                headers=_make_headers(),
            ),
        )
        resp.raise_for_status()
        facts = resp.json()
        fye_mmdd: str | None = sub.get("fiscalYearEnd")

        company_name = facts.get("entityName", identifier)
        taxonomy_data = facts.get("facts", {}).get(taxonomy)
        if taxonomy_data is None:
            available = list(facts.get("facts", {}).keys())
            return {
                "error": f"Taxonomy '{taxonomy}' not found for {company_name}.",
                "hint": f"Available taxonomies: {available}.",
            }

        quarterly_fps = {"Q1", "Q2", "Q3", "Q4"}

        def _is_single_quarter(obs: dict) -> bool:
            dur = _duration_days(obs)
            if dur is None:
                return True  # can't determine — keep it
            return 80 <= dur <= 100

        def _quarterly_obs_for(cdata: dict) -> tuple[list, str, str]:
            """Return (obs_list, best_unit, label) for a concept dict."""
            ru = cdata.get("units", {})
            bu = max(ru.keys(), key=lambda u: len(ru[u]), default=None)
            if bu is None:
                return [], "", cdata.get("label", "")
            all_o = ru[bu]
            filtered = [
                o for o in all_o
                if o.get("fp") in quarterly_fps
                and o.get("form", "").startswith("10-Q")
                and _is_single_quarter(o)
            ]
            return filtered, bu, cdata.get("label", "")

        # Resolve concept with multi-candidate selection for revenue concepts.
        # If the concept is in REVENUE_CANDIDATES, evaluate every candidate the
        # company reports; pick the one whose most-recent quarterly period_end
        # is newest (ties → larger value at that date).
        effective_concept = concept
        concept_note_q: str | None = None
        concept_data = taxonomy_data.get(concept)

        if concept in REVENUE_CANDIDATES:
            best_cname_q: str | None = None
            best_end_q: str = ""
            best_val_q: float | int | None = None
            for cname in REVENUE_CANDIDATES:
                cdata = taxonomy_data.get(cname)
                if cdata is None:
                    continue
                obs_list, _, _ = _quarterly_obs_for(cdata)
                for o in obs_list:
                    end = o.get("end", "")
                    val = o.get("val")
                    if end > best_end_q or (
                        end == best_end_q
                        and val is not None
                        and (best_val_q is None or val > best_val_q)
                    ):
                        best_end_q = end
                        best_val_q = val
                        best_cname_q = cname
            if best_cname_q is not None:
                if best_cname_q != concept:
                    concept_note_q = (
                        f"Requested '{concept}' but '{best_cname_q}' has more recent "
                        f"quarterly data (period_end {best_end_q}); using '{best_cname_q}'."
                    )
                effective_concept = best_cname_q
                concept_data = taxonomy_data.get(best_cname_q)
            # concept_data may still be None if no candidate had quarterly data —
            # fall through to the error/fallback path below.

        if concept_data is None:
            sample = list(taxonomy_data.keys())[:10]
            return {
                "error": f"Concept '{concept}' not found in taxonomy '{taxonomy}' for {company_name}.",
                "hint": (
                    f"Sample available concepts (first 10): {sample}. "
                    "Try concept='RevenueFromContractWithCustomerExcludingAssessedTax' for revenue, "
                    "or call sec_edgar_list_concepts with search='<keyword>'. "
                    "Do not retry with the same arguments."
                ),
            }

        label = concept_data.get("label", effective_concept)
        raw_units = concept_data.get("units", {})

        # Pick the unit with the most observations (same logic as compare_companies)
        best_unit = max(raw_units.keys(), key=lambda u: len(raw_units[u]), default=None)
        if best_unit is None:
            return {
                "error": f"No unit data found for concept '{effective_concept}' for {company_name}.",
                "hint": "The concept may exist but have no numeric observations.",
            }

        all_obs = raw_units[best_unit]

        # Filter to single-quarter observations from 10-Q filings.
        #
        # XBRL stores BOTH three-month and year-to-date (YTD) values under the same
        # fp label (e.g. fp=Q3 covers both "three months ended Sep 30" AND "nine months
        # ended Sep 30"). Genuine single quarters span 80–100 days; YTD periods are
        # longer.  Tightened from ≤104 to 80–100 to exclude edge-case YTD values.
        quarterly_obs = [
            o for o in all_obs
            if o.get("fp") in quarterly_fps
            and o.get("form", "").startswith("10-Q")
            and _is_single_quarter(o)
        ]

        # Sort most-recent first by period end date
        quarterly_obs.sort(key=lambda o: o.get("end", ""), reverse=True)

        note = concept_note_q or ""
        if len(quarterly_obs) == 0:
            # Before giving up: try every remaining revenue candidate (if applicable)
            # for companies where the selected concept has no quarterly 10-Q data.
            if concept in REVENUE_CANDIDATES:
                for cname in REVENUE_CANDIDATES:
                    if cname == effective_concept:
                        continue
                    cdata = taxonomy_data.get(cname)
                    if cdata is None:
                        continue
                    alt_obs, alt_unit, alt_label = _quarterly_obs_for(cdata)
                    if alt_obs:
                        effective_concept = cname
                        label = alt_label
                        best_unit = alt_unit
                        quarterly_obs = alt_obs
                        quarterly_obs.sort(key=lambda o: o.get("end", ""), reverse=True)
                        note = f"Concept '{concept}' had no quarterly data; using '{cname}' instead."
                        break

        if len(quarterly_obs) == 0:
            # Fall back to any single-quarter fp even if not from 10-Q (e.g. 10-K amended)
            quarterly_obs = [
                o for o in all_obs
                if o.get("fp") in quarterly_fps and _is_single_quarter(o)
            ]
            quarterly_obs.sort(key=lambda o: o.get("end", ""), reverse=True)
            if quarterly_obs:
                note = "Quarterly data sourced from non-10-Q filings (e.g. restated quarters in 10-K/8-K)."
            else:
                return {
                    "error": f"No single-quarter (Q1/Q2/Q3/Q4) observations found for '{effective_concept}' for {company_name}.",
                    "hint": (
                        "Try concept='RevenueFromContractWithCustomerExcludingAssessedTax' for revenue, "
                        "or call sec_edgar_list_concepts with search='<keyword>'. "
                        "Do not retry with the same arguments."
                    ),
                }

        note_parts = []
        if len(quarterly_obs) < limit:
            note_parts.append(
                f"Only {len(quarterly_obs)} single-quarter observations available "
                f"(requested {limit}). Q4 figures are not filed in 10-Qs — they appear "
                "in the annual 10-K or earnings 8-K, which are not included here."
            )
        if note:
            note_parts.append(note)
        note = " ".join(note_parts)

        # Deduplicate: keep only the latest-filed observation per (start, end) pair.
        # This correctly collapses restatements of the same period window, even when
        # (fp, fy) tags differ across filings.
        seen: dict[tuple, dict] = {}
        for o in quarterly_obs:  # already sorted most-recent end date first
            key = (o.get("start", ""), o.get("end", ""))
            if key not in seen or o.get("filed", "") > seen[key].get("filed", ""):
                seen[key] = o
        quarterly_obs = list(seen.values())
        # Re-sort after dedup
        quarterly_obs.sort(key=lambda o: o.get("end", ""), reverse=True)

        # Slice and annotate
        sliced = quarterly_obs[:limit]
        observations = []
        for o in sliced:
            fp = o.get("fp", "")
            end = o.get("end", "")
            try:
                fiscal_year = _fiscal_year_for(end, fye_mmdd)
            except Exception:
                fiscal_year = o.get("fy")
            period_label = f"{fp} FY{fiscal_year}" if fp and fiscal_year else fp
            observations.append({
                "period_label": period_label,
                "fiscal_quarter": fp,
                "fiscal_year": fiscal_year,
                "period_start": o.get("start") or None,
                "period_end": end,
                "value": o.get("val"),
                "form": o.get("form", ""),
                "accession_number": o.get("accn", ""),
                "filing_fiscal_year": o.get("fy"),
            })

        return {
            "company": company_name,
            "cik": padded_cik,
            "taxonomy": taxonomy,
            "concept": effective_concept,
            "unit": best_unit,
            "label": label,
            "observations": observations,
            "note": note,
        }
    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        return {"error": str(exc), "hint": "Check the identifier and concept, and try again."}
    except Exception as exc:
        return {"error": f"Unexpected error: {type(exc).__name__}: {exc}",
                "hint": "Report this to the toolkit maintainer; do not retry with the same arguments."}


if __name__ == "__main__":
    mcp.run(transport="stdio")
