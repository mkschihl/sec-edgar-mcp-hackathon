"""Numeric judge: deterministic, non-LLM validation of dollar figures.

Extracts every $-prefixed number (with optional scale words T/B/M or
trillion/billion/million) from the agent response, then:

  1. If any extracted value exceeds numeric_checks["max_value"], returns 0.0
     immediately (guards against YTD totals / clearly wrong magnitudes).
  2. For each value in numeric_checks["must_include"], checks whether at least
     one extracted number is within rel_tol of it.  Score = fraction matched.
  3. Returns 1.0 if no must_include values are defined (nothing to check).
  4. Returns 1.0 (no-op) if numeric_checks is None/empty/absent.

numeric_checks schema (dict):
  {
    "must_include": [float, ...],   # required values; score = fraction matched
    "rel_tol":      float,          # relative tolerance, e.g. 0.05 for ±5%
    "max_value":    float | None,   # if any extracted value exceeds this → 0.0
  }

Backward compat: the old list-of-dicts format (with "description"/"threshold_pct"
keys) is accepted but treated as no-op (returns 1.0) — migrate callers to the
new dict schema to get real checks.

The evaluator is wired into run_experiment.py via check_numeric_accuracy() which
returns a @create_evaluator-decorated function for Phoenix compatibility.
"""

from __future__ import annotations

import re
from typing import Any

# ---------------------------------------------------------------------------
# Dollar-figure extraction
# ---------------------------------------------------------------------------

# Matches: $1.23 / $1.23B / $1.23 billion / $1,234 / $1.23T / $1.23M etc.
_DOLLAR_RE = re.compile(
    r"\$"
    r"([\d,]+(?:\.\d+)?)"           # digits (with optional commas / decimal)
    r"(?:\s*"
        r"(trillion|billion|million|T|B|M)"  # optional scale word
    r")?",
    re.IGNORECASE,
)

_SCALE = {
    "t": 1e12, "trillion": 1e12,
    "b": 1e9,  "billion": 1e9,
    "m": 1e6,  "million": 1e6,
}


def extract_dollar_values(text: str) -> list[float]:
    """Return all $-prefixed numbers found in *text*, scaled to raw dollars."""
    values: list[float] = []
    for m in _DOLLAR_RE.finditer(text):
        raw = m.group(1).replace(",", "")
        try:
            num = float(raw)
        except ValueError:
            continue
        scale_word = (m.group(2) or "").lower()
        num *= _SCALE.get(scale_word, 1.0)
        values.append(num)
    return values


# ---------------------------------------------------------------------------
# Core scoring logic
# ---------------------------------------------------------------------------

def _score_numeric(response_text: str, checks: dict | list | None) -> tuple[float, str]:
    """Return (score, explanation).

    score is in [0.0, 1.0]:
      1.0  — all must_include values matched (or no checks defined)
      0.0  — a max_value violation was found
      frac — fraction of must_include values matched
    """
    if not checks:
        return 1.0, "No numeric checks defined."

    # Backward compat: old list format → no-op
    if isinstance(checks, list):
        return 1.0, "Old-style list checks (description/threshold_pct) — no-op; migrate to dict schema."

    must_include: list[float] = checks.get("must_include") or []
    rel_tol: float = float(checks.get("rel_tol", 0.05))
    max_value: float | None = checks.get("max_value")

    extracted = extract_dollar_values(response_text)

    if not extracted:
        if not must_include:
            return 1.0, "No dollar figures found and no must_include checks required."
        return 0.0, f"No $-prefixed numbers found in response; {len(must_include)} must_include value(s) unmatched."

    # Rule 1: max_value guard
    if max_value is not None:
        violations = [v for v in extracted if v > max_value]
        if violations:
            viol_str = ", ".join(f"${v/1e9:.1f}B" for v in violations[:5])
            return 0.0, (
                f"max_value violation: {len(violations)} value(s) exceed "
                f"${max_value/1e9:.0f}B threshold: {viol_str}."
            )

    # Rule 2: must_include fraction
    if not must_include:
        return 1.0, f"max_value check passed. No must_include values to verify. Extracted: {[f'${v/1e9:.2f}B' for v in extracted]}."

    matched = 0
    details: list[str] = []
    for expected in must_include:
        hit = any(
            abs(v - expected) <= rel_tol * expected
            for v in extracted
        )
        if hit:
            matched += 1
            details.append(f"✓ ${expected/1e9:.2f}B")
        else:
            closest = min(extracted, key=lambda v: abs(v - expected))
            details.append(
                f"✗ ${expected/1e9:.2f}B (closest found: ${closest/1e9:.2f}B, "
                f"diff {abs(closest-expected)/expected*100:.1f}%)"
            )

    score = matched / len(must_include)
    explanation = "; ".join(details)
    return score, explanation


# ---------------------------------------------------------------------------
# Phoenix-compatible evaluator factory
# ---------------------------------------------------------------------------

def check_numeric_accuracy():
    """Return a @create_evaluator-decorated function for Phoenix experiments.

    Phoenix auto-binds the named parameters (input, output, metadata) from the
    experiment context. The evaluator is fully deterministic — no LLM call.

    Pass the returned callable directly to run_experiment(evaluators=[...]).
    """
    from phoenix.client.resources.experiments import create_evaluator  # type: ignore

    @create_evaluator(name="numeric_accuracy")
    def _judge(input, output, metadata=None) -> dict:  # noqa: A002
        response_text = (
            output.get("result", "") if isinstance(output, dict) else str(output)
        )
        checks = (
            metadata.get("numeric_checks") if isinstance(metadata, dict) else None
        )
        score, explanation = _score_numeric(response_text, checks)
        label = "numeric_pass" if score >= 1.0 else "numeric_fail"
        return {"label": label, "score": score, "explanation": explanation}

    return _judge
