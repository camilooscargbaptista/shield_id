# Parity significance (reference)
Per segment: compute FPR + Wilson CI. Test each segment's FPR vs the rest (two-proportion z-test or
bootstrap); report the p-value and the max gap (pp). A gap is "significant" at the pre-registered alpha
(config). Verdict BLOCK if any significant gap (rule 06). Always report the full per-segment table — the
global average is secondary and can hide an 80× per-segment gap.
