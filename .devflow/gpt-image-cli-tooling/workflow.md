# Workflow · GPT Image CLI 工具链

## 路径

**重型路径（Heavy）**

## 当前阶段

**Close / Handoff（2026-07-16）** → 下轮从 **Apply T7** 或 **Verify T8** 恢复

## 目标

本地可用的 OpenAI Responses **文生图 / 图生图**工具链（中转 `shell.wyzlab.ai`），以自包含 Skill 为主入口（Claude + Codex 双目录）。

## 范围

### 已交付

| 版本 | 内容 |
| --- | --- |
| 第一版 | 纯文生图、重试、中断、RESULT、默认 gpt-image-2、自包含 skill |
| 第二版（本轮） | `--image` 图文同传；jq/node/python JSON 回退；双目录同步 |

### 下轮优先（仍属本 mission，未延期）

- T7：`--size` / `--quality` / `--ratio`
- T8：无 key / 空 prompt / Ctrl+C 等失败路径正式抽检

### 明确延期（`deferred/`）

- 异步 task 轮询
- 站点内嵌生图 UI
- 仅官方 aspect_ratio、不传 size

### Backlog（轻量想法，非承诺）

- 见 `backlog.md`（meta.json、批量出图、快捷入口、是否废弃仓库 scripts 双轨）

## 里程碑

| 里程碑 | 状态 |
| --- | --- |
| 第一版 Skill | 完成 |
| 图文同传 + JSON 回退 + 双目录 | 完成（2026-07-16） |
| T7 尺寸比例质量 | 未开始 |
| T8 Verify 补强 | 未开始 |
| 本会话 Close/Handoff | 进行中 → 完成 |

## 关键路径

| 类型 | 路径 |
| --- | --- |
| Skill 真相源 | `.claude/skills/gpt-image-generate/` |
| Skill Codex | `.codex/skills/gpt-image-generate/` |
| Align / Plan | `plans/2026-07-16-image-text-jq-*.md` |
| Spec | `spec/` |
| Handoff | `handoffs/2026-07-16-001-image-text-session-close.md` |

## 下一步（新会话）

1. 读 `state.md` + `checkpoints.md`
2. 按 `NEXT-SESSION-PROMPT-gpt-image-cli-tooling.md` 做 **T7**
3. 再 **T8**
