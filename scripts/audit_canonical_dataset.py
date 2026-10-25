#!/usr/bin/env python3
"""Run the preserved manuscript dataset audit on an arbitrary dataset root.

The scientific audit logic is loaded directly from the immutable historical
auditor preserved under provenance/canonical_dataset/audit/. This wrapper only
provides portable input/output paths and safety checks.
"""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

HISTORICAL_AUDITOR = (
    REPO_ROOT
    / "provenance"
    / "canonical_dataset"
    / "audit"
    / "historical_audit_generated_dataset.py"
)

PRESERVED_AUDIT_DIR = (
    REPO_ROOT
    / "provenance"
    / "canonical_dataset"
    / "audit"
).resolve()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the preserved manuscript dataset audit with portable "
            "dataset and output paths."
        )
    )
    parser.add_argument(
        "--dataset-root",
        type=Path,
        required=True,
        help="Dataset root containing TRAIN, VAL and TEST.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory where regenerated audit outputs will be written.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow writing into a non-empty output directory.",
    )
    return parser.parse_args()


def load_historical_auditor():
    if not HISTORICAL_AUDITOR.is_file():
        raise FileNotFoundError(
            f"Preserved historical auditor not found: {HISTORICAL_AUDITOR}"
        )

    spec = importlib.util.spec_from_file_location(
        "historical_dataset_auditor",
        HISTORICAL_AUDITOR,
    )
    if spec is None or spec.loader is None:
        raise ImportError(
            f"Could not load preserved historical auditor: {HISTORICAL_AUDITOR}"
        )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_output_dir(output_dir: Path, overwrite: bool) -> Path:
    output_dir = output_dir.expanduser().resolve()

    if output_dir == PRESERVED_AUDIT_DIR:
        raise ValueError(
            "Refusing to overwrite the preserved canonical audit evidence: "
            f"{PRESERVED_AUDIT_DIR}"
        )

    if output_dir.exists() and any(output_dir.iterdir()) and not overwrite:
        raise FileExistsError(
            f"Output directory is not empty: {output_dir}. "
            "Choose a new directory or pass --overwrite."
        )

    return output_dir


def main() -> None:
    args = parse_args()

    dataset_root = args.dataset_root.expanduser().resolve()
    output_dir = validate_output_dir(args.output_dir, args.overwrite)

    if not dataset_root.is_dir():
        raise FileNotFoundError(f"Dataset root not found: {dataset_root}")

    auditor = load_historical_auditor()

    # Only runtime paths are replaced. The preserved scientific implementation
    # itself remains byte-for-byte unchanged.
    auditor.DATASET_ROOT = dataset_root
    auditor.OUTPUT_DIR = output_dir

    # PROJECT_ROOT is used by the historical script only for final path display.
    auditor.PROJECT_ROOT = output_dir.parent

    print(f"Historical auditor: {HISTORICAL_AUDITOR.relative_to(REPO_ROOT)}")
    print(f"Dataset root: {dataset_root}")
    print(f"Output directory: {output_dir}")

    auditor.main()


if __name__ == "__main__":
    main()
