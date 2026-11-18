"""Correctness judge: compares the agent's answer to a ground-truth reference.

Uses an LLM-as-judge (JUDGE_MODEL) to classify the response as `correct` or
`incorrect`. Tolerates reasonable formatting differences: different units
presentation, surrounding prose, and extra context are all acceptable as long
as the core factual claims match the reference.

The judge wraps ClassificationEvaluator in a @create_evaluator function so that
Phoenix auto-binds the named parameters (input, output, reference) and the
_INPUT_MAPPING is applied explicitly before calling the classifier.
"""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv

load_dotenv()

_DEFAULT_JUDGE = "meta-llama/llama-3-3-70b-instruct"
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
- If the reference expects at least N items (e.g. "at least 3 annual figures") and
  the agent returns fewer, mark `incorrect` only if the shortfall is significant
  (less than half the expected minimum); minor shortfalls are `correct`.
- If the reference expects fiscal years to be labelled and the agent provides only
  raw dates, mark `correct` provided the dates clearly correspond to the fiscal
  year periods described in the reference.
- If the reference expects warnings about data comparability (e.g. different fiscal
  year ends) and the agent omits them but the data itself is accurate, mark
  `correct`; warnings are advisory, not required facts.

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


def match_expected_response():
    """Return a callable evaluator that checks correctness vs ground truth.

    Returns a wrapper function decorated with @create_evaluator. Phoenix
    auto-binds the named parameters (input, output, reference) from the
    experiment context and the wrapper extracts the relevant strings before
    calling the underlying ClassificationEvaluator.

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
    classifier = create_classifier(
        name="correctness",
        prompt_template=_TEMPLATE,
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
        result_list = classifier.evaluate(eval_input, input_mapping={
            "input":     lambda ex: ex.get("input", ""),
            "output":    lambda ex: ex.get("output", ""),
            "reference": lambda ex: ex.get("reference", ""),
        })
        if not result_list:
            return {"label": "incorrect", "score": 0, "explanation": ""}
        item = result_list[0]
        return {
            "label": getattr(item, "label", "incorrect"),
            "score": getattr(item, "score", 0),
            "explanation": getattr(item, "explanation", ""),
        }

    return _judge
