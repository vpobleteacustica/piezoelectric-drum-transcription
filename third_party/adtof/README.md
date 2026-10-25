# ADTOF adaptation used in the vibration-transcription pipeline

This directory records the minimal adaptation of the upstream ADTOF codebase
used for the canonical vibration-based drum-transcription experiments reported
with this repository.

## Upstream project

Repository:

    https://github.com/MZehren/ADTOF

Canonical upstream commit used as the patch base:

    b3968fb332f69b65ee07c089fc62f436503755db

The upstream ADTOF repository is distributed under the Creative Commons
Attribution-NonCommercial-ShareAlike 4.0 International license
(CC BY-NC-SA 4.0). A byte-for-byte copy of the upstream LICENSE file is
preserved in:

    third_party/adtof/LICENSE

The root MIT license of this companion repository does not apply to the
upstream ADTOF material or to the ADTOF adaptation recorded here.

## Adaptation strategy

The historical thesis workspace contained a complete `adtof/` source tree.
A comparison against upstream commit
`b3968fb332f69b65ee07c089fc62f436503755db` showed:

    34 Python files in the upstream tree
    34 Python files in the thesis tree
    30 files byte-identical to upstream
     4 files modified relative to upstream
     0 files unique to either tree

Rather than redistributing the complete upstream source tree, this repository
preserves only the patch required to reconstruct the exact ADTOF variant used
in the canonical experiment:

    third_party/adtof/patches/vibro5.patch

The patch modifies exactly these files:

    adtof/config.py
    adtof/io/mir.py
    adtof/model/dataLoader.py
    adtof/ressources/instrumentsMapping.py

The modifications introduce three kinds of changes:

1. A five-class vibration/piezo vocabulary (`vibro_5_toms`):
   KD, SD, T12, T14 and T16 with MIDI labels 35, 38, 47, 45 and 43.

2. Support for the pre-split custom vibration dataset:
   TRAIN, VAL and TEST directories containing paired WAV/TXT files.

3. Compatibility shims required by the historical execution environment for
   newer Python/NumPy versions and the legacy madmom dependency.

No changes were made to the upstream model architecture implementation in
`adtof/model/model.py` or to `adtof/model/hyperparameters.py`; those files were
verified byte-identical to the pinned upstream version.

## Patch identity

SHA-256:

    83dd421d96f22871664599756357a9f6cbed2b909899dd6e37fc446b6a61deef
    third_party/adtof/patches/vibro5.patch

Upstream LICENSE SHA-256:

    1349a4b6148492b44f629e64eed676612e234fe9a839e4f3b277c1482c8849f1
    third_party/adtof/LICENSE

## Reconstruction

Starting from the pinned ADTOF upstream commit:

    git clone https://github.com/MZehren/ADTOF.git
    cd ADTOF
    git checkout b3968fb332f69b65ee07c089fc62f436503755db
    git apply /path/to/piezoelectric-drum-transcription/third_party/adtof/patches/vibro5.patch

The resulting 34 Python files were verified byte-for-byte against the ADTOF
tree used in the canonical thesis experiment.

## Licensing note

ADTOF and the adaptation represented by this patch must not be interpreted as
being relicensed under the MIT license of the surrounding companion
repository. Consult `third_party/adtof/LICENSE` for the applicable upstream
license terms.
