#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Audit generated drum-vibration phrase dataset.

This script audits the current generated dataset shared by Rodrigo:
DATASET_NUEVO/

Expected structure:
    DATASET_NUEVO/
        TRAIN/
            AUDIO/*.wav
            LABELS/*.json
            ANNOTATIONS/*.txt
        VAL/
            AUDIO/*.wav
            LABELS/*.json
            ANNOTATIONS/*.txt
        TEST/
            AUDIO/*.wav
            LABELS/*.json
            ANNOTATIONS/*.txt
        dataset_config.json
        dataset_event_counts.csv
        dataset_event_counts.json

Outputs:
    data/metadata/generated_dataset_audit/
        generated_split_summary.csv
        generated_pairing_audit.csv
        generated_audio_metadata.csv
        generated_profile_bpm_summary.csv
        generated_event_counts_from_labels.csv
        generated_annotation_consistency.csv
        generated_overlap_summary.csv
        generated_source_sample_usage.csv
        generated_dataset_audit_summary.md
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd
import soundfile as sf


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATASET_ROOT = (
    PROJECT_ROOT
    / "data"
    / "DATASET_VIBRATIONS"
    / "_incoming_20260816"
    / "DATASET_NUEVO"
)

OUTPUT_DIR = PROJECT_ROOT / "data" / "metadata" / "generated_dataset_audit"

SPLITS = ["TRAIN", "VAL", "TEST"]

MIDI_TO_CLASS = {
    35: "KD",
    38: "SD",
    47: "T12",
    45: "T14",
    43: "T16",
}

CLASS_TO_MIDI = {v: k for k, v in MIDI_TO_CLASS.items()}

PROFILE_NAMES = [
    "basic_groove",
    "standard_rock",
    "fill_heavy",
    "fast_dense",
    "humanized_mixed",
]


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def parse_profile_and_bpm(stem: str) -> tuple[str | None, int | None]:
    """
    Parse profile and BPM from file stems such as:
        train_fast_dense_004603_180bpm
        train_basic_groove_003256_95bpm
    """
    bpm_match = re.search(r"_(\d+)bpm$", stem)
    bpm = int(bpm_match.group(1)) if bpm_match else None

    profile = None
    for candidate in PROFILE_NAMES:
        if candidate in stem:
            profile = candidate
            break

    return profile, bpm


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def extract_events_from_label_json(path: Path) -> list[dict]:
    """
    Rodrigo's LABELS JSON files may be either a list of event dictionaries
    or a dictionary containing an 'events' field.
    """
    data = load_json(path)

    if isinstance(data, list):
        events = data
    elif isinstance(data, dict) and "events" in data:
        events = data["events"]
    else:
        events = []

    clean_events = []

    for ev in events:
        if not isinstance(ev, dict):
            continue

        timestamp = ev.get("timestamp", ev.get("time", ev.get("onset", None)))
        instrument = ev.get("instrument", ev.get("class", None))
        source_wav = ev.get("source_wav", None)

        midi = ev.get("midi", ev.get("class_id", None))
        if midi is None and instrument in CLASS_TO_MIDI:
            midi = CLASS_TO_MIDI[instrument]

        if instrument is None and midi is not None:
            try:
                instrument = MIDI_TO_CLASS.get(int(midi), None)
            except Exception:
                instrument = None

        try:
            timestamp = float(timestamp)
        except Exception:
            timestamp = None

        try:
            midi = int(midi) if midi is not None else None
        except Exception:
            midi = None

        clean_events.append(
            {
                "timestamp": timestamp,
                "instrument": instrument,
                "midi": midi,
                "source_wav": source_wav,
                "raw_event": ev,
            }
        )

    return clean_events


def read_annotation_txt(path: Path) -> list[dict]:
    """
    Expected format:
        timestamp_seconds midi_pitch velocity
    """
    rows = []

    if not path.exists():
        return rows

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                continue

            parts = stripped.split()
            if len(parts) < 2:
                continue

            try:
                timestamp = float(parts[0])
                midi = int(float(parts[1]))
                velocity = float(parts[2]) if len(parts) >= 3 else None
            except Exception:
                continue

            rows.append(
                {
                    "timestamp": timestamp,
                    "midi": midi,
                    "instrument": MIDI_TO_CLASS.get(midi, None),
                    "velocity": velocity,
                }
            )

    return rows


def collect_split_summary() -> pd.DataFrame:
    rows = []

    for split in SPLITS:
        split_dir = DATASET_ROOT / split
        audio_dir = split_dir / "AUDIO"
        labels_dir = split_dir / "LABELS"
        annotations_dir = split_dir / "ANNOTATIONS"

        wav_files = sorted(audio_dir.glob("*.wav")) if audio_dir.exists() else []
        json_files = sorted(labels_dir.glob("*.json")) if labels_dir.exists() else []
        txt_files = sorted(annotations_dir.glob("*.txt")) if annotations_dir.exists() else []

        rows.append(
            {
                "split": split,
                "n_wav": len(wav_files),
                "n_json": len(json_files),
                "n_txt": len(txt_files),
                "audio_dir_exists": audio_dir.exists(),
                "labels_dir_exists": labels_dir.exists(),
                "annotations_dir_exists": annotations_dir.exists(),
            }
        )

    return pd.DataFrame(rows)


def collect_pairing_audit() -> pd.DataFrame:
    rows = []

    for split in SPLITS:
        split_dir = DATASET_ROOT / split
        audio_dir = split_dir / "AUDIO"
        labels_dir = split_dir / "LABELS"
        annotations_dir = split_dir / "ANNOTATIONS"

        wav_stems = {p.stem for p in audio_dir.glob("*.wav")} if audio_dir.exists() else set()
        json_stems = {p.stem for p in labels_dir.glob("*.json")} if labels_dir.exists() else set()
        txt_stems = {p.stem for p in annotations_dir.glob("*.txt")} if annotations_dir.exists() else set()

        all_stems = sorted(wav_stems | json_stems | txt_stems)

        for stem in all_stems:
            rows.append(
                {
                    "split": split,
                    "stem": stem,
                    "has_wav": stem in wav_stems,
                    "has_json": stem in json_stems,
                    "has_txt": stem in txt_stems,
                    "complete_triplet": (
                        stem in wav_stems and stem in json_stems and stem in txt_stems
                    ),
                }
            )

    return pd.DataFrame(rows)


def collect_audio_metadata() -> pd.DataFrame:
    rows = []

    for split in SPLITS:
        audio_dir = DATASET_ROOT / split / "AUDIO"

        for wav_path in sorted(audio_dir.glob("*.wav")):
            profile, bpm = parse_profile_and_bpm(wav_path.stem)

            try:
                info = sf.info(str(wav_path))
                duration = info.frames / info.samplerate if info.samplerate else None

                rows.append(
                    {
                        "split": split,
                        "file": wav_path.name,
                        "stem": wav_path.stem,
                        "profile": profile,
                        "bpm": bpm,
                        "samplerate": info.samplerate,
                        "channels": info.channels,
                        "frames": info.frames,
                        "duration_s": duration,
                        "format": info.format,
                        "subtype": info.subtype,
                        "error": None,
                    }
                )

            except Exception as exc:
                rows.append(
                    {
                        "split": split,
                        "file": wav_path.name,
                        "stem": wav_path.stem,
                        "profile": profile,
                        "bpm": bpm,
                        "samplerate": None,
                        "channels": None,
                        "frames": None,
                        "duration_s": None,
                        "format": None,
                        "subtype": None,
                        "error": repr(exc),
                    }
                )

    return pd.DataFrame(rows)


def collect_event_counts_and_sources() -> tuple[pd.DataFrame, pd.DataFrame]:
    event_rows = []
    source_rows = []

    for split in SPLITS:
        labels_dir = DATASET_ROOT / split / "LABELS"

        for json_path in sorted(labels_dir.glob("*.json")):
            profile, bpm = parse_profile_and_bpm(json_path.stem)
            events = extract_events_from_label_json(json_path)

            for i, ev in enumerate(events):
                instrument = ev["instrument"]
                midi = ev["midi"]

                event_rows.append(
                    {
                        "split": split,
                        "stem": json_path.stem,
                        "profile": profile,
                        "bpm": bpm,
                        "event_index": i,
                        "timestamp": ev["timestamp"],
                        "instrument": instrument,
                        "midi": midi,
                        "source_wav": ev["source_wav"],
                    }
                )

                if ev["source_wav"] is not None:
                    source_rows.append(
                        {
                            "split": split,
                            "stem": json_path.stem,
                            "profile": profile,
                            "instrument": instrument,
                            "midi": midi,
                            "source_wav": ev["source_wav"],
                        }
                    )

    event_df = pd.DataFrame(event_rows)
    source_df = pd.DataFrame(source_rows)

    return event_df, source_df


def summarize_event_counts(event_df: pd.DataFrame) -> pd.DataFrame:
    if event_df.empty:
        return pd.DataFrame()

    grouped = (
        event_df.groupby(["split", "instrument", "midi"], dropna=False)
        .size()
        .reset_index(name="event_count")
    )

    totals = grouped.groupby("split")["event_count"].transform("sum")
    grouped["percentage"] = 100 * grouped["event_count"] / totals

    return grouped.sort_values(["split", "midi"])


def summarize_profile_bpm(audio_df: pd.DataFrame) -> pd.DataFrame:
    if audio_df.empty:
        return pd.DataFrame()

    rows = []

    for (split, profile), group in audio_df.groupby(["split", "profile"], dropna=False):
        rows.append(
            {
                "split": split,
                "profile": profile,
                "n_files": len(group),
                "bpm_min": group["bpm"].min(),
                "bpm_median": group["bpm"].median(),
                "bpm_max": group["bpm"].max(),
                "duration_min_s": group["duration_s"].min(),
                "duration_median_s": group["duration_s"].median(),
                "duration_max_s": group["duration_s"].max(),
            }
        )

    return pd.DataFrame(rows).sort_values(["split", "profile"])


def collect_annotation_consistency() -> pd.DataFrame:
    rows = []

    for split in SPLITS:
        labels_dir = DATASET_ROOT / split / "LABELS"
        annotations_dir = DATASET_ROOT / split / "ANNOTATIONS"

        for json_path in sorted(labels_dir.glob("*.json")):
            txt_path = annotations_dir / f"{json_path.stem}.txt"

            json_events = extract_events_from_label_json(json_path)
            txt_events = read_annotation_txt(txt_path)

            json_pairs_original = [
                (float(ev["timestamp"]), int(ev["midi"]))
                for ev in json_events
                if ev["timestamp"] is not None and ev["midi"] is not None
            ]

            txt_pairs_original = [
                (float(ev["timestamp"]), int(ev["midi"]))
                for ev in txt_events
                if ev["timestamp"] is not None and ev["midi"] is not None
            ]

            json_pairs_sorted = sorted(json_pairs_original, key=lambda x: (x[0], x[1]))
            txt_pairs_sorted = sorted(txt_pairs_original, key=lambda x: (x[0], x[1]))

            same_event_count = len(json_pairs_original) == len(txt_pairs_original)

            same_sequence_exact = [
                (round(t, 6), m) for t, m in json_pairs_original
            ] == [
                (round(t, 6), m) for t, m in txt_pairs_original
            ]

            same_sequence_exact_after_sort = [
                (round(t, 6), m) for t, m in json_pairs_sorted
            ] == [
                (round(t, 6), m) for t, m in txt_pairs_sorted
            ]

            midi_sequence_equal_after_sort = False
            same_sequence_within_0_5ms_after_sort = False
            same_sequence_within_1ms_after_sort = False
            max_abs_time_difference_s_after_sort = None

            if same_event_count:
                midi_sequence_equal_after_sort = [
                    m for _, m in json_pairs_sorted
                ] == [
                    m for _, m in txt_pairs_sorted
                ]

                abs_diffs = [
                    abs(t_json - t_txt)
                    for (t_json, _), (t_txt, _) in zip(
                        json_pairs_sorted, txt_pairs_sorted
                    )
                ]

                max_abs_time_difference_s_after_sort = max(abs_diffs) if abs_diffs else 0.0

                same_sequence_within_0_5ms_after_sort = (
                    midi_sequence_equal_after_sort
                    and max_abs_time_difference_s_after_sort <= 0.0005
                )

                same_sequence_within_1ms_after_sort = (
                    midi_sequence_equal_after_sort
                    and max_abs_time_difference_s_after_sort <= 0.001
                )

            rows.append(
                {
                    "split": split,
                    "stem": json_path.stem,
                    "txt_exists": txt_path.exists(),
                    "n_json_events": len(json_pairs_original),
                    "n_txt_events": len(txt_pairs_original),
                    "same_event_count": same_event_count,
                    "same_sequence_exact_original_order": same_sequence_exact,
                    "same_sequence_exact_after_sort": same_sequence_exact_after_sort,
                    "midi_sequence_equal_after_sort": midi_sequence_equal_after_sort,
                    "same_sequence_within_0_5ms_after_sort": same_sequence_within_0_5ms_after_sort,
                    "same_sequence_within_1ms_after_sort": same_sequence_within_1ms_after_sort,
                    "max_abs_time_difference_s_after_sort": max_abs_time_difference_s_after_sort,
                }
            )

    return pd.DataFrame(rows)


def summarize_overlaps(event_df: pd.DataFrame, tolerance_s: float = 0.05) -> pd.DataFrame:
    """
    Summarize very close onsets within each phrase.

    Exact simultaneous events:
        timestamp difference == 0 after sorting.

    Close events:
        timestamp difference <= tolerance_s.
    """
    if event_df.empty:
        return pd.DataFrame()

    rows = []

    for (split, stem), group in event_df.groupby(["split", "stem"]):
        times = sorted(t for t in group["timestamp"].dropna().tolist())

        exact_simultaneous_pairs = 0
        close_pairs = 0
        min_delta = None

        for i in range(len(times) - 1):
            delta = times[i + 1] - times[i]

            if min_delta is None or delta < min_delta:
                min_delta = delta

            if abs(delta) == 0:
                exact_simultaneous_pairs += 1

            if delta <= tolerance_s:
                close_pairs += 1

        rows.append(
            {
                "split": split,
                "stem": stem,
                "n_events": len(times),
                "min_inter_onset_interval_s": min_delta,
                "exact_simultaneous_pairs": exact_simultaneous_pairs,
                f"close_pairs_le_{int(tolerance_s * 1000)}ms": close_pairs,
            }
        )

    return pd.DataFrame(rows)


def summarize_source_usage(source_df: pd.DataFrame) -> pd.DataFrame:
    if source_df.empty:
        return pd.DataFrame()

    grouped = (
        source_df.groupby(["instrument", "midi", "source_wav"], dropna=False)
        .size()
        .reset_index(name="usage_count")
    )

    return grouped.sort_values(["instrument", "usage_count"], ascending=[True, False])

def build_key_metrics_table(
    split_df: pd.DataFrame,
    pairing_df: pd.DataFrame,
    audio_df: pd.DataFrame,
    event_count_df: pd.DataFrame,
    consistency_df: pd.DataFrame,
    overlap_df: pd.DataFrame,
    source_usage_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build a compact, paper-ready table with the main dataset audit metrics.
    """
    rows = []

    total_wav = int(split_df["n_wav"].sum())
    total_json = int(split_df["n_json"].sum())
    total_txt = int(split_df["n_txt"].sum())

    rows.append(
        {
            "category": "Dataset size",
            "metric": "Total WAV files",
            "value": total_wav,
            "notes": "Across TRAIN, VAL and TEST",
        }
    )
    rows.append(
        {
            "category": "Dataset size",
            "metric": "Total LABELS JSON files",
            "value": total_json,
            "notes": "Rich event metadata",
        }
    )
    rows.append(
        {
            "category": "Dataset size",
            "metric": "Total ANNOTATIONS TXT files",
            "value": total_txt,
            "notes": "ADTOF-compatible onset annotations",
        }
    )

    n_complete = int(pairing_df["complete_triplet"].sum()) if not pairing_df.empty else 0
    n_incomplete = int((~pairing_df["complete_triplet"]).sum()) if not pairing_df.empty else 0

    rows.append(
        {
            "category": "Pairing",
            "metric": "Complete WAV/JSON/TXT triplets",
            "value": n_complete,
            "notes": "One audio file, one JSON file and one TXT file per phrase",
        }
    )
    rows.append(
        {
            "category": "Pairing",
            "metric": "Incomplete triplets",
            "value": n_incomplete,
            "notes": "Should be zero",
        }
    )

    if not audio_df.empty:
        rows.append(
            {
                "category": "Audio format",
                "metric": "Observed sample rates",
                "value": "; ".join(map(str, sorted(audio_df["samplerate"].dropna().unique()))),
                "notes": "Hz",
            }
        )
        rows.append(
            {
                "category": "Audio format",
                "metric": "Observed channels",
                "value": "; ".join(map(str, sorted(audio_df["channels"].dropna().unique()))),
                "notes": "1 = mono",
            }
        )
        rows.append(
            {
                "category": "Audio format",
                "metric": "Observed WAV subtypes",
                "value": "; ".join(map(str, sorted(audio_df["subtype"].dropna().unique()))),
                "notes": "Expected PCM_16",
            }
        )
        rows.append(
            {
                "category": "Phrase duration",
                "metric": "Median duration",
                "value": round(float(audio_df["duration_s"].median()), 4),
                "notes": "seconds, all splits pooled",
            }
        )
        rows.append(
            {
                "category": "Phrase duration",
                "metric": "Duration range",
                "value": f"{audio_df['duration_s'].min():.4f}–{audio_df['duration_s'].max():.4f}",
                "notes": "seconds, all splits pooled",
            }
        )

    if not event_count_df.empty:
        for instrument in ["KD", "SD", "T12", "T14", "T16"]:
            subset = event_count_df[event_count_df["instrument"] == instrument]
            if subset.empty:
                continue

            rows.append(
                {
                    "category": "Class balance",
                    "metric": f"{instrument} percentage",
                    "value": round(float(subset["percentage"].mean()), 4),
                    "notes": "Mean percentage across TRAIN, VAL and TEST",
                }
            )

    if not consistency_df.empty:
        rows.append(
            {
                "category": "Annotation consistency",
                "metric": "Same event count JSON/TXT",
                "value": int(consistency_df["same_event_count"].sum()),
                "notes": f"Out of {len(consistency_df)} files",
            }
        )
        rows.append(
            {
                "category": "Annotation consistency",
                "metric": "Exact sequence after chronological sorting",
                "value": int(consistency_df["same_sequence_exact_after_sort"].sum()),
                "notes": f"Out of {len(consistency_df)} files",
            }
        )
        rows.append(
            {
                "category": "Annotation consistency",
                "metric": "Sequence within 1 ms after sorting",
                "value": int(consistency_df["same_sequence_within_1ms_after_sort"].sum()),
                "notes": f"Out of {len(consistency_df)} files",
            }
        )

    if not overlap_df.empty:
        rows.append(
            {
                "category": "Temporal structure",
                "metric": "Median events per phrase",
                "value": round(float(overlap_df["n_events"].median()), 4),
                "notes": "All splits pooled",
            }
        )
        rows.append(
            {
                "category": "Temporal structure",
                "metric": "Events per phrase range",
                "value": f"{int(overlap_df['n_events'].min())}–{int(overlap_df['n_events'].max())}",
                "notes": "All splits pooled",
            }
        )
        rows.append(
            {
                "category": "Temporal structure",
                "metric": "Median close onset pairs ≤50 ms",
                "value": round(float(overlap_df["close_pairs_le_50ms"].median()), 4),
                "notes": "All splits pooled",
            }
        )

    if not source_usage_df.empty:
        rows.append(
            {
                "category": "Source traceability",
                "metric": "Unique source WAV references",
                "value": int(source_usage_df["source_wav"].nunique()),
                "notes": "References from phrase events to isolated-hit source files",
            }
        )

    return pd.DataFrame(rows)

def write_markdown_summary(
    split_df: pd.DataFrame,
    pairing_df: pd.DataFrame,
    audio_df: pd.DataFrame,
    event_count_df: pd.DataFrame,
    consistency_df: pd.DataFrame,
    overlap_df: pd.DataFrame,
    source_usage_df: pd.DataFrame,
) -> None:
    md_path = OUTPUT_DIR / "generated_dataset_audit_summary.md"

    n_complete = int(pairing_df["complete_triplet"].sum()) if not pairing_df.empty else 0
    n_incomplete = int((~pairing_df["complete_triplet"]).sum()) if not pairing_df.empty else 0

    audio_sr = sorted(audio_df["samplerate"].dropna().unique().tolist()) if not audio_df.empty else []
    audio_channels = sorted(audio_df["channels"].dropna().unique().tolist()) if not audio_df.empty else []
    audio_subtypes = sorted(audio_df["subtype"].dropna().unique().tolist()) if not audio_df.empty else []

    n_sequence_exact_original = (
        int(consistency_df["same_sequence_exact_original_order"].sum())
        if not consistency_df.empty
        else 0
    )

    n_sequence_exact_sorted = (
        int(consistency_df["same_sequence_exact_after_sort"].sum())
        if not consistency_df.empty
        else 0
    )

    n_sequence_1ms_sorted = (
        int(consistency_df["same_sequence_within_1ms_after_sort"].sum())
        if not consistency_df.empty
        else 0
    )

    n_sequence_total = len(consistency_df)

    with md_path.open("w", encoding="utf-8") as f:
        f.write("# Generated dataset audit summary\n\n")
        f.write(f"Dataset root: `{DATASET_ROOT}`\n\n")

        f.write("## Split summary\n\n")
        f.write(split_df.to_markdown(index=False))
        f.write("\n\n")

        f.write("## Pairing summary\n\n")
        f.write(f"- Complete WAV/JSON/TXT triplets: {n_complete}\n")
        f.write(f"- Incomplete triplets: {n_incomplete}\n\n")

        f.write("## Audio technical summary\n\n")
        f.write(f"- Sample rates observed: {audio_sr}\n")
        f.write(f"- Channels observed: {audio_channels}\n")
        f.write(f"- WAV subtypes observed: {audio_subtypes}\n\n")

        if not audio_df.empty:
            duration_summary = audio_df.groupby("split")["duration_s"].describe()
            f.write("### Duration by split\n\n")
            f.write(duration_summary.to_markdown())
            f.write("\n\n")

        f.write("## Event counts from LABELS JSON\n\n")
        if not event_count_df.empty:
            f.write(event_count_df.to_markdown(index=False))
        else:
            f.write("_No event counts available._")
        f.write("\n\n")

        f.write("## LABELS JSON vs ANNOTATIONS TXT consistency\n\n")
        f.write(
            f"- Files with exact same timestamp/MIDI sequence "
            f"in original order: {n_sequence_exact_original} / {n_sequence_total}\n"
        )
        f.write(
            f"- Files with exact same timestamp/MIDI sequence "
            f"after chronological sorting: {n_sequence_exact_sorted} / {n_sequence_total}\n"
        )
        f.write(
            f"- Files with matching MIDI sequence and timestamps within 1 ms "
            f"after chronological sorting: {n_sequence_1ms_sorted} / {n_sequence_total}\n\n"
        )

        f.write("## Temporal structure and overlap summary\n\n")
        if not overlap_df.empty:
            compact_overlap = (
                overlap_df.groupby("split")
                .agg(
                    n_phrases=("stem", "count"),
                    events_mean=("n_events", "mean"),
                    events_median=("n_events", "median"),
                    events_min=("n_events", "min"),
                    events_max=("n_events", "max"),
                    min_ioi_median_s=("min_inter_onset_interval_s", "median"),
                    exact_simultaneous_pairs_mean=("exact_simultaneous_pairs", "mean"),
                    close_pairs_le_50ms_mean=("close_pairs_le_50ms", "mean"),
                    close_pairs_le_50ms_median=("close_pairs_le_50ms", "median"),
                    close_pairs_le_50ms_max=("close_pairs_le_50ms", "max"),
                )
                .reset_index()
            )

            numeric_cols = compact_overlap.select_dtypes(include="number").columns
            compact_overlap[numeric_cols] = compact_overlap[numeric_cols].round(4)

            f.write(compact_overlap.to_markdown(index=False))
        else:
            f.write("_No overlap information available._")
        f.write("\n\n")

        f.write("## Source sample usage\n\n")
        if not source_usage_df.empty:
            total_sources = source_usage_df["source_wav"].nunique()
            f.write(f"- Unique source WAV references: {total_sources}\n")
            f.write("- See `generated_source_sample_usage.csv` for details.\n")
        else:
            f.write("_No source sample references found._\n")


def main() -> None:
    ensure_output_dir()

    if not DATASET_ROOT.exists():
        raise FileNotFoundError(f"Dataset root not found: {DATASET_ROOT}")

    print(f"[INFO] Auditing dataset: {DATASET_ROOT}")
    print(f"[INFO] Output directory: {OUTPUT_DIR}")

    split_df = collect_split_summary()
    pairing_df = collect_pairing_audit()
    audio_df = collect_audio_metadata()

    event_df, source_df = collect_event_counts_and_sources()
    event_count_df = summarize_event_counts(event_df)
    profile_bpm_df = summarize_profile_bpm(audio_df)
    consistency_df = collect_annotation_consistency()
    overlap_df = summarize_overlaps(event_df, tolerance_s=0.05)
    source_usage_df = summarize_source_usage(source_df)

    key_metrics_df = build_key_metrics_table(
        split_df=split_df,
        pairing_df=pairing_df,
        audio_df=audio_df,
        event_count_df=event_count_df,
        consistency_df=consistency_df,
        overlap_df=overlap_df,
        source_usage_df=source_usage_df,
    )

    split_df.to_csv(OUTPUT_DIR / "generated_split_summary.csv", index=False)
    pairing_df.to_csv(OUTPUT_DIR / "generated_pairing_audit.csv", index=False)
    audio_df.to_csv(OUTPUT_DIR / "generated_audio_metadata.csv", index=False)
    profile_bpm_df.to_csv(OUTPUT_DIR / "generated_profile_bpm_summary.csv", index=False)
    event_df.to_csv(OUTPUT_DIR / "generated_events_long.csv", index=False)
    event_count_df.to_csv(OUTPUT_DIR / "generated_event_counts_from_labels.csv", index=False)
    consistency_df.to_csv(OUTPUT_DIR / "generated_annotation_consistency.csv", index=False)
    overlap_df.to_csv(OUTPUT_DIR / "generated_overlap_summary.csv", index=False)
    source_usage_df.to_csv(OUTPUT_DIR / "generated_source_sample_usage.csv", index=False)

    key_metrics_df.to_csv(OUTPUT_DIR / "generated_dataset_audit_key_metrics.csv", index=False)

    write_markdown_summary(
        split_df=split_df,
        pairing_df=pairing_df,
        audio_df=audio_df,
        event_count_df=event_count_df,
        consistency_df=consistency_df,
        overlap_df=overlap_df,
        source_usage_df=source_usage_df,
    )

    print("[OK] Audit completed.")
    print()
    print("Generated files:")
    for path in sorted(OUTPUT_DIR.glob("*")):
        print(f"  - {path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()