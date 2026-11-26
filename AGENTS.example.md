<!-- Merge these rules into ~/.config/opencode/AGENTS.md (or your agent's global instruction file). -->
# Global execution rules

Efficiency is required; quality is not optional. Prefer fewer, larger, verified steps over many tiny steps. Never skip checks for money, auth, permissions, destructive writes, or anything irreversible.

## Lanes

State the lane in one short line, then work.

- **L0 — question/research:** answer directly; ≤2 tool calls; no plan.
- **L1 — single file, reversible, low risk (no user-data writes):** one recon batch → one edit → one targeted check; ≤8 turns.
- **L2 — multi-file/feature/data batch (including bulk file writes):** one recon batch → ≤5-line inline plan → batched implementation → one milestone check + one final check; ≤40 turns.
- **L3 — irreversible, production, money, publish, or formal deliverable with external validation:** full design + plan + independent review + backup/rollback plan. No cap.

For L0/L1, do **not** invoke `brainstorming`, `writing-plans`, TDD ceremony, `subagent-driven-development`, or per-task review chains. For L2, use TDD only for core logic; skip ceremony for docs/UI/one-off scripts. For L3, use the full process. If the user explicitly asks for a full process, follow the user.

## Acceptance contract

Before classifying, extract the acceptance contract: deliverables and formats, template/sections/figures, external runs/accounts, identity placeholders, submission limits. If a required item is impossible, stop and ask before building a substitute.

`DONE` is a checklist, not one command. For documents/PDF/PPT, render and visually check the template, sections, figures, placeholders, and page limit. Lean cuts ceremony, not scope. A budget is a ceiling, not a target: stop when the checklist is complete, and keep going if it is not.

If a lane budget is exceeded, stop and reassess (split the task, promote the lane, or ask); do not silently grind.

## Laws

1. Define "done" before the first edit: the exact command/output that proves success, plus the acceptance checklist.
2. Recon once: tree, entry points, dependencies, test command, template, external access. Batch independent tool calls in one turn.
3. Verify at milestones, not after every edit. On failure, run the narrowest diagnostic.
4. Two-strike rule: the same error twice → stop editing, diagnose, change the hypothesis, then make one fix.
5. Never re-read an unchanged file. Grep/range-read. Put long output in a file, not in context.
6. Subagents only for independent work ≥15 min serial; max 2 in parallel; file brief → file report. No per-task implementer+reviewer+fixer chains.
7. Jobs >90s: run in background with a log; poll every 30s. Do not hold a turn open.
8. Report results, not narration. Keep reasoning, errors, and code exact.

When this file conflicts with a process skill, this file wins for L0–L2. Detailed checklist: skill `lean-run`.
