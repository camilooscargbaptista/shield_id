# Eval scenario — cross-generator (leave-one-generator-out)

GIVEN a dataset with generators {A, B, C}
WHEN the model is trained on {A, B} only
AND evaluated on held-out generator C (never seen in development)
THEN the report shows recall@fixed-FPR for C with a confidence interval
AND the robustness delta (in-distribution {A,B} → cross-generator C) is the headline number
AND the run is reproducible from config + seed.
