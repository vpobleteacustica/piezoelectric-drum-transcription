# Reproducibility Guide

This document describes the reproducibility chain for the canonical experiment
reported in the manuscript accompanying this repository.

The repository distinguishes explicitly between:

1. **historical evidence preserved verbatim**, corresponding to files used or
   produced during the thesis experiments; and
2. **reproduction procedures reconstructed from that evidence**, which are
   provided to make the workflow portable without implying that they are
   literal shell commands originally executed during the experiment.

## 1. Canonical reproducibility chain

The reported manuscript results are supported by the following chain:

1. measured single-hit vibration recordings;
2. deterministic phrase-level dataset generation;
3. canonical 12,000-example WAV/JSON/TXT dataset;
4. dataset integrity and annotation-consistency audit;
5. ADTOF upstream source pinned to an exact commit;
6. a minimal patch reconstructing the ADTOF variant used for the experiment;
7. preserved training, calibration, and analysis source code;
8. preserved runtime environment;
9. preserved canonical training configuration;
10. preserved best model checkpoint;
11. full-track postprocessing selection using VAL only; and
12. final TEST metrics produced after freezing the VAL-selected configuration.

The final manuscript baseline uses the five-class schema:

| Class | MIDI |
| --- | ---: |
| KD | 35 |
| SD | 38 |
| T12 | 47 |
| T14 | 45 |
| T16 | 43 |

## 2. Canonical dataset

The canonical phrase-level dataset contains 12,000 examples:

| Split | Phrases |
| --- | ---: |
| TRAIN | 9,600 |
| VAL | 1,200 |
| TEST | 1,200 |

Each phrase is represented by a WAV file, JSON metadata, and TXT onset
annotations.

The canonical signal format is:

- mono;
- 12 kHz sampling rate;
- PCM 16-bit WAV.

Detailed dataset specifications and audit results are documented in:

    docs/DATASET.md

The public archive containing the complete dataset is prepared separately from
the Git repository because of its size. Its persistent identifier and dataset
license will be added once the archival record is finalized.

## 3. Dataset generation and audit

The exact dataset-generation source used for the canonical corpus is preserved
under:

    src/dataset_generator/

The canonical generation configuration and dataset metadata are preserved
under:

    provenance/canonical_dataset/

A portable generation entry point is provided as:

    scripts/generate_canonical_dataset.py

A portable audit entry point is provided as:

    scripts/audit_canonical_dataset.py

The portable audit has been verified against the canonical dataset and
reproduces the preserved key audit outputs byte-for-byte.

The annotation audit established that JSON and TXT event annotations are fully
consistent after chronological sorting. The maximum absolute onset-time
difference after sorting is zero for all 12,000 phrases.

## 4. ADTOF upstream and vibration adaptation

The model pipeline is based on ADTOF:

    https://github.com/MZehren/ADTOF

The upstream source is pinned to commit:

    b3968fb332f69b65ee07c089fc62f436503755db

ADTOF is distributed under the Creative Commons
Attribution-NonCommercial-ShareAlike 4.0 International license
(CC BY-NC-SA 4.0).

Instead of redistributing the complete ADTOF tree, this repository preserves
the minimal patch required to reconstruct the exact variant used in the
canonical experiment:

    third_party/adtof/patches/vibro5.patch

The upstream license and adaptation documentation are preserved in:

    third_party/adtof/LICENSE
    third_party/adtof/README.md

The patch modifies exactly four upstream files:

    adtof/config.py
    adtof/io/mir.py
    adtof/model/dataLoader.py
    adtof/ressources/instrumentsMapping.py

The remaining 30 Python files in the historical ADTOF tree were verified
byte-identical to the pinned upstream source.

### Reconstructing the adapted ADTOF tree

From a clean working directory:

    git clone https://github.com/MZehren/ADTOF.git
    cd ADTOF
    git checkout b3968fb332f69b65ee07c089fc62f436503755db
    git apply /path/to/piezoelectric-drum-transcription/third_party/adtof/patches/vibro5.patch

The resulting 34 Python files were verified byte-for-byte against the ADTOF
tree used in the canonical thesis experiment.

## 5. Preserved pipeline source snapshot

The finalized publication-oriented source snapshot for the training,
calibration, and analysis pipeline is preserved under:

    provenance/canonical_pipeline/source/

These files come from the finalized `official/v0.1-vibro5-pipeline` source
snapshot at commit:

    327b972d273961df455d591321d383ce5d19bacd

They provide the canonical release implementation used to inspect and
reconstruct the pipeline. The preserved training launcher is not claimed to
be the exact intermediate working-tree revision that launched the canonical
training run on 2026-06-28; that distinction is documented below.

They include:

    SCRIPTS/training/train_custom_split.py
    SCRIPTS/calibration/calibrate_fulltrack_thresholds.py
    SCRIPTS/analysis/analyze_run_errors.py
    SCRIPTS/common/dataset_roots.py

These files are preserved verbatim from the finalized source snapshot rather
than rewritten for publication.

Their SHA-256 values are:

    51c256a1a52c937359033017ab579561c3bf4ac45a394f83d9dcd9e136e26c82
    SCRIPTS/training/train_custom_split.py

    30504f6d53a12e87ffc1a2fc5c65e8bacd34ab01307c389a81bd4e833b774e86
    SCRIPTS/calibration/calibrate_fulltrack_thresholds.py

    ddc6986289c382bc59d9b58787b5cffdf3278fe2b0b5d743661cd91e1b343cf8
    SCRIPTS/analysis/analyze_run_errors.py

    d9d63f7d541541299be740adfae9f1a75bc4d10e8fb24c65cc1e83adaa746935
    SCRIPTS/common/dataset_roots.py

## 6. Canonical runtime environment

The historical Conda environment specification is preserved verbatim as:

    provenance/canonical_pipeline/source/environment.yml

SHA-256:

    189b2db8a977b456cadf1d475fd85c9bcfbc1101e2cc0a022586f6e2ecdf29ab

The environment is named `adtof_rod` and specifies Python 3.10.20 together
with pinned versions of TensorFlow, tf-keras, Keras, NumPy, SciPy, pandas,
matplotlib, librosa, madmom, pretty_midi, scikit-learn, soundfile, mido,
jellyfish, and mir_eval.

This file records the environment used by the historical pipeline. It should
not be silently replaced by a modernized dependency specification when
reproducing the reported experiment.

## 7. Canonical training configuration

The preserved run configuration is located at:

    provenance/canonical_run/training/config.json

The manuscript baseline uses:

| Parameter | Value |
| --- | --- |
| Model | Frame_RNN |
| Epochs | 60 |
| Steps per epoch | 600 |
| Validation steps | 150 |
| Batch size | 1 |
| Training sequence | 64 |
| Context | 9 |
| Feature sample rate | 100 Hz |
| Class weights | 1.0, 1.0, 1.2, 1.5, 1.7 |
| Class-weight order | KD, SD, T12, T14, T16 |
| Onset tolerance | 50 ms |

### Historical training-source and command limitation

The canonical run configuration records an execution time of
`2026-06-28T21:10:05.326114-04:00`.

Git history brackets that execution between:

- `60b0960106046310eac5ca73920bb77372478a22`
  (`2026-06-21 20:42:21 -0400`), and
- `df7d06bd1ba53a2c68d55e996ed39f72ca653ed9`
  (`2026-07-21 00:04:17 -0400`).

The earlier committed training launcher does not yet contain the complete
class-weight and VAL-calibration behavior recorded by the canonical run,
whereas the later finalized launcher additionally records loss-selection
fields that are absent from the canonical run configuration. This establishes
that the run was produced from an intermediate working-tree revision that was
not preserved as a Git commit.

A local Git forensic check using unreachable objects found no recoverable
intermediate blob for that launcher.

Importantly, the complete tracked `adtof/` tree (37 files) is byte-identical
between the two commits bracketing the run. The ADTOF adaptation is therefore
stable across that interval; the unresolved provenance is limited to the
project-specific training launcher revision.

No preserved artifact establishes the literal shell command originally
executed to launch the run. Therefore, any command provided for rerunning the
training stage must be described as a **reconstructed reproduction command
derived from the preserved run configuration and compatible command-line
interface**, not as a verbatim historical command.

For the reported experiment, the preserved run configuration, checkpoint,
training history, postprocessing-selection artifacts, and final metrics remain
the primary authorities.

### Training determinism boundary

The preserved ADTOF data-loading code uses fixed `random_state=0` values for
the relevant sample-order shuffling operations. However, neither the finalized
training launcher nor the underlying ADTOF model code sets a global
TensorFlow/Keras random seed for neural-network initialization.

Consequently, this repository distinguishes between two reproducibility
targets:

- **artifact reproducibility**: the exact canonical checkpoint, configuration,
  selection artifacts, and reported metrics are preserved and can be audited;
- **training-rerun reproducibility**: the architecture, dataset, split,
  hyperparameters, class weights, optimizer/loss family, and evaluation
  procedure can be reconstructed, but a fresh training run is not expected to
  reproduce the canonical checkpoint byte-for-byte.

Small numerical or optimization differences may therefore occur across fresh
training runs, hardware platforms, or TensorFlow execution environments.
The preserved checkpoint is the authoritative model artifact for reproducing
the manuscript results.

### Reconstructed training command

The following command is a **reconstructed reproduction command**. It is derived from the canonical run configuration, preserved run artifacts, and the finalized compatible training launcher. It is not claimed to be the literal shell command executed on 2026-06-28.

It assumes that the pinned ADTOF source has already been reconstructed with `third_party/adtof/patches/vibro5.patch`, that the finalized training launcher is available at `SCRIPTS/training/train_custom_split.py`, and that `DATASET_ROOT` points to the canonical 12,000-example dataset.

```bash
DATASET_ROOT="/path/to/CUSTOM_5CLASS_MULTIPROFILE_LOW_FULL"

python SCRIPTS/training/train_custom_split.py \
  --dataset-root "$DATASET_ROOT" \
  --model-name Frame_RNN \
  --batch-size 1 \
  --training-sequence 64 \
  --context 9 \
  --sample-rate 100 \
  --class-weights 1.0 1.0 1.2 1.5 1.7 \
  --loss-type bce \
  --epochs 60 \
  --steps-per-epoch 600 \
  --validation-steps 150 \
  --output-dir RUNS \
  --run-name rerun_serious_5class_low_60ep_weighted_t14t16 \
  --save-checkpoints \
  --threshold 0.5 \
  --thresholds 0.005 0.0075 0.01 0.015 0.02 0.03 0.04 0.05 0.075 0.1 0.125 \
  --onset-tolerance-ms 50 \
  --onset-thresholds 0.005 0.0075 0.01 0.015 0.02 0.03 0.04 0.05 0.075 0.1 0.125 \
  --calibrate-thresholds-on-val
```

Several details are intentional:

- `--class-weights` reproduces the canonical KD/SD/T12/T14/T16 weighting
  `[1.0, 1.0, 1.2, 1.5, 1.7]`;
- `--loss-type bce` explicitly retains the binary-crossentropy behavior
  corresponding to the canonical run, before focal-loss support was added;
- `--same-padding` is intentionally omitted, matching the canonical
  `same_padding=false` configuration;
- `--no-val` is intentionally omitted;
- `--save-checkpoints` is required to produce the best and final checkpoint
  artifacts represented in the canonical run;
- the threshold grid is supplied explicitly because the finalized launcher
  has a different default grid from the one recorded by the canonical run;
- `--calibrate-thresholds-on-val` activates VAL-based onset calibration and
  onset evaluation in the finalized launcher.

The calibration performed by this reconstructed training command corresponds
to the historical training-run calibration path. It is **not** the
authoritative postprocessing calibration used for the manuscript.

The manuscript results use the later full-track VAL selection with:

- checkpoint: `best`;
- global threshold: `0.030`;
- NMS: `110 ms`;
- onset tolerance: `50 ms`; and
- TEST reserved for final reporting after VAL-based selection.

Because the training code does not set a global TensorFlow/Keras random seed,
a fresh rerun is not expected to regenerate the canonical checkpoint
byte-for-byte. The preserved checkpoint remains the authoritative model
artifact for reproducing the manuscript results.

## 8. Canonical checkpoint

The selected model checkpoint is preserved at:

    provenance/canonical_run/checkpoint/best_weights.weights.h5

SHA-256:

    a45d9d0e21a46e477573f8aad36c9858223be1a72cef7116ba25ce4c2ddf878d

The associated checkpoint metadata is preserved alongside it.

## 9. Full-track VAL selection and TEST evaluation

Postprocessing parameters were selected using complete VAL tracks.

The canonical selected configuration is:

| Parameter | Value |
| --- | ---: |
| Checkpoint | best |
| Global threshold | 0.030 |
| NMS | 110 ms |
| Onset tolerance | 50 ms |
| Selection split | VAL |
| Final report split | TEST |

TEST was not used for checkpoint, threshold, or NMS selection.

The authoritative preserved artifacts are:

    provenance/canonical_run/fulltrack/fulltrack_nms_selected_config_from_val.json
    provenance/canonical_run/fulltrack/fulltrack_selected_inference_config.json
    provenance/canonical_run/fulltrack/fulltrack_nms_test_metrics_using_val_config.csv

Earlier batch-limited or pre-NMS threshold-selection artifacts are historical
intermediate results and are not the authority for the manuscript tables.

## 10. Canonical TEST results

With checkpoint, threshold, and NMS frozen from VAL, the complete TEST split
produced:

| Metric | Value |
| --- | ---: |
| TP | 8,657 |
| FP | 6,901 |
| FN | 5,315 |
| Micro-precision | 0.5564 |
| Micro-recall | 0.6196 |
| Micro-F1 | 0.5863 |
| Macro-F1 | 0.5855 |

Class-wise TEST F1:

| Class | F1 |
| --- | ---: |
| KD | 0.5953 |
| SD | 0.5733 |
| T12 | 0.5814 |
| T14 | 0.5425 |
| T16 | 0.6349 |

## 11. Canonical run consistency audit

The repository provides:

    scripts/audit_canonical_run.py

This audit checks, among other items:

- class schema and MIDI ordering;
- canonical training configuration;
- VAL-only postprocessing selection;
- TEST metric-table structure;
- recomputation of TP, FP, FN, micro metrics, and macro-F1;
- agreement between CSV and JSON inference artifacts; and
- canonical checkpoint SHA-256.

A successful audit ends with:

    PASS canonical run evidence is internally consistent.

## 12. Reproducibility boundaries

This repository deliberately separates three kinds of material.

### Preserved evidence

Files under `provenance/` retain the historical state required to audit the
reported experiment. Historical absolute paths or other execution-specific
metadata may therefore remain in these files.

### Publication-facing utilities

Scripts under `scripts/` are intended to provide portable entry points or
audits without modifying the preserved historical evidence.

### Third-party code

Third-party material retains its own licensing terms. In particular, the ADTOF
adaptation must not be interpreted as being relicensed under the root MIT
license. See:

    THIRD_PARTY_NOTICES.md
    third_party/adtof/README.md
    third_party/adtof/LICENSE

## 13. Release policy

The manuscript submission release will be tagged so that the exact publication
state remains recoverable even if subsequent development continues.

The final release will also record the persistent identifier and license of the
separately archived canonical dataset.

No dataset DOI should be cited until that archival record has been created and
verified.

## 14. Verified local full-track reproduction (2026-10-26)

A local reproduction of the canonical full-track calibration was
completed on 2026-10-26 using the preserved model checkpoints,
verified patched ADTOF source, and regenerated dataset.
The model was not retrained.

The portable reproduction entry point is:

    scripts/reproduce_canonical_fulltrack.py

This procedure is reconstructed, not a literal historical command.

### Reproduction command

Use the compatible `adtof_rod` Python environment, including
`h5py`, and the pinned, patched ADTOF checkout.

From the repository root:

    PYTHON="/path/to/adtof_rod/bin/python"
    DATASET_ROOT="/absolute/path/to/regenerated_dataset"
    ADTOF_ROOT="/absolute/path/to/patched_ADTOF"
    OUTPUT_DIR="/absolute/path/to/new_fulltrack_outputs"

    TF_USE_LEGACY_KERAS=True "$PYTHON" -u -B scripts/reproduce_canonical_fulltrack.py \
      --dataset-root "$DATASET_ROOT" \
      --adtof-root "$ADTOF_ROOT" \
      --output-dir "$OUTPUT_DIR"

The output directory must be outside the repository, dataset,
and ADTOF checkout, and must be nonexistent or empty.
Use `--dry-run` to check preparation without calibration.

The wrapper verifies canonical and ADTOF hashes, creates
temporary normalized HDF5 checkpoints, and preserves a
`normalized_run/` bundle after successful calibration.

### Verified scientific results

| Parameter | Reproduced value |
| --- | --- |
| Checkpoint | best |
| Global threshold | 0.030 |
| NMS | 110 ms |
| Onset tolerance | 50 ms |
| Selection | VAL |
| Final evaluation | TEST |

| Metric | VAL | TEST |
| --- | ---: | ---: |
| Micro-F1 | 0.584740590 | 0.586318998 |
| Macro-F1 | 0.586238080 | 0.585486978 |

All 198 shared numeric fields of the historical and reproduced
selected-inference configurations agreed within 1e-9.

The historical configuration contains 121 additional numeric
fields associated with supplementary TEST analysis without NMS.

### Residual differences

The only identified TP/FP/FN discrepancy in the NMS comparison
is one additional historical false positive for T14 in TEST
without NMS:

| TEST without NMS | Historical | Reproduced |
| --- | ---: | ---: |
| TP | 10237 | 10237 |
| FP | 19582 | 19581 |
| FN | 3735 | 3735 |

Its cause remains unknown.

The historical checkpoint-selection artifact records threshold
0.040, whereas the reproduced artifact records 0.030 with
selected NMS. They reflect different calibration settings
and must not be interpreted as equivalent protocols.

### Evidence and limitations

Local reproduction evidence was preserved outside Git in the
sibling directory:

    20261025_rodrigo_fulltrack_reproduction/

It includes calibration outputs, the console log, normalized
checkpoints, a verified 43-record SHA-256 manifest, an audit
report, and a supplementary evidence seal.

The successful scientific reproduction used wrapper SHA-256:

    e64a7d2dcb61f063063a2517393745b67451c716c3ebc91f6c0b116d5cbb9a33

An exact copy is preserved in
`reproduction_wrapper_snapshot.py`.

The subsequently safety-hardened wrapper had SHA-256:

    fa203b126e4b71093a0610ed85543cca215b2fa08197fe818472c3c4626e8fd7

Its output-directory protections passed six dry-run tests.
The full evaluation was not repeated with this later version.

Bytewise identity of regenerated WAVs with historical audio
has not been demonstrated.

At the time of the full-track reproduction, the regenerated
12,000-example dataset resided under `/tmp`. Subsequently,
its complete 36,003-file content was copied to the sibling
persistent directory:

    20261026_rodrigo_regenerated_dataset_preserved/

Every preserved file was SHA-256 verified during copying and
independently verified again against the file manifest:

    20261025_rodrigo_fulltrack_reproduction/regenerated_dataset_file_manifest.json

The manifest SHA-256 is:

    1145a146383257030baa636d4ec298c8614ebd4e79e256cdaefd1c320680bf7f

This post-reproduction manifest covers all 12,000 WAV files,
12,000 TXT files, 12,002 JSON files, and one CSV file.

The original 43-record reproduction manifest remains unchanged;
it includes only the three dataset metadata files.

Local preservation does not establish historical WAV identity
or constitute a public archival deposit. Public dataset
archiving, licensing, and a persistent identifier remain pending.
