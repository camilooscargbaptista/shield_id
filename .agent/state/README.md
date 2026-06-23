# .agent/state — Runtime state (schema v1)

- `current-experiment.json` — **git-ignored**, ephemeral active-experiment machine. Truth lives in
  PRs + CI + this log. Created by `scripts/agent/start_experiment.py`, mutated by `approve.py`.
- `approval-log.jsonl` — **checked-in**, append-only audit (events: experiment_started, step_approved,
  bypass_used). Never edit by hand; never delete lines.
- `no-hardcoded-exceptions.jsonl` — append-only whitelist of sanctioned rule-32 exceptions (3-artifact rule).
- `archived/` — final snapshots of completed experiments (full approval pedigree).

Query examples:
```bash
python scripts/agent/status.py
grep step_approved .agent/state/approval-log.jsonl | tail
```
