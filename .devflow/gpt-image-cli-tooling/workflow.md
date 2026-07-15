# Workflow · GPT Image CLI 工具链

## 路径

**重型路径（Heavy）**：Align → Plan → Spec → Apply → Review/Verify → Close

## 当前阶段

**Apply 部分完成 / 进入正式 Spec 收口与续作规划**

本会话已先完成可用 CLI 实现（逆向于标准顺序的「先做后记」）。现起全部续作强制走重型门禁，不再无 plan/tasks 直接改脚本。

## 目标

在本仓库提供可本地使用的 **OpenAI Responses 协议** 文生图工具链：

- 对接中转 Base URL：`https://shell.wyzlab.ai/v1`
- 使用 `tools: [{ type: "image_generation" }]` 触发 GPT Image 系列
- 提示词文件驱动、自动重试、可中断、结果落盘

## 范围

### 范围内（In Scope）

- `scripts/generate-image.sh` 主流程
- `scripts/.env` / `.env.example` 配置
- `scripts/prompts-images/prompt-image.md` 默认提示词
- `scripts/generate-image.http` REST Client 调试
- 本地产物目录 `scripts/gen-images/`（gitignore）
- 尺寸/质量/比例控制（后续 Spec 任务）
- 文档与 devflow 过程记录

### 范围外（Out of Scope）

- 前端页面内嵌生图 UI
- 官方 OpenAI 直连以外的多供应商抽象
- 异步 task 轮询协议（若中转提供，可进 backlog）

## 里程碑

| 里程碑 | 状态 |
| --- | --- |
| Mission Init | 完成 |
| Align（需求与约束对齐） | 完成（本会话回顾落盘） |
| Plan | 进行中 → 见 `plans/` |
| Spec 三件套 | 待写齐 |
| Apply：可用脚本 MVP | 已完成（实现先于 mission 记录） |
| Apply：尺寸/比例控制 | 未开始 |
| Verify / Close 本轮 | 未开始 |

## 关键文档

| 类型 | 路径 |
| --- | --- |
| Origin | `origin.md` |
| State | `state.md` |
| Plan | `plans/2026-07-15-gpt-image-cli-align-plan.md` |
| Spec | `spec/proposal.md` / `design.md` / `tasks.md` |
| Decisions | `decision-log.md` |
| Bugs | `bug-log.md` |

## 下一步

1. 补齐重型 Spec 三件套（proposal / design / tasks）
2. 按 tasks 推进「size/ratio/quality 可控」等剩余能力
3. 验证：真实调用成功落盘 + Ctrl+C 可中断 + 重试策略
