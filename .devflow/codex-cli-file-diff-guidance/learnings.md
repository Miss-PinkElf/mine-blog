# 经验记录

## 2026-07-16：Codex CLI 内联差异依赖编辑路径

- 现象：通过 PowerShell 的 `Set-Content`、`Add-Content` 等 Shell（命令行）命令写入文件时，Codex CLI 通常只展示命令输出，不会保证显示 `Added` / `Edited`。
- 原因：补丁编辑（apply_patch）提供结构化的文件和行级变更；Shell 命令的副作用不具备同等的结构化展示信息。
- 应对：在 `AGENTS.md` 约束普通文本编辑优先使用 `apply_patch`；确需 Shell 时展示目标文件的 Git 差异（git diff），但不承诺界面效果。
