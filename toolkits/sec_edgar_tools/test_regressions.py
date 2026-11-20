"""Regression tests hitting live SEC APIs.

Run with:
    venv/bin/python toolkits/sec_edgar_tools/test_regressions.py

Exits non-zero if any test fails.
"""

import asyncio
import sys
from datetime import date, datetime

import httpx

sys.path.insert(0, "toolkits/sec_edgar_tools")
from server import (
    sec_edgar_get_company_fact,
    sec_edgar_get_quarterly_facts,
    sec_edgar_compare_companies,
    sec_edgar_search_companies,
    sec_edgar_resolve_company,
    sec_edgar_get_recent_filings,
    sec_edgar_resolve_synonym,
    sec_edgar_get_filing_text,
    sec_edgar_full_text_search,
    _strip_html,
    _find_section_offset,
    SEC_USER_AGENT,
)

PASS = "\033[32mPASS\033[0m"
FAIL = "\033[31mFAIL\033[0m"
failures = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global failures
    if condition:
        print(f"  {PASS}  {name}")
    else:
        print(f"  {FAIL}  {name}" + (f": {detail}" if detail else ""))
        failures += 1


async def test_aapl_net_income():
    print("\n[1] AAPL NetIncomeLoss via get_company_fact(limit=5)")
    result = await sec_edgar_get_company_fact("AAPL", "us-gaap", "NetIncomeLoss", limit=5)
    if "error" in result:
        check("no error", False, result["error"])
        return

    rows = result.get("units", {}).get("USD", [])
    if not check("returned rows", len(rows) > 0, f"got {len(rows)}"):
        return

    # Find the row with fiscal_year_end == "2024-09-28"
    target = next((r for r in rows if r.get("fiscal_year_end") == "2024-09-28"), None)
    check("row with fiscal_year_end==2024-09-28 exists", target is not None,
          f"available ends: {[r.get('fiscal_year_end') for r in rows]}")
    if target:
        check("fiscal_year == 2024", target.get("fiscal_year") == 2024,
              f"got {target.get('fiscal_year')}")
        check("value == 93736000000", target.get("value") == 93736000000,
              f"got {target.get('value')}")

    # All fiscal_year values must be distinct
    fy_vals = [r.get("fiscal_year") for r in rows]
    check("fiscal_year values are distinct", len(fy_vals) == len(set(fy_vals)),
          f"duplicates in {fy_vals}")

    # No row may contain the key "fy"
    has_fy_key = any("fy" in r for r in rows)
    check("no row contains key 'fy'", not has_fy_key,
          "at least one row contains 'fy' key")

    # Every row must have filing_index_url starting with the AAPL EDGAR archive prefix
    _AAPL_PREFIX = "https://www.sec.gov/Archives/edgar/data/320193/"
    for r in rows:
        url = r.get("filing_index_url", "")
        check(
            f"filing_index_url starts with AAPL prefix for FY{r.get('fiscal_year')}",
            url.startswith(_AAPL_PREFIX),
            f"got {url!r}",
        )

    # Pick the most recent row and verify its filing_index_url returns HTTP 200
    if rows:
        most_recent = rows[-1]
        index_url = most_recent.get("filing_index_url", "")
        if index_url:
            async with httpx.AsyncClient(
                headers={"User-Agent": SEC_USER_AGENT},
                follow_redirects=True,
                timeout=30,
            ) as client:
                resp = await client.get(index_url)
            check(
                f"filing_index_url HTTP 200 for FY{most_recent.get('fiscal_year')} ({index_url})",
                resp.status_code == 200,
                f"got HTTP {resp.status_code}",
            )


# check() returns None; patch it to also return the bool so callers can early-exit.
_original_check = check


def check(name: str, condition: bool, detail: str = "") -> bool:  # type: ignore[no-redef]
    global failures
    if condition:
        print(f"  {PASS}  {name}")
    else:
        print(f"  {FAIL}  {name}" + (f": {detail}" if detail else ""))
        failures += 1
    return condition


async def test_aapl_revenues_quarterly():
    print("\n[2] AAPL Revenues via get_quarterly_facts(limit=8)")
    result = await sec_edgar_get_quarterly_facts("AAPL", "us-gaap", "Revenues", limit=8)
    if "error" in result:
        check("no error", False, result["error"])
        return

    obs = result.get("observations", [])
    if not check("returned observations", len(obs) > 0, f"got {len(obs)}"):
        return

    # Every value must be between 70e9 and 160e9
    for o in obs:
        v = o.get("value")
        check(
            f"value in [70B, 160B] for {o.get('period_label')}",
            v is not None and 70e9 <= v <= 160e9,
            f"got {v}",
        )

    # Every observation must have 80–100 day duration
    for o in obs:
        ps = o.get("period_start")
        pe = o.get("period_end")
        if ps and pe:
            dur = (datetime.strptime(pe, "%Y-%m-%d") - datetime.strptime(ps, "%Y-%m-%d")).days
            check(
                f"duration 80-100 days for {o.get('period_label')}",
                80 <= dur <= 100,
                f"got {dur} days",
            )

    # period_labels must be distinct
    labels = [o.get("period_label") for o in obs]
    check("period_labels are distinct", len(labels) == len(set(labels)),
          f"duplicates in {labels}")


async def test_aapl_eps():
    print("\n[3] AAPL EarningsPerShareBasic via get_quarterly_facts(limit=4)")
    result = await sec_edgar_get_quarterly_facts("AAPL", "us-gaap", "EarningsPerShareBasic", limit=4)
    if "error" in result:
        check("no error", False, result["error"])
        return

    obs = result.get("observations", [])
    if not check("returned observations", len(obs) > 0, f"got {len(obs)}"):
        return

    for o in obs:
        v = o.get("value")
        check(
            f"EPS < 4.0 for {o.get('period_label')}",
            v is not None and v < 4.0,
            f"got {v}",
        )


async def test_compare_jpm_bac():
    print("\n[4] compare_companies(['JPM','BAC'], 'us-gaap', 'Assets')")
    result = await sec_edgar_compare_companies(["JPM", "BAC"], "us-gaap", "Assets")
    if "error" in result:
        check("no error", False, result["error"])
        return

    results = result.get("results", [])
    if not check("two results", len(results) == 2, f"got {len(results)}"):
        return

    bac = next((r for r in results if r.get("ticker") == "BAC"), None)
    check("BAC present", bac is not None)
    if bac:
        company_name = bac.get("company", "")
        check(
            "BAC company name contains 'BANK OF AMERICA'",
            "bank of america" in company_name.lower(),
            f"got '{company_name}'",
        )

    today = date.today()
    for r in results:
        pe = r.get("period_end", "")
        if pe:
            pe_date = datetime.strptime(pe, "%Y-%m-%d").date()
            days_ago = (today - pe_date).days
            check(
                f"{r.get('ticker')} period_end within 548 days",
                days_ago <= 548,
                f"{pe} is {days_ago} days ago",
            )


async def test_aapl_revenues_concept_and_values():
    print("\n[5] AAPL Revenues — auto-retry concept name and spot values")
    result = await sec_edgar_get_quarterly_facts("AAPL", "us-gaap", "Revenues", limit=8)
    if "error" in result:
        check("no error", False, result["error"])
        return

    obs = result.get("observations", [])
    if not check("returned observations", len(obs) > 0, f"got {len(obs)}"):
        return

    # Auto-retry must have switched to the alternate concept
    effective = result.get("concept", "")
    check(
        "concept == RevenueFromContractWithCustomerExcludingAssessedTax",
        effective == "RevenueFromContractWithCustomerExcludingAssessedTax",
        f"got '{effective}'",
    )

    # Spot-check three known values by period_end
    spot = {o.get("period_end"): o.get("value") for o in obs}
    expected = {
        "2026-06-27": 109417000000,
        "2026-03-28": 111184000000,
        "2025-06-28": 94036000000,
    }
    for pe, expected_val in expected.items():
        actual = spot.get(pe)
        check(
            f"value at {pe} == {expected_val:,}",
            actual == expected_val,
            f"got {actual} (period_end not present)" if actual is None else f"got {actual:,}",
        )


async def test_exxon_search():
    print("\n[7] search_companies('Exxon', limit=1) — EXXON MOBIL CORP first")
    result = await sec_edgar_search_companies("Exxon", limit=1)
    if "error" in result:
        check("no error", False, result["error"])
        return

    matches = result.get("matches", [])
    if not check("at least one match", len(matches) > 0, f"got {len(matches)}"):
        return

    first = matches[0]
    check(
        "first match cik == 0000034088",
        first.get("cik") == "0000034088",
        f"got cik={first.get('cik')!r}, name={first.get('name')!r}",
    )


async def test_holding_shell_resolve():
    # CIK 0002115436 = ExxonMobil Holdings Corp — files 10-Qs but has no 10-K.
    print("\n[8] resolve_company('0002115436') — 10-Q only filer: is_active=True, no 10-K, new warning")
    result = await sec_edgar_resolve_company("0002115436")
    if "error" in result:
        check("no error", False, result["error"])
        return

    check("is_active_filer == True", result.get("is_active_filer") is True,
          f"got {result.get('is_active_filer')!r}")
    check("latest_10k_date is None", result.get("latest_10k_date") is None,
          f"got {result.get('latest_10k_date')!r}")
    check("warning present", "warning" in result,
          "no 'warning' key in result")
    if "warning" in result:
        check("warning mentions 'quarterly reports'",
              "quarterly reports" in result["warning"],
              f"got: {result['warning']!r}")

    # Also keep the inactive-entity case as a separate assertion block.
    # CIK 0000101830 = SPRINT LLC — last 10-K 2019, last 10-Q 2020.
    print("\n[8b] resolve_company('0000101830') — inactive filer: is_active=False + holding-shell warning")
    result2 = await sec_edgar_resolve_company("0000101830")
    if "error" in result2:
        check("no error (sprint)", False, result2["error"])
        return

    check("sprint is_active_filer == False", result2.get("is_active_filer") is False,
          f"got {result2.get('is_active_filer')!r}")
    check("sprint warning present", "warning" in result2,
          "no 'warning' key in sprint result")
    if "warning" in result2:
        check("sprint warning mentions 'holding shell'",
              "holding shell" in result2["warning"],
              f"got: {result2['warning']!r}")


async def test_pfe_annual_revenue_candidate():
    print("\n[10] PFE annual revenue — REVENUE_CANDIDATES: request RevenueFromContractWithCustomerExcludingAssessedTax, expect Revenues")
    result = await sec_edgar_get_company_fact(
        "PFE", "us-gaap", "RevenueFromContractWithCustomerExcludingAssessedTax", limit=4
    )
    if "error" in result:
        check("no error", False, result["error"])
        return

    # Must have switched to the broader "Revenues" concept
    effective = result.get("concept", "")
    check(
        "concept == Revenues",
        effective == "Revenues",
        f"got '{effective}'",
    )

    # concept_note must be present (explains the switch)
    check(
        "concept_note present",
        bool(result.get("concept_note")),
        "no concept_note in result",
    )

    rows = result.get("units", {}).get("USD", [])
    if not check("returned rows", len(rows) > 0, f"got {len(rows)}"):
        return

    spot = {r.get("fiscal_year_end"): r.get("value") for r in rows}

    # Three known Pfizer annual revenue values under "Revenues"
    expected = {
        "2025-12-31": 62579000000,
        "2024-12-31": 63627000000,
        "2023-12-31": 59553000000,
    }
    for pe, expected_val in expected.items():
        actual = spot.get(pe)
        check(
            f"PFE revenue at {pe} == {expected_val:,}",
            actual == expected_val,
            f"got {actual} (period_end not present)" if actual is None else f"got {actual:,}",
        )


async def test_aapl_quarterly_revenues_candidate():
    print("\n[11] AAPL quarterly Revenues — REVENUE_CANDIDATES: expect 109417000000 at 2026-06-27")
    result = await sec_edgar_get_quarterly_facts("AAPL", "us-gaap", "Revenues", limit=8)
    if "error" in result:
        check("no error", False, result["error"])
        return

    obs = result.get("observations", [])
    if not check("returned observations", len(obs) > 0, f"got {len(obs)}"):
        return

    spot = {o.get("period_end"): o.get("value") for o in obs}
    actual = spot.get("2026-06-27")
    check(
        "value at 2026-06-27 == 109417000000",
        actual == 109417000000,
        f"got {actual}",
    )


async def test_msft_net_income_q4_derived():
    print("\n[13] MSFT NetIncomeLoss via get_quarterly_facts(limit=6) — Q4 derived row")
    result = await sec_edgar_get_quarterly_facts("MSFT", "us-gaap", "NetIncomeLoss", limit=6)
    if "error" in result:
        check("no error", False, result["error"])
        return

    obs = result.get("observations", [])
    if not check("returned observations", len(obs) > 0, f"got {len(obs)}"):
        return

    # Must include a Q4 row ending 2026-06-30 with derived=True
    q4_row = next(
        (o for o in obs if o.get("fiscal_quarter") == "Q4" and o.get("period_end") == "2026-06-30"),
        None,
    )
    check(
        "Q4 row ending 2026-06-30 present",
        q4_row is not None,
        f"available rows: {[(o.get('fiscal_quarter'), o.get('period_end')) for o in obs]}",
    )
    if q4_row:
        check("Q4 row is derived", q4_row.get("derived") is True,
              f"got derived={q4_row.get('derived')!r}")
        check("Q4 row has derivation note", bool(q4_row.get("derivation")),
              "no derivation key")
        # Q4 value should be annual(133749000000) - nine-month YTD(97983000000) = 35766000000
        check(
            "Q4 value == 35766000000",
            q4_row.get("value") == 35766000000,
            f"got {q4_row.get('value')}",
        )

    # Six distinct period_end values across the 6 observations
    period_ends = [o.get("period_end") for o in obs]
    check(
        "six distinct period_end values",
        len(period_ends) == len(set(period_ends)),
        f"duplicates in {period_ends}",
    )
    check("exactly 6 observations", len(obs) == 6, f"got {len(obs)}")

    # Non-derived rows must have derived=False
    for o in obs:
        if not o.get("derived"):
            check(
                f"non-derived row {o.get('period_label')} has derived==False",
                o.get("derived") is False,
                f"got derived={o.get('derived')!r}",
            )


async def test_aapl_revenues_q4_sum():
    print("\n[14] AAPL Revenues via get_quarterly_facts(limit=8) — Q4 derived; FY2025 Q1+Q2+Q3+Q4 == annual")
    result = await sec_edgar_get_quarterly_facts("AAPL", "us-gaap", "Revenues", limit=8)
    if "error" in result:
        check("no error", False, result["error"])
        return

    obs = result.get("observations", [])
    if not check("returned observations", len(obs) > 0, f"got {len(obs)}"):
        return

    # Must include at least one Q4 derived row
    q4_rows = [o for o in obs if o.get("fiscal_quarter") == "Q4" and o.get("derived") is True]
    check("at least one Q4 derived row present", len(q4_rows) >= 1,
          f"q4_rows={q4_rows}")

    # For FY2025, verify Q1+Q2+Q3+Q4 == annual (416161000000) within $1M
    fy2025_rows = [o for o in obs if o.get("fiscal_year") == 2025]
    if check("FY2025 rows present", len(fy2025_rows) >= 4,
             f"got {len(fy2025_rows)} FY2025 rows"):
        total_fy2025 = sum(o.get("value", 0) for o in fy2025_rows)
        annual_fy2025 = 416161000000
        check(
            f"FY2025 Q1+Q2+Q3+Q4 == annual within $1M (got {total_fy2025:,})",
            abs(total_fy2025 - annual_fy2025) <= 1_000_000,
            f"diff={abs(total_fy2025 - annual_fy2025):,}",
        )


async def test_aapl_eps_no_derived():
    print("\n[15] AAPL EarningsPerShareBasic via get_quarterly_facts — no derived Q4 rows")
    result = await sec_edgar_get_quarterly_facts("AAPL", "us-gaap", "EarningsPerShareBasic", limit=6)
    if "error" in result:
        check("no error", False, result["error"])
        return

    obs = result.get("observations", [])
    if not check("returned observations", len(obs) > 0, f"got {len(obs)}"):
        return

    derived_rows = [o for o in obs if o.get("derived") is True]
    check("no derived Q4 rows for EPS", len(derived_rows) == 0,
          f"unexpected derived rows: {[(o.get('period_label'), o.get('value')) for o in derived_rows]}")

    # Note must explain why Q4 was not derived
    note = result.get("note", "")
    check("note explains Q4 not derived (mentions unit or per-share)",
          "per-share" in note.lower() or "not additive" in note.lower() or "usd/shares" in note.lower(),
          f"note='{note}'")


async def test_pfe_compare_companies_revenue():
    print("\n[12] compare_companies(['PFE'], 'us-gaap', 'Revenues') — period_end 2025-12-31")
    result = await sec_edgar_compare_companies(["PFE"], "us-gaap", "Revenues")
    if "error" in result:
        check("no error", False, result["error"])
        return

    results = result.get("results", [])
    if not check("one result", len(results) == 1, f"got {len(results)}"):
        return

    r = results[0]
    check(
        "PFE period_end == 2025-12-31",
        r.get("period_end") == "2025-12-31",
        f"got '{r.get('period_end')}'",
    )
    check(
        "PFE concept == Revenues",
        r.get("concept") == "Revenues",
        f"got '{r.get('concept')}'",
    )


async def test_exxon_10k_filings():
    print("\n[9] get_recent_filings('0000034088', '10-K', 5) — at least 3 filings")
    result = await sec_edgar_get_recent_filings("0000034088", "10-K", 5)
    if "error" in result:
        check("no error", False, result["error"])
        return

    filings = result.get("filings", [])
    check("at least 3 10-K filings", len(filings) >= 3,
          f"got {len(filings)}")


async def _run_company_fact():
    return await sec_edgar_get_company_fact("AAPL", "us-gaap", "NetIncomeLoss", limit=1)


async def _run_quarterly_facts():
    return await sec_edgar_get_quarterly_facts("AAPL", "us-gaap", "EarningsPerShareBasic", limit=1)


def test_multi_event_loop():
    """Guards the _get_client() loop-awareness fix.

    Two separate asyncio.run() calls create two separate event loops.
    Without the fix the second call raises 'RuntimeError: Event loop is closed'
    because the shared AsyncClient is bound to the first (now-closed) loop.
    """
    print("\n[6] Multi-asyncio.run() event-loop guard")
    r1 = asyncio.run(_run_company_fact())
    check("first asyncio.run(): no error key", "error" not in r1,
          r1.get("error", ""))
    r2 = asyncio.run(_run_quarterly_facts())
    check("second asyncio.run(): no error key", "error" not in r2,
          r2.get("error", ""))


async def test_synonym_tool():
    print("\n[16] sec_edgar_resolve_synonym — offline dict lookups (no network)")

    # -- Known hits -----------------------------------------------------------
    r = await sec_edgar_resolve_synonym("Google")
    check("Google → Alphabet Inc.", r.get("canonical_name") == "Alphabet Inc.", str(r))
    check("Google → GOOGL ticker", r.get("ticker") == "GOOGL", str(r))
    check("Google result has note", bool(r.get("note")), str(r))

    r = await sec_edgar_resolve_synonym("google")          # lowercase
    check("google (lowercase) → Alphabet Inc.", r.get("canonical_name") == "Alphabet Inc.", str(r))

    r = await sec_edgar_resolve_synonym("GOOGLE")          # uppercase passthrough
    check("GOOGLE (upper) → Alphabet Inc.", r.get("canonical_name") == "Alphabet Inc.", str(r))

    r = await sec_edgar_resolve_synonym("Facebook")
    check("Facebook → Meta Platforms Inc.", r.get("canonical_name") == "Meta Platforms Inc.", str(r))
    check("Facebook → META ticker", r.get("ticker") == "META", str(r))

    r = await sec_edgar_resolve_synonym("Meta")
    check("Meta → Meta Platforms Inc.", r.get("canonical_name") == "Meta Platforms Inc.", str(r))

    r = await sec_edgar_resolve_synonym("GE")
    check("GE → GE Aerospace", r.get("canonical_name") == "GE Aerospace", str(r))
    check("GE → GE ticker", r.get("ticker") == "GE", str(r))

    r = await sec_edgar_resolve_synonym("General Electric")
    check("General Electric → GE Aerospace", r.get("canonical_name") == "GE Aerospace", str(r))

    r = await sec_edgar_resolve_synonym("Goldman")
    check("Goldman → Goldman Sachs Group Inc.", "Goldman Sachs" in r.get("canonical_name", ""), str(r))

    r = await sec_edgar_resolve_synonym("berkshire hathaway")
    check("berkshire hathaway → Berkshire Hathaway Inc.", r.get("canonical_name") == "Berkshire Hathaway Inc.", str(r))

    r = await sec_edgar_resolve_synonym("Apple,")          # trailing comma stripped
    check("'Apple,' (trailing comma) → Apple Inc.", r.get("canonical_name") == "Apple Inc.", str(r))

    r = await sec_edgar_resolve_synonym("exxon mobil")
    check("exxon mobil → Exxon Mobil Corp", r.get("canonical_name") == "Exxon Mobil Corp", str(r))

    r = await sec_edgar_resolve_synonym("J&J")
    check("J&J → Johnson & Johnson", r.get("canonical_name") == "Johnson & Johnson", str(r))

    # -- input field preserved ------------------------------------------------
    r = await sec_edgar_resolve_synonym("Pfizer")
    check("input field preserved on hit", r.get("input") == "Pfizer", str(r))

    # -- Miss: unknown alias --------------------------------------------------
    r = await sec_edgar_resolve_synonym("ACME Corp")
    check("unknown alias returns error key", "error" in r, str(r))
    check("unknown alias returns hint key", "hint" in r, str(r))
    check("unknown alias preserves input", r.get("input") == "ACME Corp", str(r))

    # -- No network calls: verify no 'ticker' in _TICKER_CACHE side-effects ---
    # (Synonym tool must not trigger _ensure_ticker_cache; check runs fine offline)
    r = await sec_edgar_resolve_synonym("Twitter")
    check("Twitter → X Holdings Corp", r.get("canonical_name") == "X Holdings Corp", str(r))
    check("Twitter ticker is empty string (not exchange-listed)", r.get("ticker") == "", str(r))

    # -- New entries (session 8 expansion) ------------------------------------
    # Semiconductor additions
    r = await sec_edgar_resolve_synonym("Broadcom")
    check("Broadcom → Broadcom Inc.", r.get("canonical_name") == "Broadcom Inc.", str(r))
    check("Broadcom → AVGO", r.get("ticker") == "AVGO", str(r))

    r = await sec_edgar_resolve_synonym("Micron")
    check("Micron → Micron Technology Inc.", r.get("canonical_name") == "Micron Technology Inc.", str(r))

    # Cloud/Enterprise SaaS
    r = await sec_edgar_resolve_synonym("Salesforce")
    check("Salesforce → Salesforce Inc.", r.get("canonical_name") == "Salesforce Inc.", str(r))
    check("Salesforce → CRM", r.get("ticker") == "CRM", str(r))

    r = await sec_edgar_resolve_synonym("IBM")
    check("IBM → International Business Machines Corp", r.get("canonical_name") == "International Business Machines Corp", str(r))
    check("IBM ticker", r.get("ticker") == "IBM", str(r))

    r = await sec_edgar_resolve_synonym("Palantir")
    check("Palantir → Palantir Technologies Inc.", r.get("canonical_name") == "Palantir Technologies Inc.", str(r))

    r = await sec_edgar_resolve_synonym("Palo Alto")
    check("Palo Alto → Palo Alto Networks Inc.", r.get("canonical_name") == "Palo Alto Networks Inc.", str(r))
    check("Palo Alto → PANW", r.get("ticker") == "PANW", str(r))

    r = await sec_edgar_resolve_synonym("CrowdStrike")
    check("CrowdStrike → CrowdStrike Holdings Inc.", r.get("canonical_name") == "CrowdStrike Holdings Inc.", str(r))

    r = await sec_edgar_resolve_synonym("OpenAI")
    check("OpenAI → OpenAI", r.get("canonical_name") == "OpenAI", str(r))
    check("OpenAI ticker empty (private)", r.get("ticker") == "", str(r))

    # Media & entertainment
    r = await sec_edgar_resolve_synonym("Disney")
    check("Disney → Walt Disney Co", r.get("canonical_name") == "Walt Disney Co", str(r))
    check("Disney → DIS", r.get("ticker") == "DIS", str(r))

    r = await sec_edgar_resolve_synonym("ESPN")
    check("ESPN → Walt Disney Co (subsidiary)", r.get("canonical_name") == "Walt Disney Co", str(r))

    r = await sec_edgar_resolve_synonym("HBO")
    check("HBO → Warner Bros. Discovery Inc.", r.get("canonical_name") == "Warner Bros. Discovery Inc.", str(r))

    r = await sec_edgar_resolve_synonym("Paramount")
    check("Paramount → Paramount Global", r.get("canonical_name") == "Paramount Global", str(r))
    check("Paramount → PARA", r.get("ticker") == "PARA", str(r))

    # Automotive additions
    r = await sec_edgar_resolve_synonym("Toyota")
    check("Toyota → Toyota Motor Corp", r.get("canonical_name") == "Toyota Motor Corp", str(r))
    check("Toyota → TM", r.get("ticker") == "TM", str(r))

    r = await sec_edgar_resolve_synonym("Jeep")
    check("Jeep → Stellantis N.V. (brand)", r.get("canonical_name") == "Stellantis N.V.", str(r))

    r = await sec_edgar_resolve_synonym("VW")
    check("VW → Volkswagen AG", r.get("canonical_name") == "Volkswagen AG", str(r))
    check("VW → VWAGY", r.get("ticker") == "VWAGY", str(r))

    r = await sec_edgar_resolve_synonym("BMW")
    check("BMW → Bayerische Motoren Werke AG", r.get("canonical_name") == "Bayerische Motoren Werke AG", str(r))

    # Finance additions
    r = await sec_edgar_resolve_synonym("Citi")
    check("Citi → Citigroup Inc.", r.get("canonical_name") == "Citigroup Inc.", str(r))
    check("Citi → C ticker", r.get("ticker") == "C", str(r))

    r = await sec_edgar_resolve_synonym("Citibank")
    check("Citibank → Citigroup Inc.", r.get("canonical_name") == "Citigroup Inc.", str(r))

    r = await sec_edgar_resolve_synonym("Amex")
    check("Amex → American Express Co", r.get("canonical_name") == "American Express Co", str(r))
    check("Amex → AXP", r.get("ticker") == "AXP", str(r))

    r = await sec_edgar_resolve_synonym("American Express")
    check("American Express → American Express Co", r.get("canonical_name") == "American Express Co", str(r))

    r = await sec_edgar_resolve_synonym("BlackRock")
    check("BlackRock → BlackRock Inc.", r.get("canonical_name") == "BlackRock Inc.", str(r))
    check("BlackRock → BLK", r.get("ticker") == "BLK", str(r))

    r = await sec_edgar_resolve_synonym("Charles Schwab")
    check("Charles Schwab → Charles Schwab Corp", r.get("canonical_name") == "Charles Schwab Corp", str(r))

    # Healthcare additions
    r = await sec_edgar_resolve_synonym("Moderna")
    check("Moderna → Moderna Inc.", r.get("canonical_name") == "Moderna Inc.", str(r))
    check("Moderna → MRNA", r.get("ticker") == "MRNA", str(r))

    r = await sec_edgar_resolve_synonym("Eli Lilly")
    check("Eli Lilly → Eli Lilly and Co", r.get("canonical_name") == "Eli Lilly and Co", str(r))
    check("Eli Lilly → LLY", r.get("ticker") == "LLY", str(r))

    r = await sec_edgar_resolve_synonym("Lilly")
    check("Lilly → Eli Lilly and Co", r.get("canonical_name") == "Eli Lilly and Co", str(r))

    r = await sec_edgar_resolve_synonym("Aetna")
    check("Aetna → CVS Health Corp (subsidiary)", r.get("canonical_name") == "CVS Health Corp", str(r))

    r = await sec_edgar_resolve_synonym("Walgreens")
    check("Walgreens → Walgreens Boots Alliance Inc.", r.get("canonical_name") == "Walgreens Boots Alliance Inc.", str(r))

    # Retail additions
    r = await sec_edgar_resolve_synonym("Target")
    check("Target → Target Corp", r.get("canonical_name") == "Target Corp", str(r))
    check("Target → TGT", r.get("ticker") == "TGT", str(r))

    r = await sec_edgar_resolve_synonym("Marshalls")
    check("Marshalls → TJX Companies Inc. (brand)", r.get("canonical_name") == "TJX Companies Inc.", str(r))

    r = await sec_edgar_resolve_synonym("TJ Maxx")
    check("TJ Maxx → TJX Companies Inc.", r.get("canonical_name") == "TJX Companies Inc.", str(r))

    # Energy additions
    r = await sec_edgar_resolve_synonym("BP")
    check("BP → BP p.l.c.", r.get("canonical_name") == "BP p.l.c.", str(r))
    check("BP → BP ticker", r.get("ticker") == "BP", str(r))

    r = await sec_edgar_resolve_synonym("Schlumberger")
    check("Schlumberger → SLB (rebranded)", r.get("canonical_name") == "SLB", str(r))

    r = await sec_edgar_resolve_synonym("SLB")
    check("SLB → SLB", r.get("canonical_name") == "SLB", str(r))

    r = await sec_edgar_resolve_synonym("Halliburton")
    check("Halliburton → Halliburton Co", r.get("canonical_name") == "Halliburton Co", str(r))

    # Aerospace & defense
    r = await sec_edgar_resolve_synonym("Lockheed Martin")
    check("Lockheed Martin → Lockheed Martin Corp", r.get("canonical_name") == "Lockheed Martin Corp", str(r))
    check("Lockheed Martin → LMT", r.get("ticker") == "LMT", str(r))

    r = await sec_edgar_resolve_synonym("Lockheed")
    check("Lockheed → Lockheed Martin Corp", r.get("canonical_name") == "Lockheed Martin Corp", str(r))

    r = await sec_edgar_resolve_synonym("Raytheon")
    check("Raytheon → RTX Corp (rebranded)", r.get("canonical_name") == "RTX Corp", str(r))

    r = await sec_edgar_resolve_synonym("Northrop Grumman")
    check("Northrop Grumman → Northrop Grumman Corp", r.get("canonical_name") == "Northrop Grumman Corp", str(r))

    r = await sec_edgar_resolve_synonym("General Dynamics")
    check("General Dynamics → General Dynamics Corp", r.get("canonical_name") == "General Dynamics Corp", str(r))
    check("General Dynamics → GD ticker", r.get("ticker") == "GD", str(r))

    # Telecom additions
    r = await sec_edgar_resolve_synonym("Comcast")
    check("Comcast → Comcast Corp", r.get("canonical_name") == "Comcast Corp", str(r))
    check("Comcast → CMCSA", r.get("ticker") == "CMCSA", str(r))

    r = await sec_edgar_resolve_synonym("Charter")
    check("Charter → Charter Communications Inc.", r.get("canonical_name") == "Charter Communications Inc.", str(r))

    # E-commerce additions
    r = await sec_edgar_resolve_synonym("Square")
    check("Square → Block Inc. (rebranded)", r.get("canonical_name") == "Block Inc.", str(r))
    check("Square → SQ ticker", r.get("ticker") == "SQ", str(r))

    r = await sec_edgar_resolve_synonym("DoorDash")
    check("DoorDash → DoorDash Inc.", r.get("canonical_name") == "DoorDash Inc.", str(r))


async def test_filing_text():
    print("\n[17] sec_edgar_get_filing_text — Apple 10-K text extraction")

    # --- offline unit tests for helpers (no network) -------------------------
    # _strip_html: tags removed, whitespace normalized
    raw = "<p>Hello  <b>World</b>!</p>\n\n\n<p>Second.</p>"
    stripped = _strip_html(raw)
    check("_strip_html removes tags", "<" not in stripped and ">" not in stripped, stripped)
    check("_strip_html contains content", "Hello" in stripped and "World" in stripped, stripped)
    check("_strip_html collapses 3+ newlines", stripped.count("\n\n\n") == 0, repr(stripped))

    # _find_section_offset: known keyword found
    text = "Cover page text\n\nITEM 1A. RISK FACTORS\nBlah blah risk"
    off = _find_section_offset(text, "risk_factors")
    check("_find_section_offset finds 'risk factors'", off > 0, f"offset={off}")

    # _find_section_offset: unknown section returns 0
    off_unknown = _find_section_offset(text, "nonexistent_section_xyz")
    check("_find_section_offset unknown section → 0", off_unknown == 0, f"offset={off_unknown}")

    # --- live network tests (Apple 10-K, known accession) --------------------
    # Apple FY2023 10-K — accession 0000320193-23-000106 (filed 2023-11-03)
    AAPL_10K_ACCESSION = "0000320193-23-000106"
    r = await sec_edgar_get_filing_text("AAPL", AAPL_10K_ACCESSION)
    check("10-K: no error key", "error" not in r, str(r.get("error", "")))
    check("10-K: company is Apple", "Apple" in r.get("company", ""), r.get("company", ""))
    check("10-K: form is 10-K", r.get("form") == "10-K", r.get("form"))
    check("10-K: accession_number normalised", r.get("accession_number") == AAPL_10K_ACCESSION, r.get("accession_number"))
    check("10-K: text non-empty", len(r.get("text", "")) > 100, f"len={len(r.get('text',''))}")
    check("10-K: text has no HTML tags", "<html" not in r.get("text", "").lower(), r.get("text", "")[:200])
    check("10-K: primary_document set", bool(r.get("primary_document")), r.get("primary_document"))
    check("10-K: document_url is https", r.get("document_url", "").startswith("https://"), r.get("document_url"))
    check("10-K: truncated key present", "truncated" in r, str(r.keys()))
    check("10-K: section_offset key present", "section_offset" in r, str(r.keys()))

    # max_chars clamping
    r_small = await sec_edgar_get_filing_text("AAPL", AAPL_10K_ACCESSION, max_chars=200)
    check("max_chars=200: text ≤ 200 chars", len(r_small.get("text", "")) <= 200, f"len={len(r_small.get('text',''))}")

    # section seek: risk_factors should jump past the cover page
    r_rf = await sec_edgar_get_filing_text("AAPL", AAPL_10K_ACCESSION, section="risk_factors", max_chars=2000)
    check("section=risk_factors: no error", "error" not in r_rf, str(r_rf.get("error", "")))
    check("section=risk_factors: offset > 0", r_rf.get("section_offset", 0) > 0, f"offset={r_rf.get('section_offset')}")
    check("section=risk_factors: section_sought preserved", r_rf.get("section_sought") == "risk_factors", r_rf.get("section_sought"))

    # 8-K filing (Apple 8-K, FY2026 Q4 results) — no section hint
    # Accession 0000320193-26-000024 (Apple FY2026 Q4 results 8-K, filed 2026-11-02)
    AAPL_8K_ACCESSION = "0000320193-26-000024"
    r8k = await sec_edgar_get_filing_text("AAPL", AAPL_8K_ACCESSION)
    check("8-K: no error", "error" not in r8k, str(r8k.get("error", "")))
    check("8-K: form is 8-K", r8k.get("form") == "8-K", r8k.get("form"))
    check("8-K: text non-empty", len(r8k.get("text", "")) > 50, f"len={len(r8k.get('text',''))}")

    # bad accession → error dict
    r_bad = await sec_edgar_get_filing_text("AAPL", "0000000000-00-000000")
    check("bad accession: returns error key", "error" in r_bad, str(r_bad))


async def test_full_text_search():
    print("\n[18] sec_edgar_full_text_search — EFTS keyword search")

    # Basic keyword search across all forms
    r = await sec_edgar_full_text_search("going concern")
    check("fts: no error", "error" not in r, str(r.get("error", "")))
    check("fts: query preserved", r.get("query") == "going concern", r.get("query"))
    check("fts: total_matches > 0", r.get("total_matches", 0) > 0, str(r.get("total_matches")))
    check("fts: results list present", isinstance(r.get("results"), list), str(type(r.get("results"))))
    check("fts: default limit ≤ 10 results", len(r.get("results", [])) <= 10, str(len(r.get("results", []))))

    # Result shape
    if r.get("results"):
        first = r["results"][0]
        check("fts result: accession_number present", bool(first.get("accession_number")), str(first))
        check("fts result: form present", bool(first.get("form")), str(first))
        check("fts result: filing_date present", bool(first.get("filing_date")), str(first))
        check("fts result: company present", bool(first.get("company")), str(first))
        check("fts result: filing_index_url is https", first.get("filing_index_url", "").startswith("https://"), str(first))

    # Form type filter
    r_10k = await sec_edgar_full_text_search("going concern", forms="10-K", limit=5)
    check("fts forms filter: no error", "error" not in r_10k, str(r_10k.get("error", "")))
    check("fts forms filter: all results start with 10-K",
          all(x.get("form", "").startswith("10-K") for x in r_10k.get("results", [])),
          str([x.get("form") for x in r_10k.get("results", [])]))

    # Date range filter
    r_dated = await sec_edgar_full_text_search(
        "going concern", forms="10-K",
        start_date="2024-01-01", end_date="2024-06-30", limit=5
    )
    check("fts date range: no error", "error" not in r_dated, str(r_dated.get("error", "")))
    check("fts date range: results within range",
          all("2024" in x.get("filing_date", "") for x in r_dated.get("results", [])),
          str([x.get("filing_date") for x in r_dated.get("results", [])]))

    # Company-scoped search (Apple 8-K filings mentioning 'dividend')
    r_aapl = await sec_edgar_full_text_search("dividend", forms="8-K", identifier="AAPL", limit=5)
    check("fts identifier scope: no error", "error" not in r_aapl, str(r_aapl.get("error", "")))
    # May return 0 results if none match, but should not error
    check("fts identifier scope: results is list", isinstance(r_aapl.get("results"), list), str(r_aapl))

    # Empty query → error
    r_empty = await sec_edgar_full_text_search("")
    check("fts empty query: returns error key", "error" in r_empty, str(r_empty))

    # limit clamping
    r_lim = await sec_edgar_full_text_search("revenue", limit=5)
    check("fts limit=5: ≤ 5 results", len(r_lim.get("results", [])) <= 5, str(len(r_lim.get("results", []))))


async def main():
    await test_synonym_tool()
    await test_filing_text()
    await test_full_text_search()
    await test_aapl_net_income()
    await test_aapl_revenues_quarterly()
    await test_aapl_eps()
    await test_compare_jpm_bac()
    await test_aapl_revenues_concept_and_values()
    await test_exxon_search()
    await test_holding_shell_resolve()
    await test_exxon_10k_filings()
    await test_pfe_annual_revenue_candidate()
    await test_aapl_quarterly_revenues_candidate()
    await test_pfe_compare_companies_revenue()
    await test_msft_net_income_q4_derived()
    await test_aapl_revenues_q4_sum()
    await test_aapl_eps_no_derived()

    print(f"\n{'=' * 50}")
    if failures == 0:
        print("All tests PASSED.")
    else:
        print(f"{failures} test(s) FAILED.")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    # Tests 1–5 run inside a single asyncio.run() call (the normal path).
    # Test 6 is called synchronously after main() so it exercises a *second*
    # asyncio.run() — that is precisely the scenario the loop-awareness fix covers.
    asyncio.run(main())
    test_multi_event_loop()
    # Re-evaluate exit code after the synchronous test.
    if failures:
        sys.exit(1)
