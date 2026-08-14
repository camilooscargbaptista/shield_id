#!/usr/bin/env python3
"""Independent evaluation gate (M5/D4) — the REAL isolated `claude -p` reviewer.

PORT-2 of EPIC-FRAMEWORK-EVOLUTIONS. Python-pure, stdlib-only.

> There is exactly ONE independent-reviewer entrypoint in SHIELD-ID: THIS file.
> A parallel `eval_independent.py` would trip framework_selfcheck.py assertion C
> (the one-reviewer rule). Do NOT create a second reviewer — upgrade this one.

What it does (M5 / decision D4):
  1. Assemble a self-contained REVIEW PACKAGE (one prompt): the eval-independent card
     persona + the shield ML kill-list + a reinjected eval-validity playbook +
     pre-registered acceptance bar + the artifact under review (diff/experiment/report).
  2. Spawn an ISOLATED reviewer via `claude -p "<package>"` in a fresh session — zero
     builder context. That isolation is the whole point: the number becomes credible.
  3. The reviewer must emit ONLY a JSON object matching the eval-independent
     `verdict_schema`. We parse + TYPE-validate it, fail-CLOSED: a missing / unparseable /
     type-invalid / enum-invalid verdict is an ERROR verdict (exit != 0), NEVER silently
     defaulted to PASS. A reviewer that returns garbage = FAIL, not pass.
  4. Persist the validated verdict into current-experiment.json (state.set_verdict).
  5. Exit code gates the pipeline: 0 only on PASS / PASS_WITH_WARNINGS; non-zero on FAIL
     or any validation/spawn error.

Also reuses scripts/guards/metric_honesty.py for kill-list #4 (metric without
cross-generator + reproducible artifact): we run it against the artifact and hand its
result to the reviewer as an additional, deterministic signal.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib import state  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CARD = ROOT / ".agent" / "agents" / "eval-independent.md"
METRIC_HONESTY = ROOT / "scripts" / "guards" / "metric_honesty.py"

VALID_VERDICTS = {"PASS", "PASS_WITH_WARNINGS", "FAIL"}
GATING_VERDICTS = {"PASS", "PASS_WITH_WARNINGS"}  # exit 0 only for these

# ---------------------------------------------------------------------------
# The shield ML kill-list — baked verbatim into the review package.
# Each item names the ACTUAL defect an IEEE evaluator would flag (not a near-token).
# ---------------------------------------------------------------------------
ML_KILL_LIST = """\
SHIELD-ID ML KILL-LIST (any present => this is a FAIL, name it in fails[]):
  (1) CIRCULARITY — the held-out generator is trained on or its threshold is tuned on it.
      Concretely: the held-out/test generator id (e.g. "gpt4") appears in train_generators,
      or the decision threshold is fit using held-out-generator data. (I4 / rule 05 / D8)
  (2) TRAIN/TEST LEAKAGE — the same samples/identities appear in both train and test splits.
  (3) THRESHOLD TUNED ON THE TEST SET — the operating threshold is selected by looking at
      test-set/held-out metrics rather than a config/validation split.
  (4) METRIC WITHOUT CROSS-GENERATOR + REPRODUCIBLE ARTIFACT — a headline % with no
      cross-generator evaluation, or no notebook+seed to reproduce it. (I3/I4, D5/D8)
      A deterministic metric_honesty.py check is attached below as a signal for this item.
  (5) RAW-BIOMETRIC PERSISTENCE — a schema/field persists raw face/voice/biometric bytes
      instead of a derived feature vector. (I1 / rule 04)
  (6) REAL PII — any real personal data (CPF/CNPJ/real email/name) in a dataset. Must be
      synthetic-only. (I2 / rule 03)
  (7) METRIC AS PROMISE NOT TARGET — a number stated as a guarantee ("we achieve 95%")
      rather than a measured outcome with methodology, or a target reported as if measured.
      (I5 / D5)"""

# ---------------------------------------------------------------------------
# Eval-validity playbook — hard-won lessons, reinjected on every run.
# ---------------------------------------------------------------------------
PLAYBOOK = """\
EVAL-VALIDITY PLAYBOOK (reinjected — read before you decide):
  - You are a NEUTRAL ADJUDICATOR that CAN and MUST return PASS on a clean case. You are NOT
    a purely adversarial reviewer: a pure adversary saturates (kills everything) and can no
    longer discriminate a clean artifact from a defective one. Keep the falsify-the-headline
    stance, but PASS is a REAL, REACHABLE verdict when the artifact is genuinely clean.
  - Anchor every kill on the ACTUAL defect, quoting the offending token. Say
    "held-out generator 'gpt4' appears in train_generators", not a vague "possible leakage".
  - The acceptance BAR is PRE-REGISTERED below and is FIXED before you saw the artifact.
    Do not invent new criteria post-hoc; judge the artifact against the pre-registered bar.
  - FALSE-ALARM SANITY CHECK: do NOT raise a kill on a clean artifact. If the held-out
    generator is genuinely absent from training, the metric is cross-generator, reproducible
    (notebook+seed), and the threshold comes from config — that is a PASS (or
    PASS_WITH_WARNINGS if the honest cross-generator number is merely lower than hoped).
  - Verdict truth table: cross-generator absent => FAIL (I4). Not reproducible => FAIL (I3).
    Circularity / held-out-in-train => FAIL (I4). Clean + honest => PASS/PASS_WITH_WARNINGS."""

# ---------------------------------------------------------------------------
# Pre-registered acceptance bar — fixed BEFORE the reviewer runs.
# ---------------------------------------------------------------------------
PREREGISTERED_BAR = """\
PRE-REGISTERED ACCEPTANCE BAR (fixed before this review; judge against exactly this):
  PASS requires ALL of:
    - cross_generator == true  (held-out generator C never seen in training)
    - reproducible   == true   (notebook + seed present)
    - no kill-list item (1)-(7) present
    - raw_biometric_detected == false
  PASS_WITH_WARNINGS: as PASS, but the honest cross-generator metric is lower than the
    aspirational target (an honest, reproducible, cross-generator number that merely
    missed target is NOT a FAIL — it is the correct, reportable outcome; I5).
  FAIL: any kill-list item present, OR cross_generator false, OR reproducible false, OR a
    raw biometric persisted, OR a metric stated as a promise not a target."""

OUTPUT_CONTRACT = """\
OUTPUT CONTRACT (STRICT — output ONLY this, nothing else):
Return a SINGLE JSON object and NOTHING else (no prose, no markdown fences). Schema:
{
  "verdict": "PASS" | "PASS_WITH_WARNINGS" | "FAIL",
  "metrics": { "recall_at_fixed_fpr": <float>, "ci": [<float>, <float>], "robustness_delta_pp": <float> },
  "cross_generator": <bool>,
  "reproducible": <bool>,
  "parity_gap_significant": <bool>,
  "raw_biometric_detected": <bool>,
  "fails": [ <string>, ... ]
}
If the artifact reports no numeric metric, use 0.0 / [0.0, 0.0] placeholders for the metrics
block but set the boolean flags and fails[] honestly. fails[] MUST name the ACTUAL defect
(quoting the offending token) for every kill you raise, and MUST be empty on a clean PASS."""


def run_metric_honesty(artifact: Path):
    """Kill-list #4 leg: reuse the metric_honesty guard deterministically as a signal."""
    argv = [sys.executable, str(METRIC_HONESTY), "--require-cross-generator", str(artifact)]
    try:
        r = subprocess.run(argv, capture_output=True, text=True, cwd=str(ROOT), timeout=60)
    except Exception as e:  # noqa: BLE001
        return {"ran": False, "error": str(e), "exit": None, "output": ""}
    return {"ran": True, "exit": r.returncode, "output": (r.stdout + r.stderr).strip()}


def build_package(artifact: Path, artifact_text: str, mh: dict) -> str:
    """Assemble the single review-package prompt fed to the isolated reviewer."""
    persona = CARD.read_text(errors="ignore") if CARD.is_file() else "(eval-independent card missing)"
    mh_block = (
        f"metric_honesty.py --require-cross-generator (kill-list #4 signal): "
        f"exit={mh.get('exit')}  ran={mh.get('ran')}\n{mh.get('output', '')}"
    )
    return f"""You are the SHIELD-ID INDEPENDENT EVALUATOR (M5 / decision D4), running in an
ISOLATED session with ZERO context from whoever built this artifact. You never saw the code
being written. Your job: falsify the headline, but adjudicate NEUTRALLY — PASS is reachable.

=== YOUR PERSONA CARD (eval-independent) ===
{persona}

=== {ML_KILL_LIST}

=== {PLAYBOOK}

=== {PREREGISTERED_BAR}

=== DETERMINISTIC SIGNAL (already computed for you) ===
{mh_block}

=== ARTIFACT UNDER REVIEW: {artifact.name} ===
{artifact_text}
=== END ARTIFACT ===

{OUTPUT_CONTRACT}
"""


def extract_json(raw: str):
    """Pull the first balanced top-level JSON object out of the reviewer's stdout.
    Returns a dict, or None if no parseable object is found (fail-closed upstream)."""
    if not raw:
        return None
    # strip common markdown fences the model may add despite instructions
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.S)
    candidates = []
    if fenced:
        candidates.append(fenced.group(1))
    # also scan for the first balanced { ... } block
    start = raw.find("{")
    while start != -1:
        depth = 0
        for i in range(start, len(raw)):
            c = raw[i]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    candidates.append(raw[start:i + 1])
                    break
        start = raw.find("{", start + 1)
        if len(candidates) > 6:
            break
    for cand in candidates:
        try:
            obj = json.loads(cand)
            if isinstance(obj, dict):
                return obj
        except Exception:
            continue
    return None


def validate_verdict(obj):
    """TYPE + ENUM validation against the eval-independent verdict_schema. Fail-CLOSED.
    Returns (ok: bool, errors: [str])."""
    errors = []
    if not isinstance(obj, dict):
        return False, ["verdict is not a JSON object"]

    v = obj.get("verdict")
    if v not in VALID_VERDICTS:
        errors.append(f"verdict '{v}' not in enum {sorted(VALID_VERDICTS)}")

    m = obj.get("metrics")
    if not isinstance(m, dict):
        errors.append("metrics is not an object")
    else:
        if not isinstance(m.get("recall_at_fixed_fpr"), (int, float)) or isinstance(
            m.get("recall_at_fixed_fpr"), bool
        ):
            errors.append("metrics.recall_at_fixed_fpr not a float")
        ci = m.get("ci")
        if (
            not isinstance(ci, list)
            or len(ci) != 2
            or not all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in ci)
        ):
            errors.append("metrics.ci not a [float, float]")
        if not isinstance(m.get("robustness_delta_pp"), (int, float)) or isinstance(
            m.get("robustness_delta_pp"), bool
        ):
            errors.append("metrics.robustness_delta_pp not a float")

    for b in ("cross_generator", "reproducible", "parity_gap_significant", "raw_biometric_detected"):
        if not isinstance(obj.get(b), bool):
            errors.append(f"{b} not a bool")

    fails = obj.get("fails")
    if not isinstance(fails, list) or not all(isinstance(x, str) for x in fails):
        errors.append("fails not a list[str]")

    return (len(errors) == 0), errors


def error_verdict(reason: str, detail: str = "") -> dict:
    """A fail-closed ERROR verdict — a reviewer that returns garbage = FAIL, not pass."""
    return {
        "verdict": "FAIL",
        "error": "REVIEWER_ERROR",
        "reason": reason,
        "detail": detail[:2000],
        "metrics": {"recall_at_fixed_fpr": 0.0, "ci": [0.0, 0.0], "robustness_delta_pp": 0.0},
        "cross_generator": False,
        "reproducible": False,
        "parity_gap_significant": False,
        "raw_biometric_detected": False,
        "fails": [f"reviewer error ({reason}): {detail[:180]}"],
    }


def spawn_reviewer(package: str, timeout: int):
    """Spawn the ISOLATED `claude -p` reviewer. Returns (stdout, err_or_None)."""
    argv = ["claude", "-p", package]
    try:
        r = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        return None, "claude CLI not found on PATH"
    except subprocess.TimeoutExpired:
        return None, f"claude -p timed out after {timeout}s"
    except Exception as e:  # noqa: BLE001
        return None, f"claude -p spawn failed: {e}"
    if r.returncode != 0:
        return r.stdout, f"claude -p exited {r.returncode}: {(r.stderr or '').strip()[:300]}"
    return r.stdout, None


def main():
    ap = argparse.ArgumentParser(description="Isolated M5/D4 independent-reviewer gate.")
    ap.add_argument("artifact", help="diff / experiment / eval-report under review")
    ap.add_argument("--step", default="eval", help="verdict-gated step to record under (default: eval)")
    ap.add_argument("--timeout", type=int, default=300, help="claude -p timeout seconds")
    ap.add_argument("--print-package", action="store_true", help="print the review package and exit")
    a = ap.parse_args()

    artifact = Path(a.artifact)
    if not artifact.exists():
        verdict = error_verdict("artifact_not_found", str(artifact))
        try:
            state.set_verdict(a.step, verdict)
        except Exception:
            pass
        print(json.dumps(verdict, indent=2))
        raise SystemExit(1)

    artifact_text = artifact.read_text(errors="ignore")
    mh = run_metric_honesty(artifact)
    package = build_package(artifact, artifact_text, mh)

    if a.print_package:
        print(package)
        raise SystemExit(0)

    stdout, spawn_err = spawn_reviewer(package, a.timeout)
    if spawn_err and stdout is None:
        verdict = error_verdict("spawn_failed", spawn_err)
        _persist_and_exit(a.step, verdict)

    obj = extract_json(stdout or "")
    if obj is None:
        verdict = error_verdict("unparseable_output", (stdout or "")[:2000])
        _persist_and_exit(a.step, verdict)

    ok, errs = validate_verdict(obj)
    if not ok:
        verdict = error_verdict("schema_invalid", "; ".join(errs))
        _persist_and_exit(a.step, verdict)

    # valid typed verdict from the reviewer
    _persist_and_exit(a.step, obj)


def _persist_and_exit(step: str, verdict: dict):
    try:
        state.set_verdict(step, verdict)
    except Exception as e:  # noqa: BLE001 — persistence failure must not fake a pass
        print(f"WARNING: failed to persist verdict to current-experiment.json: {e}", file=sys.stderr)
    print(json.dumps(verdict, indent=2))
    gated = verdict.get("verdict") in GATING_VERDICTS
    raise SystemExit(0 if gated else 1)


if __name__ == "__main__":
    main()
