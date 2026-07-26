#!/usr/bin/env python3
"""Generic single-role ISOLATED runner (PORT-3 of EPIC-FRAMEWORK-EVOLUTIONS).

Python-pure, stdlib-only. This GENERALIZES PORT-2's reviewer (`verify_eval.py`, the M5
independent-reviewer) into a reusable PRIMITIVE: PORT-2 is one *specialization* of this
pattern (role = eval-independent, schema = verdict_schema). This file is NOT a reviewer
entrypoint — it is the isolation + typed-fail-closed-validation mechanism that a reviewer
(or any other single-role task) can be built on top of.

>>> NOTE FOR framework_selfcheck.py assertion C (single-reviewer rule):
>>> This is a GENERIC-RUNNER-PRIMITIVE, NOT an independent-reviewer entrypoint. It carries
>>> NO reviewer marker (see scripts/guards/framework_selfcheck.py). A real second reviewer
>>> (e.g. eval_independent.py) is still caught; this primitive is not.

What it does, given (a) a role prompt/persona, (b) an input artifact, (c) a typed output
JSON Schema:

  1. Spawns the role ISOLATED: `claude -p --output-format json "<prompt>"` in a fresh
     session (zero caller context). subprocess + timeout.
  2. Extracts the model's answer AND the REAL run metadata from the CLI's JSON envelope:
     `total_cost_usd` (cost) and `duration_ms` (duration). These are the ACTUAL values the
     CLI returns — never fabricated (M1). A sample envelope is documented in the epic proof.
  3. Validates the answer vs the provided JSON Schema — TYPE + ENUM, fail-CLOSED. Any
     invalid / missing / unparseable / timeout / spawn failure lands in a DISTINCT error
     slot (`status: "invalid_output"` or `"spawn_error"`), NEVER conflated with a valid
     result and NEVER defaulted to success. This is the primitive's core guarantee.
  4. Writes a FLAT artifact (the validated result, or the error slot) to `--out`, AND
     appends one line to `.agent/state/trace.jsonl` (append-only, alongside
     approval-log.jsonl) with: timestamp, role, input ref, status, cost_usd, duration_ms,
     schema id, and the output (or error).

Library + CLI:
    agent_run.py --role <file|inline> --input <file> --schema <file> [--out <path>]
    from agent_run import run; run(role, input_text, schema) -> dict

The supported JSON Schema subset (stdlib validator, no third-party deps): a top-level
object schema with "type": "object", "properties": {<name>: {<field-schema>}},
optional "required": [...], optional "additionalProperties": bool. Field schemas support
"type" in {string, number, integer, boolean, array, object} and "enum": [...]. This is the
subset the SHIELD-ID typed-output contracts use; unknown keywords are ignored (they cannot
turn an invalid output into a pass — validation stays fail-closed).
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRACE = ROOT / ".agent" / "state" / "trace.jsonl"

STATUS_OK = "ok"
STATUS_INVALID = "invalid_output"   # spawned fine, but output failed schema/parse
STATUS_SPAWN_ERROR = "spawn_error"  # could not even get a usable model answer

_JSON_TYPE_CHECKS = {
    "string": lambda v: isinstance(v, str),
    "boolean": lambda v: isinstance(v, bool),
    # bool is a subclass of int in Python — exclude it from number/integer.
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "array": lambda v: isinstance(v, list),
    "object": lambda v: isinstance(v, dict),
}


def now() -> str:
    import datetime
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# JSON Schema validation — TYPE + ENUM, fail-CLOSED. stdlib only.
# ---------------------------------------------------------------------------
def _validate_field(name: str, spec: dict, value, errors: list):
    t = spec.get("type")
    if t is not None:
        check = _JSON_TYPE_CHECKS.get(t)
        if check is None:
            # unknown declared type => cannot prove valid => fail closed
            errors.append(f"{name}: unknown schema type '{t}' (fail-closed)")
            return
        if not check(value):
            errors.append(f"{name}: expected type '{t}', got {type(value).__name__}")
            return  # type wrong: don't also enum-check garbage
    enum = spec.get("enum")
    if enum is not None:
        if not isinstance(enum, list):
            errors.append(f"{name}: schema enum is not a list (fail-closed)")
        elif value not in enum:
            errors.append(f"{name}: value {value!r} not in enum {enum}")


def validate_output(obj, schema: dict):
    """TYPE + ENUM validation of `obj` against `schema`. Fail-CLOSED.
    Returns (ok: bool, errors: list[str])."""
    errors: list = []
    if not isinstance(schema, dict):
        return False, ["schema is not a JSON object"]
    if schema.get("type", "object") != "object":
        return False, [f"top-level schema type must be 'object', got {schema.get('type')!r}"]
    if not isinstance(obj, dict):
        return False, ["output is not a JSON object"]

    props = schema.get("properties") or {}
    required = schema.get("required") or []
    if not isinstance(required, list):
        required = []

    for key in required:
        if key not in obj:
            errors.append(f"missing required property: {key}")

    for key, spec in props.items():
        if key in obj:
            if not isinstance(spec, dict):
                errors.append(f"{key}: property schema is not an object (fail-closed)")
                continue
            _validate_field(key, spec, obj[key], errors)

    if schema.get("additionalProperties") is False:
        extra = [k for k in obj if k not in props]
        if extra:
            errors.append(f"additional properties not allowed: {sorted(extra)}")

    return (len(errors) == 0), errors


# ---------------------------------------------------------------------------
# Envelope + answer extraction from `claude -p --output-format json`.
# Sample envelope (real, captured 2026-06):
#   {"type":"result","subtype":"success","is_error":false,"duration_ms":2065,
#    "result":"PING","session_id":"...","total_cost_usd":0.0978..., "usage":{...}}
# We read cost from total_cost_usd (fallback cost_usd), duration from duration_ms, and the
# model's answer from `result`. These are the ACTUAL CLI values (M1: never fabricated).
# ---------------------------------------------------------------------------
def parse_envelope(stdout: str):
    """Parse the CLI JSON envelope. Returns (answer_text, cost_usd, duration_ms, env_err).
    env_err is None on a well-formed successful envelope, else a string reason."""
    if not stdout or not stdout.strip():
        return None, None, None, "empty CLI stdout"
    try:
        env = json.loads(stdout)
    except Exception as e:  # noqa: BLE001
        return None, None, None, f"CLI envelope not JSON: {e}"
    if not isinstance(env, dict):
        return None, None, None, "CLI envelope is not a JSON object"

    cost = env.get("total_cost_usd", env.get("cost_usd"))
    duration = env.get("duration_ms")
    if env.get("is_error") is True or env.get("subtype") not in (None, "success"):
        return env.get("result"), cost, duration, f"CLI reported error envelope: subtype={env.get('subtype')} is_error={env.get('is_error')}"
    answer = env.get("result")
    if not isinstance(answer, str):
        return None, cost, duration, "CLI envelope has no string `result` field"
    return answer, cost, duration, None


def extract_json(raw: str):
    """Pull the first balanced top-level JSON object out of the model's answer text.
    Returns a dict, or None if none is parseable (fail-closed upstream). Same shape as
    verify_eval.py's extractor — models sometimes wrap JSON in prose / markdown fences."""
    if not raw:
        return None
    candidates = []
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.S)
    if fenced:
        candidates.append(fenced.group(1))
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


# ---------------------------------------------------------------------------
# Isolated spawn.
# ---------------------------------------------------------------------------
def spawn(prompt: str, timeout: int):
    """Spawn the ISOLATED `claude -p --output-format json` role. Fresh session, zero
    caller context. Returns (stdout, err_or_None)."""
    argv = ["claude", "-p", "--output-format", "json", prompt]
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


# ---------------------------------------------------------------------------
# The primitive.
# ---------------------------------------------------------------------------
def build_prompt(role: str, input_text: str, schema: dict) -> str:
    """Assemble the single isolated-role prompt: persona + input + strict typed contract."""
    schema_json = json.dumps(schema, indent=2)
    schema_id = schema.get("$id") or schema.get("id") or schema.get("title") or "output-schema"
    return f"""You are running in an ISOLATED session with ZERO context from whoever invoked
you. Perform ONLY the role below against the input, then emit ONLY the typed JSON result.

=== ROLE ===
{role}

=== INPUT ARTIFACT ===
{input_text}
=== END INPUT ===

=== OUTPUT CONTRACT (STRICT) ===
Return a SINGLE JSON object and NOTHING else — no prose, no markdown fences. It MUST validate
against this JSON Schema (schema id: {schema_id}):
{schema_json}
"""


def run(role: str, input_text: str, schema: dict, timeout: int = 300) -> dict:
    """Core library entrypoint. Spawn the role isolated, parse the real envelope, validate
    the answer vs `schema` (TYPE+ENUM, fail-closed), and return a flat result dict:

        {"status": ok|invalid_output|spawn_error,
         "role_ref": ..., "schema_id": ..., "cost_usd": <float|None>,
         "duration_ms": <int|None>, "ts": ...,
         + on ok:            "output": <validated dict>
         + on error:         "error": <reason>, "detail": <str>, and (if any) "raw_answer"}

    The status slots are DISTINCT and never conflated: a valid result is ONLY "ok".
    """
    schema_id = schema.get("$id") or schema.get("id") or schema.get("title") or "output-schema"
    base = {"ts": now(), "schema_id": schema_id, "cost_usd": None, "duration_ms": None}

    prompt = build_prompt(role, input_text, schema)
    stdout, spawn_err = spawn(prompt, timeout)

    if stdout is None:
        return {**base, "status": STATUS_SPAWN_ERROR, "error": "spawn_failed",
                "detail": spawn_err or "no stdout from CLI"}

    answer, cost, duration, env_err = parse_envelope(stdout)
    base["cost_usd"] = cost
    base["duration_ms"] = duration
    if env_err is not None and answer is None:
        return {**base, "status": STATUS_SPAWN_ERROR, "error": "bad_envelope",
                "detail": env_err}

    obj = extract_json(answer or "")
    if obj is None:
        return {**base, "status": STATUS_INVALID, "error": "unparseable_output",
                "detail": "no parseable JSON object in model answer",
                "raw_answer": (answer or "")[:2000]}

    ok, errs = validate_output(obj, schema)
    if not ok:
        return {**base, "status": STATUS_INVALID, "error": "schema_invalid",
                "detail": "; ".join(errs), "raw_answer": (answer or "")[:2000]}

    return {**base, "status": STATUS_OK, "output": obj}


def append_trace(result: dict, role_ref: str, input_ref: str):
    """Append ONE line to .agent/state/trace.jsonl (append-only audit)."""
    TRACE.parent.mkdir(parents=True, exist_ok=True)
    line = {
        "ts": result.get("ts") or now(),
        "role": role_ref,
        "input": input_ref,
        "status": result.get("status"),
        "cost_usd": result.get("cost_usd"),
        "duration_ms": result.get("duration_ms"),
        "schema_id": result.get("schema_id"),
    }
    if result.get("status") == STATUS_OK:
        line["output"] = result.get("output")
    else:
        line["error"] = result.get("error")
        line["detail"] = result.get("detail")
    with TRACE.open("a") as f:
        f.write(json.dumps(line) + "\n")
    return line


def _load_role(spec: str) -> tuple:
    """--role accepts a file path or an inline string. Returns (text, ref)."""
    p = Path(spec)
    if p.is_file():
        return p.read_text(errors="ignore"), str(p)
    return spec, "inline"


def main():
    ap = argparse.ArgumentParser(description="Generic single-role isolated runner (PORT-3).")
    ap.add_argument("--role", required=True, help="role persona: a file path OR an inline string")
    ap.add_argument("--input", required=True, help="input artifact file")
    ap.add_argument("--schema", required=True, help="typed output JSON Schema file")
    ap.add_argument("--out", default=None, help="flat-artifact output path (default: stdout only)")
    ap.add_argument("--timeout", type=int, default=300, help="claude -p timeout seconds")
    ap.add_argument("--no-trace", action="store_true", help="do not append to trace.jsonl")
    a = ap.parse_args()

    role_text, role_ref = _load_role(a.role)

    input_path = Path(a.input)
    if not input_path.is_file():
        print(f"ERROR: --input file not found: {input_path}", file=sys.stderr)
        raise SystemExit(2)
    input_text = input_path.read_text(errors="ignore")

    schema_path = Path(a.schema)
    if not schema_path.is_file():
        print(f"ERROR: --schema file not found: {schema_path}", file=sys.stderr)
        raise SystemExit(2)
    try:
        schema = json.loads(schema_path.read_text())
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: --schema is not valid JSON: {e}", file=sys.stderr)
        raise SystemExit(2)

    result = run(role_text, input_text, schema, timeout=a.timeout)

    if a.out:
        out_path = Path(a.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(result, indent=2) + "\n")

    if not a.no_trace:
        append_trace(result, role_ref, str(input_path))

    print(json.dumps(result, indent=2))
    # exit 0 only on a valid, ok result; distinct error slots => non-zero (fail-closed).
    raise SystemExit(0 if result.get("status") == STATUS_OK else 1)


if __name__ == "__main__":
    main()
