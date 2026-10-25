# Canonical pipeline source provenance

This directory preserves the finalized source snapshot associated with the
canonical vibration-transcription pipeline.

## Preserved source snapshot

The files in this directory were copied byte-for-byte from the finalized
`official/v0.1-vibro5-pipeline` workspace corresponding to Git commit:

    327b972d273961df455d591321d383ce5d19bacd

The preserved training, calibration, analysis, and runtime-environment files
are intended to retain the finalized implementation and provide a stable basis
for reproducibility.

## Canonical training-run timing

The canonical run

    serious_5class_low_60ep_weighted_t14t16

records:

    execution_datetime = 2026-06-28T21:10:05.326114-04:00

The nearest committed repository states bracketing that execution are:

    60b0960106046310eac5ca73920bb77372478a22
    2026-06-21 20:42:21 -0400

and:

    df7d06bd1ba53a2c68d55e996ed39f72ca653ed9
    2026-07-21 00:04:17 -0400

The training launcher changed between those repository states.

The earlier committed launcher did not yet contain the complete combination of
class weighting and VAL-based calibration represented in the canonical run
artifacts. The later finalized launcher contains additional loss-selection
fields (`loss_type`, `focal_gamma`, and `focal_alpha`) that are absent from the
canonical run `config.json`.

The exact intermediate working-tree revision that launched the canonical run
was therefore not preserved as a Git commit.

A local forensic check with:

    git fsck --full --unreachable --no-reflogs

reported zero unreachable blobs, so no intermediate launcher blob could be
recovered from the local Git object database.

## ADTOF stability across the run interval

The complete tracked `adtof/` tree contains 37 files.

All 37 files have identical Git blob identities at both commits bracketing the
canonical run:

    60b0960106046310eac5ca73920bb77372478a22
    df7d06bd1ba53a2c68d55e996ed39f72ca653ed9

Thus, the ADTOF adaptation was stable across the canonical run interval. The
unresolved historical revision is the project-specific training launcher, not
the ADTOF adaptation.

## Interpretation

The files preserved here are a finalized canonical source snapshot. They must
not be described as a proven byte-for-byte copy of the exact training launcher
present in the working tree on 2026-06-28.

The canonical run artifacts remain authoritative for the run parameters,
checkpoint identity, training history, VAL-only postprocessing selection, and
TEST results.

Any publication-facing training command reconstructed from these materials
must be labeled explicitly as a reconstructed reproduction command rather than
as the original historical command.
