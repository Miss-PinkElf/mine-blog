# devflow CLI Worker

devflow CLI Worker（devflow CLI Worker）用于在 macOS 上启动可见、可介入的 worker 会话。

## 依赖

- macOS
- Node.js
- tmux（tmux）
- Terminal.app 或 iTerm2

## 常用命令

```bash
node .codex/skills/devflow-cli-worker/cli/bin/devflow-worker.mjs start --id research-a --command codex --prompt "把结果写到 result.md"
node .codex/skills/devflow-cli-worker/cli/bin/devflow-worker.mjs start-and-open-in-vscode --id research-a --command codex
node .codex/skills/devflow-cli-worker/cli/bin/devflow-worker.mjs ensure-in-vscode --id macos-worker --command codex
node .codex/skills/devflow-cli-worker/cli/bin/devflow-worker.mjs open-in-vscode --id research-a
node .codex/skills/devflow-cli-worker/cli/bin/devflow-worker.mjs clear research-a
node .codex/skills/devflow-cli-worker/cli/bin/devflow-worker.mjs command research-a "/compact"
node .codex/skills/devflow-cli-worker/cli/bin/devflow-worker.mjs get-info research-a --tail 5
node .codex/skills/devflow-cli-worker/cli/bin/devflow-worker.mjs wait-agent research-a --timeout 1200 --poll 15 --stale 30
node .codex/skills/devflow-cli-worker/cli/bin/devflow-worker.mjs send research-a "继续，并更新 result.md"
node .codex/skills/devflow-cli-worker/cli/bin/devflow-worker.mjs kill research-a
```

macOS VSCode 插件入口（VSCode Extension Entry）会在内置终端中执行：

```bash
node .codex/skills/devflow-cli-worker/cli/bin/devflow-worker.mjs start-in-vscode --id <worker-id> --command codex && tmux attach -t devflow-worker-<worker-id>
```

打开工作区后，插件会自动创建 `devflow worker: macos-worker`，并执行：

```bash
node .codex/skills/devflow-cli-worker/cli/bin/devflow-worker.mjs ensure-in-vscode --id macos-worker --command codex && tmux attach -t devflow-worker-macos-worker
```

已有同名 tmux（tmux）会话且 `cli-session.json` 完整时，`ensure-in-vscode` 直接复用并 attach，不会重启 Codex CLI（Codex CLI）。手动运行 `Start devflow CLI Worker` 用于创建其它 worker id。

普通提示词使用 `send`，它会自行提交。直接执行的 slash 命令使用 `command`；菜单型 slash 命令才使用 `paste` 后读取屏幕，再显式用 `key` 选择。`clear` 只由专用命令处理并验证 Context 100%。

## Session 文件

```text
.devflow/devflow-cli-worker/sessions/<worker-id>/
├── cli-session.json
├── result.md
├── transcript.log
├── screen.txt
└── prompt.md
```

如果 tmux 会话存在但 `cli-session.json` 缺失，或其 worker id、tmux session 名称、相对 session 路径、result 路径与当前 worker 不匹配，CLI 会拒绝 `ensure-in-vscode` 和 `open-in-vscode`，防止把未知会话当作可控 worker。确认该会话已经无用后，手工清理：

```bash
tmux kill-session -t devflow-worker-<worker-id>
```

随后重新运行启动或 attach 命令。CLI 不会自动终止会话，也不会补造 session 附件。

## 当前限制

- Windows 原生、PowerShell（pwsh）、WSL（Windows Subsystem for Linux）不在本轮范围内。
- macOS 真实终端冒烟验证需要在 Mac 上执行。
