# Canonical Source Snapshot

## Purpose

This document records the exact source state from which the publication-facing
code and reproducibility materials are being curated.

The source workspace corresponds to the official five-class vibration pipeline
used to produce the dataset, trained model, full-track inference configuration,
and test-set results reported in the manuscript:

**Piezoelectric vibration sensing for automatic drum transcription using a traceable onset-labeled phrase dataset**

No source file should be incorporated into this publication repository without
being checked against this snapshot and the canonical manuscript state.

## Source repository

Repository:

`https://github.com/RodrigoKstor42/Automatic-Drum-Transcription-with-Vibrations.git`

Canonical source branch:

`official/v0.1-vibro5-pipeline`

Canonical source commit:

`327b972d273961df455d591321d383ce5d19bacd`

Commit subject:

`Prepare official vibro5 pipeline release`

The source working tree was clean when the snapshot below was recorded.

## Dataset-generation source files

| Source file | SHA-256 |
| --- | --- |
| `DATASET_GENERATOR/SRC/phrase_generator.py` | `d35a8db980716bed2d33c4671513605ce1b04e77835f084910984b43b15e8372` |
| `DATASET_GENERATOR/SRC/generation_profiles.py` | `7d59184333d7c949d00e734eb818a70d9d2c3b3415d9ab5c3f8c705791c3afe3` |
| `DATASET_GENERATOR/json_to_adtof_txt.py` | `9e390dad7858bffdb2838bf0225b5ebf8d4b3e36a5c1eb6c8d7c032c68b2b87c` |
| `DATASET_GENERATOR/CUSTOM_5CLASS_MULTIPROFILE_LOW_FULL/dataset_config.json` | `20e696dde48aab43196606f1287fd8994b0c88fcc3cefc95149b536379efe165` |
| `DATASET_GENERATOR/CUSTOM_5CLASS_MULTIPROFILE_LOW_FULL/dataset_event_counts.json` | `dce174140f2d33c678a7deeb892fd03ab8a1cfd3fed49a4ad8b6ea05dac3eee6` |

## Training and full-track evaluation source files

| Source file | SHA-256 |
| --- | --- |
| `SCRIPTS/training/train_custom_split.py` | `51c256a1a52c937359033017ab579561c3bf4ac45a394f83d9dcd9e136e26c82` |
| `SCRIPTS/calibration/calibrate_fulltrack_thresholds.py` | `30504f6d53a12e87ffc1a2fc5c65e8bacd34ab01307c389a81bd4e833b774e86` |
| `SCRIPTS/analysis/analyze_run_errors.py` | `ddc6986289c382bc59d9b58787b5cffdf3278fe2b0b5d743661cd91e1b343cf8` |
| `SCRIPTS/common/dataset_roots.py` | `d9d63f7d541541299be740adfae9f1a75bc4d10e8fb24c65cc1e83adaa746935` |
| `adtof/config.py` | `2407bb014a2e1adfa10c2ab36fe0f77dd6ff1197b423f789f25d4913b8cfbdaa` |
| `adtof/model/dataLoader.py` | `75cd8e61f063cd8cb95734143aa0b9ab8cca9520944d8a6b3133ca4bb483a212` |

The `adtof/` files originate from the adapted ADTOF code base. Their hashes are
recorded here for provenance, but inclusion in the publication repository
requires a separate license, attribution, and minimal-patch review.

## Official manuscript run

Canonical run:

`RUNS/serious_5class_low_60ep_weighted_t14t16`

Training characteristics relevant to the manuscript:

- model: `Frame_RNN`;
- epochs: 60;
- steps per epoch: 600;
- validation steps: 150;
- batch size: 1;
- training sequence: 64;
- context: 9;
- feature sample rate: 100;
- class schema: `vibro_5_toms`;
- class order: KD, SD, T12, T14, T16;
- class weights: 1.0, 1.0, 1.2, 1.5, 1.7.

## Official run artifacts

| Source file | SHA-256 |
| --- | --- |
| `RUNS/serious_5class_low_60ep_weighted_t14t16/config.json` | `10a624e471516f3f8a08cec97d1ce4c4e4e1a6a22c4ec3e0923f126b5049ce00` |
| `RUNS/serious_5class_low_60ep_weighted_t14t16/checkpoints/checkpoint_metadata.json` | `822659e252c31ce42fcc8f3f4636811f7e8acd801156a6010dd2b1939190e28c` |
| `RUNS/serious_5class_low_60ep_weighted_t14t16/checkpoints/best_weights.weights.h5` | `a45d9d0e21a46e477573f8aad36c9858223be1a72cef7116ba25ce4c2ddf878d` |
| `RUNS/serious_5class_low_60ep_weighted_t14t16/fulltrack_calibration_f1_nms/fulltrack_selected_inference_config.json` | `ccc70cdd6852656c9296ab523223bd60e093c1aae0084cedf9a0d70edafeaca3` |

## Manuscript inference authority

The authoritative inference configuration for the manuscript is:

`RUNS/serious_5class_low_60ep_weighted_t14t16/fulltrack_calibration_f1_nms/fulltrack_selected_inference_config.json`

It specifies:

- selected checkpoint: `best`;
- global decision threshold: `0.030`;
- onset NMS window: `110 ms`;
- onset-matching tolerance: `50 ms`;
- parameter-selection split: `VAL`;
- final reporting split: `TEST`;
- TEST not used for parameter selection.

This full-track configuration supersedes the earlier batch-limited calibration
summary retained in the run-level `README.md`.

## Canonical TEST result

Under the authoritative full-track configuration:

- TP: 8657;
- FP: 6901;
- FN: 5315;
- micro-precision: 0.5564;
- micro-recall: 0.6196;
- micro-F1: 0.5863;
- macro-F1: 0.5855.

These values define the official manuscript baseline.

## Curation rule

Files may be migrated from the source repository only when they:

1. match the source commit recorded above;
2. are required to reproduce a manuscript method or result;
3. do not contain obsolete experimental defaults presented as current settings;
4. do not depend on unreviewed absolute local paths;
5. have appropriate licensing and attribution for redistribution; and
6. remain consistent with `docs/DATASET.md` and `configs/baseline_v1.yaml`.

The publication repository should contain a minimal, auditable reproduction
path rather than a wholesale copy of the historical development repository.
