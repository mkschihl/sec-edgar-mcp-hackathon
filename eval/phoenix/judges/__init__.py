"""LLM-as-judge evaluator factories for the SEC EDGAR eval harness.

Each factory returns a callable wrapped with @create_evaluator, ready to be
passed to phoenix.client.experiments.run_experiment(evaluators=[...]).

Usage:
    from judges import match_expected_response, check_answer_scope, check_numeric_accuracy

    evaluators = [
        check_answer_scope(),
        match_expected_response(),
        check_numeric_accuracy(),
    ]
    client.experiments.run_experiment(dataset=ds, task=task, evaluators=evaluators)
"""

from .correctness_judge import match_expected_response, majority_vote_correctness
from .numeric_judge import check_numeric_accuracy
from .relevance_judge import check_answer_scope

__all__ = [
    "match_expected_response",
    "majority_vote_correctness",
    "check_answer_scope",
    "check_numeric_accuracy",
]
