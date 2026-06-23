"""SHIELD-ID agent state: the active-experiment machine + append-only approval log.
Single source of truth for "which experiment is active and which gates passed".
stdlib-only. Mirrors zeca_site/.agent/state semantics, adapted to ML steps.
"""
import json, os, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]            # shield_id/
STATE_DIR = ROOT / ".agent" / "state"
CURRENT = STATE_DIR / "current-experiment.json"        # git-ignored, ephemeral
LOG = STATE_DIR / "approval-log.jsonl"                  # checked-in, append-only audit
ARCHIVE = STATE_DIR / "archived"

# Ordered gate steps per experiment type. required=True steps block src edits until approved.
STEP_SETS = {
    "experiment": ["kickoff", "spec", "c4", "eval-plan", "data", "implementation", "eval", "verify", "pr-opened"],
    "api":        ["kickoff", "spec", "c4", "threat-model", "implementation", "eval", "verify", "pr-opened"],
    "dataset":    ["kickoff", "datasheet", "data", "eval-plan", "verify", "pr-opened"],
    "policy":     ["kickoff", "outline", "draft", "framework-alignment", "review"],
}
# Steps that gate src/ edits (must be approved before code).
SRC_GATING = {"kickoff", "spec", "c4", "eval-plan", "threat-model", "datasheet"}

def now(): return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def load():
    if not CURRENT.exists(): return None
    try: return json.loads(CURRENT.read_text())
    except Exception: return None

def save(state): STATE_DIR.mkdir(parents=True, exist_ok=True); CURRENT.write_text(json.dumps(state, indent=2))

def log_event(event, **kw):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    rec = {"ts": now(), "event": event, **kw}
    with LOG.open("a") as f: f.write(json.dumps(rec) + "\n")

def start(slug, type_):
    steps = STEP_SETS.get(type_, STEP_SETS["experiment"])
    state = {"schema_version": 1, "experiment": slug, "type": type_,
             "branch": f"exp/{slug}", "current_step": steps[0],
             "steps": {s: {"approved": False, "approved_at": None, "approver": None,
                           "required": True, "gates_src": s in SRC_GATING} for s in steps},
             "tech_debt": [], "notes": ""}
    save(state); log_event("experiment_started", experiment=slug, type=type_)
    return state

def approve(step, approver="camilo"):
    state = load()
    if not state: raise SystemExit("No active experiment. Run start_experiment.py first.")
    if step not in state["steps"]: raise SystemExit(f"Unknown step '{step}'. Steps: {list(state['steps'])}")
    state["steps"][step].update(approved=True, approved_at=now(), approver=approver)
    # auto-advance current_step to next unapproved
    for s in state["steps"]:
        if not state["steps"][s]["approved"]: state["current_step"] = s; break
    else: state["current_step"] = "done"
    save(state); log_event("step_approved", experiment=state["experiment"], step=step, approver=approver)
    return state

def unapproved_src_gates():
    """Return required src-gating steps not yet approved (used by guard_src_edits)."""
    state = load()
    if not state: return None  # no active experiment
    return [s for s, v in state["steps"].items() if v.get("gates_src") and v.get("required") and not v.get("approved")]
