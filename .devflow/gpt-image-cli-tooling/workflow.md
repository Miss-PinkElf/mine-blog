# Workflow · GPT Image CLI 工具链

## 路径

**重型路径（Heavy）**：Align → Plan → Spec → Apply → Review/Verify → Close

## 当前阶段

**Close / Handoff（本会话）** → 下一会话从 **Apply T7** 或 **Verify T8** 恢复

## 目标（不变）

本地可用的 OpenAI Responses 文生图工具链（中转 `shell.wyzlab.ai`），以 **自包含 Claude Skill** 为主入口。

## 范围（更新后）

### 第一版已交付（In · Done）

- 自包含 skill：`.claude/skills/gpt-image-generate/`
- `run.sh` + 同级 `.env` / `gen-images` / `prompts`
- 仓库旁路脚本：`scripts/generate-image.sh`（非 skill 依赖）
- 重试、中断、流式解码、RESULT 汇报、默认 `gpt-image-2`

### 下一版（In · Pending）

- T7：`--size` / `--quality` / `--ratio`
- T8：失败路径与中断的正式抽检记录

### 范围外 / 延期

- 站点内生图 UI
- 异步 task 轮询（见 deferred）
- 纯 aspect_ratio 官方字段（用 size 映射代替）

## 里程碑

| 里程碑 | 状态 |
| --- | --- |
| Mission Init / Align / Plan / Spec | 完成 |
| Apply：脚本 MVP + 热修 | 完成 |
| Apply：T9 自包含 Skill | 完成 |
| Apply：默认 gpt-image-2 + 中断/超时修复 | 完成 |
| Apply：T7 尺寸比例质量 | **未开始** |
| Verify T8 | **未开始** |
| 本会话 Close/Handoff | **进行中 → 完成** |

## 关键文档

| 类型 | 路径 |
| --- | --- |
| State | `state.md` |
| Handoff | `handoffs/2026-07-15-001-session-close.md` |
| 下次提示 | `NEXT-SESSION-PROMPT-gpt-image-cli-tooling.md` |
| Spec | `spec/tasks.md` |
| Deferred | `deferred/` |

## 下一步（新会话）

1. 读 `state.md` + `checkpoints.md`
2. 按 `spec/tasks.md` 做 **T7**
3. 再做 **T8** Verify
