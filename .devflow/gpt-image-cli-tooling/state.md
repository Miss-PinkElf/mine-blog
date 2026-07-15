# State · gpt-image-cli-tooling

- **阶段**：Close / Handoff（本会话收尾，2026-07-16）
- **路径**：Heavy
- **本轮已交付（第二版增量）**：
  - 图文同传：`--image` / `-i`，多模态 `input_text`+`input_image`，`action=edit`
  - JSON 回退：jq → node(`lib/json_codec.cjs`) → python(`lib/json_codec.py`)
  - RESULT：`mode` / `json_backend` / `source_image`
  - 双目录：`.claude/skills/gpt-image-generate/`（真相源）↔ `.codex/skills/gpt-image-generate/`
- **Verify**：node 回退路径实测 HTTP 200；`gen-images/2026-07-16-00-22-25.png`（约 1.67MB，~74s）
- **第一版保留**：纯文生图、重试、中断、流式 base64、默认 `gpt-image-2`
- **下轮优先**：T7 size/ratio/quality；T8 失败路径抽检
- **明确延期**：异步 task、站点 UI、纯 aspect_ratio 官方字段（`deferred/`）
- **阻塞**：无
- **最新 handoff**：`handoffs/2026-07-16-001-image-text-session-close.md`
- **下次入口**：`NEXT-SESSION-PROMPT-gpt-image-cli-tooling.md`
