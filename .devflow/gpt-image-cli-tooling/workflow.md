# Workflow · GPT Image CLI 工具链

## 路径

**重型路径（Heavy）**

## 当前阶段

**Close / Handoff（2026-07-17）** → 下轮从 **Apply T7（Chat 适配）** 或 **Verify T8** 恢复

## 目标

本地可用的 GPT Image **文生图 / 图生图**工具链（中转 `shell.wyzlab.ai`），以自包含 Skill 为主入口（Claude + Codex 双目录）。

**现行协议（2026-07-17 起）**：OpenAI **Chat Completions**（`POST /v1/chat/completions`），**不再**以 `/v1/responses` + `image_generation` 为 skill 主路径。

## 范围

### 已交付

| 版本 | 内容 |
| --- | --- |
| 第一版 | 纯文生图、重试、中断、RESULT、默认 gpt-image-2、自包含 skill（原 Responses） |
| 第二版 | `--image` 图文同传；jq/node/python JSON 回退；双目录同步（原 Responses 多模态） |
| 第三版（本轮） | **协议切换 Chat Completions**；Markdown URL/data URL 落盘；printf / has 边界修复；真实 OC 参考图验证 |

### 下轮优先（仍属本 mission，未延期）

- T7：`--size` / `--quality` / `--ratio`（**第一版实现即可**；须适配 Chat：写入 messages 约定 / 可选顶层字段，不再写 `tools[0]`）
- T8：无 key / 空 prompt / Ctrl+C 等失败路径正式抽检

### 明确延期（`deferred/`）

- 异步 task 轮询
- 站点内嵌生图 UI
- 仅官方 aspect_ratio、不传 size
- 仓库 `scripts/generate-image.sh` 同步迁 Chat（或废弃双轨）— 见 backlog，非本轮

### Backlog（轻量想法，非承诺）

- 见 `backlog.md`（meta.json、批量出图、快捷入口、scripts 双轨）

## 里程碑

| 里程碑 | 状态 |
| --- | --- |
| 第一版 Skill | 完成 |
| 图文同传 + JSON 回退 + 双目录 | 完成（2026-07-16） |
| Chat 协议主路径 | 完成（2026-07-17） |
| T7 尺寸比例质量 | 未开始（需 Chat 适配） |
| T8 Verify 补强 | 未开始 |
| 本会话 Close/Handoff | 完成 |

## 关键路径

| 类型 | 路径 |
| --- | --- |
| Skill 真相源 | `.claude/skills/gpt-image-generate/` |
| Skill Codex | `.codex/skills/gpt-image-generate/` |
| Align / Plan | `plans/2026-07-16-image-text-jq-*.md`（协议描述已过时，以 skill 与本 workflow 为准） |
| Spec | `spec/`（design 已随本轮协议更新） |
| Handoff | `handoffs/2026-07-17-001-chat-protocol-session-close.md` |

## 下一步（新会话）

1. 读 `state.md` + `checkpoints.md`
2. 按 `NEXT-SESSION-PROMPT-gpt-image-cli-tooling.md` 做 **T7（Chat 适配第一版）**
3. 再 **T8**
