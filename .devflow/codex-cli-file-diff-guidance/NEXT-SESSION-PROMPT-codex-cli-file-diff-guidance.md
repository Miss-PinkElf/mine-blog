# 下一会话提示词：Codex CLI 文件变更展示规范

请先恢复并核对 mission `codex-cli-file-diff-guidance`：

1. 先读取 `.devflow/codex-cli-file-diff-guidance/state.md` 与 `.devflow/codex-cli-file-diff-guidance/checkpoints.md`。
2. 本 mission 已由提交 `51035b8` 完成并关闭；没有未完成任务、未讨论议题或明确延期项。
3. 若需要理解决策，再读取 `.devflow/codex-cli-file-diff-guidance/handoffs/2026-07-16-001-close.md`、`decision-log.md` 与 `learnings.md`。
4. 仅在需要追溯原始输入或旧状态时，读取 `origin.md` 与 `state-history.md`。
5. 如果新需求与本 mission 无关，请创建新的 DevFlow（DevFlow）mission，不要混入本目录。

注意：`AGENTS.md` 已规定普通文本编辑优先使用补丁编辑（apply_patch）；必要 Shell（命令行）写入后展示目标文件的 Git 差异（git diff），但该方式不保证 CLI 渲染 `Added` / `Edited`。
