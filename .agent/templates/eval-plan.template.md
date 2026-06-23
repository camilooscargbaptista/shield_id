# Eval Plan — <experiment/model>

**Owner:** eval-independent (designs the plan; builder does NOT) · **Maps to:** rules 05,06,07,11

## System type & failure modes
type: <detector|gnn|pipeline> · failure modes: [ ... ]

## Datasets & splits
attack set (synthetic) · control set (legit synthetic) · stress tier · **held-out generator(s): <C>**
splits-manifest: train generators {A,B} / test generator C (never seen in dev).

## Metrics (curves, not points)
- P/R @ fixed FPR (ROC/PR + CI) · **robustness delta** (in-dist→cross-gen; standard→stress) [HEADLINE]
- disaggregated FPR per segment (fairness-auditor) · calibration · latency p50/p95/p99 (measure only)

## Measurement type
Code | LLM-Judge | Human — per metric.

## Protocol
seeds · model versions · thresholds (config) · reproducible notebook path. Published in full.

## Pass criteria
cross-generator present · reproducible artifact attached · no significant parity gap · no raw-biometric.
