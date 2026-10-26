#!/usr/bin/env python3
"""Reproduce the canonical full-track VAL selection and frozen TEST evaluation."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import h5py

THRESHOLDS = [0.005, 0.0075, 0.01, 0.015, 0.02, 0.03, 0.04, 0.05, 0.075, 0.1, 0.125]
NMS_GRID_MS = [0, 50, 75, 90, 100, 110, 125, 150]

EXPECTED_ADTOF_ADAPTATION_SHA256 = {
    "adtof/config.py": "2407bb014a2e1adfa10c2ab36fe0f77dd6ff1197b423f789f25d4913b8cfbdaa",
    "adtof/io/mir.py": "eabcee0a5470435b9d66f9576d02a7f0d48ab13a0ed454f66df1d3283005a836",
    "adtof/model/dataLoader.py": "75cd8e61f063cd8cb95734143aa0b9ab8cca9520944d8a6b3133ca4bb483a212",
    "adtof/ressources/instrumentsMapping.py": "abd4e2178ac13c826c65d9aca94639e10670bde08b32c7f15925c3f86e18b235",
}

EXPECTED_CANONICAL_ARTIFACT_SHA256 = {
    "config": "10a624e471516f3f8a08cec97d1ce4c4e4e1a6a22c4ec3e0923f126b5049ce00",
    "metadata": "822659e252c31ce42fcc8f3f4636811f7e8acd801156a6010dd2b1939190e28c",
    "best": "a45d9d0e21a46e477573f8aad36c9858223be1a72cef7116ba25ce4c2ddf878d",
    "final": "39c5c4d3b972423f5da60221da9358a666e3c3d7630a7267edcc80fe82a054e9",
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Reproduce canonical full-track calibration from preserved artifacts."
    )
    parser.add_argument("--dataset-root", required=True)
    parser.add_argument(
        "--adtof-root",
        required=True,
        help="Root of the pinned ADTOF checkout with the preserved vibro5 patch applied.",
    )
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def require(path: Path, description: str) -> Path:
    if not path.exists():
        raise FileNotFoundError(f"Missing {description}: {path}")
    return path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_adtof_adaptation(adtof_root: Path) -> None:
    for relative, expected in EXPECTED_ADTOF_ADAPTATION_SHA256.items():
        path = require(adtof_root / relative, f"ADTOF adaptation file {relative}")
        actual = sha256(path)
        if actual != expected:
            raise ValueError(
                f"ADTOF adaptation hash mismatch for {relative}: "
                f"expected {expected}, got {actual}"
            )
    print("PASS ADTOF vibro5 adaptation hashes verified")


def validate_canonical_artifacts(config, metadata, best, final) -> None:
    artifacts = {
        "config": config,
        "metadata": metadata,
        "best": best,
        "final": final,
    }
    for name, path in artifacts.items():
        actual = sha256(path)
        expected = EXPECTED_CANONICAL_ARTIFACT_SHA256[name]
        if actual != expected:
            raise ValueError(
                f"Canonical artifact hash mismatch for {name}: "
                f"expected {expected}, got {actual}"
            )
    print("PASS canonical run artifact hashes verified")

def create_portable_checkpoint(source: Path, destination: Path) -> None:
    """Create a temporary checkpoint with portable HDF5 internal paths."""
    with h5py.File(source, "r") as fin:
        names = []
        fin.visit(names.append)
        needs_normalization = any("\\" in name for name in names) or any(
            "\\" in key for key in fin.keys()
        )

        if not needs_normalization:
            shutil.copy2(source, destination)
            print(f"Checkpoint already portable: {source.name}")
            return

        with h5py.File(destination, "w") as fout:
            for key, value in fin.attrs.items():
                fout.attrs[key] = value

            def copy_object(name, obj):
                normalized = name.replace("\\", "/")

                if isinstance(obj, h5py.Group):
                    target_group = fout.require_group(normalized)
                    for key, value in obj.attrs.items():
                        target_group.attrs[key] = value
                elif isinstance(obj, h5py.Dataset):
                    parent, _, leaf = normalized.rpartition("/")
                    group = fout.require_group(parent) if parent else fout
                    target_dataset = group.create_dataset(leaf, data=obj[()])
                    for key, value in obj.attrs.items():
                        target_dataset.attrs[key] = value

            fin.visititems(copy_object)

    with h5py.File(destination, "r") as fout:
        names = []
        fout.visit(names.append)
        if any("\\" in name for name in names) or any(
            "\\" in key for key in fout.keys()
        ):
            raise ValueError(
                f"Checkpoint HDF5 path normalization failed: {destination}"
            )

    print(f"PASS normalized checkpoint HDF5 paths: {source.name}")


def main():
    args = parse_args()

    repo = Path(__file__).resolve().parents[1]
    source = repo / "provenance" / "canonical_pipeline" / "source"
    canonical = repo / "provenance" / "canonical_run"

    calibrator = require(
        source / "SCRIPTS" / "calibration" / "calibrate_fulltrack_thresholds.py",
        "preserved calibration script",
    )
    config = require(
        canonical / "training" / "config.json",
        "canonical run config",
    )
    metadata = require(
        canonical / "checkpoint" / "checkpoint_metadata.json",
        "checkpoint metadata",
    )
    best = require(
        canonical / "checkpoint" / "best_weights.weights.h5",
        "best checkpoint",
    )
    final = require(
        canonical / "checkpoint" / "final_weights.weights.h5",
        "final checkpoint",
    )

    validate_canonical_artifacts(config, metadata, best, final)

    dataset_root = require(
        Path(args.dataset_root).expanduser().resolve(),
        "dataset root",
    )
    adtof_root = require(
        Path(args.adtof_root).expanduser().resolve(),
        "ADTOF root",
    )
    require(adtof_root / "adtof", "ADTOF Python package")
    validate_adtof_adaptation(adtof_root)

    output_dir = Path(args.output_dir).expanduser().resolve()

    # Never write calibration outputs inside preserved inputs.
    protected_roots = (
        ("repository", repo),
        ("dataset", dataset_root),
        ("ADTOF checkout", adtof_root),
    )

    for label, protected_root in protected_roots:
        if output_dir == protected_root or output_dir.is_relative_to(protected_root):
            raise ValueError(
                f"Output directory must be outside {label}: {output_dir}"
            )

    if output_dir.exists():
        if not output_dir.is_dir() or any(output_dir.iterdir()):
            raise FileExistsError(
                f"Output directory is not an empty directory: {output_dir}"
            )

    with tempfile.TemporaryDirectory(prefix="canonical_fulltrack_") as tmp:
        tmp_root = Path(tmp)

        dataset_view = tmp_root / "dataset"
        dataset_view.mkdir()

        # ADTOF appends the verified preprocessing parameters
        # to the cache prefix used by build_model_and_data().
        cache_dir = dataset_view / "PREPROCESS_MINI_TRAIN20-20000-12-1"
        cache_dir.mkdir()

        for split in ("TRAIN", "VAL", "TEST"):
            source_split = require(
                dataset_root / split,
                f"canonical dataset {split} split",
            )
            (dataset_view / split).symlink_to(
                source_split,
                target_is_directory=True,
            )

        run_dir = tmp_root / "canonical_run"
        checkpoints = run_dir / "checkpoints"
        checkpoints.mkdir(parents=True)

        shutil.copy2(config, run_dir / "config.json")
        shutil.copy2(metadata, checkpoints / "checkpoint_metadata.json")
        create_portable_checkpoint(
            best,
            checkpoints / "best_weights.weights.h5",
        )
        create_portable_checkpoint(
            final,
            checkpoints / "final_weights.weights.h5",
        )

        command = [
            sys.executable,
            str(calibrator),
            "--run-dir", str(run_dir),
            "--dataset-root", str(dataset_view),
            "--onset-tolerance-ms", "50",
            "--thresholds",
            *[str(x) for x in THRESHOLDS],
            "--threshold-mode", "global",
            "--selection-metric", "f1",
            "--beta", "1.5",
            "--onset-nms-ms", "0",
            "--nms-grid-ms",
            *[str(x) for x in NMS_GRID_MS],
            "--output-dir", str(output_dir),
        ]

        env = os.environ.copy()
        env["TF_USE_LEGACY_KERAS"] = "True"

        existing = env.get("PYTHONPATH")
        roots = [str(source), str(adtof_root)]
        if existing:
            roots.append(existing)
        env["PYTHONPATH"] = os.pathsep.join(roots)

        print(f"Canonical dataset source: {dataset_root}")
        print(f"Temporary read/write dataset view: {dataset_view}")
        print("Canonical full-track reproduction command:")
        print(" ".join(command))

        if args.dry_run:
            print("DRY RUN: calibration not executed.")
            return

        subprocess.run(command, check=True, env=env)

        # Preserve the normalized checkpoint bundle only after
        # successful calibration. Keep raw outputs unchanged.
        normalized_run = output_dir / "normalized_run"
        shutil.copytree(run_dir, normalized_run)
        print(f"PASS normalized run preserved: {normalized_run}")


if __name__ == "__main__":
    main()
