---
name: lean-run
description: Acceptance-first execution for multi-file or formal-deliverable tasks. Use when a task spans multiple files, produces a document/PDF/PPT, depends on an external run, or is taking too long. Not for L0/L1 trivia. Triggers include "任务太久", "省时间", "少回合", "完美交付", "模板", "验收", "返工", "lean", "right-size".
---

# Lean Run

## Principle

Accepted delivery is the objective. Turns are the cost. Rework is the biggest cost. Lean cuts ceremony, not scope.

## 0. Requirements matrix (before lane)

Extract from the prompt, task file, template, and platform. Build a table:

| requirement | source | evidence | status |
|---|---|---|---|
| template section / heading | template or task | rendered page or text check | PASS / FAIL |
| required figure / table | task or template | rendered page | PASS / FAIL |
| identity fields (name/school/date) | task | text check | PASS / FAIL |
| external run (hardware/API/deploy) | task | run id / bitstring / URL | PASS / BLOCKED |
| submission limit / account / quota | platform | checked value | PASS / BLOCKED |

Every row must be PASS before `DONE`. If a row cannot be satisfied, mark it BLOCKED and stop; do not build a substitute.

## 1. Classify

| Lane | Signals | Budget | Gates |
|---|---|---|---|
| L0 | Question, lookup, explanation | ≤2 calls | Answer directly |
| L1 | 1 file, reversible, low risk, no user-data writes | ≤8 turns | 1 targeted check |
| L2 | Multi-file, feature, data batch, bulk file writes | ≤40 turns/phase | Milestone + final check + delivery gate if a document is delivered |
| L3 | Irreversible, production, money, publish, or formal deliverable with external validation | Soft cap 80/phase | Full process + delivery gate + independent review |

State the lane in one line. If unsure L1/L2 → L2. Bulk data writes → L2; irreversible → L3. A formal PDF/PPT/DOCX with a template or external run uses the delivery gate even at L2.

### Budgets for large tasks

Budgets are per **phase**, not per task. Split large work into milestones; each milestone gets its own subset of the requirements matrix and its own phase budget. The total task budget is `phases × phase budget`; split before extending.

At 80% of a phase budget, run a checkpoint:

- phase matrix on track → continue;
- phase matrix not on track → split the phase, promote the lane, or extend once with a written reason (what remains, why it cannot split, new budget);
- harness step cap reached → treat it as a phase boundary, write `HANDOFF.md` with completed/remaining rows and the next command, then resume in a new run.

Budget exhaustion is **not** BLOCKED. BLOCKED means an external dependency is missing. Never silently grind past a budget, and never stop mid-deliverable without a handoff.

Count turns from the harness step indicator or session stats. If the harness does not expose a count, use a proxy: tool-call batches + wall time, label it `estimated`, and apply a 1.5× margin. Never present a self-estimate as exact.

A phase may overrun only with a written EXTEND/SPLIT decision. Completion and acceptance beat the budget; silent grinding and incomplete delivery are the only failures.

## 2. DONE

`DONE` = every requirements-matrix row PASS + acceptance command passes. For multi-phase tasks, DONE is per phase; the whole task is done only when every phase's rows pass. No row, no done. Do not substitute "tests pass" for "deliverable accepted".

## 3. Recon in one batch

Collect in one turn, parallel where possible:

- tree/glob of the relevant directories
- entry point, config, dependency manifest
- existing test/lint/build command
- one real example of the expected input/output
- if a template exists, parse it first: `template_spec.py` for docx, or read sections/images/placeholders directly
- external dependencies: account, license, quota, API key

Missing external dependency → BLOCKED. If you cannot ask (subagent/unattended), write `BLOCKED.md` with: what is done, what is missing, the exact blocker, the next action. Deliver everything that does not depend on it; never mark a blocked row PASS.

## 4. Execute in batches

- Group edits by file or module; make independent edits in one turn.
- Prefer one script that processes all items over N one-item runs.
- Cache expensive artifacts (OCR, parsing, extraction) to disk, keyed by input hash.
- For UI/docs, render once and inspect once; do not re-render for every tweak if a text check suffices.

## 5. Verify at milestones

- During iteration: narrowest check only (single test, one file, one page).
- At a milestone: run the done command once.
- On failure: read the actual error, form one hypothesis, fix, rerun the narrow check.
- Two-strike: same failure twice → stop, gather evidence, change the approach. Do not "try again".
- Final: run the done command fresh and report the exact output. No claim without evidence.
- Trust text edits; never trust a generated PDF/PPTX/DOCX without rerunning its gate.

## 6. Delivery gate (documents, PDF, PPT)

Text extraction is not enough.

```bash
# derive headings/placeholders/images from the template
python skills/lean-run/template_spec.py answer_template.docx

# mechanical gate
python skills/lean-run/delivery_check.py answer.pdf \
  --min-pages 2 \
  --heading "问题建模" --heading "QUBO" --heading "代码实现" --heading "提交结果" \
  --text "5.5" --min-images 3 --forbid "________"
```

Then render pages/slides to PNG and inspect visually:

- Check the template: cover, section order, fonts, page/slide limit.
- Check figures: required count, captions, legibility. Default to one pipeline/architecture figure + one results/comparison chart unless the task says text-only. `delivery_check.py` counts raster images; for vector figures, use a caption `--text` check or inspect visually.
- Scan placeholders: `________`, `TODO`, `TBD`, `XXX`, empty name/school/date.
- Check Chinese/Unicode glyphs render (no tofu / U+FFFD).
- Fix before declaring done.

## 7. Subagent economics

Dispatch only if:

- the work is independent and would take ≥15 minutes serial, or
- a broad bounded search would flood your context.

Rules: max 2 parallel; one brief file in, one report file out; specify the model; no per-task reviewer/fixer chain. Small tasks: do them yourself.

## 8. Long jobs

If a command may exceed 90 seconds:

- start it in the background with output redirected to a log
- prefer one blocking wait with a timeout; poll only when you have other work
- do not hold a turn open waiting
- record the command/PID so status can be checked

## 9. Context hygiene

- Grep before read; read ranges, not whole files.
- Never re-read a file you just edited; trust the text edit result, but not a generated artifact.
- Keep a scratch file for facts (paths, schema, decisions) instead of repeating tool calls.
- Redirect long outputs to files; read only the relevant lines.
- Do not paste accumulated history into subagent prompts; point to files.

## Anti-patterns

| Don't | Do |
|---|---|
| Text-only PDF for a template/visual task | Render and check template/figures |
| Substitute a local solver for a required external run | Mark BLOCKED; get access |
| Stop at technical PASS with placeholders | Run the requirements matrix |
| Stop early because the budget isn't exhausted | Stop when the matrix is all PASS |
| Treat "lean" as "less scope" | Cut ceremony, not deliverables |
| Re-render/recheck a generated artifact after every text edit | Recheck after the final rebuild, not mid-edit |

## Quality floor

Never trade away: money/auth/permission checks, destructive-write confirmation, data-loss prevention, final verification evidence, template/format compliance for formal deliverables.

## Measure

Track turns, step minutes, and **first-pass acceptance**:

```bash
python skills/lean-run/measure.py --days 7 --limit 10 --include-children
python skills/lean-run/measure.py --all --limit 10 --no-titles
```

Turns and step minutes are the cost metrics; tool/reasoning shares are diagnostic. A fast draft that is rejected is not a win: log `accepted_first_pass: yes/no` and `rework_turns` in the benchmark log. Do not claim a speed win until the rework is included.

## Reporting

- One line for lane and plan.
- One line per milestone with the exact command and result.
- Final: what changed, requirements-matrix status, evidence, residual risks. No narration.
