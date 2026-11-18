"""Relevance/scope judge: decides whether the agent answered within its scope.

Uses an LLM-as-judge (JUDGE_MODEL) to classify the response as `within_scope`
or `out_of_scope`. No ground-truth reference is needed — it evaluates whether
the agent used its tools to answer an answerable question, or appropriately
refused an unanswerable one (e.g. stock price predictions).

The judge wraps ClassificationEvaluator in a @create_evaluator function so that
Phoenix auto-binds the named parameters (input, output) and the _INPUT_MAPPING
is applied explicitly before calling the classifier.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

_DEFAULT_JUDGE = "meta-llama/llama-3-3-70b-instruct"

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


def check_answer_scope():
    """Return a callable evaluator that checks scope without a reference answer.

    Returns a wrapper function decorated with @create_evaluator. Phoenix
    auto-binds the named parameters (input, output) from the experiment context
    and the wrapper extracts the relevant strings before calling the underlying
    ClassificationEvaluator.

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
        name="scope",
        prompt_template=_TEMPLATE,
        llm=llm,
        choices={"within_scope": 1, "out_of_scope": 0},
        direction="maximize",
    )

    @create_evaluator(name="scope")
    def _judge(input, output) -> dict:  # noqa: A002
        # Extract plain strings from Phoenix dicts
        query = input.get("query", "") if isinstance(input, dict) else str(input)
        result = (
            output.get("result", "") if isinstance(output, dict) else str(output)
        )
        eval_input = {"input": query, "output": result}
        result_list = classifier.evaluate(eval_input, input_mapping={
            "input":  lambda ex: ex.get("input", ""),
            "output": lambda ex: ex.get("output", ""),
        })
        if not result_list:
            return {"label": "out_of_scope", "score": 0, "explanation": ""}
        item = result_list[0]
        return {
            "label": getattr(item, "label", "out_of_scope"),
            "score": getattr(item, "score", 0),
            "explanation": getattr(item, "explanation", ""),
        }

    return _judge
