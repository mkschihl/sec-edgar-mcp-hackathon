"""Regression tests hitting live SEC APIs.

Run with:
    venv/bin/python toolkits/sec_edgar_tools/test_regressions.py

Exits non-zero if any test fails.
"""

import asyncio
import sys
from datetime import date, datetime

sys.path.insert(0, "toolkits/sec_edgar_tools")
from server import (
    sec_edgar_get_company_fact,
    sec_edgar_get_quarterly_facts,
    sec_edgar_compare_companies,
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


async def main():
    await test_aapl_net_income()
    await test_aapl_revenues_quarterly()
    await test_aapl_eps()
    await test_compare_jpm_bac()
    await test_aapl_revenues_concept_and_values()

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
