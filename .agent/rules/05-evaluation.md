---
id: rule-05-evaluation
version: 2.0.0
last_updated: 2026-06-17
next_review: 2026-09-15
trigger: always_on
priority: CRITICAL
tokens: ~1200
description: Held-out + cross-generator mandatory. Report curves not points. The full protocol. SSOT owner: evaluation.
---

# 05 — Evaluation Protocol (SSOT owner: evaluation)

> **Invariant I4 / D8: Cross-generator evaluation is mandatory.** This rule exists to kill the **#1
> credibility risk** of the entire project: the circularity trap.

## The circularity trap (why this rule is CRITICAL, not nice-to-have)
Generating your own synthetic attacks AND testing detection against them measures **"can my detector
recognize artifacts from my own generator"** — which is nearly tautological, and **collapses against any
generator you did not use.** An IEEE/OECD evaluator sees this on the first read, because it is the classic
error of deepfake-detection papers. If our headline number comes from an in-distribution test, our
credibility is gone regardless of how high the number is. (LESSON LC-001.)

## The mandatory protocol
1. **Leave-one-generator-out.** Train on generators **{A, B}**; test on a held-out generator **C that was
   never seen during development.** The number that matters is the **cross-generator** number, not the
   in-distribution one. The held-out split is sacred — data-redteam builds it by construction (rule 03).
2. **Robustness delta is the HEADLINE.** Report the accuracy drop:
   - in-distribution {A,B} → cross-generator C  (generalization)
   - standard tier → stress tier  (adversarial resilience)
   The deck/report leads with the delta, not the best-case point.
3. **Report curves, not points.** P/R at a *fixed* FPR, with confidence intervals; ROC and PR curves.
   Never a single "95%". In adversarial detection, pushing recall up raises FPR and vice-versa — a single
   point is meaningless without the operating curve.
4. **No training a Layer-1 detector from scratch.** Fine-tune existing open-source detectors and report the
   delta vs the base. Training from scratch on our own red-team set guarantees overfitting to our own
   generators (see the trap above) and burns solo-team time. (rule 01, knowledge/layer1.)
5. **Harness and frozen splits BEFORE the models.** Build EPIC-EVAL-HARNESS first. No model training begins
   before the protocol and the held-out splits are frozen — so the number can never be quietly tuned-to.

## Worked example (honest vs dishonest reporting)
- ❌ Dishonest: "Our detector achieves 96% precision." (in-distribution, single point, our generators)
- ✅ Honest: "Cross-generator recall 84% @ FPR 0.3% (CI ±2pp) on held-out generator C; robustness delta
  −12pp from in-distribution; ROC/PR attached; reproducible via `notebooks/eval.ipynb`, seed 42."
  The second one **wins** under IEEE scrutiny even though the number is lower.

## Acceptance checklist (eval-independent enforces)
- [ ] Held-out generator C never seen in development (check splits-manifest).
- [ ] Robustness delta reported as the headline.
- [ ] Curves + CI, not a point.
- [ ] Base model named; no from-scratch detector.
- [ ] Reproducible: notebook + seed regenerate identical curves.

## Enforcement
`scripts/guards/metric_honesty.py --require-cross-generator` (pre-push) + `verify_eval.py` (isolated
eval-independent) + the EVAL-GATE. A metric % in a committed file without "cross-generator" + a
notebook/seed reference is **blocked**.

## Anti-patterns (forbidden)
- ❌ Reporting in-distribution accuracy as the headline. ❌ A single-point metric. ❌ Training Layer-1 from
  scratch. ❌ Building the model before the harness. ❌ Tuning the threshold against the held-out split.
