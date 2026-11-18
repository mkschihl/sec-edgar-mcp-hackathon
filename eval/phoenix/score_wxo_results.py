"""Score raw WXO agent responses against judge criteria.

Reads evaluation/raw_results.json (responses from the production WXO agent),
runs the correctness, scope, and numeric judges on each response using the
pass_criteria from benchmark_questions.py, and prints a per-question table with
the full judge explanation for every failure plus a routing column (informational).

No Phoenix experiment needed — scores run locally against the LLM judge.

Usage (from workspace root, with venv active and .env sourced):
    source .env && export WATSONX_URL WATSONX_API_KEY WATSONX_PROJECT_ID JUDGE_MODEL
    venv/bin/python eval/phoenix/score_wxo_results.py

Optional flags:
    --ids BQ-07 BQ-09   Score only specific question IDs
    --raw-path PATH      Override path to raw_results.json
    --no-llm             Skip LLM judges (correctness + scope); only run numeric

Columns:
    Routing  (informational only) — routing_ok if all expected_tools fired,
             routing_diff if some expected tools were absent. This reflects
             which tool path the agent took, not whether the answer is correct.
             Optional tools (optional_tools key) are never counted as missing.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
WORKSPACE = Path(__file__).resolve().parent.parent.parent
EVAL_DIR  = WORKSPACE / "evaluation"
RAW_PATH  = EVAL_DIR / "raw_results.json"

sys.path.insert(0, str(EVAL_DIR))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from benchmark_questions import BENCHMARK_QUESTIONS  # noqa: E402


# ---------------------------------------------------------------------------
# Build pass_criteria lookup and numeric_checks lookup from benchmark
# ---------------------------------------------------------------------------
_BQ_BY_ID: dict[str, dict] = {q["id"]: q for q in BENCHMARK_QUESTIONS}


def _build_reference(bq: dict) -> str:
    """Return the reference string to pass to the correctness judge."""
    return bq.get("pass_criteria", "")


# ---------------------------------------------------------------------------
# LLM judge helpers (reuse the same classifiers from the judges package)
# ---------------------------------------------------------------------------

def _run_correctness_judge(question: str, response: str, reference: str) -> dict:
    from judges.correctness_judge import _TEMPLATE, _DEFAULT_JUDGE
    from datetime import date as _date
    from phoenix.evals import LLM, create_classifier

    judge_model = os.getenv("JUDGE_MODEL", _DEFAULT_JUDGE)
    llm = LLM(provider="litellm", model=f"watsonx/{judge_model}", temperature=0.0)
    prompt = _TEMPLATE.replace("{today}", _date.today().isoformat())
    classifier = create_classifier(
        name="correctness",
        prompt_template=prompt,
        llm=llm,
        choices={"correct": 1, "incorrect": 0},
        direction="maximize",
    )
    eval_input = {"input": question, "output": response, "reference": reference}
    input_mapping = {
        "input":     lambda ex: ex.get("input", ""),
        "output":    lambda ex: ex.get("output", ""),
        "reference": lambda ex: ex.get("reference", ""),
    }
    items = classifier.evaluate(eval_input, input_mapping=input_mapping)
    if not items:
        return {"label": "incorrect", "score": 0, "explanation": ""}
    item = items[0]
    return {
        "label": getattr(item, "label", "incorrect"),
        "score": getattr(item, "score", 0),
        "explanation": getattr(item, "explanation", ""),
    }


def _run_scope_judge(question: str, response: str) -> dict:
    from judges.relevance_judge import _TEMPLATE, _DEFAULT_JUDGE
    from datetime import date as _date
    from phoenix.evals import LLM, create_classifier

    judge_model = os.getenv("JUDGE_MODEL", _DEFAULT_JUDGE)
    llm = LLM(provider="litellm", model=f"watsonx/{judge_model}", temperature=0.0)
    prompt = _TEMPLATE.replace("{today}", _date.today().isoformat())
    classifier = create_classifier(
        name="scope",
        prompt_template=prompt,
        llm=llm,
        choices={"within_scope": 1, "out_of_scope": 0},
        direction="maximize",
    )
    eval_input = {"input": question, "output": response}
    input_mapping = {
        "input":  lambda ex: ex.get("input", ""),
        "output": lambda ex: ex.get("output", ""),
    }
    items = classifier.evaluate(eval_input, input_mapping=input_mapping)
    if not items:
        return {"label": "out_of_scope", "score": 0, "explanation": ""}
    item = items[0]
    return {
        "label": getattr(item, "label", "out_of_scope"),
        "score": getattr(item, "score", 0),
        "explanation": getattr(item, "explanation", ""),
    }


def _run_numeric_judge(response: str, checks) -> dict:
    from judges.numeric_judge import _score_numeric

    score, explanation = _score_numeric(response, checks)
    if score is None:
        label = "numeric_na"
    elif score == 0.0 and "numeric_config_error" in explanation:
        label = "numeric_config_error"
    elif score >= 1.0:
        label = "numeric_pass"
    else:
        label = "numeric_fail"
    return {"label": label, "score": score, "explanation": explanation}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Score raw WXO results against judge criteria (no Phoenix needed)."
    )
    parser.add_argument("--ids", nargs="+", metavar="ID", help="Score only these question IDs.")
    parser.add_argument(
        "--raw-path", default=str(RAW_PATH),
        metavar="PATH", help=f"Path to raw_results.json (default: {RAW_PATH})."
    )
    parser.add_argument(
        "--no-llm", action="store_true",
        help="Skip LLM judges (correctness + scope); only run numeric judge."
    )
    args = parser.parse_args()

    raw_path = Path(args.raw_path)
    if not raw_path.exists():
        print(f"ERROR: {raw_path} not found. Run evaluation/run_evaluation.py first.")
        sys.exit(1)

    results: list[dict] = json.loads(raw_path.read_text())

    if args.ids:
        results = [r for r in results if r["id"] in args.ids]
        if not results:
            print(f"No results matched: {args.ids}")
            sys.exit(1)

    print(f"Scoring {len(results)} result(s) from {raw_path}")
    print(f"LLM judges: {'disabled' if args.no_llm else 'enabled'}")
    print("=" * 80)

    rows = []
    for r in results:
        bq_id = r["id"]
        bq = _BQ_BY_ID.get(bq_id, {})
        question  = r.get("question", bq.get("question", ""))
        response  = r.get("response_text", "")
        reference = _build_reference(bq)
        checks    = bq.get("numeric_checks")

        # Routing: informational only — did all expected tools fire?
        # optional_tools are never counted as missing.
        expected_tools = bq.get("expected_tools", [])
        optional_tools = set(bq.get("optional_tools") or [])
        tools_fired    = r.get("tools_fired", [])
        missing_tools  = [t for t in expected_tools if t not in tools_fired and t not in optional_tools]
        routing = "routing_ok" if not missing_tools else f"routing_diff (missing: {missing_tools})"

        corr_result  = _run_correctness_judge(question, response, reference) if not args.no_llm else {"label": "skipped", "score": None, "explanation": ""}
        scope_result = _run_scope_judge(question, response) if not args.no_llm else {"label": "skipped", "score": None, "explanation": ""}
        num_result   = _run_numeric_judge(response, checks)

        rows.append({
            "id": bq_id,
            "question": question[:60],
            "routing": routing,
            "corr": corr_result,
            "scope": scope_result,
            "num": num_result,
        })

        c_icon = "✅" if corr_result["score"] == 1 else ("⬜" if corr_result["label"] == "skipped" else "❌")
        s_icon = "✅" if scope_result["score"] == 1 else ("⬜" if scope_result["label"] == "skipped" else "❌")
        n_icon = "✅" if num_result["score"] == 1.0 else ("—" if num_result["score"] is None else "❌")
        r_icon = "🗺" if routing == "routing_ok" else "⚠"
        print(f"\n{bq_id}: {question[:70]}")
        print(f"  Routing     : {r_icon} {routing}  [informational]")
        print(f"  Correctness : {c_icon} {corr_result['label']}")
        print(f"  Scope       : {s_icon} {scope_result['label']}")
        print(f"  Numeric     : {n_icon} {num_result['label']}")
        # Full explanations — no truncation
        if corr_result["label"] not in ("correct", "skipped") and corr_result.get("explanation"):
            print(f"  → corr fail :")
            print(f"    {corr_result['explanation']}")
        if scope_result["label"] not in ("within_scope", "skipped") and scope_result.get("explanation"):
            print(f"  → scope fail:")
            print(f"    {scope_result['explanation']}")
        if num_result["label"] not in ("numeric_pass", "numeric_na") and num_result.get("explanation"):
            print(f"  → num fail  :")
            print(f"    {num_result['explanation']}")

    # Summary
    print("\n" + "=" * 80)
    if not args.no_llm:
        corr_pass  = sum(1 for r in rows if r["corr"]["score"] == 1)
        scope_pass = sum(1 for r in rows if r["scope"]["score"] == 1)
        num_scored = [r for r in rows if r["num"]["score"] is not None]
        num_pass   = sum(1 for r in num_scored if r["num"]["score"] == 1.0)
        print(f"SUMMARY  correctness={corr_pass}/{len(rows)}  scope={scope_pass}/{len(rows)}  "
              f"numeric={num_pass}/{len(num_scored)} (of {len(num_scored)} with checks)")
    else:
        num_scored = [r for r in rows if r["num"]["score"] is not None]
        num_pass   = sum(1 for r in num_scored if r["num"]["score"] == 1.0)
        print(f"SUMMARY  numeric={num_pass}/{len(num_scored)} (of {len(num_scored)} with checks)")
    print("=" * 80)


if __name__ == "__main__":
    main()
