"""Correctness judge: compares the agent's answer to a ground-truth reference.

Uses an LLM-as-judge (JUDGE_MODEL) to classify the response as `correct` or
`incorrect`. Tolerates reasonable formatting differences: different units
presentation, surrounding prose, and extra context are all acceptable as long
as the core factual claims match the reference.

Returns a phoenix.evals.evaluators.ClassificationEvaluator created via
create_classifier(), which is compatible with phoenix.client run_experiment().
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from phoenix.evals import LLM, create_classifier

load_dotenv()

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


def match_expected_response() -> object:
    """Return a ClassificationEvaluator that checks correctness vs ground truth.

    Returns the evaluator object — pass it directly to run_experiment(evaluators=[...]).
    """
    llm = LLM(
        provider="openai",
        model=os.getenv("JUDGE_MODEL", "claude_4_6_sonnet"),
        api_key=os.getenv("USAI_API_KEY", ""),
        base_url=os.getenv("USAI_BASE_URL", "") + "/api/v1",
        temperature=0.0,
    )
    return create_classifier(
        name="correctness",
        prompt_template=_TEMPLATE,
        llm=llm,
        choices={"correct": 1, "incorrect": 0},
        direction="maximize",
    )
