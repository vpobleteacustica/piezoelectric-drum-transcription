# Generated dataset audit summary

Dataset root: `/Users/vpoblete/Documents/20230208_vpoblete/20260703_rodrigo_drum_vibration_dataset/data/DATASET_VIBRATIONS/_incoming_20260816/DATASET_NUEVO`

## Split summary

| split   |   n_wav |   n_json |   n_txt | audio_dir_exists   | labels_dir_exists   | annotations_dir_exists   |
|:--------|--------:|---------:|--------:|:-------------------|:--------------------|:-------------------------|
| TRAIN   |    9600 |     9600 |    9600 | True               | True                | True                     |
| VAL     |    1200 |     1200 |    1200 | True               | True                | True                     |
| TEST    |    1200 |     1200 |    1200 | True               | True                | True                     |

## Pairing summary

- Complete WAV/JSON/TXT triplets: 12000
- Incomplete triplets: 0

## Audio technical summary

- Sample rates observed: [12000]
- Channels observed: [1]
- WAV subtypes observed: ['PCM_16']

### Duration by split

| split   |   count |    mean |      std |     min |     25% |     50% |     75% |     max |
|:--------|--------:|--------:|---------:|--------:|--------:|--------:|--------:|--------:|
| TEST    |    1200 | 3.9146  | 0.326491 | 3.02183 | 3.69473 | 3.91508 | 4.13856 | 4.88983 |
| TRAIN   |    9600 | 3.92488 | 0.337513 | 2.94583 | 3.69285 | 3.93425 | 4.15979 | 4.96842 |
| VAL     |    1200 | 3.9407  | 0.332236 | 2.94133 | 3.72204 | 3.93467 | 4.17317 | 4.96792 |

## Event counts from LABELS JSON

| split   | instrument   |   midi |   event_count |   percentage |
|:--------|:-------------|-------:|--------------:|-------------:|
| TEST    | KD           |     35 |          4891 |     35.0057  |
| TEST    | SD           |     38 |          4890 |     34.9986  |
| TEST    | T16          |     43 |          1397 |      9.99857 |
| TEST    | T14          |     45 |          1397 |      9.99857 |
| TEST    | T12          |     47 |          1397 |      9.99857 |
| TRAIN   | KD           |     35 |         39008 |     35.0004  |
| TRAIN   | SD           |     38 |         39007 |     34.9996  |
| TRAIN   | T16          |     43 |         11145 |     10       |
| TRAIN   | T14          |     45 |         11145 |     10       |
| TRAIN   | T12          |     47 |         11145 |     10       |
| VAL     | KD           |     35 |          4870 |     34.9957  |
| VAL     | SD           |     38 |          4870 |     34.9957  |
| VAL     | T16          |     43 |          1392 |     10.0029  |
| VAL     | T14          |     45 |          1392 |     10.0029  |
| VAL     | T12          |     47 |          1392 |     10.0029  |

## LABELS JSON vs ANNOTATIONS TXT consistency

- Files with exact same timestamp/MIDI sequence in original order: 1857 / 12000
- Files with exact same timestamp/MIDI sequence after chronological sorting: 12000 / 12000
- Files with matching MIDI sequence and timestamps within 1 ms after chronological sorting: 12000 / 12000

## Temporal structure and overlap summary

| split   |   n_phrases |   events_mean |   events_median |   events_min |   events_max |   min_ioi_median_s |   exact_simultaneous_pairs_mean |   close_pairs_le_50ms_mean |   close_pairs_le_50ms_median |   close_pairs_le_50ms_max |
|:--------|------------:|--------------:|----------------:|-------------:|-------------:|-------------------:|--------------------------------:|---------------------------:|-----------------------------:|--------------------------:|
| TEST    |        1200 |       11.6433 |              11 |           10 |           16 |             0.0003 |                          0.1517 |                     3.2625 |                            3 |                         9 |
| TRAIN   |        9600 |       11.6094 |              11 |           10 |           16 |             0.0003 |                          0.1745 |                     3.2774 |                            3 |                         9 |
| VAL     |        1200 |       11.5967 |              11 |           10 |           16 |             0.0002 |                          0.1808 |                     3.2458 |                            3 |                         8 |

## Source sample usage

- Unique source WAV references: 19733
- See `generated_source_sample_usage.csv` for details.
