"""Run a Phoenix experiment against the SEC EDGAR agent.

Usage (from eval/phoenix/):
    python run_experiment.py --dataset-name sec-edgar-eval-0
    python run_experiment.py --dataset-name sec-edgar-eval-0 --system-prompt-version v2
    python run_experiment.py --dataset-name sec-edgar-eval-0 --no-validate

The experiment:
  1. Loads the named Phoenix dataset (must have been uploaded via create_dataset.py).
  2. Initializes the SECEdgarAgent with the chosen system prompt version.
  3. Runs every example through the agent.
  4. Scores each response with LLM-as-judge evaluators:
     - match_expected_response  (correctness vs ground truth)
     - check_answer_scope       (within-scope vs out-of-scope)
  5. Logs all traces and scores to Phoenix (http://localhost:6006 by default).

Required .env variables:
    WATSONX_URL, WATSONX_API_KEY, WATSONX_PROJECT_ID, AGENT_MODEL, JUDGE_MODEL
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Make sure sibling modules (judges) are importable
sys.path.insert(0, str(Path(__file__).resolve().parent))

EVAL_ROOT = Path(__file__).resolve().parent
PROMPT_VERSIONS = ["v1", "v2"]


def validate_env() -> list[str]:
    """Check required env vars. Return list of missing ones."""
    required = ["WATSONX_URL", "WATSONX_API_KEY", "WATSONX_PROJECT_ID", "AGENT_MODEL"]
    return [k for k in required if not os.getenv(k)]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a Phoenix experiment against the SEC EDGAR MCP agent."
    )
    parser.add_argument(
        "--dataset-name",
        metavar="NAME",
        required=True,
        help="Phoenix dataset name (as uploaded via create_dataset.py).",
    )
    parser.add_argument(
        "--system-prompt-version",
        choices=PROMPT_VERSIONS,
        default="v1",
        help=f"System prompt version to use. Choices: {PROMPT_VERSIONS}. Default: v1.",
    )
    parser.add_argument(
        "--project-name",
        metavar="NAME",
        default=os.getenv("PHOENIX_PROJECT", "sec-edgar-eval"),
        help="Phoenix project name (default: sec-edgar-eval).",
    )
    parser.add_argument(
        "--phoenix-endpoint",
        metavar="URL",
        default=os.getenv("PHOENIX_ENDPOINT", "http://localhost:6006"),
        help="Phoenix server UI + API endpoint (default: http://localhost:6006).",
    )
    parser.add_argument(
        "--experiment-description",
        metavar="DESC",
        default=None,
        help="Optional human-readable description for this experiment run.",
    )
    parser.add_argument(
        "--dataset-version-id",
        metavar="ID",
        default=None,
        help="Pin to a specific Phoenix dataset version ID.",
    )
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip env-var validation check before running.",
    )
    args = parser.parse_args()

    # --- Env validation ---
    if not args.no_validate:
        missing = validate_env()
        if missing:
            print(f"ERROR: Missing required environment variables: {missing}")
            print("Populate these in .env at the repo root, or pass --no-validate to skip.")
            sys.exit(1)

    print("SEC EDGAR Phoenix Experiment")
    print(f"  Dataset          : {args.dataset_name}")
    print(f"  Prompt version   : {args.system_prompt_version}")
    print(f"  Project          : {args.project_name}")
    print(f"  Phoenix endpoint : {args.phoenix_endpoint}")
    print(f"  Agent model      : {os.getenv('AGENT_MODEL', '(not set)')}")
    print(f"  Judge model      : {os.getenv('JUDGE_MODEL', 'meta-llama/llama-3-3-70b-instruct')}")
    print()

    # --- Late imports (require venv) ---
    from phoenix.client import Client

    from agent import SECEdgarAgent
    from judges import check_answer_scope, match_expected_response

    # --- Load Phoenix dataset ---
    phoenix_url = args.phoenix_endpoint
    client = Client(base_url=phoenix_url)

    dataset_kwargs: dict = {"dataset": args.dataset_name}
    if args.dataset_version_id:
        dataset_kwargs["version_id"] = args.dataset_version_id

    dataset = client.datasets.get_dataset(**dataset_kwargs)
    print(f"Loaded dataset '{args.dataset_name}' ({len(dataset)} examples)")

    # --- Build the agent task ---
    agent = SECEdgarAgent(
        system_prompt_version=args.system_prompt_version,
        phoenix_endpoint=args.phoenix_endpoint.replace(":6006", ":4317"),  # OTLP port
        project_name=args.project_name,
    )
    task = agent.create_experiment_task()

    # --- Build experiment metadata ---
    description = args.experiment_description or (
        f"sec_edgar_agent prompt={args.system_prompt_version} "
        f"model={os.getenv('AGENT_MODEL', 'unknown')}"
    )

    # --- Run experiment ---
    print(f"Starting experiment: {description}")
    print("This may take several minutes for 20 questions...")
    print()

    experiment = client.experiments.run_experiment(
        dataset=dataset,
        task=task,
        evaluators=[check_answer_scope(), match_expected_response()],
        experiment_description=description,
    )

    print()
    print(f"Experiment complete!")
    print(f"  Experiment ID : {getattr(experiment, 'id', 'n/a')}")
    print(f"  View results  : {args.phoenix_endpoint}")
    print()
    print("Per-question traces and scores are available in the Phoenix UI.")
    print("Filter by project name to see only this experiment.")


if __name__ == "__main__":
    main()
