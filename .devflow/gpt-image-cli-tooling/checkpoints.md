# Checkpoints（仅保留最近 3 条）

## 2026-07-17 · Close / Handoff（Chat 协议切换）

- **阶段**：Close / Handoff
- **已完成**：Skill 主路径改 `POST /chat/completions`；文生图/图生图实测；printf/has 修复；双目录同步；文档收尾
- **未完成**：T7、T8；`scripts/generate-image.sh` 仍为旧协议
- **下一步**：新对话按 NEXT-SESSION-PROMPT 做 T7（Chat 适配）

## 2026-07-16 · Close / Handoff（图文同传会话）

- **阶段**：Close / Handoff
- **已完成**：T11–T15；`--image` 编辑；JSON 回退；双目录；实测出图；文档收尾
- **未完成**：T7、T8
- **下一步**：新对话按 NEXT-SESSION-PROMPT 做 T7

## 2026-07-16 · Apply T11–T15 图文同传 + JSON 回退

- **阶段**：Apply / Verify
- **已完成**：多模态 edit；jq/node/python；RESULT mode；同步 codex；HTTP 200 实测
- **未完成**：T7、T8
