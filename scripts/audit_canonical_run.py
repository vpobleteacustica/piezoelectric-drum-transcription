#!/usr/bin/env python3
"""Audit internal consistency of the canonical manuscript model run."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ROOT = REPO_ROOT / "provenance" / "canonical_run"

TRAINING = ROOT / "training" / "config.json"
CHECKPOINT_META = ROOT / "checkpoint" / "checkpoint_metadata.json"
CHECKPOINT = ROOT / "checkpoint" / "best_weights.weights.h5"

VAL_SELECTION = (
    ROOT
    / "fulltrack"
    / "fulltrack_nms_selected_config_from_val.json"
)

INFERENCE = (
    ROOT
    / "fulltrack"
    / "fulltrack_selected_inference_config.json"
)

TEST_CSV = (
    ROOT
    / "fulltrack"
    / "fulltrack_nms_test_metrics_using_val_config.csv"
)

EXPECTED_CLASSES = ["KD", "SD", "T12", "T14", "T16"]
EXPECTED_MIDI = [35, 38, 47, 45, 43]
EXPECTED_WEIGHTS = [1.0, 1.0, 1.2, 1.5, 1.7]

EXPECTED_CHECKPOINT_SHA256 = (
    "a45d9d0e21a46e477573f8aad36c9858"
    "223be1a72cef7116ba25ce4c2ddf878d"
)


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)
    print(f"PASS {message}")


def close(a, b, tol: float = 1e-12) -> bool:
    return math.isclose(
        float(a),
        float(b),
        rel_tol=0.0,
        abs_tol=tol,
    )


def main() -> None:
    training = load_json(TRAINING)
    checkpoint_meta = load_json(CHECKPOINT_META)
    val_selection = load_json(VAL_SELECTION)
    inference = load_json(INFERENCE)

    with TEST_CSV.open("r", encoding="utf-8", newline="") as f:
        test_rows = list(csv.DictReader(f))

    print("\n=== 1. CLASS SCHEMA ===")

    check(
        training["class_schema"] == "vibro_5_toms",
        "training class schema = vibro_5_toms",
    )
    check(
        checkpoint_meta["class_schema"] == training["class_schema"],
        "checkpoint metadata class schema matches training",
    )
    check(
        val_selection["class_schema"] == training["class_schema"],
        "VAL selection class schema matches training",
    )
    check(
        inference["class_schema"] == training["class_schema"],
        "final inference class schema matches training",
    )

    check(
        training["class_names"] == EXPECTED_CLASSES,
        "training class order = KD, SD, T12, T14, T16",
    )
    check(
        checkpoint_meta["class_names"] == EXPECTED_CLASSES,
        "checkpoint class order matches training",
    )
    check(
        val_selection["class_names"] == EXPECTED_CLASSES,
        "VAL-selection class order matches training",
    )
    check(
        inference["class_names"] == EXPECTED_CLASSES,
        "inference class order matches training",
    )

    check(
        training["labels"] == EXPECTED_MIDI,
        "training MIDI order = 35, 38, 47, 45, 43",
    )
    check(
        checkpoint_meta["labels"] == EXPECTED_MIDI,
        "checkpoint MIDI order matches training",
    )
    check(
        val_selection["labels"] == EXPECTED_MIDI,
        "VAL-selection MIDI order matches training",
    )
    check(
        inference["midi_labels"] == EXPECTED_MIDI,
        "inference MIDI order matches training",
    )

    print("\n=== 2. TRAINING / CHECKPOINT METADATA ===")

    expected_training = {
        "model_name": "Frame_RNN",
        "epochs": 60,
        "steps_per_epoch": 600,
        "validation_steps": 150,
        "batch_size": 1,
        "training_sequence": 64,
        "context": 9,
        "sample_rate": 100,
    }

    for field, expected in expected_training.items():
        check(
            training[field] == expected,
            f"{field} = {expected}",
        )

    check(
        training["class_weights"] == EXPECTED_WEIGHTS,
        "training class weights match canonical values",
    )
    check(
        checkpoint_meta["class_weights"] == EXPECTED_WEIGHTS,
        "checkpoint class weights match training",
    )
    check(
        checkpoint_meta["class_weights_order"]
        == training["class_weights_order"]
        == EXPECTED_CLASSES,
        "class-weight order is consistent",
    )

    print("\n=== 3. VAL-ONLY POSTPROCESSING SELECTION ===")

    check(
        val_selection["selection_split"] == "VAL",
        "postprocessing selection split = VAL",
    )
    check(
        val_selection["selected_checkpoint"] == "best",
        "selected checkpoint = best",
    )
    check(
        close(val_selection["selected_threshold"], 0.03),
        "VAL-selected threshold = 0.03",
    )
    check(
        close(val_selection["selected_onset_nms_ms"], 110.0),
        "VAL-selected NMS = 110 ms",
    )
    check(
        close(val_selection["onset_tolerance_ms"], 50.0),
        "VAL evaluation tolerance = 50 ms",
    )
    check(
        val_selection["test_not_used_for_selection"] is True,
        "VAL selection record states TEST was not used for selection",
    )

    check(
        inference["selected_checkpoint"] == "best",
        "final inference checkpoint = best",
    )
    check(
        inference["threshold_mode"] == "global",
        "final inference threshold mode = global",
    )
    check(
        close(inference["threshold_global"], 0.03),
        "final inference threshold = 0.03",
    )
    check(
        close(inference["onset_nms_ms"], 110.0),
        "final inference NMS = 110 ms",
    )
    check(
        close(inference["min_peak_distance_ms"], 110.0),
        "final minimum peak distance = 110 ms",
    )
    check(
        close(inference["onset_tolerance_ms"], 50.0),
        "final evaluation tolerance = 50 ms",
    )
    check(
        inference["selection_split"] == "VAL",
        "final config records VAL as selection split",
    )
    check(
        inference["final_report_split"] == "TEST",
        "final report split = TEST",
    )
    check(
        inference["test_not_used_for_selection"] is True,
        "TEST explicitly not used for selection",
    )
    check(
        inference["recommended_for_inference"] is True,
        "configuration marked recommended for inference",
    )

    print("\n=== 4. TEST TABLE STRUCTURE ===")

    check(
        len(test_rows) == 5,
        "canonical TEST metrics contain exactly five class rows",
    )

    check(
        [row["class"] for row in test_rows] == EXPECTED_CLASSES,
        "TEST CSV class order matches canonical order",
    )
    check(
        [int(row["midi_pitch"]) for row in test_rows] == EXPECTED_MIDI,
        "TEST CSV MIDI order matches canonical order",
    )

    check(
        all(close(row["threshold"], 0.03) for row in test_rows),
        "all TEST rows use threshold 0.03",
    )
    check(
        all(close(row["onset_nms_ms"], 110.0) for row in test_rows),
        "all TEST rows use NMS 110 ms",
    )
    check(
        all(close(row["tolerance_ms"], 50.0) for row in test_rows),
        "all TEST rows use tolerance 50 ms",
    )
    check(
        all(row["split"] == "TEST" for row in test_rows),
        "all canonical metric rows are TEST",
    )
    check(
        all(row["checkpoint"] == "best" for row in test_rows),
        "all canonical metric rows use best checkpoint",
    )

    print("\n=== 5. RECOMPUTE GLOBAL TEST METRICS ===")

    tp = sum(int(row["TP"]) for row in test_rows)
    fp = sum(int(row["FP"]) for row in test_rows)
    fn = sum(int(row["FN"]) for row in test_rows)

    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    micro_f1 = 2 * precision * recall / (precision + recall)
    macro_f1 = (
        sum(float(row["f1"]) for row in test_rows)
        / len(test_rows)
    )

    print(f"TP        = {tp}")
    print(f"FP        = {fp}")
    print(f"FN        = {fn}")
    print(f"micro P   = {precision:.12f}")
    print(f"micro R   = {recall:.12f}")
    print(f"micro F1  = {micro_f1:.12f}")
    print(f"macro F1  = {macro_f1:.12f}")

    check(tp == 8657, "TEST TP sum = 8657")
    check(fp == 6901, "TEST FP sum = 6901")
    check(fn == 5315, "TEST FN sum = 5315")

    check(
        close(precision, 0.5564339889445944),
        "recomputed micro precision matches canonical result",
    )
    check(
        close(recall, 0.6195963355281993),
        "recomputed micro recall matches canonical result",
    )
    check(
        close(micro_f1, 0.5863189976295292),
        "recomputed micro F1 matches canonical result",
    )
    check(
        close(macro_f1, 0.5854869775873086),
        "recomputed macro F1 matches canonical result",
    )

    print("\n=== 6. CROSS-CHECK PRESERVED JSON RESULTS ===")

    inference_test = inference["test_metrics"]["selected_config"]

    check(
        int(inference_test["TP"]) == tp,
        "inference JSON TEST TP matches CSV",
    )
    check(
        int(inference_test["FP"]) == fp,
        "inference JSON TEST FP matches CSV",
    )
    check(
        int(inference_test["FN"]) == fn,
        "inference JSON TEST FN matches CSV",
    )
    check(
        close(inference_test["micro_precision"], precision),
        "inference JSON micro precision matches recomputation",
    )
    check(
        close(inference_test["micro_recall"], recall),
        "inference JSON micro recall matches recomputation",
    )
    check(
        close(inference_test["micro_f1"], micro_f1),
        "inference JSON micro F1 matches recomputation",
    )
    check(
        close(inference_test["macro_f1"], macro_f1),
        "inference JSON macro F1 matches recomputation",
    )

    inference_rows = inference["test_metrics"]["by_class_selected_config"]
    selection_rows = val_selection["test_metrics_using_val_config"]

    check(
        len(inference_rows) == 5,
        "inference JSON contains five TEST class results",
    )
    check(
        len(selection_rows) == 5,
        "VAL-selection JSON contains five held-out TEST class results",
    )

    for csv_row, inference_row, selection_row in zip(
        test_rows,
        inference_rows,
        selection_rows,
    ):
        cls = csv_row["class"]

        check(
            inference_row["class"] == cls == selection_row["class"],
            f"{cls}: class identity agrees across CSV and JSON records",
        )

        for field in ("TP", "FP", "FN"):
            check(
                int(csv_row[field])
                == int(inference_row[field])
                == int(selection_row[field]),
                f"{cls}: {field} agrees across canonical records",
            )

        for field in ("precision", "recall", "f1"):
            check(
                close(csv_row[field], inference_row[field])
                and close(csv_row[field], selection_row[field]),
                f"{cls}: {field} agrees across canonical records",
            )

    print("\n=== 7. CHECKPOINT IDENTITY ===")

    digest = hashlib.sha256(CHECKPOINT.read_bytes()).hexdigest()
    print(f"checkpoint SHA-256 = {digest}")

    check(
        digest == EXPECTED_CHECKPOINT_SHA256,
        "checkpoint SHA-256 matches canonical source",
    )

    print("\n=== RESULT ===")
    print("PASS canonical run evidence is internally consistent.")


if __name__ == "__main__":
    main()
