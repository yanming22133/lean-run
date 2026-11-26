# Lean Run

**面向编码 Agent 的“最快通过验收”执行技能。**

[English](README.md) | **简体中文**

Lean Run 是一个很小的执行技能，适用于 OpenCode、Codex、Claude Code 等 Agent。它砍掉的是仪式感，不是交付范围：更少的重复读取、更少的重复运行、更少的来回交接，同时保留防止返工的需求矩阵。

## 为什么需要它

大多数 Agent 变慢不是“思考”慢，而是回合太多。每多一个回合，就要重读上下文、等一次工具结果。但如果只优化回合数，很容易产出一份“很快但会被退回”的草稿：模板章节缺失、没有图、姓名占位符没填，或者任务要求真机运行时拿本地结果替代。

Lean Run 优化的是唯一重要的指标：**从开始到交付被接受的时间**。

## 它做什么

- **先建需求矩阵。** 每个交付物、模板章节、图、身份字段、外部运行和提交限制都占一行：`需求 | 来源 | 证据 | 状态`。没有矩阵，不算 DONE。
- **四个 Lane。** L0 问答、L1 单文件、L2 多文件、L3 不可逆或需要外部验证的正式交付。只在高风险处上重流程。
- **交付闸门。** 解析模板、渲染页面、检查图/章节/占位符，并跑机械化的 PDF 检查。
- **BLOCKED 协议。** 如果真机、账号、License 或外部运行拿不到，标记 BLOCKED 并停下；无人值守时写 `BLOCKED.md`，只交付不依赖它的部分。
- **预算优先级。** 预算是上限，不是目标；预算用完但矩阵没完成 = BLOCKED 报告，不是硬磨。
- **可测量。** 记录回合和步进时间；基准日志记录首次验收率，返工要计入速度成本。

## 安装（OpenCode）

```powershell
# 0. 可选工具（PDF/DOCX 检查）
python -m pip install -r requirements.txt

# 1. 技能
Copy-Item -Recurse -Force .\skills\lean-run "$HOME\.config\opencode\skills\lean-run"

# 2. 命令
Copy-Item -Force .\commands\lean.md "$HOME\.config\opencode\commands\lean.md"

# 3. 全局规则：把 AGENTS.example.md 合并进
#    $HOME\.config\opencode\AGENTS.md
```

如果目标目录已经存在，`Copy-Item -Recurse` 可能产生嵌套的 `lean-run\lean-run`；请复制目录内容，或先删掉旧目录。

重启会话或新开一个会话。`/lean <任务>` 可以强制走精益路径；技能也会在多文件、正式交付、外部运行类任务上自动触发。

### 其他 Agent

- **Codex / Claude Code：** 把 `skills/lean-run` 复制到对应 Agent 的技能目录，并把 `AGENTS.example.md` 合并进项目或全局指令文件。技能本身是纯 Markdown，只有 `measure.py` 是 OpenCode 专用。

## 使用

```text
/lean 给报表页加一个 CSV 导出
```

Agent 会先说明 Lane，写出需求矩阵，然后开始执行。对于文档类交付，它会在宣布完成前跑交付闸门。

## 交付检查器

```bash
# 1. 从模板提取章节/占位符/图片
python skills/lean-run/template_spec.py answer_template.docx

# 2. 机械化检查
python skills/lean-run/delivery_check.py answer.pdf \
  --min-pages 2 \
  --heading "问题建模" --heading "方法" --heading "结果" \
  --text "42.0" --min-images 2 --forbid "________"
```

PowerShell 里用反引号续行，或把命令写成一行。

它能抓出：章节缺失或顺序错误、图缺失、占位符没填、页数不对、关键结果缺失、Unicode 损坏。模板和版式质量仍需要渲染后目检。图片计数只覆盖嵌入的位图；矢量图请用图注 `--text` 检查，或目检。`template_spec.py` 把模板直接变成检查参数，这是最直接防止第 3 轮那种返工的一步。

## 基准测试（作者自测，n=3）

下面的时间是到**第一版产物**，不是到验收通过。第 3 轮只用于展示成本，**不是速度结论**。

| 轮次 | 任务 | control | lean | 首次验收 |
|---|---|---|---:|---|
| 1 | CSV 归一化 + 测试 | 19 回合 / 1.97 分钟 | 8 / 0.86 分钟 | 两边通过 |
| 2 | Excel 对账，5 个 sheet | 19 / 3.68 分钟 | 9 / 1.32 分钟 | 两边通过 |
| 3 | QUBO 推荐 + 正式 PDF | 80 / 10.87 分钟（两轮，撞步数上限） | 24 / 3.09 分钟 | 两边未通过* |

\* 第 3 轮技术上是正确的，但第一次交付没通过“交付合同”：PDF 没用提供的模板、没有图；control 也需要续跑才补上 PDF。重建成本没有算进 24 回合。这正是 Lean Run 后来加入需求矩阵和交付闸门的原因；**新闸门还没有在第 3 轮上重新验证过**。教训是：**快但被退回的草稿不算赢。**

说明：单机、单模型、小样本。数字只作方向参考，不是保证值。详细数据见 [`benchmarks/2026-11-26.md`](benchmarks/2026-11-26.md)。

## 设计原则

1. 回合是成本，但验收才是目标。
2. 砍仪式，不砍范围。
3. 模板优先；渲染检查，不要只提取文字。
4. 停在需求矩阵全部 PASS 时，不是停在预算用完时。
5. 绝不伪造外部运行结果。

## License

MIT
