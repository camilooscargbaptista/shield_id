#!/usr/bin/env python3
"""I3/I4 (rules 05/07): a file that claims a metric must also evidence the cross-generator
protocol AND a reproducible artifact. Scans given files (e.g., staged reports/SUMMARY).
--require-cross-generator hard-fails if a metric lacks 'cross-generator'. Exit 1 = BLOCK.

Hardening (LC-004, found by eval-independent on US-001 certification): the exemption for a
*target* declaration must be ADJACENT to the number (a tight window), not merely the word
"target" appearing anywhere in the file. Otherwise an unrelated "target" whitelisted a whole
dishonest report. The exemption now requires an exempt word within ~12 chars of the number.

T-FIX-02 hardening (2026-08-13, defect fixture passed the gate 22 days green):
  - METRIC now also catches NAMED FRACTIONS (recall = 0.96) and 1-DIGIT percents (FPR 0.3%).
  - New DETERMINISTIC circularity check: held_out_generator declared inside train_generators
    (kill-list #1 / I4 / D8) — a circular 'cross-generator' claim is not real evidence.
  - New HEURISTIC threshold-on-held-out check: a tuning verb near a held-out/test-split
    reference (kill-list #4), unless negated adjacently (LC-004 adjacency, e.g. 'NOT tuned').
  - Parse/read errors BLOCK with a message (never fail-open to exit 0)."""
import sys, re
from pathlib import Path

# --- metric detection ---------------------------------------------------------------------
# A percent with 1-3 leading digits (now catches "0.3%") OR a metric named as a bare fraction.
METRIC_PCT = re.compile(r"\b\d{1,3}(?:\.\d+)?\s*%")
_METRIC_NAMES = r"(recall|precision|fpr|tpr|fnr|auroc|auprc|accuracy|f1|robustness[ _-]?delta)"
METRIC_FRAC = re.compile(_METRIC_NAMES + r"\b[^=:\n]{0,25}[=:]\s*-?[01]?\.\d+", re.I)

# A bare TARGET/pedagogical declaration is exempt ONLY when the exempt word is adjacent to the
# number. PORT-1.1 (2026-07-21) extended the same tight-adjacency rule to teaching text
# (example/illustrative/hypothetical/estimate). Window stays 12 chars so a real result cannot be
# laundered by a distant word (LC-004 rationale). T-FIX-02: the number can now also be a 1-digit
# percent or a bare fraction — the window is UNCHANGED (still 12).
EXEMPT_WORDS = r"(?:target|aspirational|example|illustrative|hypothetical|estimate|estimativa|exemplo)"
_ANY_NUM = r"(?:\d{1,3}(?:\.\d+)?\s*%|-?[01]?\.\d+)"
TARGET_ADJ = re.compile(EXEMPT_WORDS + r"\W{0,12}" + _ANY_NUM +
                        r"|" + _ANY_NUM + r"\W{0,12}" + EXEMPT_WORDS, re.I)

# --- deterministic circularity (kill-list #1 / I4 / D8) -----------------------------------
TRAIN_GENS_RE = re.compile(r"train_generators\s*[=:]\s*\[([^\]]*)\]", re.I)
HELD_OUT_RE = re.compile(r"held_out_generator\s*[=:]\s*[\"']?([\w\-]+)", re.I)

# --- heuristic threshold-on-held-out (kill-list #4) ---------------------------------------
TUNE_VERB_RE = re.compile(r"(sweep|swept|sweeping|tun\w+|varr\w+|selected|picking|maximiz\w+)", re.I)
HELDOUT_REF_RE = re.compile(r"(held-?out|test split)", re.I)
# LC-004 adjacency: a negation within 12 chars BEFORE the tuning verb marks it as a non-claim.
NEG_BEFORE_RE = re.compile(r"(not|never|n[aã]o|nunca)\W{0,12}$", re.I)

# PORT-1.1 (2026-07-21): policy/pedagogy scope. `.agent/` and `.context/` hold rules,
# thresholds ("coverage >= 80%") and teaching examples — never measured RESULTS (SSOT:
# results live in docs/reports + the verification artifacts emitted by verify_eval.py,
# rule 15). Scanning them produced only false positives, which trains humans to ignore
# the gate. Everything outside these trees keeps the strict scan.
PEDAGOGICAL_PREFIXES = (".agent/", ".context/")


def _is_pedagogical(path: str) -> bool:
    norm = path.replace("\\", "/")
    while norm.startswith("./"):
        norm = norm[2:]
    return norm.startswith(PEDAGOGICAL_PREFIXES)


def _is_source_code(path: str) -> bool:
    """The two STRUCTURAL declaration checks (circularity + threshold-on-held-out) are for report
    ARTIFACTS (the pre-push gate scans only .md/.json; verify_eval feeds reports/experiments), NOT
    for .py source — where these tokens appear in code, comments, kill-list DESCRIPTIONS and
    NEGATIVE tests (a test that builds a circular manifest to assert the code rejects it). Real
    circularity in the training path is already caught at RUNTIME (ValueError in train_text_detector
    / redteam / eval.splits). This is NOT a widening of PEDAGOGICAL_PREFIXES nor of the 12-char
    window — it scopes two brand-new checks to the artifacts where a *declared* claim can live.
    The metric %/fraction detection below still runs on every file (unchanged)."""
    return path.replace("\\", "/").lower().endswith(".py")


def _detect_circularity(text: str):
    """Return (held_out, train_items) if the held-out generator is declared inside
    train_generators (circularity, I4/D8); else None. If either field is absent, return None
    (that sophistication is the LLM reviewer's job, not this deterministic gate)."""
    mt = TRAIN_GENS_RE.search(text)
    mh = HELD_OUT_RE.search(text)
    if not mt or not mh:
        return None
    items = [x.strip().strip("\"'") for x in mt.group(1).split(",") if x.strip()]
    held = mh.group(1).strip().strip("\"'")
    if held and held in items:
        return held, items
    return None


def _detect_threshold_on_heldout(text: str) -> bool:
    """Heuristic: a tuning verb within 80 chars of a held-out/test-split reference => BLOCK,
    UNLESS a negation is adjacent (<=12 chars) before that verb (LC-004 adjacency: 'NOT tuned
    on the held-out set' is a legitimate disclaimer, not a confession)."""
    for vm in TUNE_VERB_RE.finditer(text):
        window = text[max(0, vm.start() - 80): vm.end() + 80]
        if not HELDOUT_REF_RE.search(window):
            continue
        before = text[max(0, vm.start() - 20): vm.start()]
        if NEG_BEFORE_RE.search(before):
            continue                      # this occurrence is negated -> not a claim
        return True
    return False


def main():
    files = [a for a in sys.argv[1:] if not a.startswith("--")]
    fails = []
    for f in files:
        p = Path(f)
        if not p.is_file():
            continue
        if _is_pedagogical(f):
            continue
        try:
            text = p.read_text(errors="ignore")
        except Exception as e:  # read error must BLOCK, never fail-open (exit 0)
            fails.append((f, f"could not read file — refusing to pass silently (fail-closed): {e}"))
            continue
        try:
            low = text.lower()
            has_cross = ("cross-generator" in low) or ("cross generator" in low)
            has_repro = bool(re.search(r"(notebook|seed|reproducib)", low))

            # STRUCTURAL declaration checks apply to report artifacts, not .py source (see
            # _is_source_code): in code these tokens are variable names, kill-list descriptions
            # and negative tests, not a *declared* claim.
            structural = not _is_source_code(f)

            # deterministic circularity: a circular 'cross-generator' claim is NOT evidence,
            # so it also invalidates has_cross for the metric checks below (the reported number
            # is not truly cross-generator).
            if structural:
                circ = _detect_circularity(text)
                if circ:
                    held, items = circ
                    fails.append((f, f"declared circularity — held_out_generator '{held}' is inside "
                                     f"train_generators {items}: the reported metric is NOT cross-generator "
                                     f"(kill-list #1 / I4 / D8)"))
                    has_cross = False

                # heuristic threshold tuned on the held-out/test split (selection leakage)
                if _detect_threshold_on_heldout(text):
                    fails.append((f, "decision threshold selected/tuned on the held-out/test split — "
                                     "selection leakage (kill-list #4 / rule 05)"))

            # metric detection (line by line so the exemption is scoped to the actual metric)
            for ln in low.splitlines():
                if not (METRIC_PCT.search(ln) or METRIC_FRAC.search(ln)):
                    continue
                if TARGET_ADJ.search(ln):        # adjacent "target 95%" / "recall 0.9 (target)" allowed bare
                    continue
                if not has_cross:
                    fails.append((f, f"metric without cross-generator evidence (I4/D8): '{ln.strip()[:60]}'"))
                if not has_repro:
                    fails.append((f, f"metric without reproducible artifact (I3/D5): '{ln.strip()[:60]}'"))
        except Exception as e:  # any parse error must BLOCK, never fail-open (exit 0)
            fails.append((f, f"parse error while checking honesty — BLOCK (fail-closed): {e}"))
            continue
    if fails:
        print("BLOCKED — metric honesty (rules 05/07). A reported number needs cross-generator + reproducibility:")
        for f, m in fails:
            print(f"  {f}: {m}")
        raise SystemExit(1)
    print("metric_honesty: OK")
    raise SystemExit(0)

if __name__ == "__main__":
    main()
