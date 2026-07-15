# State · gpt-image-cli-tooling

- **阶段**：Close / Handoff（本轮会话收尾）；第一版 CLI + Skill 已可用
- **路径**：Heavy
- **本轮提交**（相关）：`f76cec2` / `e84276d` / `f35d114` 等（见 development-overview）
- **第一版已完成**：
  - 仓库脚本 `scripts/generate-image.sh`（可保留作对照）
  - **主入口**：自包含 skill `.claude/skills/gpt-image-generate/`（`run.sh` + 同级 `.env`）
  - 默认 model：`gpt-image-2`；重试 5 次；流式解码；Ctrl+C 可强制退出
  - 成功输出 `---RESULT---`（耗时 / bytes / path）
  - `scripts/generate-image.http` **仅本机**（已 untrack + ignore，勿再提交）
- **未做（下轮）**：T7 size/ratio/quality；T8 正式 Verify
- **延期**：见 `deferred/` 与 `backlog.md`
- **阻塞**：无
- **下一步**：新对话按 `NEXT-SESSION-PROMPT-gpt-image-cli-tooling.md`；优先 T7
- **最新 handoff**：`handoffs/2026-07-15-001-session-close.md`
