# Lean Run

**Fastest time to accepted delivery for coding agents.**

**English** | [简体中文](README.zh-CN.md)

Lean Run is a small execution skill for OpenCode, Codex, Claude Code, and similar agents. It cuts ceremony, not scope: fewer redundant reads, fewer repeat runs, fewer hand-offs — while keeping the requirements matrix that prevents rework.

## Why

Most agent slowdowns are not "thinking" — they are turns. Every extra turn re-reads the context and waits for a tool. But optimizing turns alone produces fast drafts that get rejected: missing template sections, no figures, unfilled placeholders, or a local result where the task requires a real run.

Lean Run optimizes the only metric that matters: **time to an accepted deliverable**.

## What it does

- **Requirements matrix first.** Every deliverable, template section, figure, identity field, external run, and submission limit gets a `requirement | source | evidence | status` row. No row, no done.
- **Four lanes.** L0 answer, L1 single-file, L2 multi-file, L3 irreversible or formal deliverable with external validation. Heavy process only where it pays.
- **Delivery gate.** Parses the template, renders pages, checks figures/sections/placeholders, and runs a mechanical PDF checker.
- **BLOCKED protocol.** If hardware, an account, a license, or a real-machine run is unavailable, mark the row BLOCKED and stop. Unattended agents write `BLOCKED.md` and deliver only the independent parts.
- **Budget precedence.** A budget is a ceiling, not a target. Exhausted budget + incomplete matrix = BLOCKED report, not silent grinding.
- **Measurement.** Tracks turns and step time; the benchmark log records first-pass acceptance, so rework counts against speed.

## Install (OpenCode)

```powershell
# 0. optional tools (PDF/DOCX checks)
python -m pip install -r requirements.txt

# 1. skill
Copy-Item -Recurse -Force .\skills\lean-run "$HOME\.config\opencode\skills\lean-run"

# 2. command
Copy-Item -Force .\commands\lean.md "$HOME\.config\opencode\commands\lean.md"

# 3. global rules: merge AGENTS.example.md into
#    $HOME\.config\opencode\AGENTS.md
```

If the destination directory already exists, `Copy-Item -Recurse` can create a nested `lean-run\lean-run`; copy the contents instead or remove the old directory first.

Restart the session or open a new one. `/lean <task>` forces the lean path; the skill also auto-triggers on multi-file, formal-deliverable, and external-run tasks.

### Other agents

- **Codex / Claude Code:** copy `skills/lean-run` into the agent's skills directory and merge `AGENTS.example.md` into the project or global instruction file. The skill is plain Markdown; only `measure.py` is OpenCode-specific.

## Usage

```text
/lean Add CSV export to the report page
```

The agent states the lane, writes the requirements matrix, then works. For a document deliverable, it runs the delivery gate before claiming completion.

## Delivery checker

```bash
# 1. derive headings/placeholders/images from the template
python skills/lean-run/template_spec.py answer_template.docx

# 2. mechanical gate
python skills/lean-run/delivery_check.py answer.pdf \
  --min-pages 2 \
  --heading "Problem" --heading "Method" --heading "Results" \
  --text "42.0" --min-images 2 --forbid "________"
```

On PowerShell, use backticks for line continuation or put the command on one line.

It catches missing or out-of-order sections, missing figures, leftover placeholders, page-count issues, absent key results, and broken Unicode. Visual inspection is still required for template and layout quality. Image count covers embedded raster images; for vector figures, add a caption `--text` check or verify visually. `template_spec.py` turns the template into the check arguments, which is the step that most directly prevents the round-3 failure.

## Benchmark (author-measured, n=3)

Times below are to the **first artifact**, not to acceptance. Round 3 is shown for cost context only; it is **not** a speed claim.

| Round | Task | Control | Lean | First-pass acceptance |
|---|---|---:|---:|---|
| 1 | CSV normalization + tests | 19 turns / 1.97 min | 8 / 0.86 min | both yes |
| 2 | Excel reconciliation, 5 sheets | 19 / 3.68 min | 9 / 1.32 min | both yes |
| 3 | QUBO recommendation + formal PDF | 80 / 10.87 min (two runs, step cap) | 24 / 3.09 min | both no* |

\* Round 3 was technically correct but failed the delivery contract: the first PDF did not use the provided template and had no figures; the control also needed a follow-up. The rebuild cost is not included in the 24 turns. This is why Lean Run now has a requirements matrix and a delivery gate; **the new gate has not yet been re-validated on round 3**. The lesson: a fast draft that is rejected is not a win.

Caveats: single machine, one model, small sample. Treat the numbers as directional, not a guarantee. See [`benchmarks/2026-11-26.md`](benchmarks/2026-11-26.md) for details.

## Design principles

1. Turns are the currency, but acceptance is the objective.
2. Cut ceremony, not scope.
3. Template-first; render, don't just extract text.
4. Stop on an all-PASS requirements matrix, not on an exhausted budget.
5. Never fake an external run.

## License

MIT
