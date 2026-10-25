# Piezoelectric Drum Transcription

Reproducible code and resources for piezoelectric vibration-based automatic drum transcription using a traceable onset-labeled phrase dataset.

## Manuscript

**Piezoelectric vibration sensing for automatic drum transcription using a traceable onset-labeled phrase dataset**

Rodrigo Sánchez, Jorge P. Arenas, and Víctor Poblete  
Institute of Acoustics, Faculty of Engineering Sciences, Austral University of Chile, Valdivia, Chile.

This repository is the scientific companion to the manuscript and is being curated to contain the exact code, configuration files, audit outputs, and provenance information needed to reproduce the results reported in the paper.

> **Repository status:** pre-submission curation.  
> The canonical dataset archive and its persistent identifier will be added before manuscript submission. Files or commands that have not yet been audited against the manuscript are intentionally not included.

## Study overview

The study evaluates whether local mechanical vibration responses acquired directly from acoustic drum components with piezoelectric triggers can support onset-based automatic drum transcription.

The sensing-to-transcription workflow comprises:

1. piezoelectric vibration acquisition from acoustic drum components;
2. extraction of isolated real-hit vibration responses;
3. procedural generation of traceable phrase-level examples;
4. WAV/JSON/TXT onset-labeled annotations;
5. adaptation of an ADTOF-based onset-transcription pipeline;
6. thresholding and non-maximum suppression (NMS); and
7. event-level evaluation on an independent test split.

The five drum classes are:

| Class | MIDI label |
|---|---:|
| KD | 35 |
| SD | 38 |
| T12 | 47 |
| T14 | 45 |
| T16 | 43 |

## Canonical dataset snapshot used in the manuscript

| Property | Canonical value |
|---|---|
| Total phrase examples | 12,000 |
| Training split | 9,600 |
| Validation split | 1,200 |
| Test split | 1,200 |
| File organization | WAV/JSON/TXT triplets |
| Phrase WAV format | Mono PCM16 |
| Phrase sampling rate | 12 kHz |
| Number of classes | 5 |
| Class schema | KD, SD, T12, T14, T16 |
| Target class distribution | KD 35%, SD 35%, T12 10%, T14 10%, T16 10% |
| Median events per phrase | 11 |
| Events per phrase | 10–16 |
| JSON/TXT consistency after chronological sorting | 12,000/12,000 pairs |
| Source-sample traceability | Preserved through JSON metadata |

The phrase-level corpus was generated from measured isolated real-hit piezoelectric vibration responses rather than purely synthetic waveforms. Each event retains provenance information linking it to its measured source sample.

## Official baseline reported in the manuscript

The official baseline was selected using validation-set behavior and then applied unchanged to the independent test split.

| Parameter | Value |
|---|---:|
| Global decision threshold | 0.030 |
| NMS window | 110 ms |
| Onset-matching tolerance | 50 ms |

### Test-set results

| Metric | Value |
|---|---:|
| True positives | 8,657 |
| False positives | 6,901 |
| False negatives | 5,315 |
| Micro-precision | 0.5564 |
| Micro-recall | 0.6196 |
| Micro-F1 | 0.5863 |
| Macro-F1 | 0.5855 |

Class-wise F1 scores are KD 0.5953, SD 0.5733, T12 0.5814, T14 0.5425, and T16 0.6349.

## Data availability

The complete 12,000-example phrase-level dataset is **not yet archived in this repository**. A versioned public dataset archive containing the canonical WAV/JSON/TXT triplets will be created before manuscript submission, and its persistent identifier will be added here and to the manuscript.

This repository will contain the code and lightweight reproducibility resources corresponding to the archived dataset and reported results.

## Reproducibility policy

For the manuscript release, this repository will distinguish between:

- the immutable dataset archive used for the reported experiments;
- the exact code and configuration used for the official baseline;
- audit outputs documenting dataset integrity and annotation consistency; and
- subsequent exploratory or development work.

The submission release will be tagged so that the version cited by the manuscript remains recoverable even if development continues.

The complete canonical reproducibility chain, including the distinction between preserved historical evidence and reconstructed reproduction procedures, is documented in [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md).

## Relationship to the development repository

The original thesis-development repository documents the historical replication and adaptation of ADTOF and contains material created during the research process. This companion repository is a curated publication artifact and should be used when reproducing or citing the manuscript results.

## License

Original project code in this repository is released under the MIT License. Third-party material retains its own applicable license; see `THIRD_PARTY_NOTICES.md` and `third_party/adtof/README.md` for the ADTOF attribution and licensing information.

Dataset licensing will be specified separately in the archived dataset record.
