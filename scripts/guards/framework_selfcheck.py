#!/usr/bin/env python3
"""Framework self-check — a fail-CLOSED meta-guard for the SHIELD-ID `.agent/` framework.

PORT-1 of EPIC-FRAMEWORK-EVOLUTIONS. Python-pure, stdlib-only (matches the other guards).

It audits STRUCTURAL coherence of the agent framework itself — the layer the per-invariant
guards (no_raw_biometric, no_real_pii, metric_honesty, ...) do not cover:

  A. Invariant->guard wiring : each hard invariant I1..I5 maps to a guard that EXISTS and,
     run in a scoped deterministic way, EXITS 0. The map is encoded here so it is auditable.
  B. Card coherence          : #(.agent/agents/*.md) == roster in INDEX.md == schema roster;
     every card parses its `agent_card` frontmatter with the mandatory fields, declares
     `kind: process|prompt-module`, and validators/audit/governance/coordination are
     can_write_code: false.
  C. Single reviewer path    : exactly ONE independent-reviewer entrypoint
     (scripts/agent/verify_eval.py). A second reviewer script => FAIL.
  D. DAG integrity           : every depends_on / delegates_to id resolves to a real card.
  E. Label honesty           : any ATIVO/Completo/Complete status *claim* in a card's
     enforcement_status must name a guard that exists and exits 0.
  F. Framework hygiene       : PORT-1.1 (2026-07-21) — encodes the failure classes found
     in the credit_analyser `.agent/` audit, so they can never recur here:
       F1 entry points intact (AGENTS.md + CLAUDE.md/GEMINI.md symlinks + .cursorrules);
       F2 no framework file left UNVERSIONED (untracked in git);
       F3 enforcement actually installed (core.hooksPath=.githooks, hooks executable,
          no fail-open `|| true` on guard lines inside the git hooks);
       F4 every path the core docs reference actually exists (no phantom references).

Any drift => a distinct FAIL line, exit 1. Zero drift => "framework_selfcheck: OK", exit 0.
No third-party deps: a tiny frontmatter reader parses the constrained YAML the cards use.
"""
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = ROOT / ".agent" / "agents"
INDEX = ROOT / ".agent" / "INDEX.md"
SCHEMA = ROOT / ".agent" / "AGENT-CARD-SCHEMA.md"
GUARDS = ROOT / "scripts" / "guards"
AGENT_SCRIPTS = ROOT / "scripts" / "agent"

MANDATORY_FIELDS = [
    "id", "name", "role", "can_write_code", "capabilities",
    "inputs", "outputs", "depends_on", "model_hint",
]
VALID_KINDS = {"process", "prompt-module"}
# roles whose cards MUST be read-only (M5): builder is the only writer role.
NON_WRITER_ROLES = {"validation", "audit", "governance", "coordination", "policy"}

# ---------------------------------------------------------------------------
# A. Invariant -> guard wiring. EXPLICIT so the mapping itself is auditable.
#   Each entry: a scoped, deterministic invocation that must exit 0 on a clean tree.
#   We run each guard against a tiny KNOWN-CLEAN fixture (or a bare invocation) so a PASS
#   means "the guard exists and green-lights clean input", never "it happened to find nothing".
# ---------------------------------------------------------------------------
CLEAN_FIXTURE = ROOT / "scripts" / "guards" / "_selfcheck_clean_fixture.md"
CLEAN_METRIC_FIXTURE = ROOT / "scripts" / "guards" / "_selfcheck_metric_fixture.md"

INVARIANT_GUARD_MAP = {
    "I1": {
        "desc": "never persist raw biometrics (rule 04)",
        "guard": GUARDS / "no_raw_biometric.py",
        "argv": lambda: [str(CLEAN_FIXTURE)],
    },
    "I2": {
        "desc": "no real personal data / synthetic-only (rule 03)",
        "guard": GUARDS / "no_real_pii.py",
        "argv": lambda: [str(CLEAN_FIXTURE)],
    },
    "I3": {
        "desc": "no self-reported metric without reproducible artifact (rule 07) — reproducibility leg",
        "guard": GUARDS / "metric_honesty.py",
        "argv": lambda: [str(CLEAN_METRIC_FIXTURE)],
    },
    "I4": {
        "desc": "cross-generator evaluation mandatory (rule 05/D8) — cross-generator leg",
        "guard": GUARDS / "metric_honesty.py",
        "argv": lambda: ["--require-cross-generator", str(CLEAN_METRIC_FIXTURE)],
    },
    "I5": {
        "desc": "metrics are targets to test, not promises (D5) — adjacent-target exemption leg",
        "guard": GUARDS / "metric_honesty.py",
        "argv": lambda: [str(CLEAN_METRIC_FIXTURE)],
    },
}

# A clean fixture that every scanning guard must pass: no biometrics, no PII.
CLEAN_FIXTURE_TEXT = (
    "# selfcheck clean fixture (synthetic, derived features only)\n"
    "This file is intentionally clean. It stores only derived feature_vector data.\n"
    "No raw biometrics, no real PII. Contact: user@example.com\n"
)
# A clean METRIC fixture: a metric declared as an adjacent target (I5 exemption) with
# cross-generator + reproducibility evidence present (I3/I4 legs pass green).
CLEAN_METRIC_FIXTURE_TEXT = (
    "# selfcheck metric fixture (honest, reproducible, cross-generator)\n"
    "Aspirational target 90% recall (target).\n"
    "Measured under the cross-generator protocol; reproducible from notebook + seed.\n"
)


def _write_fixtures():
    CLEAN_FIXTURE.write_text(CLEAN_FIXTURE_TEXT)
    CLEAN_METRIC_FIXTURE.write_text(CLEAN_METRIC_FIXTURE_TEXT)


def _cleanup_fixtures():
    for f in (CLEAN_FIXTURE, CLEAN_METRIC_FIXTURE):
        try:
            f.unlink()
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Minimal frontmatter reader (stdlib only). Cards use a constrained YAML subset:
# a top-level `agent_card:` block with 2-space indented scalars/inline-lists, plus
# a few top-level scalars after it. We extract just what the assertions need.
# ---------------------------------------------------------------------------
def _read_frontmatter(path: Path):
    text = path.read_text(errors="ignore")
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    return text[3:end]


def _parse_card(path: Path):
    """Return a flat dict of the agent_card fields we assert on. Robust to the subset
    the cards use (inline `[a, b]` lists, scalars, nested one-liners). Not a full YAML."""
    fm = _read_frontmatter(path)
    if fm is None:
        return None
    card = {}
    in_card = False
    for raw in fm.splitlines():
        if raw.strip() == "agent_card:":
            in_card = True
            continue
        if not in_card:
            continue
        # a non-indented, non-blank line ends the agent_card block
        if raw and not raw.startswith(" ") and not raw.startswith("\t"):
            break
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        # only capture direct children of agent_card (2-space indent). deeper nesting ignored.
        indent = len(raw) - len(raw.lstrip(" "))
        if indent != 2:
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        card[key] = _coerce(val)
    return card


def _coerce(val: str):
    if val == "":
        return None
    if val.startswith("[") and val.endswith("]"):
        inner = val[1:-1].strip()
        if not inner:
            return []
        return [x.strip() for x in inner.split(",") if x.strip()]
    low = val.lower()
    if low in ("true", "false"):
        return low == "true"
    return val


# ---------------------------------------------------------------------------
# Assertions
# ---------------------------------------------------------------------------
def check_invariant_wiring(fails):
    """A. each I1..I5 -> a guard that EXISTS and PASSES (exit 0) on a scoped clean input."""
    for inv, spec in sorted(INVARIANT_GUARD_MAP.items()):
        guard = spec["guard"]
        if not guard.is_file():
            fails.append(f"[A] {inv} ({spec['desc']}): guard MISSING: {guard.relative_to(ROOT)}")
            continue
        argv = [sys.executable, str(guard)] + spec["argv"]()
        try:
            r = subprocess.run(argv, capture_output=True, text=True, cwd=str(ROOT), timeout=60)
        except Exception as e:  # noqa: BLE001 - report any launch failure as a wiring fail
            fails.append(f"[A] {inv}: guard FAILED to launch ({guard.name}): {e}")
            continue
        if r.returncode != 0:
            tail = (r.stdout + r.stderr).strip().splitlines()
            tail = tail[-1] if tail else "(no output)"
            fails.append(f"[A] {inv} ({spec['desc']}): guard {guard.name} scoped run exit "
                         f"{r.returncode} (expected 0): {tail}")


def _roster_from_index():
    """Roster the INDEX declares under the Agents section (the `·`-separated list)."""
    text = INDEX.read_text()
    m = re.search(r"## Agents.*?\n(.*?)(?:\n##|\Z)", text, re.S)
    if not m:
        return set()
    block = m.group(1)
    ids = re.split(r"[·\n]", block)
    out = set()
    for tok in ids:
        tok = tok.strip().strip(".").strip()
        # keep kebab-ish tokens, drop prose
        if tok and re.fullmatch(r"[a-z0-9-]+", tok, re.I):
            out.add(tok.lower())
    return out


def _roster_from_schema():
    """Roster the AGENT-CARD-SCHEMA implies (the builder/validator firewall table §5)."""
    text = SCHEMA.read_text()
    ids = set()
    # the §5 table lists concrete agent ids; harvest known kebab ids mentioned there.
    for tok in re.findall(r"[a-z][a-z-]*[a-z]", text):
        ids.add(tok)
    return ids


def check_card_coherence(fails, cards):
    """B. count parity + mandatory fields + kind + M5 read-only roles."""
    card_ids = {c["_id"] for c in cards}
    index_roster = _roster_from_index()
    schema_roster = _roster_from_schema()

    # count parity: filesystem == INDEX roster
    if card_ids != index_roster:
        missing = card_ids - index_roster
        extra = index_roster - card_ids
        detail = []
        if missing:
            detail.append(f"in files not INDEX: {sorted(missing)}")
        if extra:
            detail.append(f"in INDEX not files: {sorted(extra)}")
        fails.append(f"[B] card roster != INDEX roster ({'; '.join(detail)})")

    # schema roster must reference every real card id (schema is the SSOT for the firewall)
    unref = sorted(cid for cid in card_ids if cid not in schema_roster)
    if unref:
        fails.append(f"[B] cards not referenced in AGENT-CARD-SCHEMA firewall table: {unref}")

    for c in cards:
        cid = c["_id"]
        for field in MANDATORY_FIELDS:
            if field not in c or c[field] is None:
                fails.append(f"[B] card '{cid}' missing mandatory field: {field}")
        kind = c.get("kind")
        if kind is None:
            fails.append(f"[B] card '{cid}' missing mandatory field: kind (process|prompt-module)")
        elif kind not in VALID_KINDS:
            fails.append(f"[B] card '{cid}' invalid kind '{kind}' (must be process|prompt-module)")
        role = c.get("role")
        cwc = c.get("can_write_code")
        if role in NON_WRITER_ROLES and cwc is not False:
            fails.append(f"[B] card '{cid}' role={role} must have can_write_code:false (M5), got {cwc}")


# C. Single-reviewer detection. PRECISE, not broad: a script is an independent-reviewer
# entrypoint iff it looks like one BY NAME (the classic reviewer-ish stems) OR carries the
# explicit reviewer marker in its body. A generic primitive (agent_run.py) that merely
# spawns `claude -p` is NOT a reviewer — it carries no marker and has a non-reviewer name,
# so it is not flagged. This keeps real detection intact (a bland-named eval_independent.py
# decoy is still caught by the name test) without flagging the PORT-3 generic runner.
CANONICAL_REVIEWER = "verify_eval.py"
# Scripts explicitly known NOT to be a second reviewer (the canonical one + generic
# primitives). Being allowlisted does NOT bypass the marker/name test for OTHER files.
REVIEWER_ALLOWLIST = {"verify_eval.py", "agent_run.py"}
# Name heuristic: reviewer-ish stems. Kept deliberately narrow (an "eval"-only match is
# not enough — agent_run/eval_plan etc. must not trip it).
REVIEWER_NAME_RE = re.compile(
    r"(eval_independent|independent_eval|verify_eval|reviewer|second_review|eval_review)",
    re.I,
)
# Body marker: the unambiguous, explicit self-declaration of a reviewer entrypoint.
REVIEWER_MARKER_RE = re.compile(
    r"(REVIEWER-ENTRYPOINT|independent-reviewer entrypoint)", re.I,
)


def _looks_like_reviewer(p: Path) -> bool:
    if REVIEWER_NAME_RE.search(p.stem):
        return True
    try:
        body = p.read_text(errors="ignore")
    except OSError:
        return False
    return bool(REVIEWER_MARKER_RE.search(body))


def check_single_reviewer(fails):
    """C. exactly ONE independent-reviewer entrypoint: scripts/agent/verify_eval.py.
    Detection is precise (name OR explicit marker), with an allowlist for the canonical
    reviewer and generic primitives — so a real second reviewer is still caught but a
    generic runner is not."""
    canonical = AGENT_SCRIPTS / CANONICAL_REVIEWER
    if not canonical.is_file():
        fails.append(f"[C] canonical reviewer entrypoint MISSING: {canonical.relative_to(ROOT)}")
    offenders = []
    for p in AGENT_SCRIPTS.glob("*.py"):
        if p.name in REVIEWER_ALLOWLIST:
            continue
        if _looks_like_reviewer(p):
            offenders.append(p.name)
    for name in sorted(offenders):
        fails.append(f"[C] a SECOND reviewer entrypoint exists (breaks one-reviewer rule): {name}")


def check_dag(fails, cards):
    """D. every depends_on id resolves; every orchestrator delegates_to id resolves."""
    card_ids = {c["_id"] for c in cards}
    for c in cards:
        cid = c["_id"]
        for dep in c.get("depends_on") or []:
            if dep not in card_ids:
                fails.append(f"[D] card '{cid}' depends_on unknown id: {dep}")
        for tgt in c.get("delegates_to") or []:
            if tgt not in card_ids:
                fails.append(f"[D] orchestrator '{cid}' delegates_to unknown id: {tgt}")


def check_label_honesty(fails, cards):
    """E. any ATIVO/Completo/Complete claim in enforcement_status must name a guard that
    exists and exits 0 (scoped clean run). Hand-off markers in card BODY are not claims."""
    claim_re = re.compile(r"(ativo|completo|complete)", re.I)
    guard_re = re.compile(r"scripts/guards/([a-z0-9_]+\.py)", re.I)
    for c in cards:
        for key, val in c.get("_enforcement_status", {}).items():
            if not claim_re.search(val):
                continue
            m = guard_re.search(val)
            if not m:
                fails.append(f"[E] card '{c['_id']}' enforcement_status.{key} claims '{val.strip()}' "
                             f"but names NO scripts/guards/*.py to back it")
                continue
            guard = GUARDS / m.group(1)
            if not guard.is_file():
                fails.append(f"[E] card '{c['_id']}' enforcement_status.{key} names missing guard: {m.group(1)}")
                continue
            argv = [sys.executable, str(guard), str(CLEAN_FIXTURE)]
            try:
                r = subprocess.run(argv, capture_output=True, text=True, cwd=str(ROOT), timeout=60)
            except Exception as e:  # noqa: BLE001
                fails.append(f"[E] card '{c['_id']}' guard {m.group(1)} failed to launch: {e}")
                continue
            if r.returncode != 0:
                fails.append(f"[E] card '{c['_id']}' claims ATIVO but {m.group(1)} scoped run exit "
                             f"{r.returncode} (expected 0)")


def _extract_enforcement_status(path: Path):
    """Pull the (key -> value) pairs under enforcement_status: from a card's frontmatter."""
    fm = _read_frontmatter(path)
    if not fm:
        return {}
    out = {}
    lines = fm.splitlines()
    i = 0
    while i < len(lines):
        if lines[i].strip() == "enforcement_status:":
            base_indent = len(lines[i]) - len(lines[i].lstrip(" "))
            i += 1
            while i < len(lines):
                raw = lines[i]
                if not raw.strip():
                    i += 1
                    continue
                indent = len(raw) - len(raw.lstrip(" "))
                if indent <= base_indent:
                    break
                if ":" in raw:
                    k, _, v = raw.strip().partition(":")
                    out[k.strip()] = v.strip().strip('"')
                i += 1
            break
        i += 1
    return out


# ---------------------------------------------------------------------------
# F. Framework hygiene (PORT-1.1). Root cause: the credit_analyser audit (2026-07-21)
# found a full `.agent/` framework that was INERT — no entry points, unversioned, no
# enforcement, phantom references. These checks make each of those states a hard FAIL.
# ---------------------------------------------------------------------------
ENTRYPOINT = ROOT / "AGENTS.md"
SYMLINK_ENTRYPOINTS = {"CLAUDE.md": "AGENTS.md", "GEMINI.md": "AGENTS.md"}
CURSORRULES = ROOT / ".cursorrules"
GIT_HOOKS = ROOT / ".githooks"
CLAUDE_HOOKS = ROOT / ".claude" / "hooks"
# Everything that IS the framework must be under version control (F2).
FRAMEWORK_TRACK_PATHS = [
    ".agent", ".claude", ".githooks", "scripts/guards", "scripts/agent", "scripts/lib",
    "AGENTS.md", "AGENTS.pt-BR.md", ".cursorrules",
    ".github/workflows/framework-selfcheck.yml",
]
# Core docs whose referenced paths must resolve (F4).
CORE_DOCS = ["AGENTS.md", ".agent/INDEX.md", ".agent/CONSTITUTION.md", ".agent/BOOTSTRAP.md"]
_REF_RE = re.compile(r"`((?:\.agent|\.claude|\.context|\.githooks|scripts)/[A-Za-z0-9_\-./]+)`")
_FAIL_OPEN_RE = re.compile(r"guards/.*\|\|\s*true")


def check_entrypoints(fails):
    """F1. Multi-runtime entry points must exist and point at the single physical entry."""
    if not ENTRYPOINT.is_file():
        fails.append("[F1] entry point MISSING: AGENTS.md (framework is INERT without it)")
    for link, target in SYMLINK_ENTRYPOINTS.items():
        p = ROOT / link
        if not p.is_symlink():
            fails.append(f"[F1] {link} must be a symlink -> {target} (multi-runtime entry)")
            continue
        actual = os.readlink(p)
        if actual != target:
            fails.append(f"[F1] {link} symlink points to '{actual}', expected '{target}'")
    if not CURSORRULES.is_file():
        fails.append("[F1] .cursorrules condensed mirror MISSING")


def check_versioning(fails):
    """F2. No framework file may be untracked — an unversioned framework only exists on
    one machine (exactly how credit_analyser lost its `.agent/`). Skips if git absent."""
    try:
        r = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard", "--"] + FRAMEWORK_TRACK_PATHS,
            capture_output=True, text=True, cwd=str(ROOT), timeout=30,
        )
    except Exception:
        return  # no git available in this environment — nothing to assert
    if r.returncode != 0:
        return
    for f in sorted(l for l in r.stdout.splitlines() if l.strip()):
        if Path(f).name.startswith("_selfcheck_"):
            continue  # transient fixtures written/removed by this very script
        fails.append(f"[F2] framework file NOT under version control: {f} (git add it)")
    # A repo with no remote exists on exactly one machine — one disk failure from zero.
    # (Local machines only; CI checkouts always have an origin.)
    if not os.environ.get("CI"):
        try:
            rr = subprocess.run(["git", "remote"], capture_output=True, text=True,
                                cwd=str(ROOT), timeout=15)
            if rr.returncode == 0 and not rr.stdout.strip():
                fails.append("[F2] no git remote configured — framework + approval-log exist "
                             "only on this machine (git remote add origin <url> && git push)")
        except Exception:
            pass


def check_enforcement_installed(fails):
    """F3. Rules without installed enforcement are documentation, not gates."""
    # hooksPath — local machines only (CI runners legitimately have no hooksPath).
    if not os.environ.get("CI"):
        try:
            r = subprocess.run(["git", "config", "core.hooksPath"],
                               capture_output=True, text=True, cwd=str(ROOT), timeout=15)
            if r.stdout.strip() != ".githooks":
                fails.append("[F3] core.hooksPath is not '.githooks' — git hooks NOT installed "
                             "(run: git config core.hooksPath .githooks)")
        except Exception:
            pass
    for hook in ("pre-commit", "pre-push"):
        p = GIT_HOOKS / hook
        if not p.is_file():
            fails.append(f"[F3] .githooks/{hook} MISSING")
            continue
        if not os.access(p, os.X_OK):
            fails.append(f"[F3] .githooks/{hook} not executable (chmod +x)")
        for n, line in enumerate(p.read_text(errors="ignore").splitlines(), 1):
            if _FAIL_OPEN_RE.search(line):
                fails.append(f"[F3] fail-open pattern in .githooks/{hook}:{n} — "
                             f"a guard invocation must never end in '|| true'")
    if CLAUDE_HOOKS.is_dir():
        for sh in sorted(CLAUDE_HOOKS.glob("*.sh")):
            if not os.access(sh, os.X_OK):
                fails.append(f"[F3] .claude/hooks/{sh.name} not executable (chmod +x)")


def check_core_links(fails):
    """F4. Paths referenced in the core docs must exist — no phantom references."""
    for rel in CORE_DOCS:
        doc = ROOT / rel
        if not doc.is_file():
            fails.append(f"[F4] core doc MISSING: {rel}")
            continue
        for ref in sorted(set(_REF_RE.findall(doc.read_text(errors="ignore")))):
            if "*" in ref:
                continue  # glob mention, not a concrete path
            if not (ROOT / ref.rstrip("/")).exists():
                fails.append(f"[F4] {rel} references missing path: {ref}")


def load_cards():
    cards = []
    for p in sorted(AGENTS_DIR.glob("*.md")):
        parsed = _parse_card(p)
        if parsed is None:
            cards.append({"_id": p.stem, "_parse_error": True, "_path": p})
            continue
        parsed["_id"] = parsed.get("id", p.stem)
        parsed["_path"] = p
        parsed["_enforcement_status"] = _extract_enforcement_status(p)
        cards.append(parsed)
    return cards


def main():
    fails = []
    _write_fixtures()
    try:
        cards = load_cards()
        for c in cards:
            if c.get("_parse_error"):
                fails.append(f"[B] card '{c['_id']}' has no parseable agent_card frontmatter")
        check_invariant_wiring(fails)
        check_card_coherence(fails, [c for c in cards if not c.get("_parse_error")])
        check_single_reviewer(fails)
        check_dag(fails, [c for c in cards if not c.get("_parse_error")])
        check_label_honesty(fails, [c for c in cards if not c.get("_parse_error")])
        check_entrypoints(fails)
        check_versioning(fails)
        check_enforcement_installed(fails)
        check_core_links(fails)
    finally:
        _cleanup_fixtures()

    if fails:
        print("BLOCKED — framework_selfcheck: structural drift detected "
              f"({len(fails)} finding(s)). Fix all before push:")
        for f in fails:
            print(f"  FAIL {f}")
        raise SystemExit(1)
    print("framework_selfcheck: OK")
    raise SystemExit(0)


if __name__ == "__main__":
    main()
