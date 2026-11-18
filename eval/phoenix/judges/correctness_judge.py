"""Correctness judge: compares the agent's answer to a ground-truth reference.

Uses an LLM-as-judge (JUDGE_MODEL) to classify the response as `correct` or
`incorrect`. Tolerates reasonable formatting differences: different units
presentation, surrounding prose, and extra context are all acceptable as long
as the core factual claims match the reference.

The judge wraps ClassificationEvaluator in a @create_evaluator function so that
Phoenix auto-binds the named parameters (input, output, reference) and the
_INPUT_MAPPING is applied explicitly before calling the classifier.

Majority-vote mode
------------------
Both `majority_vote_correctness()` (standalone) and the Phoenix-bound
`match_expected_response()` run the classifier **3 times** per question and
return the majority label.  When the 3 votes disagree the label is "unstable"
and the score is 0.5.  All 3 raw explanations are stored in
``result["all_explanations"]`` so callers can display them on failure.
"""

from __future__ import annotations

import os
import sys
import time
from collections import Counter
from datetime import date as _date

from dotenv import load_dotenv

load_dotenv()

_DEFAULT_JUDGE = "mistralai/mistral-small-3-1-24b-instruct-2503"
_AGENT_DEFAULT  = "meta-llama/llama-3-3-70b-instruct"

# Warn at import time if JUDGE_MODEL == AGENT_MODEL (self-preference bias risk)
_judge_model = os.getenv("JUDGE_MODEL", _DEFAULT_JUDGE)
_agent_model = os.getenv("AGENT_MODEL", _AGENT_DEFAULT)
if _judge_model == _agent_model:
    print(
        f"WARNING [correctness_judge]: JUDGE_MODEL == AGENT_MODEL ({_judge_model!r}). "
        "Using the same model for judging and the agent-under-test increases self-preference bias. "
        "Set JUDGE_MODEL to a different (ideally stronger) model in .env.",
        file=sys.stderr,
    )

_TEMPLATE = """\
Today's date is {today}. SEC filings dated up to today are real historical data, \
not forecasts. Do not mark data incorrect or out of scope because its dates are \
later than your training data. \
A period whose end date is on or before {today} is historical. \
Companies' fiscal years differ from calendar years \
(e.g. Microsoft's FY2027 Q1 ended 2026-09-30). \
Never mark data incorrect or out of scope for being 'future' unless its \
period end date is after {today}.

You are a financial-data accuracy judge for an SEC EDGAR research assistant.

## Task
Decide whether the AGENT RESPONSE correctly answers the USER QUESTION given the
REFERENCE ANSWER. The reference describes the minimum factual content a correct
response must contain.

## Grading rules
- Mark `correct` if the agent's response satisfies the reference criteria.
  Minor differences in formatting, units presentation (e.g. "$94B" vs "$94,000,000,000"),
  extra explanatory prose, or additional context are all acceptable.
- Mark `incorrect` if the agent's response is missing required facts, fabricates
  data, refuses to answer when it should not, or contradicts the reference.
- If the agent correctly reports that a ticker/company was not found (error-handling
  question), mark `correct` provided no data was fabricated.
- Any figure that differs from a figure in the reference by more than 1% is incorrect.
- If the reference attributes a value to a period end date or fiscal year, the
  response must attribute that value to the same period. Mislabeled years are incorrect.
- Quarterly figures that are year-to-date or multi-quarter totals are incorrect.
- If the reference says no warning is needed, the absence of a warning is correct.

## Inputs
USER QUESTION:
{input}

REFERENCE ANSWER (what a correct response must contain):
{reference}

AGENT RESPONSE:
{output}

## Your verdict
Reply with ONLY one of the provided label choices.
"""

_INPUT_MAPPING = {
    "input": lambda example: example.get("input", {}).get("query", ""),
    "output": lambda example: (
        example.get("output", {}).get("result", "")
        if isinstance(example.get("output"), dict)
        else str(example.get("output", ""))
    ),
    "reference": lambda example: example.get("expected", {}).get("responses", ""),
}


def _single_classify(classifier, eval_input: dict, input_mapping: dict) -> dict:
    """Run the classifier once with 3-attempt retry; return a result dict."""
    last_exc: Exception | None = None
    for attempt in range(1, 4):
        try:
            result_list = classifier.evaluate(eval_input, input_mapping=input_mapping)
            if not result_list:
                return {"label": "incorrect", "score": 0, "explanation": ""}
            item = result_list[0]
            return {
                "label": getattr(item, "label", "incorrect"),
                "score": getattr(item, "score", 0),
                "explanation": getattr(item, "explanation", ""),
            }
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            if attempt < 3:
                time.sleep(2 ** attempt)  # 2s, 4s back-off
    return {
        "label": "judge_error",
        "score": None,
        "explanation": f"classifier.evaluate failed after 3 attempts: {last_exc}",
    }


def _majority_vote(runs: list[dict]) -> dict:
    """Aggregate 3 classifier runs into a single majority-vote result.

    Rules:
    - If any run is judge_error, treat it as "incorrect" for voting purposes
      (conservative: a broken judge should not inflate scores).
    - Majority label wins (2-of-3 or 3-of-3).
    - When all 3 labels differ (impossible for binary choices, but guard anyway)
      or when it's judge_error on all 3, return label="judge_error".
    - When the 3 votes are split 2-1 (not 3-of-3 unanimous), set
      ``"stable": False`` and label="unstable" with score=0.5.
    - ``"all_explanations"`` always holds the list of 3 raw explanations.
    """
    labels = [r["label"] if r["label"] != "judge_error" else "incorrect" for r in runs]
    explanations = [r.get("explanation", "") for r in runs]

    counter = Counter(labels)
    winner, count = counter.most_common(1)[0]

    unanimous = (count == 3)
    all_errors = all(r["label"] == "judge_error" for r in runs)

    if all_errors:
        return {
            "label": "judge_error",
            "score": None,
            "explanation": runs[0].get("explanation", ""),
            "all_explanations": explanations,
            "stable": False,
        }

    if not unanimous:
        # 2-of-3: majority label wins but mark as unstable
        return {
            "label": "unstable",
            "score": 0.5,
            "explanation": f"Majority={winner} (2/3); votes={labels}",
            "all_explanations": explanations,
            "stable": False,
        }

    # 3-of-3 unanimous
    score_map = {"correct": 1, "incorrect": 0}
    return {
        "label": winner,
        "score": score_map.get(winner, 0),
        "explanation": explanations[0],  # all 3 agree — first suffices
        "all_explanations": explanations,
        "stable": True,
    }


def majority_vote_correctness(
    question: str,
    response: str,
    reference: str,
) -> dict:
    """Run the correctness judge 3 times and return a majority-vote result.

    Returns a dict with keys:
        label        — "correct" | "incorrect" | "unstable" | "judge_error"
        score        — 1 (correct) | 0 (incorrect) | 0.5 (unstable) | None (error)
        explanation  — summary explanation
        all_explanations — list[str] with all 3 raw explanations
        stable       — True when all 3 votes agree
    """
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

    runs = [_single_classify(classifier, eval_input, input_mapping) for _ in range(3)]
    return _majority_vote(runs)


def match_expected_response():
    """Return a callable evaluator that checks correctness vs ground truth.

    Returns a wrapper function decorated with @create_evaluator. Phoenix
    auto-binds the named parameters (input, output, reference) from the
    experiment context and the wrapper extracts the relevant strings before
    calling the underlying ClassificationEvaluator.

    Uses majority-vote (3 runs) per question. When the 3 votes disagree the
    label is "unstable" with score 0.5.

    Pass the returned callable directly to run_experiment(evaluators=[...]).
    """
    from phoenix.evals import LLM, create_classifier
    from phoenix.client.resources.experiments import create_evaluator  # type: ignore

    judge_model = os.getenv("JUDGE_MODEL", _DEFAULT_JUDGE)
    llm = LLM(
        provider="litellm",
        model=f"watsonx/{judge_model}",
        # WATSONX_URL / WATSONX_API_KEY / WATSONX_PROJECT_ID are read from env by LiteLLM
        temperature=0.0,
    )
    # Fill {today} at classifier-build time (once per experiment run)
    prompt = _TEMPLATE.replace("{today}", _date.today().isoformat())
    classifier = create_classifier(
        name="correctness",
        prompt_template=prompt,
        llm=llm,
        choices={"correct": 1, "incorrect": 0},
        direction="maximize",
    )

    @create_evaluator(name="correctness")
    def _judge(input, output, reference) -> dict:  # noqa: A002
        # Extract plain strings from Phoenix dicts
        query = input.get("query", "") if isinstance(input, dict) else str(input)
        result = (
            output.get("result", "") if isinstance(output, dict) else str(output)
        )
        ref_text = (
            reference.get("responses", "") if isinstance(reference, dict) else str(reference)
        )
        eval_input = {"input": query, "output": result, "reference": ref_text}
        input_mapping = {
            "input":     lambda ex: ex.get("input", ""),
            "output":    lambda ex: ex.get("output", ""),
            "reference": lambda ex: ex.get("reference", ""),
        }

        runs = [_single_classify(classifier, eval_input, input_mapping) for _ in range(3)]
        result_dict = _majority_vote(runs)
        # Phoenix expects only label/score/explanation keys; drop extras
        return {
            "label": result_dict["label"],
            "score": result_dict["score"],
            "explanation": result_dict["explanation"],
        }

    return _judge
