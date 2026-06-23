# Cross-generator protocol (reference)
1. Freeze splits-manifest: train {A,B}, held-out C, seed. 2. Train/load fine-tuned model on {A,B} only.
3. Evaluate on C (never seen). 4. Compute P/R@fixed-FPR (config), bootstrap CI, ROC/PR. 5. Robustness delta
= in-dist({A,B}) − cross-gen(C). 6. Stress tier delta = standard − stress. 7. Headline = the deltas + the
cross-gen curve, never the in-dist point. FAIL the report if cross-gen is absent (rule 05/I4).
