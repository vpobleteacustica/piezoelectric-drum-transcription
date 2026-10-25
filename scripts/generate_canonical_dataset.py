#!/usr/bin/env python3
"""Regenerate the canonical phrase dataset reported in the manuscript.

This publication-facing wrapper reads the preserved canonical dataset
configuration and invokes the original dataset generator with exactly those
parameters. It does not modify or reimplement the preserved generator source.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = (
    REPO_ROOT
    / "provenance"
    / "canonical_dataset"
    / "dataset_config.json"
)
GENERATOR_PATH = (
    REPO_ROOT
    / "src"
    / "dataset_generator"
    / "SRC"
    / "phrase_generator.py"
)
GENERATOR_ROOT = GENERATOR_PATH.parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Regenerate the canonical 12,000-phrase vibration dataset "
            "using the preserved manuscript configuration."
        )
    )
    parser.add_argument(
        "--samples-dir",
        type=Path,
        required=True,
        help=(
            "Directory containing the isolated vibration-hit source samples. "
            "For provenance compatibility, this path must be located under "
            "src/dataset_generator (normally src/dataset_generator/MUESTRAS). "
            "That directory may be a symlink to separately archived data."
        ),
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        required=True,
        help="New or empty directory where TRAIN/VAL/TEST will be generated.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the exact generator command without executing it.",
    )
    return parser.parse_args()


def load_config() -> dict:
    if not CONFIG_PATH.is_file():
        raise FileNotFoundError(f"Canonical dataset config not found: {CONFIG_PATH}")

    with CONFIG_PATH.open("r", encoding="utf-8") as handle:
        config = json.load(handle)

    required = {
        "split_sizes",
        "profiles",
        "profile_weights",
        "tom_boost",
        "balance_individual_toms",
        "target_tom_share",
        "sample_rate",
        "wav_subtype",
        "peak_limit",
        "write_annotations",
        "seed",
    }
    missing = sorted(required.difference(config))
    if missing:
        raise ValueError(
            "Canonical dataset config is missing required fields: "
            + ", ".join(missing)
        )

    return config


def lexical_absolute(path: Path) -> Path:
    """Return an absolute path without resolving symbolic links."""
    return Path(os.path.abspath(os.fspath(path.expanduser())))


def validate_samples_location(samples_dir: Path) -> Path:
    """Keep source paths compatible with the preserved generator metadata."""
    samples_dir = lexical_absolute(samples_dir)

    try:
        samples_dir.relative_to(GENERATOR_ROOT)
    except ValueError as exc:
        raise ValueError(
            "The preserved generator records each source WAV relative to "
            f"{GENERATOR_ROOT}. Therefore --samples-dir must be located "
            "under src/dataset_generator. Use "
            "src/dataset_generator/MUESTRAS directly, or make that path "
            "a symlink to the separately archived source samples."
        ) from exc

    return samples_dir


def build_command(
    config: dict,
    samples_dir: Path,
    output_root: Path,
) -> list[str]:
    split_sizes = config["split_sizes"]
    samples_dir = validate_samples_location(samples_dir)

    command = [
        sys.executable,
        str(GENERATOR_PATH),
        "--samples-dir",
        str(samples_dir),
        "--output-root",
        str(output_root.resolve()),
        "--num-train",
        str(split_sizes["TRAIN"]),
        "--num-val",
        str(split_sizes["VAL"]),
        "--num-test",
        str(split_sizes["TEST"]),
        "--profiles",
        *[str(value) for value in config["profiles"]],
        "--profile-weights",
        *[str(value) for value in config["profile_weights"]],
        "--tom-boost",
        str(config["tom_boost"]),
        "--target-tom-share",
        str(config["target_tom_share"]),
        "--peak-limit",
        str(config["peak_limit"]),
        "--target-sr",
        str(config["sample_rate"]),
        "--wav-subtype",
        str(config["wav_subtype"]),
        "--seed",
        str(config["seed"]),
    ]

    command.append(
        "--balance-individual-toms"
        if config["balance_individual_toms"]
        else "--no-balance-individual-toms"
    )

    if config["write_annotations"]:
        command.append("--write-annotations")

    return command


def main() -> None:
    args = parse_args()
    config = load_config()

    if not GENERATOR_PATH.is_file():
        raise FileNotFoundError(
            f"Preserved dataset generator not found: {GENERATOR_PATH}"
        )

    samples_dir = validate_samples_location(args.samples_dir)

    if not args.dry_run and not samples_dir.is_dir():
        raise FileNotFoundError(
            f"Source-sample directory not found: {samples_dir}"
        )

    command = build_command(
        config=config,
        samples_dir=samples_dir,
        output_root=args.output_root,
    )

    print(f"Canonical config: {CONFIG_PATH.relative_to(REPO_ROOT)}")
    print(f"Generator: {GENERATOR_PATH.relative_to(REPO_ROOT)}")
    print("Command:")
    print(shlex.join(command))

    if args.dry_run:
        print("Dry run only; dataset generation was not started.")
        return

    subprocess.run(command, cwd=REPO_ROOT, check=True)


if __name__ == "__main__":
    main()
