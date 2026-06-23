# Model Card — <model> v<x>

## Overview
layer: <1|2> · modality: <document|voice|face> · base model: <fine-tuned from, rule 05> · NOT from scratch.

## Intended use / out-of-scope
financial KYC onboarding detection · NOT mass surveillance.

## Training data
dataset: <datasheet ref> · derived feature vectors only (Layer 2 — no raw biometrics, I1).

## Evaluation (filled by eval-independent ONLY — M5)
cross-generator result · robustness delta · disaggregated FPR · curves (ROC/PR) · reproducible notebook.

## Limitations & risks
generator arms race · demographic exposure · honest sequencing.

## Privacy
no raw-biometric persistence · non-retention test path.
