"""LLM-as-judge evaluator factories for the SEC EDGAR eval harness.

Each factory returns a phoenix.evals.ClassificationEvaluator instance
ready to be passed to phoenix.client.experiments.run_experiment(evaluators=[...]).

Usage:
    from judges import match_expected_response, check_answer_scope

    evaluators = [check_answer_scope(), match_expected_response()]
    client.experiments.run_experiment(dataset=ds, task=task, evaluators=evaluators)
"""

from .correctness_judge import match_expected_response
from .relevance_judge import check_answer_scope

__all__ = ["match_expected_response", "check_answer_scope"]
