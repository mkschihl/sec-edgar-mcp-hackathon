"""Numeric judge: validates that numeric values in the agent response match
the expected magnitudes within a tolerance.

Uses an LLM-as-judge (JUDGE_MODEL) to classify the response as `numeric_pass`
or `numeric_fail`. This judge is only applied when the dataset example has a
`numeric_checks` metadata entry — a list of dicts with `description` and
`threshold_pct` keys that describe the numeric constraints to verify.

The judge wraps ClassificationEvaluator in a @create_evaluator function so that
Phoenix auto-binds the named parameters (input, output, metadata) from the
experiment context and the wrapper extracts the relevant data before calling
the underlying ClassificationEvaluator.

Example numeric_checks entry in the dataset CSV (as a JSON string in `metadata`):
  [
    {"description": "Apple FY2024 net income ~$93.7B USD", "threshold_pct": 5},
    {"description": "Apple FY2023 net income ~$96.0B USD", "threshold_pct": 5}
  ]

If `numeric_checks` is None or empty in `metadata`, the judge returns
`numeric_pass` without calling the LLM (no-op for non-numeric questions).
"""

from __future__ import annotations

import json
import os

from dotenv import load_dotenv

load_dotenv()

_DEFAULT_JUDGE = "meta-llama/llama-3-3-70b-instruct"

_TEMPLATE = """\
You are a numeric-accuracy judge for an SEC EDGAR financial research assistant.

## Task
Decide whether the AGENT RESPONSE reports numeric values that are consistent
with the NUMERIC CONSTRAINTS below. Each constraint describes a known correct
value with an allowed tolerance (threshold_pct = acceptable % deviation).

## Numeric constraints to check
{numeric_checks}

## Grading rules
- Mark `numeric_pass` if ALL numeric values mentioned in the agent response are
  within the stated threshold of the expected values in the constraints. Minor
  rounding differences are acceptable.
- Mark `numeric_fail` if the agent response reports a value that deviates from
  any constraint by more than the threshold, or if the agent refuses to provide
  numbers when the question clearly requires them.
- If the agent correctly says a value is not available or was not found, and the
  constraint describes a value that might not exist for that company, mark
  `numeric_pass`.
- If the response does not contain any numbers at all and numeric data was
  expected, mark `numeric_fail`.

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
    "numeric_checks": lambda example: _format_checks(
        example.get("metadata", {}).get("numeric_checks")
    ),
}


def _format_checks(checks) -> str:
    """Format numeric_checks for injection into the prompt template."""
    if not checks:
        return "(none)"
    if isinstance(checks, str):
        try:
            checks = json.loads(checks)
        except (json.JSONDecodeError, TypeError):
            return str(checks)
    if isinstance(checks, list):
        lines = []
        for i, c in enumerate(checks, 1):
            if isinstance(c, dict):
                desc = c.get("description", str(c))
                thr = c.get("threshold_pct", 5)
                lines.append(f"{i}. {desc} (tolerance ±{thr}%)")
            else:
                lines.append(f"{i}. {c}")
        return "\n".join(lines)
    return str(checks)


def _has_numeric_checks(metadata) -> bool:
    """Return True if the metadata has non-empty numeric_checks."""
    if not metadata:
        return False
    checks = metadata.get("numeric_checks")
    if checks is None:
        return False
    if isinstance(checks, str):
        try:
            parsed = json.loads(checks)
            return bool(parsed)
        except (json.JSONDecodeError, TypeError):
            return bool(checks.strip())
    return bool(checks)


def check_numeric_accuracy():
    """Return a callable evaluator that validates numeric accuracy.

    Returns a wrapper function decorated with @create_evaluator. Phoenix
    auto-binds the named parameters (input, output, metadata) from the
    experiment context. If the example has no numeric_checks in metadata,
    the evaluator short-circuits to numeric_pass without calling the LLM.

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
        name="numeric_accuracy",
        prompt_template=_TEMPLATE,
        llm=llm,
        choices={"numeric_pass": 1, "numeric_fail": 0},
        direction="maximize",
    )

    @create_evaluator(name="numeric_accuracy")
    def _judge(input, output, metadata=None) -> dict:  # noqa: A002
        # Short-circuit if no numeric checks defined for this question
        if not _has_numeric_checks(metadata):
            return {
                "label": "numeric_pass",
                "score": 1,
                "explanation": "No numeric checks defined for this question.",
            }

        # Extract plain strings
        query = input.get("query", "") if isinstance(input, dict) else str(input)
        result = (
            output.get("result", "") if isinstance(output, dict) else str(output)
        )
        checks_str = _format_checks(
            metadata.get("numeric_checks") if isinstance(metadata, dict) else None
        )

        eval_input = {
            "input": query,
            "output": result,
            "numeric_checks": checks_str,
        }
        result_list = classifier.evaluate(eval_input, input_mapping={
            "input":          lambda ex: ex.get("input", ""),
            "output":         lambda ex: ex.get("output", ""),
            "numeric_checks": lambda ex: ex.get("numeric_checks", "(none)"),
        })
        if not result_list:
            return {"label": "numeric_fail", "score": 0, "explanation": ""}
        item = result_list[0]
        return {
            "label": getattr(item, "label", "numeric_fail"),
            "score": getattr(item, "score", 0),
            "explanation": getattr(item, "explanation", ""),
        }

    return _judge
