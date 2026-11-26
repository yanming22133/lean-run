<!-- Merge these rules into ~/.config/opencode/AGENTS.md (or your agent's global instruction file). -->
# Global execution rules

Efficiency is required; quality is not optional. Never skip checks for money, auth, permissions, destructive writes, or anything irreversible.

## Lanes

State the lane in one short line, then work.

- **L0 — question/research:** answer directly; ≤2 tool calls; no plan.
- **L1 — single file, reversible, low risk (no user-data writes):** one recon batch → one edit → one targeted check; ≤8 turns.
- **L2 — multi-file/feature/data batch (including bulk file writes):** one recon batch → ≤5-line inline plan → batched implementation → milestone check + final check; delivery gate if a document is delivered; ≤40 turns.
- **L3 — irreversible, production, money, publish, or formal deliverable with external validation:** full design + plan + independent review + rollback plan; delivery gate; soft cap 80 turns.

For L0/L1, do **not** invoke `brainstorming`, `writing-plans`, TDD ceremony, `subagent-driven-development`, or per-task review chains. For L2, use TDD only for core logic; skip ceremony for docs/UI/one-off scripts. If the user explicitly asks for a full process, follow the user.

## Acceptance and stopping

Before classifying, build a requirements matrix: `requirement | source | evidence | status`. `DONE` means every row is PASS and the acceptance command passes.

If a required account, license, hardware run, or quota is missing, mark the row BLOCKED and stop. If you cannot ask (subagent/unattended), write `BLOCKED.md` with done/missing/blocker/next and deliver everything that does not depend on it.

A budget is a ceiling, not a target. If the budget is exhausted and the matrix is incomplete, write a BLOCKED report and stop; do not silently grind.

## Laws

1. Recon once: tree, entry points, dependencies, test command, template, external access. Batch independent tool calls in one turn.
2. Two-strike rule: the same error twice → stop editing, diagnose, change the hypothesis, then make one fix.
3. Verify at milestones, not after every edit. Trust text edits; recheck generated PDF/PPTX/DOCX after the final rebuild.
4. Subagents only for independent work ≥15 min serial; max 2 in parallel; file brief → file report. No per-task implementer+reviewer+fixer chains.
5. Jobs >90s: background + log; prefer one blocking wait with a timeout; poll only when you have other work.
6. Report results, not narration. Keep reasoning, errors, and code exact.

When this file conflicts with a process skill, this file wins for L0–L2. Detailed checklist: skill `lean-run`.
