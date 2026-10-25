# Publication Repository Version Status

## Current status

This repository is currently in **pre-submission curation**.

It is being prepared as the scientific companion repository for the manuscript:

**Piezoelectric vibration sensing for automatic drum transcription using a traceable onset-labeled phrase dataset**

The repository is not yet a formal paper release.

## Current validated components

The following publication-facing components have been established and audited against the current manuscript state:

- scientific repository README;
- machine-readable citation metadata;
- canonical dataset specification;
- canonical manuscript baseline configuration.

## Canonical scientific state

The current repository documents the following manuscript-level facts:

- 12,000 phrase examples;
- train/validation/test splits of 9,600 / 1,200 / 1,200;
- complete WAV/JSON/TXT triplets;
- phrase-level WAV format: mono PCM16 at 12 kHz;
- five classes: KD, SD, T12, T14, T16;
- official decision threshold: 0.030;
- NMS window: 110 ms;
- onset-matching tolerance: 50 ms;
- micro-F1: 0.5863;
- macro-F1: 0.5855.

These values define the baseline reported in the manuscript.

## Current provenance checkpoints

The following commits establish the current publication repository state:

- `7980439` — Establish scientific companion repository README
- `db426c4` — Add citation metadata for publication repository
- `1a5232a` — Document canonical vibration dataset specification
- `b1fc424` — Record canonical manuscript baseline configuration

## Not yet incorporated

The following components are intentionally **not yet considered part of the publication release**:

- audited source code corresponding exactly to the manuscript pipeline;
- dataset generation scripts;
- dataset audit scripts;
- model training scripts;
- inference scripts;
- evaluation scripts;
- final reproducibility commands;
- canonical public dataset archive;
- dataset persistent identifier / DOI;
- dataset license;
- dataset checksums;
- archived software release;
- final paper citation.

These items will be incorporated only after they have been checked against the manuscript and the canonical experimental state.

## Development repository

The historical thesis-development repository is separate from this publication repository.

It contains material created during the replication, troubleshooting, adaptation, and development process.

Material from that repository must not be copied into this publication repository without first verifying that:

1. it corresponds to the experiment reported in the manuscript;
2. its parameters match the canonical manuscript state;
3. it does not introduce superseded or exploratory configurations;
4. it can be documented reproducibly; and
5. it does not conflict with the dataset specification or official baseline.

## Planned submission release

The intended formal submission release is:

`v1.0.0-paper-submission`

This tag must not be created until:

- the publication code has been audited;
- the public dataset archive has been deposited;
- the dataset identifier has been added;
- checksums have been recorded;
- repository documentation has been updated with exact reproduction instructions; and
- the manuscript Data Availability statement matches the public resources.

## Versioning principle

The release cited by the manuscript should remain immutable and recoverable.

Subsequent development, reviewer-response analyses, calibration studies, or additional experiments should be recorded in later commits and, where appropriate, later releases rather than modifying the scientific state represented by the submission release.
