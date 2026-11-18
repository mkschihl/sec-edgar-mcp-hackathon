"""Sanity-check script for correctness_judge and numeric_judge.

Runs both judges directly (no Phoenix experiment) on five hand-crafted cases
derived from BQ-07 and BQ-09.  Reference text and numeric_checks are loaded
directly from evaluation/benchmark_questions.py — nothing is hardcoded here.

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
_REPO_ROOT = Path(__file__).resolve().parents[3]
_EVAL_DIR  = Path(__file__).resolve().parents[2]  # eval/phoenix/
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

# ---------------------------------------------------------------------------
# BQ-09 actual response from evaluation/raw_results.json (case e)
# ---------------------------------------------------------------------------
_BQ09_ACTUAL_RESPONSE = (
    "**Apple\u202fInc. \u2013 Quarterly Revenue (last\u202f8 quarters)**  \n"
    "*XBRL concept used: **RevenueFromContractWithCustomerExcludingAssessedTax** (us\u2011gaap)*  \n\n"
    "| Fiscal Quarter | Fiscal Year | Period End | Revenue (USD) | Form | Accession Number |\n"
    "|----------------|------------|------------|----------------|------|-------------------|\n"
    "| Q3 | 2026 | 2026\u201106\u201127 | $109.4\u202fbillion | 10\u2011Q | 0000320193\u201126\u2011000020 |\n"
    "| Q2 | 2026 | 2026\u201103\u201128 | $111.2\u202fbillion | 10\u2011Q | 0000320193\u201126\u2011000013 |\n"
    "| Q1 | 2026 | 2025\u201112\u201127 | $143.8\u202fbillion | 10\u2011Q | 0000320193\u201126\u2011000006 |\n"
    "| Q3 | 2025 | 2025\u201106\u201128 | $94.0\u202fbillion | 10\u2011Q | 0000320193\u201126\u2011000020 |\n"
    "| Q2 | 2025 | 2025\u201103\u201129 | $95.4\u202fbillion | 10\u2011Q | 0000320193\u201126\u2011000013 |\n"
    "| Q1 | 2025 | 2024\u201112\u201128 | $124.3\u202fbillion | 10\u2011Q | 0000320193\u201126\u2011000006 |\n"
    "| Q3 | 2024 | 2024\u201106\u201129 | $85.8\u202fbillion | 10\u2011Q | 0000320193\u201125\u2011000073 |\n"
    "| Q2 | 2024 | 2024\u201103\u201130 | $90.8\u202fbillion | 10\u2011Q | 0000320193\u201125\u2011000057 |\n\n"
    "**Notes**\n\n"
    "* The data come from Apple\u2019s 10\u2011Q filings (quarterly reports).  \n"
    "* Q4 figures are not included in the quarterly\u2011facts endpoint because they are "
    "reported in the annual 10\u2011K (or occasional 8\u2011K), not in a separate 10\u2011Q. "
    "If you need the Q4 (full\u2011year) revenue, let me know and I can retrieve the "
    "annual figure via the company\u2011fact call."
)

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
]

# ---------------------------------------------------------------------------
# Judge invocation helpers
# ---------------------------------------------------------------------------

def _run_correctness(question: str, response: str, reference: str) -> dict:
    """Call the correctness judge directly (bypasses Phoenix experiment context)."""
    from phoenix.evals import LLM, create_classifier  # noqa: PLC0415
    from eval.phoenix.judges.correctness_judge import _TEMPLATE  # noqa: PLC0415

    judge_model = os.getenv("JUDGE_MODEL", "mistralai/mistral-small-3-1-24b-instruct-2503")
    llm = LLM(provider="litellm", model=f"watsonx/{judge_model}", temperature=0.0)
    classifier = create_classifier(
        name="correctness",
        prompt_template=_TEMPLATE,
        llm=llm,
        choices={"correct": 1, "incorrect": 0},
        direction="maximize",
    )
    eval_input = {"input": question, "output": response, "reference": reference}
    results = classifier.evaluate(eval_input, input_mapping={
        "input":     lambda ex: ex.get("input", ""),
        "output":    lambda ex: ex.get("output", ""),
        "reference": lambda ex: ex.get("reference", ""),
    })
    if not results:
        return {"label": "incorrect", "score": 0, "explanation": "(no result)"}
    item = results[0]
    return {
        "label": getattr(item, "label", "incorrect"),
        "score": getattr(item, "score", 0),
        "explanation": getattr(item, "explanation", ""),
    }


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
    judge_model = os.getenv("JUDGE_MODEL", "mistralai/mistral-small-3-1-24b-instruct-2503")
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
        pass_c = c["label"] == exp_c
        all_pass = all_pass and pass_c
        status_c = "PASS ✅" if pass_c else "FAIL ❌"
        print(f"  label       : {c['label']}")
        print(f"  score       : {c['score']}")
        print(f"  expected    : {exp_c}")
        print(f"  result      : {status_c}")
        print(f"  explanation : {textwrap.shorten(c['explanation'], width=200, placeholder='…')}")
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
