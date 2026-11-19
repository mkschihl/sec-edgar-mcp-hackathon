"""SEC EDGAR MCP Toolkit — stdio transport.

Eleven tools exposed to watsonx Orchestrate:
  - sec_edgar_resolve_synonym       : map a common company nickname/alias to canonical EDGAR name + ticker
  - sec_edgar_search_companies      : search all SEC-registered companies by partial name
  - sec_edgar_resolve_company       : resolve ticker or CIK to canonical company info
  - sec_edgar_get_recent_filings    : recent filing history with optional form-type filter
  - sec_edgar_get_company_fact      : XBRL concept time series for one company
  - sec_edgar_compare_companies     : compare one XBRL concept across multiple companies
  - sec_edgar_get_filing_metadata   : filing doc list and EDGAR URL for an accession number
  - sec_edgar_get_filing_text       : extract readable text from an SEC filing document
  - sec_edgar_full_text_search      : search EDGAR full-text index by keyword across all filings
  - sec_edgar_list_concepts         : discover available XBRL concepts for a company
  - sec_edgar_get_quarterly_facts   : quarterly XBRL observations (Q1/Q2/Q3/Q4) for one company

Orchestrate starts this file as a subprocess and communicates over stdin/stdout.
SEC APIs require no API key. Rate limit: 10 req/s per IP.
"""

from __future__ import annotations

import asyncio
import re
import time
from datetime import date, datetime, timedelta
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
        "SEC EDGAR toolkit with eleven tools for authoritative SEC filing data.\n\n"
        "TOOL SELECTION GUIDE:\n"
        "- Resolve a common nickname/alias to canonical name + ticker → sec_edgar_resolve_synonym\n"
        "- Find companies by partial name → sec_edgar_search_companies\n"
        "- Resolve a ticker or CIK to canonical info → sec_edgar_resolve_company\n"
        "- List recent 10-K/10-Q/8-K filings → sec_edgar_get_recent_filings\n"
        "- Fetch an XBRL annual concept time series → sec_edgar_get_company_fact\n"
        "- Fetch quarterly (Q1/Q2/Q3/Q4) observations → sec_edgar_get_quarterly_facts\n"
        "- Compare a concept across multiple companies → sec_edgar_compare_companies\n"
        "- Look up a specific filing by accession number → sec_edgar_get_filing_metadata\n"
        "- Read narrative text from a filing document → sec_edgar_get_filing_text\n"
        "- Search EDGAR full-text for any keyword across all filings → sec_edgar_full_text_search\n"
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

# ---------------------------------------------------------------------------
# Global SEC rate limiter
# ---------------------------------------------------------------------------
# EDGAR's published rate limit is 10 requests/second per IP address.  A
# semaphore of 8 permits up to 8 concurrent in-flight requests, leaving
# headroom for the HTTP round-trip time and ensuring we never burst to 10.
#
# The semaphore is per-event-loop: asyncio.Semaphore is bound to the loop
# that created it.  We use the same rebuild pattern as _http_client so that
# the test suite (which calls asyncio.run() multiple times) gets a fresh
# semaphore for each loop without raising "attached to a different loop".
_edgar_sem: asyncio.Semaphore | None = None
_edgar_sem_loop: asyncio.AbstractEventLoop | None = None


def _get_sem() -> asyncio.Semaphore:
    """Return a Semaphore bound to the current running event loop."""
    global _edgar_sem, _edgar_sem_loop
    try:
        current_loop = asyncio.get_running_loop()
    except RuntimeError:
        current_loop = None
    if (
        _edgar_sem is None
        or _edgar_sem_loop is None
        or _edgar_sem_loop is not current_loop
        or (_edgar_sem_loop is not None and _edgar_sem_loop.is_closed())
    ):
        _edgar_sem = asyncio.Semaphore(8)
        _edgar_sem_loop = current_loop
    return _edgar_sem


async def _edgar_get(url: str, **kwargs) -> httpx.Response:
    """Rate-limited GET wrapper.  Acquires the global semaphore before issuing
    the request so that at most 8 outbound EDGAR calls are in-flight at once.
    """
    async with _get_sem():
        return await _get_client().get(url, **kwargs)


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


async def _ensure_ticker_cache() -> None:
    """Fetch company_tickers.json and populate _TICKER_CACHE / _CIK_CACHE if empty."""
    global _TICKER_CACHE, _CIK_CACHE
    if _TICKER_CACHE:
        return
    resp = await _edgar_get(
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
    query: str, limit: int
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
        resp = await _edgar_get(url, headers=_make_headers(), timeout=10.0)
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
    await _ensure_ticker_cache()
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
        resp = await _edgar_get(
            f"https://data.sec.gov/submissions/CIK{cik}.json",
            headers=_make_headers(),
        )
        resp.raise_for_status()
        _SUBMISSION_CACHE[cik] = resp.json()
    return _SUBMISSION_CACHE[cik]


# Cache for companyfacts JSON (all XBRL data) keyed by padded CIK.
# Values are (data_dict, fetch_timestamp_monotonic).  TTL = 24 h.
# The companyfacts payload is large (5–10 MB per company); caching it
# eliminates redundant round-trips when an agent asks multiple XBRL
# questions about the same company in one session.
_FACTS_CACHE: dict[str, tuple[dict, float]] = {}
_FACTS_CACHE_TTL_SECONDS: float = 86_400.0  # 24 hours


async def _fetch_company_facts(cik: str) -> dict:
    """Fetch and TTL-cache the companyfacts JSON for a company by padded CIK.

    Re-fetches if the cached entry is older than _FACTS_CACHE_TTL_SECONDS (24 h).
    Within a single process lifetime the same company is almost never stale —
    EDGAR publishes new facts only when a company files a new 10-K/10-Q.
    """
    cached = _FACTS_CACHE.get(cik)
    if cached is not None:
        data, fetched_at = cached
        if time.monotonic() - fetched_at < _FACTS_CACHE_TTL_SECONDS:
            return data
    resp = await _edgar_get(
        f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json",
        headers=_make_headers(),
    )
    resp.raise_for_status()
    data = resp.json()
    _FACTS_CACHE[cik] = (data, time.monotonic())
    return data


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
# Synonym / alias lookup table
# ---------------------------------------------------------------------------
# Maps lowercase common names / nicknames / abbreviations to a canonical
# EDGAR-searchable name and the primary exchange ticker.  This covers the
# most frequent cases where users refer to a company by a brand or nickname
# rather than the SEC-registered legal name.
#
# Keys    : lowercase alias (may include spaces, punctuation stripped)
# Values  : {"canonical_name": str, "ticker": str, "note": str}
#
# When adding entries: prefer the name that EDGAR full-text search returns
# reliably (usually the legal name or its well-known abbreviation).

_SYNONYM_TABLE: dict[str, dict] = {
    # Big Tech ---------------------------------------------------------------
    "google":           {"canonical_name": "Alphabet Inc.", "ticker": "GOOGL", "note": "Google is the main product brand of Alphabet Inc."},
    "alphabet":         {"canonical_name": "Alphabet Inc.", "ticker": "GOOGL", "note": "Alphabet Inc. is the parent company of Google."},
    "meta":             {"canonical_name": "Meta Platforms Inc.", "ticker": "META", "note": "Meta Platforms (formerly Facebook Inc.) since 2021."},
    "facebook":         {"canonical_name": "Meta Platforms Inc.", "ticker": "META", "note": "Facebook rebranded to Meta Platforms in 2021."},
    "instagram":        {"canonical_name": "Meta Platforms Inc.", "ticker": "META", "note": "Instagram is owned by Meta Platforms Inc."},
    "whatsapp":         {"canonical_name": "Meta Platforms Inc.", "ticker": "META", "note": "WhatsApp is owned by Meta Platforms Inc."},
    "apple":            {"canonical_name": "Apple Inc.", "ticker": "AAPL", "note": "Apple Inc. is the SEC-registered legal name."},
    "microsoft":        {"canonical_name": "Microsoft Corp", "ticker": "MSFT", "note": "Microsoft Corp is the SEC-registered legal name."},
    "amazon":           {"canonical_name": "Amazon.com Inc.", "ticker": "AMZN", "note": "Amazon.com Inc. is the SEC-registered legal name."},
    "aws":              {"canonical_name": "Amazon.com Inc.", "ticker": "AMZN", "note": "AWS (Amazon Web Services) is a division of Amazon.com Inc."},
    "nvidia":           {"canonical_name": "NVIDIA Corp", "ticker": "NVDA", "note": "NVIDIA Corp is the SEC-registered legal name."},
    # Social & streaming -----------------------------------------------------
    "twitter":          {"canonical_name": "X Holdings Corp", "ticker": "", "note": "Twitter rebranded to X; parent entity is X Holdings Corp."},
    "x":                {"canonical_name": "X Holdings Corp", "ticker": "", "note": "X (formerly Twitter) parent is X Holdings Corp."},
    "tiktok":           {"canonical_name": "ByteDance", "ticker": "", "note": "TikTok is a product of ByteDance Ltd; not separately SEC-registered."},
    "youtube":          {"canonical_name": "Alphabet Inc.", "ticker": "GOOGL", "note": "YouTube is a wholly-owned subsidiary of Alphabet Inc."},
    "linkedin":         {"canonical_name": "Microsoft Corp", "ticker": "MSFT", "note": "LinkedIn is a wholly-owned subsidiary of Microsoft Corp."},
    "netflix":          {"canonical_name": "Netflix Inc.", "ticker": "NFLX", "note": "Netflix Inc. is the SEC-registered legal name."},
    "spotify":          {"canonical_name": "Spotify Technology S.A.", "ticker": "SPOT", "note": "Spotify Technology S.A. is the SEC-registered legal name."},
    # E-commerce & payments --------------------------------------------------
    "ebay":             {"canonical_name": "eBay Inc.", "ticker": "EBAY", "note": "eBay Inc. is the SEC-registered legal name."},
    "paypal":           {"canonical_name": "PayPal Holdings Inc.", "ticker": "PYPL", "note": "PayPal Holdings Inc. is the SEC-registered legal name."},
    "shopify":          {"canonical_name": "Shopify Inc.", "ticker": "SHOP", "note": "Shopify Inc. is the SEC-registered legal name."},
    "uber":             {"canonical_name": "Uber Technologies Inc.", "ticker": "UBER", "note": "Uber Technologies Inc. is the SEC-registered legal name."},
    "lyft":             {"canonical_name": "Lyft Inc.", "ticker": "LYFT", "note": "Lyft Inc. is the SEC-registered legal name."},
    "airbnb":           {"canonical_name": "Airbnb Inc.", "ticker": "ABNB", "note": "Airbnb Inc. is the SEC-registered legal name."},
    # Automotive & energy ----------------------------------------------------
    "tesla":            {"canonical_name": "Tesla Inc.", "ticker": "TSLA", "note": "Tesla Inc. is the SEC-registered legal name."},
    "ford":             {"canonical_name": "Ford Motor Co", "ticker": "F", "note": "Ford Motor Co is the SEC-registered legal name."},
    "gm":               {"canonical_name": "General Motors Co", "ticker": "GM", "note": "GM is the common abbreviation for General Motors Co."},
    "general motors":   {"canonical_name": "General Motors Co", "ticker": "GM", "note": "General Motors Co is the SEC-registered legal name."},
    "exxon":            {"canonical_name": "Exxon Mobil Corp", "ticker": "XOM", "note": "Exxon is a shorthand for Exxon Mobil Corp."},
    "exxonmobil":       {"canonical_name": "Exxon Mobil Corp", "ticker": "XOM", "note": "ExxonMobil is a shorthand for Exxon Mobil Corp."},
    "exxon mobil":      {"canonical_name": "Exxon Mobil Corp", "ticker": "XOM", "note": "Exxon Mobil Corp is the SEC-registered legal name."},
    "chevron":          {"canonical_name": "Chevron Corp", "ticker": "CVX", "note": "Chevron Corp is the SEC-registered legal name."},
    # Finance & banking ------------------------------------------------------
    "jpmorgan":         {"canonical_name": "JPMorgan Chase & Co", "ticker": "JPM", "note": "JPMorgan is a shorthand for JPMorgan Chase & Co."},
    "jp morgan":        {"canonical_name": "JPMorgan Chase & Co", "ticker": "JPM", "note": "JP Morgan is a shorthand for JPMorgan Chase & Co."},
    "bank of america":  {"canonical_name": "Bank of America Corp", "ticker": "BAC", "note": "Bank of America Corp is the SEC-registered legal name."},
    "boa":              {"canonical_name": "Bank of America Corp", "ticker": "BAC", "note": "BofA is an abbreviation for Bank of America Corp."},
    "wells fargo":      {"canonical_name": "Wells Fargo & Co", "ticker": "WFC", "note": "Wells Fargo & Co is the SEC-registered legal name."},
    "goldman":          {"canonical_name": "Goldman Sachs Group Inc.", "ticker": "GS", "note": "Goldman refers to The Goldman Sachs Group Inc."},
    "goldman sachs":    {"canonical_name": "Goldman Sachs Group Inc.", "ticker": "GS", "note": "The Goldman Sachs Group Inc. is the SEC-registered legal name."},
    "morgan stanley":   {"canonical_name": "Morgan Stanley", "ticker": "MS", "note": "Morgan Stanley is the SEC-registered legal name."},
    "berkshire":        {"canonical_name": "Berkshire Hathaway Inc.", "ticker": "BRK-B", "note": "Berkshire is a shorthand for Berkshire Hathaway Inc."},
    "berkshire hathaway": {"canonical_name": "Berkshire Hathaway Inc.", "ticker": "BRK-B", "note": "Berkshire Hathaway Inc. is the SEC-registered legal name."},
    "visa":             {"canonical_name": "Visa Inc.", "ticker": "V", "note": "Visa Inc. is the SEC-registered legal name."},
    "mastercard":       {"canonical_name": "Mastercard Inc.", "ticker": "MA", "note": "Mastercard Inc. is the SEC-registered legal name."},
    # Healthcare & pharma ----------------------------------------------------
    "pfizer":           {"canonical_name": "Pfizer Inc.", "ticker": "PFE", "note": "Pfizer Inc. is the SEC-registered legal name."},
    "johnson and johnson": {"canonical_name": "Johnson & Johnson", "ticker": "JNJ", "note": "Johnson & Johnson is the SEC-registered legal name."},
    "johnson & johnson": {"canonical_name": "Johnson & Johnson", "ticker": "JNJ", "note": "Johnson & Johnson is the SEC-registered legal name."},
    "j&j":              {"canonical_name": "Johnson & Johnson", "ticker": "JNJ", "note": "J&J is an abbreviation for Johnson & Johnson."},
    "abbvie":           {"canonical_name": "AbbVie Inc.", "ticker": "ABBV", "note": "AbbVie Inc. is the SEC-registered legal name."},
    "unitedhealth":     {"canonical_name": "UnitedHealth Group Inc.", "ticker": "UNH", "note": "UnitedHealth refers to UnitedHealth Group Inc."},
    "united health":    {"canonical_name": "UnitedHealth Group Inc.", "ticker": "UNH", "note": "UnitedHealth Group Inc. is the SEC-registered legal name."},
    # Industrials & conglomerates --------------------------------------------
    "ge":               {"canonical_name": "GE Aerospace", "ticker": "GE", "note": "GE is the ticker and common name for GE Aerospace (formerly General Electric Co)."},
    "general electric": {"canonical_name": "GE Aerospace", "ticker": "GE", "note": "General Electric rebranded to GE Aerospace in 2024."},
    "boeing":           {"canonical_name": "Boeing Co", "ticker": "BA", "note": "Boeing Co is the SEC-registered legal name."},
    "3m":               {"canonical_name": "3M Co", "ticker": "MMM", "note": "3M Co is the SEC-registered legal name."},
    "honeywell":        {"canonical_name": "Honeywell International Inc.", "ticker": "HON", "note": "Honeywell International Inc. is the SEC-registered legal name."},
    # Retail & consumer ------------------------------------------------------
    "walmart":          {"canonical_name": "Walmart Inc.", "ticker": "WMT", "note": "Walmart Inc. is the SEC-registered legal name."},
    "costco":           {"canonical_name": "Costco Wholesale Corp", "ticker": "COST", "note": "Costco Wholesale Corp is the SEC-registered legal name."},
    "home depot":       {"canonical_name": "Home Depot Inc.", "ticker": "HD", "note": "Home Depot Inc. is the SEC-registered legal name."},
    "mcdonalds":        {"canonical_name": "McDonald's Corp", "ticker": "MCD", "note": "McDonald's Corp is the SEC-registered legal name."},
    "mcdonald's":       {"canonical_name": "McDonald's Corp", "ticker": "MCD", "note": "McDonald's Corp is the SEC-registered legal name."},
    "starbucks":        {"canonical_name": "Starbucks Corp", "ticker": "SBUX", "note": "Starbucks Corp is the SEC-registered legal name."},
    "nike":             {"canonical_name": "Nike Inc.", "ticker": "NKE", "note": "Nike Inc. is the SEC-registered legal name."},
    # Telecom ----------------------------------------------------------------
    "at&t":             {"canonical_name": "AT&T Inc.", "ticker": "T", "note": "AT&T Inc. is the SEC-registered legal name."},
    "att":              {"canonical_name": "AT&T Inc.", "ticker": "T", "note": "AT&T Inc. is the SEC-registered legal name."},
    "verizon":          {"canonical_name": "Verizon Communications Inc.", "ticker": "VZ", "note": "Verizon Communications Inc. is the SEC-registered legal name."},
    "t-mobile":         {"canonical_name": "T-Mobile US Inc.", "ticker": "TMUS", "note": "T-Mobile US Inc. is the SEC-registered legal name."},
    "tmobile":          {"canonical_name": "T-Mobile US Inc.", "ticker": "TMUS", "note": "T-Mobile US Inc. is the SEC-registered legal name."},
    # Semiconductor ----------------------------------------------------------
    "intel":            {"canonical_name": "Intel Corp", "ticker": "INTC", "note": "Intel Corp is the SEC-registered legal name."},
    "amd":              {"canonical_name": "Advanced Micro Devices Inc.", "ticker": "AMD", "note": "AMD is an abbreviation for Advanced Micro Devices Inc."},
    "advanced micro devices": {"canonical_name": "Advanced Micro Devices Inc.", "ticker": "AMD", "note": "Advanced Micro Devices Inc. is the SEC-registered legal name."},
    "qualcomm":         {"canonical_name": "QUALCOMM Inc.", "ticker": "QCOM", "note": "QUALCOMM Inc. is the SEC-registered legal name."},
    "tsmc":             {"canonical_name": "Taiwan Semiconductor Manufacturing Co", "ticker": "TSM", "note": "TSMC is an abbreviation for Taiwan Semiconductor Manufacturing Co."},
}


# ---------------------------------------------------------------------------
# Tool 0 — Resolve company synonym / alias
# ---------------------------------------------------------------------------

@mcp.tool(
    name="sec_edgar_resolve_synonym",
    annotations={
        "title": "Resolve Company Synonym or Alias",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def sec_edgar_resolve_synonym(
    name: Annotated[str, "Common company name, nickname, or alias to look up, e.g. 'Google', 'Meta', 'GE', 'Goldman'. Case-insensitive."],
) -> dict:
    """Resolve a common company nickname or alias to its canonical EDGAR name and primary ticker.

    Use this tool BEFORE sec_edgar_search_companies or sec_edgar_resolve_company when the
    user refers to a company by a brand name, nickname, or abbreviation rather than its
    SEC-registered legal name.  Examples:
      "Google"          → Alphabet Inc.  / GOOGL
      "Meta"            → Meta Platforms Inc. / META
      "Facebook"        → Meta Platforms Inc. / META
      "GE"              → GE Aerospace / GE
      "General Electric"→ GE Aerospace / GE
      "Goldman"         → Goldman Sachs Group Inc. / GS

    Returns a dict with keys:
      input           — the alias as supplied
      canonical_name  — SEC-registered or best-known EDGAR name to use in searches
      ticker          — primary exchange ticker (empty string if not exchange-listed)
      note            — brief explanation of the mapping

    If the alias is not found in the synonym table, returns:
      {"error": "...", "hint": "...", "input": "..."}
    In that case, pass the original name directly to sec_edgar_search_companies.
    """
    key = name.strip().lower()
    # Strip trailing punctuation that users sometimes include (e.g. "Apple,")
    key = key.rstrip(".,;:!?")
    match = _SYNONYM_TABLE.get(key)
    if match is None:
        return {
            "error": f"No synonym mapping found for '{name}'.",
            "hint": (
                "Pass the company name directly to sec_edgar_search_companies to find it, "
                "or use the canonical SEC-registered name if known."
            ),
            "input": name,
        }
    return {
        "input": name,
        "canonical_name": match["canonical_name"],
        "ticker": match["ticker"],
        "note": match["note"],
    }


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
    warnings: list[str] = []
    try:
        # Warm the ticker cache, then run both passes concurrently.
        await _ensure_ticker_cache()
        query_lower = query.lower()
        primary_all = [
            {"ticker": v["ticker"], "cik": v["cik_str"], "name": v["title"], "source": "exchange_listed"}
            for v in _TICKER_CACHE.values()
            if query_lower in v["title"].lower()
        ]

        # Run the all-filers search concurrently with building primary list (already done above).
        fallback_result = await _search_all_filers(query, effective_limit)

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

        # Fetch submission and companyfacts concurrently to reduce latency.
        # _fetch_company_facts uses a 24h TTL cache; second call for same CIK is free.
        sub, facts = await asyncio.gather(
            _fetch_submission(padded_cik),
            _fetch_company_facts(padded_cik),
        )
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
                facts = await _fetch_company_facts(padded_cik)
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
# Tool 7 — Read narrative text from a filing document
# ---------------------------------------------------------------------------

# EDGAR HTML filing documents can be large (100–500 KB).  We fetch the filing
# index JSON first to find the primary document filename, then fetch and
# strip the HTML from that document.  No external HTML-parsing library is
# needed — the standard-library `re` module (already imported) is sufficient
# for EDGAR's well-structured HTML.

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_MULTI_SPACE_RE = re.compile(r"[ \t]+")
_MULTI_NEWLINE_RE = re.compile(r"\n{3,}")

# Common section heading keywords → representative text that appears near
# the start of that section in 10-K/10-Q filings.  Used for best-effort
# section seeking only — not a parser.
_SECTION_KEYWORDS: dict[str, list[str]] = {
    "risk_factors":    ["risk factors", "item 1a"],
    "mda":             ["management", "discussion and analysis", "item 7"],
    "business":        ["item 1.", "item 1 ", "business overview", "our business"],
    "financials":      ["financial statements", "item 8", "consolidated balance"],
    "legal":           ["legal proceedings", "item 3"],
    "controls":        ["controls and procedures", "item 9a"],
    "8k_items":        ["item 1.", "item 2.", "item 5.", "item 7.", "item 8.", "item 9."],
}

_FILING_TEXT_MAX_CHARS = 32_000
_FILING_TEXT_DEFAULT_CHARS = 8_000


def _strip_html(raw: str) -> str:
    """Strip HTML tags and normalize whitespace from a filing document."""
    text = _HTML_TAG_RE.sub(" ", raw)
    # Collapse runs of spaces/tabs to a single space per line
    lines = [_MULTI_SPACE_RE.sub(" ", line).strip() for line in text.splitlines()]
    # Rejoin and collapse excessive blank lines
    text = "\n".join(lines)
    text = _MULTI_NEWLINE_RE.sub("\n\n", text)
    return text.strip()


# Matches a lowercase letter or digit followed by a period then a space and
# an uppercase letter — a heuristic for a sentence-ending full stop, e.g.
# "operations. The" vs a section-number dot like "Item 1B. Unresolved".
_PROSE_PERIOD_RE = re.compile(r"[a-z]\. [A-Z]")


def _find_section_offset(text: str, section: str) -> int:
    """Return the character offset of the best-matching section heading, or 0.

    EDGAR filings have a Table of Contents that lists every section heading
    before the actual content.  The TOC and the real section both contain the
    same keyword, but only the real section is followed by prose.  We walk
    through up to 4 occurrences and pick the first whose following 400-char
    context contains a sentence-ending period (lowercase word + ". " + upper).
    """
    keywords = _SECTION_KEYWORDS.get(section.lower().strip(), [section.lower()])
    best = len(text)  # sentinel: not found

    for kw in keywords:
        kw_lower = kw.lower()
        text_lower = text.lower()
        pos = 0
        found_prose = False
        for _ in range(4):  # examine up to 4 occurrences per keyword
            p = text_lower.find(kw_lower, pos)
            if p < 0:
                break
            ctx = text[p: p + 400]
            if _PROSE_PERIOD_RE.search(ctx):
                if p < best:
                    best = p
                found_prose = True
                break
            pos = p + len(kw_lower)
        if not found_prose:
            # No prose-like context found — fall back to first occurrence
            p0 = text_lower.find(kw_lower)
            if 0 <= p0 < best:
                best = p0

    return 0 if best == len(text) else best


@mcp.tool(
    name="sec_edgar_get_filing_text",
    annotations={
        "title": "Get SEC Filing Text",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def sec_edgar_get_filing_text(
    identifier: Annotated[str, "Company ticker or CIK. Used together with accession_number."],
    accession_number: Annotated[str, "Accession number of the filing, e.g. '0000320193-24-000123' (dashes optional)."],
    section: Annotated[str, (
        "Optional section of the filing to seek to before extracting text. "
        "Supported hints: 'risk_factors', 'mda', 'business', 'financials', 'legal', 'controls', '8k_items'. "
        "Leave empty to start from the beginning of the document."
    )] = "",
    max_chars: Annotated[int, (
        "Maximum number of characters to return (default 8000, max 32000). "
        "Increase for longer sections; decrease for a quick overview."
    )] = _FILING_TEXT_DEFAULT_CHARS,
) -> dict:
    """Extract readable plain text from an SEC filing's primary HTML document.

    Workflow:
      1. Use sec_edgar_get_recent_filings or sec_edgar_get_filing_metadata to
         find an accession number.
      2. Call this tool with that accession number to read the filing's text.

    The tool fetches the filing index from EDGAR, identifies the primary
    document, downloads it, strips HTML tags, and returns the plain text.

    Use the optional ``section`` parameter to skip to a named section
    (risk_factors, mda, business, financials, legal, controls) before
    extracting text — useful for long 10-K filings where the section of
    interest is deep in the document.

    Use ``max_chars`` to control how much text is returned.  The default
    (8 000) is enough for most single-section reads.  Set to 32 000 for
    a broader pass over a whole document.

    Returns a dict with keys:
      company           — company name
      cik               — zero-padded 10-digit CIK
      accession_number  — dashed accession number
      form              — form type (10-K, 10-Q, 8-K, …)
      filing_date       — YYYY-MM-DD filing date
      primary_document  — filename of the primary HTML document
      section_sought    — section hint used (empty string if none)
      section_offset    — character offset where extraction began
      text              — extracted plain text (up to max_chars characters)
      truncated         — true if the document was longer than max_chars
      document_url      — direct URL to the primary document on EDGAR

    On failure returns {"error": "...", "hint": "..."}.
    """
    max_chars = max(100, min(max_chars, _FILING_TEXT_MAX_CHARS))

    try:
        resolved = await _resolve_identifier(identifier)
        if isinstance(resolved, dict):
            return resolved
        padded_cik, _ = resolved

        sub = await _fetch_submission(padded_cik)
        company_name = sub.get("name", identifier)
        accession_dashed = _normalize_accession(accession_number.strip())
        accession_path = _accession_to_path(accession_dashed)
        numeric_cik = str(int(padded_cik))
        base_url = (
            f"https://www.sec.gov/Archives/edgar/data/{numeric_cik}/{accession_path}"
        )

        # --- Step 1: resolve metadata from submissions JSON -------------------
        recent = sub.get("filings", {}).get("recent", {})
        accessions = recent.get("accessionNumber", [])
        accession_index = {
            _normalize_accession(acc): i for i, acc in enumerate(accessions)
        }
        idx = accession_index.get(accession_dashed)

        form = ""
        filing_date = ""
        primary_doc = ""
        if idx is not None:
            forms = recent.get("form", [])
            filing_dates = recent.get("filingDate", [])
            primary_docs = recent.get("primaryDocument", [])
            form = forms[idx] if idx < len(forms) else ""
            filing_date = filing_dates[idx] if idx < len(filing_dates) else ""
            primary_doc = primary_docs[idx] if idx < len(primary_docs) else ""

        # --- Step 2: fall back to index.json if primary_doc not in submissions --
        if not primary_doc:
            index_resp = await _edgar_get(
                f"{base_url}/index.json",
                headers=_make_headers(),
            )
            index_resp.raise_for_status()
            index_data = index_resp.json()
            # index.json has {"directory": {"item": [{"name": "...", "type": "..."}]}}
            items = index_data.get("directory", {}).get("item", [])
            # Prefer the first .htm/.html file that isn't the index itself
            for item in items:
                name = item.get("name", "")
                if name.lower().endswith((".htm", ".html")) and "index" not in name.lower():
                    primary_doc = name
                    break
            if not primary_doc:
                # Accept any .txt file as a fallback
                for item in items:
                    name = item.get("name", "")
                    if name.lower().endswith(".txt") and "index" not in name.lower():
                        primary_doc = name
                        break

        if not primary_doc:
            return {
                "error": f"Could not identify a primary document for accession '{accession_dashed}'.",
                "hint": (
                    "The filing index did not contain an .htm/.html document. "
                    "Try sec_edgar_get_filing_metadata to inspect available files."
                ),
            }

        document_url = f"{base_url}/{primary_doc}"

        # --- Step 3: fetch the primary document --------------------------------
        doc_resp = await _edgar_get(document_url, headers=_make_headers())
        doc_resp.raise_for_status()
        raw_content = doc_resp.text

        # --- Step 4: strip HTML and extract text window -----------------------
        plain_text = _strip_html(raw_content)

        section_offset = 0
        if section.strip():
            section_offset = _find_section_offset(plain_text, section)

        window = plain_text[section_offset:]
        truncated = len(window) > max_chars
        text_out = window[:max_chars]

        return {
            "company": company_name,
            "cik": padded_cik,
            "accession_number": accession_dashed,
            "form": form,
            "filing_date": filing_date,
            "primary_document": primary_doc,
            "section_sought": section.strip(),
            "section_offset": section_offset,
            "text": text_out,
            "truncated": truncated,
            "document_url": document_url,
        }
    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        return {"error": str(exc), "hint": "Check the identifier and accession number and try again."}
    except Exception as exc:
        return {
            "error": f"Unexpected error: {type(exc).__name__}: {exc}",
            "hint": "Report this to the toolkit maintainer; do not retry with the same arguments.",
        }


# ---------------------------------------------------------------------------
# Tool 8 — Discover available XBRL concepts for a company
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

        facts = await _fetch_company_facts(padded_cik)

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
    """Return quarterly (Q1/Q2/Q3/Q4) XBRL observations for a single concept and company.

    Q1, Q2, and Q3 observations come directly from 10-Q filings.  Q4 is DERIVED for
    flow items (USD monetary concepts with a start date) by computing:
        Q4 = annual FY value  −  nine-month YTD value
    where both values share the same period_start.  Derived rows carry derived=True
    and a derivation note referencing both accession numbers.

    Q4 derivation is skipped (and a note is added) for:
      • per-share units (e.g. "USD/shares") — not additive across quarters
      • share-count units (e.g. "shares")   — not additive
      • instant (balance-sheet) facts       — no start date; not a flow concept

    Filters to 10-Q observations with a single-quarter duration of 80–100 days.
    This eliminates year-to-date (YTD) cumulative values (e.g. a nine-month total
    tagged fp=Q3 would exceed the duration window and is excluded).

    Revenue concept auto-retry: if concept='Revenues' returns zero quarterly
    observations, the tool automatically retries with
    'RevenueFromContractWithCustomerExcludingAssessedTax' (the concept Apple and
    many other companies switched to after 2018). The result includes a 'concept'
    field showing which concept name was actually used.

    Each observation key reference:
      fiscal_quarter  — the SEC fp value (Q1/Q2/Q3) or "Q4" for derived rows
      fiscal_year     — derived from the period end date (not the filing year)
      period_label    — human-readable, e.g. "Q3 FY2024" or "Q4 FY2024"
      period_start / period_end — ISO dates bounding the quarter
      value           — the numeric fact value
      derived         — True if the row was derived (annual minus nine-month YTD);
                        False for real 10-Q observations
      derivation      — present only on derived rows; describes the computation
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

        # Fetch submission and companyfacts concurrently to reduce latency.
        # _fetch_company_facts uses a 24h TTL cache; second call for same CIK is free.
        sub, facts = await asyncio.gather(
            _fetch_submission(padded_cik),
            _fetch_company_facts(padded_cik),
        )
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
        if note:
            note_parts.append(note)

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

        # ----------------------------------------------------------------
        # Q4 derivation — only for USD flow items (not per-share, not
        # share-count, not instant/balance-sheet facts).
        # For each fiscal year that has BOTH an annual FY record (350–380
        # days, 10-K) AND a nine-month YTD record (260–285 days, same
        # period_start), compute Q4 = annual − nine-month YTD.
        # ----------------------------------------------------------------
        derived_q4_obs: list[dict] = []
        can_derive_q4 = (
            best_unit == "USD"
            and any(o.get("start") for o in all_obs)  # flow items have start
        )
        if not can_derive_q4:
            if best_unit in ("shares",) or "/" in best_unit:
                note_parts.append(
                    f"Q4 derivation skipped: unit '{best_unit}' is not additive "
                    "(per-share or share-count values cannot be derived as annual minus nine-month YTD)."
                )
            else:
                # Instant (balance-sheet) facts have no start date
                note_parts.append(
                    "Q4 derivation skipped: concept appears to be an instant "
                    "(balance-sheet) fact with no period start date."
                )
        else:
            # Find annual FY records from 10-K filings (350–380 days)
            annual_fy: list[dict] = []
            for o in all_obs:
                if o.get("fp") != "FY":
                    continue
                if not o.get("form", "").startswith("10-K"):
                    continue
                dur = _duration_days(o)
                if dur is not None and 350 <= dur <= 380:
                    annual_fy.append(o)

            # Deduplicate annual by period_start: keep latest-filed per start
            ann_seen: dict[str, dict] = {}
            for o in annual_fy:
                start = o.get("start", "")
                if not start:
                    continue
                if start not in ann_seen or o.get("filed", "") > ann_seen[start].get("filed", ""):
                    ann_seen[start] = o

            # Find nine-month YTD records (fp=Q3, 260–285 days): same period_start key
            ytd_seen: dict[str, dict] = {}
            for o in all_obs:
                if o.get("fp") != "Q3":
                    continue
                dur = _duration_days(o)
                if dur is None or not (260 <= dur <= 285):
                    continue
                start = o.get("start", "")
                if not start:
                    continue
                if start not in ytd_seen or o.get("filed", "") > ytd_seen[start].get("filed", ""):
                    ytd_seen[start] = o

            # Match annual ↔ nine-month YTD by period_start → derive Q4
            for start, ann in ann_seen.items():
                ytd = ytd_seen.get(start)
                if ytd is None:
                    continue
                ann_val = ann.get("val")
                ytd_val = ytd.get("val")
                if ann_val is None or ytd_val is None:
                    continue
                q4_val = ann_val - ytd_val
                # Q4 period: start = day after nine-month end, end = annual end
                try:
                    ytd_end = datetime.strptime(ytd.get("end", ""), "%Y-%m-%d").date()
                    q4_start = str(ytd_end + timedelta(days=1))
                except (ValueError, TypeError):
                    continue
                q4_end = ann.get("end", "")
                derived_q4_obs.append({
                    "start": q4_start,
                    "end": q4_end,
                    "val": q4_val,
                    "fp": "Q4",
                    "form": ann.get("form", ""),
                    "accn": ann.get("accn", ""),
                    "fy": ann.get("fy"),
                    "filed": ann.get("filed", ""),
                    "_derived": True,
                    "_derivation": (
                        f"annual ({ann.get('accn','')}) minus "
                        f"nine-month YTD ({ytd.get('accn','')})"
                    ),
                })

        # Merge Q1–Q3 real rows with derived Q4 rows, re-sort, then limit
        combined = quarterly_obs + derived_q4_obs
        combined.sort(key=lambda o: o.get("end", ""), reverse=True)
        sliced = combined[:limit]

        # Build final observations list
        observations = []
        for o in sliced:
            fp = o.get("fp", "")
            end = o.get("end", "")
            try:
                fiscal_year = _fiscal_year_for(end, fye_mmdd)
            except Exception:
                fiscal_year = o.get("fy")
            period_label = f"{fp} FY{fiscal_year}" if fp and fiscal_year else fp
            is_derived = bool(o.get("_derived"))
            obs_entry: dict = {
                "period_label": period_label,
                "fiscal_quarter": fp,
                "fiscal_year": fiscal_year,
                "period_start": o.get("start") or None,
                "period_end": end,
                "value": o.get("val"),
                "form": o.get("form", ""),
                "accession_number": o.get("accn", ""),
                "filing_fiscal_year": o.get("fy"),
                "derived": is_derived,
            }
            if is_derived:
                obs_entry["derivation"] = o.get("_derivation", "")
            observations.append(obs_entry)

        if len(observations) < limit and len(quarterly_obs) < limit:
            note_parts.append(
                f"Only {len(observations)} quarterly observations available "
                f"(requested {limit})."
            )

        note = " ".join(note_parts)

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


# ---------------------------------------------------------------------------
# Tool 11 — Full-text search across all SEC filings (EFTS)
# ---------------------------------------------------------------------------

@mcp.tool(
    name="sec_edgar_full_text_search",
    annotations={
        "title": "Search SEC Filings by Keyword",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def sec_edgar_full_text_search(
    query: Annotated[str, (
        "Keyword or phrase to search for in filing text, e.g. 'artificial intelligence', "
        "'supply chain disruption', 'tariff impact'. Wrap multi-word phrases in quotes for "
        "exact matching, e.g. '\"going concern\"'."
    )],
    forms: Annotated[str, (
        "Comma-separated list of form types to restrict results, e.g. '10-K', '8-K,10-Q', "
        "'10-K,10-Q'. Leave empty to search all form types."
    )] = "",
    start_date: Annotated[str, "Earliest filing date to include (YYYY-MM-DD). Leave empty for no lower bound."] = "",
    end_date: Annotated[str, "Latest filing date to include (YYYY-MM-DD). Leave empty for no upper bound."] = "",
    identifier: Annotated[str, (
        "Optional ticker or CIK to scope the search to one company, "
        "e.g. 'AAPL' or '0000320193'. Leave empty to search all filers."
    )] = "",
    limit: Annotated[int, "Maximum number of results to return (default 10, max 40)."] = 10,
) -> dict:
    """Search the EDGAR full-text search index for filings whose text contains a keyword.

    Unlike sec_edgar_search_companies (which searches company names) or
    sec_edgar_get_recent_filings (which lists filings by company), this tool
    searches across the actual text content of all SEC filings and returns
    the filings that mention the query term.

    Useful for questions like:
      - "Which companies mentioned 'going concern' in their 2024 10-K filings?"
      - "Find Apple's 8-K filings that mention 'dividend'."
      - "What companies disclosed 'tariff impact' in recent filings?"

    Use sec_edgar_get_filing_text with the returned accession_number to read
    the actual text of any matching filing.

    Returns a dict with keys:
      query           — the search query as submitted
      forms           — form type filter (empty = all)
      total_matches   — total number of matching filings in EDGAR (may exceed limit)
      results         — list of matching filings (up to limit entries), each with:
          accession_number  — filing identifier
          form              — form type (10-K, 8-K, …)
          filing_date       — YYYY-MM-DD
          period_ending     — reporting period end date (may be empty)
          company           — company name
          ticker            — primary ticker (may be empty)
          cik               — 10-digit CIK
          filing_index_url  — direct link to the EDGAR filing index

    On failure returns {"error": "...", "hint": "..."}.
    """
    query = query.strip()
    if not query:
        return {
            "error": "query must not be empty.",
            "hint": "Provide a keyword or phrase, e.g. 'going concern' or 'artificial intelligence'.",
        }
    limit = max(1, min(limit, 40))

    try:
        # --- Build EFTS URL ---------------------------------------------------
        encoded_q = _url_quote(query)
        url_parts = [
            f"https://efts.sec.gov/LATEST/search-index?q={encoded_q}",
        ]

        if forms.strip():
            # Comma-separated → repeated &forms= params
            for form in forms.split(","):
                form = form.strip()
                if form:
                    url_parts.append(f"forms={_url_quote(form)}")

        if start_date.strip() or end_date.strip():
            url_parts.append("dateRange=custom")
            if start_date.strip():
                url_parts.append(f"startdt={_url_quote(start_date.strip())}")
            if end_date.strip():
                url_parts.append(f"enddt={_url_quote(end_date.strip())}")

        # Scope to a single company if identifier provided
        if identifier.strip():
            id_clean = identifier.strip()
            if id_clean.isdigit():
                url_parts.append(f"entity={_url_quote(id_clean)}")
            else:
                # Resolve ticker → CIK for the entity param
                await _ensure_ticker_cache()
                record = _TICKER_CACHE.get(id_clean.upper())
                if record:
                    url_parts.append(f"entity={_url_quote(record['cik_str'])}")
                else:
                    url_parts.append(f"entity={_url_quote(id_clean)}")

        # EFTS returns up to 100 hits per page; we only need `limit`
        url_parts.append(f"hits.hits._source=adsh,display_names,file_date,form,period_ending")
        full_url = url_parts[0] + "&" + "&".join(url_parts[1:]) if len(url_parts) > 1 else url_parts[0]

        resp = await _edgar_get(full_url, headers=_make_headers(), timeout=15.0)
        resp.raise_for_status()
        data = resp.json()

        hits_data = data.get("hits", {})
        total = hits_data.get("total", {})
        total_value = total.get("value", 0) if isinstance(total, dict) else int(total)
        raw_hits = hits_data.get("hits", [])[:limit]

        results = []
        for hit in raw_hits:
            src = hit.get("_source", {})
            accession_dashed = _normalize_accession(src.get("adsh", ""))
            accession_path = _accession_to_path(accession_dashed)

            # Parse the first display_name entry for company name, ticker, CIK
            display_names = src.get("display_names", [])
            parsed = _parse_display_name(display_names[0]) if display_names else None

            company = parsed["name"] if parsed else ""
            ticker = parsed.get("ticker", "") if parsed else ""
            cik = parsed["cik"] if parsed else ""
            if cik:
                cik = f"{int(cik):010d}"
                filing_index_url = (
                    f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_path}/"
                )
            else:
                filing_index_url = ""

            results.append({
                "accession_number": accession_dashed,
                "form": src.get("form", ""),
                "filing_date": src.get("file_date", ""),
                "period_ending": src.get("period_ending", ""),
                "company": company,
                "ticker": ticker,
                "cik": cik,
                "filing_index_url": filing_index_url,
            })

        return {
            "query": query,
            "forms": forms.strip(),
            "total_matches": total_value,
            "results": results,
        }

    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        return {"error": str(exc), "hint": "EDGAR full-text search may be temporarily unavailable; try again shortly."}
    except Exception as exc:
        return {
            "error": f"Unexpected error: {type(exc).__name__}: {exc}",
            "hint": "Report this to the toolkit maintainer; do not retry with the same arguments.",
        }


if __name__ == "__main__":
    mcp.run(transport="stdio")
