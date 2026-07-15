---
name: devflow-cli-worker
description: |
  当需要把黑盒 subagent 改成可见、可介入的独立 CLI worker 时使用本技能。适用于用户要求“不要黑盒 subagent”、“开一个可见 worker”、“让主 Agent 操作终端里的 codex/claude”、“多 worker 并行”、“轮询 worker 状态”、“把结果写到 result.md”或在 devflow mission 中分派可观察子任务。本技能指导主 Agent 使用 devflow Worker CLI（devflow Worker CLI）启动、观察、控制、轮询并收回 worker 结果。
---

# devflow CLI Worker

## 适用范围

使用 devflow Worker CLI（devflow Worker CLI）把子任务放进可见、可介入的 macOS tmux（tmux）会话中运行。

本技能默认只覆盖 macOS。Windows 原生、PowerShell（pwsh）、WSL（Windows Subsystem for Linux）和 Windows / WSL VSCode 入口不在本轮范围内。

macOS VSCode 插件（VSCode Extension）安装后，打开工作区会自动创建 `devflow worker: macos-worker` 内置终端（VSCode Integrated Terminal）。该终端使用 `ensure-in-vscode`：已有 `devflow-worker-macos-worker` tmux 会话且 CLI 会话元数据完整时直接 attach，不会启动第二个 Codex CLI（Codex CLI）worker。命令面板的 `Start devflow CLI Worker` 保留给额外 worker id。

## 核心原则

- 保留用户原始提示词（Original Prompt），不要改写。
- 每个 worker 必须有独立 worker id。
- 每个 worker 必须写入自己的 result.md（Result File）。
- 主 Agent 必须轮询观察，不要长时间盲等。
- worker 的长期结论必须回写到当前 devflow mission，不把 session 附件当成唯一真相源。

## 启动流程

1. 选择 worker id，例如 `research-a`。
2. 读取 `references/prompt-template.md`。
3. 组装 prompt，明确写入 result.md 相对路径。
4. 在 VSCode 场景依次运行，以创建新 worker 和新内置终端：

```bash
node .codex/skills/devflow-cli-worker/cli/bin/devflow-worker.mjs start-and-open-in-vscode --id research-a --command codex --prompt "<assembled prompt>"
```

需要在脚本或插件中确保默认 VSCode worker 已启动时，运行：

```bash
node .codex/skills/devflow-cli-worker/cli/bin/devflow-worker.mjs ensure-in-vscode --id macos-worker --command codex
```

如果同名 tmux（tmux）会话存在，但对应的 `cli-session.json` 缺失或其归属字段与 worker 不匹配，CLI 会拒绝复用，且不会自动终止会话或补造元数据。确认该会话不再使用后，可执行：

```bash
tmux kill-session -t devflow-worker-<worker-id>
```

再重试 `ensure-in-vscode` 或 `open-in-vscode`。

需要在 VSCode 中显示已运行的指定 worker 时，运行：

```bash
node .codex/skills/devflow-cli-worker/cli/bin/devflow-worker.mjs open-in-vscode --id research-a
```

该命令只请求插件创建或聚焦 attach 终端；提示词、`/clear`、Bash 命令和轮询继续由 Worker CLI（Worker CLI）直接控制 tmux（tmux）。

## 观察与控制

优先使用轻量轮询：

```bash
node .codex/skills/devflow-cli-worker/cli/bin/devflow-worker.mjs get-info research-a --tail 5
```

Codex CLI（Codex CLI）发送下一步指令时，使用 `send`；它会在同一操作内输入并提交：

```bash
node .codex/skills/devflow-cli-worker/cli/bin/devflow-worker.mjs send research-a "继续执行下一步，并把结论写入 result.md"
```

新开 Codex 对话使用 `clear <worker-id>`；不要再手工组合 `/clear` 与 Enter。

直接执行的 slash 命令使用 `command`，只输入并提交一次：

```bash
node .codex/skills/devflow-cli-worker/cli/bin/devflow-worker.mjs command research-a "/compact"
```

会打开菜单或需要确认的 slash 命令，使用 `paste` 输入命令，读取屏幕后再显式使用 `key` 选择；不要自动发送额外 Enter。

需要等待但不能盲等：

```bash
node .codex/skills/devflow-cli-worker/cli/bin/devflow-worker.mjs wait-agent research-a --timeout 1200 --poll 15 --stale 30
```

## 多 worker 并行

多 worker 并行（Parallel Workers）时，不要同时长阻塞多个 `wait-agent`。

推荐循环读取：

```bash
node .codex/skills/devflow-cli-worker/cli/bin/devflow-worker.mjs get-info worker-a --tail 5
node .codex/skills/devflow-cli-worker/cli/bin/devflow-worker.mjs get-info worker-b --tail 5
```

## 收回结果

读取对应 session 的 result.md，并将有效结论整合回当前任务。

结果路径格式：

```text
.devflow/devflow-cli-worker/sessions/<worker-id>/result.md
```
