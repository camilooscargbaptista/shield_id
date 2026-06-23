# Threat Model — <component> (STRIDE)

**Owner:** security-auditor · **Mandatory if:** money/auth/PII/external integration touched.

| STRIDE | Threat | Likelihood | Impact | Mitigation | Status |
|--------|--------|-----------|--------|------------|--------|
| Spoofing | ... |  |  |  |  |
| Tampering | ... |  |  |  |  |
| Repudiation | ... |  |  |  |  |
| Info disclosure | raw biometric / PII leak |  | CRIT | derived vectors only, masking | |
| DoS | ... |  |  |  |  |
| Elevation | ... |  |  |  |  |

Pipeline threats (100%-agent-built): dependency supply-chain, secret handling, prompt-injection in data.
