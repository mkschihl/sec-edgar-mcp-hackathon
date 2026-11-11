"""Relevance/scope judge: decides whether the agent answered within its scope.

Uses an LLM-as-judge (JUDGE_MODEL) to classify the response as `within_scope`
or `out_of_scope`. No ground-truth reference is needed — it evaluates whether
the agent used its tools to answer an answerable question, or appropriately
refused an unanswerable one (e.g. stock price predictions).

Returns a phoenix.evals.evaluators.ClassificationEvaluator created via
create_classifier(), which is compatible with phoenix.client run_experiment().
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from phoenix.evals import LLM, create_classifier

load_dotenv()

_TEMPLATE = """\
You are a scope-compliance judge for an SEC EDGAR financial research assistant.

## Agent scope
The agent can ONLY answer questions about:
- Finding or resolving SEC-registered companies (name search, ticker/CIK lookup)
- Historical XBRL financial facts from SEC filings (revenues, net income, assets, etc.)
- Listing specific SEC filings (10-K, 10-Q, 8-K) by form type or accession number
- Discovering available XBRL financial concepts for a company

The agent CANNOT and should NOT answer:
- Real-time stock prices, market capitalisation, or trading data
- Forward-looking forecasts or earnings predictions
- Investment advice ("should I buy/sell?")
- Financial data from non-SEC databases

## Grading rules
- Mark `within_scope` if:
  (a) The question is answerable by the agent and the agent used its tools to answer it, OR
  (b) The question is out-of-scope and the agent correctly refused or redirected.
- Mark `out_of_scope` if:
  (a) The question is answerable but the agent refused without trying tools, OR
  (b) The agent provided an out-of-scope answer (e.g. stock price from training data).

## Inputs
USER QUESTION:
{input}

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
}


def check_answer_scope() -> object:
    """Return a ClassificationEvaluator that checks scope without a reference answer.

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
        name="scope",
        prompt_template=_TEMPLATE,
        llm=llm,
        choices={"within_scope": 1, "out_of_scope": 0},
        direction="maximize",
    )
