# Lean Run

**面向编码 Agent 的“最快通过验收”执行技能。**

[English](README.md) | **简体中文**

Lean Run 是一个很小的执行技能，适用于 OpenCode、Codex、Claude Code 等 Agent。它砍掉的是仪式感，不是交付范围：更少的重复读取、更少的重复运行、更少的来回交接，同时保留防止返工的验收清单。

## 为什么需要它

大多数 Agent 变慢不是“思考”慢，而是回合太多。每多一个回合，就要重读上下文、等一次工具结果。但如果只优化回合数，很容易产出一份“很快但会被退回”的草稿：模板章节缺失、没有图、姓名占位符没填，或者任务要求真机运行时拿本地结果替代。

Lean Run 优化的是唯一重要的指标：**从开始到交付被接受的时间**。

## 它做什么

- **先定验收合同。** 在选 Lane 之前，先提取交付物、模板、图表、外部运行、身份字段和提交限制。
- **四个 Lane。** L0 问答、L1 单文件、L2 多文件、L3 不可逆/正式交付。只在高风险处上重流程。
- **DONE 是清单，不是一条命令。** 技术通过 + 格式 + 模板 + 占位符 + 外部证据 + 提交限制。
- **模板优先侦察。** 先解析提供的 docx/pptx/xlsx，再动手。
- **交付闸门。** 渲染页面，检查图、章节、占位符，并跑机械化的 PDF 检查。
- **外部依赖闸门。** 如果任务要求真机、账号、License 或外部运行而当前拿不到，先停下来问，绝不用本地结果替代后说“完成”。
- **可测量。** 记录回合、步进时间和首次验收率；返工要计入速度成本。

## 安装（OpenCode）

```powershell
# 1. 技能
Copy-Item -Recurse .\skills\lean-run "$HOME\.config\opencode\skills\lean-run"

# 2. 命令
Copy-Item .\commands\lean.md "$HOME\.config\opencode\commands\lean.md"

# 3. 全局规则：把 AGENTS.example.md 合并进
#    $HOME\.config\opencode\AGENTS.md
```

重启会话或新开一个会话。`/lean <任务>` 可以强制走精益路径；技能也会在出现效率、验收、返工等关键词时自动触发。

### 其他 Agent

- **Codex / Claude Code：** 把 `skills/lean-run` 复制到对应 Agent 的技能目录，并把 `AGENTS.example.md` 合并进项目或全局指令文件。技能本身是纯 Markdown，只有 `measure.py` 是 OpenCode 专用。

## 使用

```text
/lean 给报表页加一个 CSV 导出
```

Agent 会先说明 Lane，写出 ACCEPT 和 DONE 清单，然后开始执行。对于文档类交付，它会在宣布完成前跑交付闸门。

## 交付检查器

```bash
python skills/lean-run/delivery_check.py answer.pdf \
  --min-pages 2 \
  --heading "问题建模" --heading "方法" --heading "结果" \
  --text "42.0" --min-images 2 --forbid "________"
```

它能抓出：章节缺失、图缺失、占位符没填、页数不对、关键结果缺失。模板和版式质量仍需要渲染后目检。

## 基准测试（作者自测，n=3）

| 轮次 | 任务 | control | lean | 首次验收 |
|---|---|---|---:|---|
| 1 | CSV 归一化 + 测试 | 19 回合 / 1.97 分钟 | 8 / 0.86 分钟 | 两边通过 |
| 2 | Excel 对账，5 个 sheet | 19 / 3.68 分钟 | 9 / 1.32 分钟 | 两边通过 |
| 3 | QUBO 推荐 + 正式 PDF | 80 / 10.87 分钟（两轮，撞步数上限） | 24 / 3.09 分钟 | 两边未通过* |

\* 第 3 轮技术上是正确的，但第一次交付没通过“交付合同”：PDF 没用提供的模板、没有图；control 也需要续跑才补上 PDF。这正是 Lean Run 后来加入交付闸门的原因。教训是：**快但被退回的草稿不算赢。**

说明：单机、单模型、小样本。百分比只作方向参考，不是保证值。详细数据见 [`benchmarks/2026-11-26.md`](benchmarks/2026-11-26.md)。

## 设计原则

1. 回合是成本，但验收才是目标。
2. 砍仪式，不砍范围。
3. 模板优先；渲染检查，不要只提取文字。
4. 停在验收清单完成时，不是停在预算用完时。
5. 绝不伪造外部运行结果。

## License

MIT
