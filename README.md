# Lean Run

**Fastest time to accepted delivery for coding agents.**

**English** | [简体中文](README.zh-CN.md)

Lean Run is a small execution skill for OpenCode, Codex, Claude Code, and similar agents. It cuts ceremony, not scope: fewer redundant reads, fewer repeat runs, fewer hand-offs — while keeping the acceptance checklist that prevents rework.

## Why

Most agent slowdowns are not "thinking" — they are turns. Every extra turn re-reads the context and waits for a tool. But optimizing turns alone produces fast drafts that get rejected: missing template sections, no figures, unfilled placeholders, or a local result where the task requires a real run.

Lean Run optimizes the only metric that matters: **time to an accepted deliverable**.

## What it does

- **Acceptance contract first.** Extracts deliverables, template, figures, external runs, identity fields, and submission limits before choosing a lane.
- **Four lanes.** L0 answer, L1 single-file, L2 multi-file, L3 irreversible/formal deliverable. Heavy process only where it pays.
- **DONE as a checklist.** Technical pass + format + template + placeholders + external evidence + submission limits.
- **Template-first recon.** Parses the provided docx/pptx/xlsx before writing.
- **Delivery gate.** Renders pages, checks figures/sections/placeholders, and runs a mechanical PDF checker.
- **External dependency gate.** If hardware, an account, a license, or a real-machine run is required and unavailable, stop and ask — never substitute a local result and call it done.
- **Measurement.** Tracks turns, step time, and first-pass acceptance; rework is counted against speed.

## Install (OpenCode)

```powershell
# 1. skill
Copy-Item -Recurse .\skills\lean-run "$HOME\.config\opencode\skills\lean-run"

# 2. command
Copy-Item .\commands\lean.md "$HOME\.config\opencode\commands\lean.md"

# 3. global rules: merge AGENTS.example.md into
#    $HOME\.config\opencode\AGENTS.md
```

Restart the session or open a new one. `/lean <task>` forces the lean path; the skill also auto-triggers on efficiency and acceptance language.

### Other agents

- **Codex / Claude Code:** copy `skills/lean-run` into the agent's skills directory and merge `AGENTS.example.md` into the project or global instruction file. The skill is plain Markdown; only `measure.py` is OpenCode-specific.

## Usage

```text
/lean Add CSV export to the report page
```

The agent states the lane, writes the ACCEPT and DONE checklists, then works. For a document deliverable, it runs the delivery gate before claiming completion.

## Delivery checker

```bash
python skills/lean-run/delivery_check.py answer.pdf \
  --min-pages 2 \
  --heading "Problem" --heading "Method" --heading "Results" \
  --text "42.0" --min-images 2 --forbid "________"
```

It catches missing sections, missing figures, leftover placeholders, page-count issues, and absent key results. Visual inspection is still required for template and layout quality.

## Benchmark (author-measured, n=3)

| Round | Task | Control | Lean | First-pass acceptance |
|---|---|---|---:|---|
| 1 | CSV normalization + tests | 19 turns / 1.97 min | 8 / 0.86 min | both yes |
| 2 | Excel reconciliation, 5 sheets | 19 / 3.68 min | 9 / 1.32 min | both yes |
| 3 | QUBO recommendation + formal PDF | 80 / 10.87 min (two runs, step cap) | 24 / 3.09 min | both no* |

\* Round 3 was technically correct but failed the delivery contract: the first PDF did not use the provided template and had no figures; the control also needed a follow-up. This is exactly why Lean Run now has a delivery gate. The lesson: a fast draft that is rejected is not a win.

Caveats: single machine, one model, small sample. Treat the percentages as directional, not a guarantee. See [`benchmarks/2026-11-26.md`](benchmarks/2026-11-26.md) for details.

## Design principles

1. Turns are the currency, but acceptance is the objective.
2. Cut ceremony, not scope.
3. Template-first; render, don't just extract text.
4. Stop on a completed checklist, not on an exhausted budget.
5. Never fake an external run.

## License

MIT
