# Dataset Specification

This document records the canonical dataset specification used in the manuscript:

**Piezoelectric vibration sensing for automatic drum transcription using a traceable onset-labeled phrase dataset**

## 1. Dataset scope

The dataset was constructed from measured isolated piezoelectric vibration responses associated with real acoustic-drum strokes.

The phrase-level corpus was generated procedurally from these measured source responses. Therefore, the generated phrases are not purely synthetic waveforms and are not recordings of complete continuous drum performances. They are controlled recombinations of measured real-hit vibration events.

This design preserves a traceable relationship between the physical acquisition stage and the phrase-level examples used for training, validation, and evaluation.

## 2. Source recording corpus

The original source recordings contain isolated piezoelectric vibration responses acquired from individual drum strokes.

Important characteristics of the source recording corpus are:

- recordings acquired at 32-bit depth;
- source material acquired using two sampling rates: 8 kHz and 12 kHz;
- five target drum components:
  - kick drum (KD);
  - snare drum (SD);
  - 12-inch tom (T12);
  - 14-inch tom (T14);
  - 16-inch tom (T16).

These properties describe the original acquisition corpus only.

They must not be confused with the standardized technical format of the generated phrase-level dataset used for model training and evaluation.

## 3. Canonical phrase-level dataset

The generated corpus used in the manuscript contains:

- **12,000 phrase examples** in total;
- **9,600 training phrases**;
- **1,200 validation phrases**;
- **1,200 test phrases**.

The three splits are non-overlapping.

Each phrase is represented by one complete:

- WAV file;
- JSON metadata file; and
- ADTOF-compatible TXT annotation file.

The audited corpus therefore contains:

- **12,000 complete WAV/JSON/TXT triplets**;
- **0 incomplete triplets**.

## 4. Phrase-level signal format

All phrase-level WAV files used in the manuscript were standardized as:

- mono;
- PCM16;
- 12 kHz sampling rate.

This **mono PCM16 / 12 kHz** specification is the canonical technical format of the phrase-level dataset reported in the paper.

## 5. Drum-class schema

The five-class schema is:

| Class | Drum component | MIDI label | Target distribution |
|---|---|---:|---:|
| KD | Kick drum | 35 | 35% |
| SD | Snare drum | 38 | 35% |
| T12 | 12-inch tom | 47 | 10% |
| T14 | 14-inch tom | 45 | 10% |
| T16 | 16-inch tom | 43 | 10% |

The resulting event distribution matched these intended proportions approximately across the generated corpus.

## 6. Annotation formats

Each phrase includes two complementary annotation representations.

### JSON metadata

The JSON representation retains rich event-level metadata, including information such as:

- drum class;
- onset time;
- onset sample;
- event duration;
- gain-related parameters;
- timing offsets; and
- reference to the isolated source WAV file used to render the event.

The source-file reference preserves traceability from each generated phrase-level event back to a measured piezoelectric vibration response.

### TXT onset annotations

The TXT representation provides the compact event format used by the adapted ADTOF-vibro transcription pipeline.

Each event row encodes:

- event timestamp;
- MIDI drum label; and
- velocity value.

## 7. Annotation consistency audit

The JSON and TXT annotations were compared to verify event-level consistency.

Because very close or near-simultaneous events may appear in different file orders, the comparison was performed after chronological sorting by onset time.

After sorting:

- **12,000/12,000 JSON/TXT pairs** contained identical timestamp and MIDI-label sequences.

## 8. Phrase-level temporal structure

The audited phrase corpus contains:

- median events per phrase: **11**;
- range: **10–16 events per phrase**;
- close onset pairs within **50 ms**.

These properties indicate that the corpus includes temporally dense drum-event patterns rather than only widely separated isolated events.

## 9. Source-sample traceability

Each generated event retains provenance information linking it to the isolated real-hit WAV file from which the vibration response was drawn.

The phrase-level dataset can therefore be audited at multiple levels:

1. phrase WAV signal;
2. event-level JSON metadata;
3. compact TXT onset annotations; and
4. original measured source response.

## 10. Public release status

**Pre-submission curation in progress.**

The canonical public dataset archive will contain the exact WAV/JSON/TXT corpus used to produce the manuscript results.

Before manuscript submission, the archive will be assigned:

- a persistent identifier;
- an explicit dataset license;
- version information; and
- cryptographic checksums.

The persistent identifier will then be added to this repository and to the manuscript Data Availability statement.

No dataset DOI should be cited until that archival step is complete.
