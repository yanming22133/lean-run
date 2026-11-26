---
name: lean-run
description: Right-size execution for any task, optimized for fastest time-to-accepted-delivery. Use when starting a multi-step task, when a task is taking too long, or when about to invoke brainstorming/TDD/plan/subagent workflows. Triggers include "任务太久", "效率", "省时间", "少回合", "lean", "fast path", "完美交付", "模板", "验收", "返工", "right-size".
---

# Lean Run

## Principle

Fast means fast to an **accepted** deliverable, not fast to a first draft. Rework is the biggest cost. Lean cuts ceremony, not scope.

## 0. Acceptance contract (before lane)

Extract from the prompt, task file, template, and platform:

- Deliverables: files, formats, names, locations
- Template/style: cover, fonts, section order, page/slide limit
- Visuals: required figures, tables, screenshots
- Evidence: test output, command output, external run IDs (CIM/deploy/API)
- Identity: name/school/date/signature placeholders
- Submission: attempts, deadline, account/quota

Write `ACCEPT = [...]`. If an item is impossible (no account/license/quota), stop and ask **before** building a substitute.

## 1. Classify

| Lane | Signals | Budget | Gates |
|---|---|---|---|
| L0 | Question, lookup, explanation | ≤2 calls | Answer directly |
| L1 | 1 file, reversible, low risk, no user-data writes | ≤8 turns | 1 targeted check |
| L2 | Multi-file, feature, data batch, bulk file writes | ≤40 turns | Milestone + final check |
| L3 | Irreversible, production, money, publish, or formal deliverable with external validation | No cap | Full process + delivery gate |

State the lane in one line. If unsure L1/L2 → L2. Bulk data writes → L2; irreversible → L3. A formal report/PPT/PDF with a template or external run is at least L2, and L3 if external validation is required.

## 2. DONE checklist

`DONE` is a checklist, not a single command:

- [ ] Acceptance command(s) pass
- [ ] Files/formats/names match
- [ ] Template/sections/figures match (if any)
- [ ] Identity placeholders filled
- [ ] External evidence captured (if required)
- [ ] Submission limits/account/quota checked

Use only the applicable items for L0/L1.

## 3. Recon in one batch

Collect in one turn, parallel where possible:

- tree/glob of the relevant directories
- entry point, config, dependency manifest
- existing test/lint/build command
- one real example of the expected input/output
- if a template exists, parse it first: docx sections/images/placeholders, pptx layouts, xlsx sheets
- external dependencies: account, license, quota, API key

Stop as soon as you can act. Do not read whole files; grep first, then read the needed range. Missing external dependency → stop and ask now, not after building a substitute.

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

## 6. Delivery gate (documents, PDF, PPT)

Text extraction is not enough. Run the mechanical gate first:

```bash
python "$HOME/.config/opencode/skills/lean-run/delivery_check.py" answer.pdf \
  --min-pages 2 \
  --heading "问题建模" --heading "QUBO" --heading "代码实现" --heading "提交结果" \
  --text "5.5" --min-images 3 --forbid "________"
```

Then render pages/slides to PNG and inspect visually:

- Check the template: cover, section order, fonts, page/slide limit.
- Check figures: required count, captions, legibility. Default to one pipeline/architecture figure + one results/comparison chart unless the task says text-only.
- Scan placeholders: `________`, `TODO`, `TBD`, `XXX`, empty name/school/date.
- Check Chinese/Unicode glyphs render (no tofu).
- Fix before declaring done.

## 7. Subagent economics

Dispatch only if:

- the work is independent and would take ≥15 minutes serial, or
- a broad bounded search would flood your context.

Rules: max 2 parallel; one brief file in, one report file out; specify the model; no per-task reviewer/fixer chain. Small tasks: do them yourself.

## 8. Long jobs

If a command may exceed 90 seconds:

- start it in the background with output redirected to a log
- continue other work or poll every 30 seconds
- never hold a turn open waiting
- record the command/PID so status can be checked

## 9. Context hygiene

- Grep before read; read ranges, not whole files.
- Never re-read a file you just edited; trust the edit result.
- Keep a scratch file for facts (paths, schema, decisions) instead of repeating tool calls.
- Redirect long outputs to files; read only the relevant lines.
- Do not paste accumulated history into subagent prompts; point to files.

## Anti-patterns

| Don't | Do |
|---|---|
| Run the full suite after every edit | Narrow check during iteration; full at milestone |
| One tool call per turn | Batch independent calls |
| Re-read the same file to "check" | Trust the edit; verify the output |
| Spawn implementer + reviewer per task | One implementer per batch; review at milestone |
| Re-run OCR/parse/render from scratch | Cache by input hash |
| Retry the same failing command | Diagnose after the second failure |
| Text-only PDF for a template/visual task | Render and check template/figures |
| Substitute a local solver for a required external run | Stop and ask; get access |
| Stop at technical PASS with placeholders | Run the DONE checklist |
| Polish before checking the template | Template-first recon |
| Stop early because the budget isn't exhausted | Stop when the checklist is complete |
| Treat "lean" as "less scope" | Cut ceremony, not deliverables |

## Quality floor

Never trade away: money/auth/permission checks, destructive-write confirmation, data-loss prevention, final verification evidence, template/format compliance for formal deliverables. For L3, the full design/TDD/review process applies.

## Measure

Track turns, step minutes, and **first-pass acceptance**:

```bash
# recent baseline / after
python "$HOME/.config/opencode/skills/lean-run/measure.py" --days 7 --limit 10

# full history (may include migrated sessions without parts)
python "$HOME/.config/opencode/skills/lean-run/measure.py" --all --limit 10
```

Turns and step minutes are the primary cost metrics; tool/reasoning shares are diagnostic. A fast draft that is rejected is not a win: count rework turns and log `accepted_first_pass: yes/no` in the benchmark log. Compare before/after on the same 3 representative tasks.

## Reporting

- One line for lane and plan.
- One line per milestone with the exact command and result.
- Final: what changed, evidence, acceptance checklist, residual risks. No narration.
