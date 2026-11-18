"""Sanity-check script for correctness_judge and numeric_judge.

Runs both judges directly (no Phoenix experiment) on hand-crafted cases
derived from BQ-07, BQ-09, and BQ-17.  Reference text and numeric_checks are
loaded directly from evaluation/benchmark_questions.py — nothing is hardcoded here.

Captured agent responses are stored as plain-text fixtures under
eval/phoenix/judges/fixtures/ so this script has no dependency on
evaluation/raw_results.json (which is overwritten by every run_evaluation.py run).

The correctness judge is called through match_expected_response() (the same code
path used in Phoenix experiments), so the 3-attempt retry and judge_error return
value are exercised here too.  judge_error is treated as FAIL.

Usage:
    source .env && export WATSONX_URL WATSONX_API_KEY WATSONX_PROJECT_ID JUDGE_MODEL
    cd /home/itzuser/wxo-agentic-workflow
    venv/bin/python eval/phoenix/judges/sanity_check.py
"""

from __future__ import annotations

import os
import sys
import textwrap
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup — allow running from any working directory
# ---------------------------------------------------------------------------
_REPO_ROOT   = Path(__file__).resolve().parents[3]
_EVAL_DIR    = Path(__file__).resolve().parents[2]  # eval/phoenix/
_FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_EVAL_DIR))

from dotenv import load_dotenv
load_dotenv()

# ---------------------------------------------------------------------------
# Load reference data from benchmark_questions.py (single source of truth)
# ---------------------------------------------------------------------------
from evaluation.benchmark_questions import BENCHMARK_QUESTIONS  # noqa: E402

def _get_bq(bq_id: str) -> dict:
    q = next((q for q in BENCHMARK_QUESTIONS if q["id"] == bq_id), None)
    if q is None:
        raise KeyError(f"BQ id {bq_id!r} not found in benchmark_questions.py")
    return q

BQ07 = _get_bq("BQ-07")
BQ09 = _get_bq("BQ-09")
BQ17 = _get_bq("BQ-17")

# ---------------------------------------------------------------------------
# Captured agent responses — loaded from fixtures/, NOT from raw_results.json.
# raw_results.json is overwritten by every run_evaluation.py run; fixtures are
# static and version-controlled.
# ---------------------------------------------------------------------------

def _load_fixture(name: str) -> str:
    """Load a response fixture from eval/phoenix/judges/fixtures/<name>.txt."""
    path = _FIXTURES_DIR / name
    if not path.exists():
        raise FileNotFoundError(
            f"Fixture {name!r} not found at {path}. "
            "Run the agent once and save its response to that file."
        )
    return path.read_text(encoding="utf-8")

_BQ09_ACTUAL_RESPONSE = _load_fixture("BQ-09e.txt")
# BQ-09 actual response (Apple quarterly revenue, 8 quarters).
# Holiday Q1 FY2026=$143.8B is legitimate; $109.4B and $111.2B are present.

_BQ17_OLD_RESPONSE = _load_fixture("BQ-17d.txt")
# BQ-17 old response (Pfizer revenue, wrong concept RevenueFromContractWithCustomer...).
# Reports $50.91B for FY2023 — expect incorrect + numeric < 1.0 after REVENUE_CANDIDATES fix.

# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------

CASES = [
    # --- BQ-07 cases ---
    {
        "id": "BQ-07a",
        "label": "BQ-07 CORRECT answer",
        "bq_id": "BQ-07",
        "question": BQ07["question"],
        "response": (
            "Here are Apple's last 5 annual net income figures:\n"
            "- FY2020 (ended 2020-09-26): $57.4B\n"
            "- FY2021 (ended 2021-09-25): $94.7B\n"
            "- FY2022 (ended 2022-09-24): $99.8B\n"
            "- FY2023 (ended 2023-09-30): $97.0B\n"
            "- FY2024 (ended 2024-09-28): $93.7B\n"
        ),
        "expect_correctness": "correct",
        "expect_numeric": ("==", 1.0),
    },
    {
        "id": "BQ-07b",
        "label": "BQ-07 WRONG — FY2023 duplicated, FY2024 off by $3B",
        "bq_id": "BQ-07",
        "question": BQ07["question"],
        "response": (
            "Here are Apple's last 5 annual net income figures:\n"
            "- FY2022: $99.8B\n"
            "- FY2023: $99.8B\n"
            "- FY2024: $96.7B\n"
            "- FY2025: $112.0B\n"
            "- FY2026: $132.2B\n"
        ),
        "expect_correctness": "incorrect",
        "expect_numeric": ("<", 1.0),
    },
    # --- BQ-09 cases ---
    {
        "id": "BQ-09c",
        "label": "BQ-09 WRONG — YTD values reported instead of single-quarter",
        "bq_id": "BQ-09",
        "question": BQ09["question"],
        "response": (
            "Here are Apple's quarterly revenue figures:\n"
            "- Q3 FY2026 (9-month YTD): $364.4B\n"
            "- Q2 FY2026 (6-month YTD): $254.9B\n"
            "- Q1 FY2026: $143.8B\n"
        ),
        "expect_correctness": "incorrect",
        # max_value=200B → $364.4B and $254.9B trigger the guard → score 0.0
        "expect_numeric": ("==", 0.0),
    },
    {
        "id": "BQ-09d",
        "label": "BQ-09 WRONG — spot values shifted (109.4→107.0, 111.2→108.0)",
        "bq_id": "BQ-09",
        "question": BQ09["question"],
        "response": (
            "Apple quarterly revenue (last 8 quarters):\n"
            "- Q3 FY2026 (ended 2026-06-27): $107.0B\n"
            "- Q2 FY2026 (ended 2026-03-28): $108.0B\n"
            "- Q1 FY2026 (ended 2025-12-27): $143.8B\n"
            "- Q3 FY2025 (ended 2025-06-28): $94.0B\n"
        ),
        "expect_correctness": "incorrect",
        # $109.4B±2% = [107.2B, 111.6B]; $107.0B is 2.2% below → miss
        # $111.2B±2% = [109.0B, 113.4B]; $108.0B is 2.9% below → miss
        "expect_numeric": ("<", 1.0),
    },
    {
        "id": "BQ-09e",
        "label": "BQ-09 ACTUAL response from raw_results.json — expect correct + numeric 1.0",
        "bq_id": "BQ-09",
        "question": BQ09["question"],
        "response": _BQ09_ACTUAL_RESPONSE,
        # Holiday Q1 FY2026=$143.8B is legitimate — must NOT be blocked by any range check.
        # must_include checks: $109.4B at ±2% and $111.2B at ±2% → both present.
        # max_value=200B → all values ≤$143.8B, no violation.
        "expect_correctness": "correct",
        "expect_numeric": ("==", 1.0),
    },
    # --- BQ-17 cases ---
    {
        "id": "BQ-17d",
        "label": "BQ-17 ACTUAL raw_results.json — old response with $50.91B (wrong concept) — expect incorrect + numeric < 1.0",
        "bq_id": "BQ-17",
        "question": BQ17["question"],
        "response": _BQ17_OLD_RESPONSE,
        # Old response used RevenueFromContractWithCustomer... concept.
        # None of $62.579B / $63.627B / $59.553B appear → numeric < 1.0.
        # pass_criteria explicitly says values should NOT be from that concept → incorrect.
        "expect_correctness": "incorrect",
        "expect_numeric": ("<", 1.0),
    },
    {
        "id": "BQ-17e",
        "label": "BQ-17 WRONG — shifted values (62.579→60.0, 63.627→61.5)",
        "bq_id": "BQ-17",
        "question": BQ17["question"],
        "response": (
            "PFIZER INC (PFE, CIK 0000078003) annual revenue (concept: Revenues):\n"
            "- FY2024 (ended 2024-12-31): $61.5B\n"
            "- FY2023 (ended 2023-12-31): $60.0B\n"
            "- FY2022 (ended 2022-12-31): $100.3B\n"
            "- FY2021 (ended 2021-12-31): $81.3B\n"
        ),
        "expect_correctness": "incorrect",
        # $62.579B ± 0.5% = [62.26B, 62.89B]; $60.0B outside → miss
        # $63.627B ± 0.5% = [63.31B, 63.94B]; $61.5B outside → miss
        "expect_numeric": ("<", 1.0),
    },
]

# ---------------------------------------------------------------------------
# Judge invocation helpers — call through the same code path as experiments
# ---------------------------------------------------------------------------

def _run_correctness(question: str, response: str, reference: str) -> dict:
    """Call the correctness judge through match_expected_response().

    This exercises the 3-attempt retry wrapper and the judge_error return path,
    exactly as it will run during a Phoenix experiment.
    """
    from eval.phoenix.judges.correctness_judge import match_expected_response  # noqa: PLC0415

    judge_fn = match_expected_response()
    # judge_fn is a @create_evaluator-wrapped function.
    # When called outside Phoenix, we pass plain strings — the wrapper converts
    # them via isinstance checks (str → str, dict → dict.get(...)).
    return judge_fn(
        input={"query": question},
        output={"result": response},
        reference={"responses": reference},
    )


def _run_numeric(response: str, numeric_checks) -> dict:
    """Call the deterministic numeric judge directly."""
    from eval.phoenix.judges.numeric_judge import _score_numeric  # noqa: PLC0415

    score, explanation = _score_numeric(response, numeric_checks)
    label = "numeric_pass" if score >= 1.0 else "numeric_fail"
    return {"label": label, "score": score, "explanation": explanation}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    judge_model = os.getenv("JUDGE_MODEL", "meta-llama/llama-3-3-70b-instruct")
    print(f"\n{'='*70}")
    print("Sanity check — correctness judge (LLM) + numeric judge (deterministic)")
    print(f"JUDGE_MODEL = {judge_model}")
    print(f"{'='*70}\n")

    all_pass = True

    for case in CASES:
        bq = _get_bq(case["bq_id"])
        reference   = bq["pass_criteria"]
        num_checks  = bq["numeric_checks"]
        ref_source  = f"evaluation/benchmark_questions.py #{case['bq_id']}"

        sep = "─" * 70
        print(sep)
        print(f"Case : {case['id']} — {case['label']}")
        print(f"BQ   : {case['bq_id']}")
        print()

        # Print the reference text the judge will receive and where it came from
        print(f"REFERENCE TEXT (from {ref_source}):")
        print(textwrap.indent(reference, "  "))
        print()
        print(f"NUMERIC CHECKS (from {ref_source}):")
        print(f"  {num_checks!r}")
        print()

        # --- Correctness judge ---
        print("Running correctness judge (LLM) …")
        c = _run_correctness(case["question"], case["response"], reference)
        exp_c = case["expect_correctness"]

        # judge_error is always a FAIL
        if c["label"] == "judge_error":
            pass_c = False
            status_c = "FAIL ❌  (judge_error — LLM returned malformed JSON after 3 attempts)"
        else:
            pass_c = c["label"] == exp_c
            status_c = "PASS ✅" if pass_c else "FAIL ❌"

        all_pass = all_pass and pass_c
        print(f"  label       : {c['label']}")
        print(f"  score       : {c['score']}")
        print(f"  expected    : {exp_c}")
        print(f"  result      : {status_c}")
        expl = c.get("explanation") or ""
        print(f"  explanation : {textwrap.shorten(str(expl), width=200, placeholder='…')}")
        print()

        # --- Numeric judge ---
        print("Running numeric judge (deterministic) …")
        n = _run_numeric(case["response"], num_checks)

        op, exp_val = case["expect_numeric"]
        if op == "==":
            pass_n = n["score"] == exp_val
            exp_n_desc = f"== {exp_val}"
        elif op == "<":
            pass_n = n["score"] < exp_val
            exp_n_desc = f"< {exp_val}"
        elif op == ">=":
            pass_n = n["score"] >= exp_val
            exp_n_desc = f">= {exp_val}"
        else:
            pass_n = True
            exp_n_desc = "(any)"

        all_pass = all_pass and pass_n
        status_n = "PASS ✅" if pass_n else "FAIL ❌"
        print(f"  label       : {n['label']}")
        print(f"  score       : {n['score']}")
        print(f"  expected    : {exp_n_desc}")
        print(f"  result      : {status_n}")
        print(f"  explanation : {n['explanation']}")
        print()

    print("─" * 70)
    if all_pass:
        print("Overall: ALL CASES PASSED ✅")
    else:
        print("Overall: SOME CASES FAILED ❌")
    print()


if __name__ == "__main__":
    main()
