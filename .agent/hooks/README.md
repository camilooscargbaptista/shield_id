# .agent/hooks — INTENT only

These files describe the INTENT of each hook. **Real execution lives in `.claude/hooks/*.sh`
and `scripts/guards/*.py`** (SSOT). Editing the .md here changes nothing at runtime.

| Hook (intent) | Real impl | Effect |
|---------------|-----------|--------|
| guard-src-edits | `.claude/hooks/guard-src-edits.sh` + `scripts/guards/src_gate.py` | exit 2 — blocks src/ edits before gates approved (M3) |
| guard-bash-bypass | `.claude/hooks/guard-bash-bypass.sh` | exit 2 — blocks --no-verify + state tampering |
| no-raw-biometric | `scripts/guards/no_raw_biometric.py` (pre-commit) | exit 1 — blocks raw biometric persistence (I1) |
| no-real-pii | `scripts/guards/no_real_pii.py` (pre-commit) | exit 1 — blocks real PII in data (I2) |
| metric-honesty | `scripts/guards/metric_honesty.py` (pre-push) | exit 1 — blocks metric without cross-generator + repro (I3/I4) |
| index-drift | `scripts/guards/index_drift.py` (pre-push) | exit 1 — blocks INDEX drift |
| cost-router | `.claude/hooks/session-start-cost-routing.sh` | advisory model routing |
