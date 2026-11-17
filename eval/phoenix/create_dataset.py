"""Upload a CSV dataset to Phoenix for use in experiments.

Usage (from eval/phoenix/):
    python create_dataset.py --dataset-name sec-edgar-eval-0
    python create_dataset.py --dataset-name sec-edgar-eval-0 --dry-run
    python create_dataset.py --list

All datasets are registered in datasets.yaml.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import pandas as pd
import yaml
from dotenv import load_dotenv

load_dotenv()

EVAL_ROOT = Path(__file__).resolve().parent
DATASETS_YAML = EVAL_ROOT / "datasets.yaml"


def load_registry() -> dict:
    """Load datasets.yaml and return the datasets mapping."""
    with open(DATASETS_YAML) as f:
        return yaml.safe_load(f).get("datasets", {})


def resolve_csv_path(csv_path_str: str) -> Path:
    """Resolve csv_path relative to eval/phoenix/ (where datasets.yaml lives)."""
    p = Path(csv_path_str)
    if not p.is_absolute():
        p = EVAL_ROOT / p
    return p


def validate_csv(csv_path: Path, input_keys: list[str], output_keys: list[str]) -> pd.DataFrame:
    """Load CSV and verify required columns exist. Raises on failure."""
    df = pd.read_csv(csv_path)
    required = set(input_keys) | set(output_keys)
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"CSV {csv_path} is missing required columns: {missing}. "
            f"Found columns: {list(df.columns)}"
        )
    return df


def upload_dataset(
    dataset_name: str,
    phoenix_name: str | None,
    csv_path_override: str | None,
    dry_run: bool,
    phoenix_endpoint: str,
) -> None:
    """Validate and optionally upload a single dataset to Phoenix."""
    registry = load_registry()
    if dataset_name not in registry:
        print(f"ERROR: Dataset '{dataset_name}' not found in datasets.yaml.")
        print(f"Available: {list(registry.keys())}")
        sys.exit(1)

    entry = registry[dataset_name]
    csv_path = resolve_csv_path(csv_path_override or entry["csv_path"])
    input_keys: list[str] = entry["input_keys"]
    output_keys: list[str] = entry["output_keys"]
    description: str = entry.get("description", "")
    px_name = phoenix_name or dataset_name

    print(f"Dataset      : {dataset_name}")
    print(f"Phoenix name : {px_name}")
    print(f"CSV path     : {csv_path}")
    print(f"Input keys   : {input_keys}")
    print(f"Output keys  : {output_keys}")
    print(f"Description  : {description.strip()}")
    print()

    df = validate_csv(csv_path, input_keys, output_keys)
    print(f"Rows         : {len(df)}")

    if dry_run:
        print("\n[DRY RUN] Validation passed — dataset not uploaded.")
        return

    from phoenix.client import Client

    client = Client(base_url=phoenix_endpoint)
    client.datasets.create_dataset(
        name=px_name,
        dataframe=df,
        input_keys=input_keys,
        output_keys=output_keys,
        dataset_description=description.strip(),
    )
    print(f"\nDataset '{px_name}' uploaded to Phoenix at {phoenix_endpoint}.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Upload a dataset to Phoenix for SEC EDGAR eval experiments."
    )
    parser.add_argument("--list", action="store_true", help="List registered datasets and exit.")
    parser.add_argument("--dataset-name", metavar="NAME", help="Dataset name from datasets.yaml.")
    parser.add_argument(
        "--phoenix-name",
        metavar="NAME",
        help="Override the Phoenix dataset name (default: same as --dataset-name).",
    )
    parser.add_argument(
        "--csv-path",
        metavar="PATH",
        help="Override the CSV path from datasets.yaml.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate the CSV without uploading to Phoenix.",
    )
    parser.add_argument(
        "--phoenix-endpoint",
        metavar="URL",
        default=os.getenv("PHOENIX_ENDPOINT", "http://localhost:6006"),
        help="Phoenix server endpoint (default: http://localhost:6006).",
    )
    args = parser.parse_args()

    if args.list:
        registry = load_registry()
        print(f"Registered datasets ({len(registry)}):")
        for name, entry in registry.items():
            print(f"  {name}")
            print(f"    csv_path   : {entry['csv_path']}")
            print(f"    input_keys : {entry['input_keys']}")
            print(f"    output_keys: {entry['output_keys']}")
        return

    if not args.dataset_name:
        parser.error("--dataset-name is required (or use --list).")

    upload_dataset(
        dataset_name=args.dataset_name,
        phoenix_name=args.phoenix_name,
        csv_path_override=args.csv_path,
        dry_run=args.dry_run,
        phoenix_endpoint=args.phoenix_endpoint,
    )


if __name__ == "__main__":
    main()
