# Proposal · GPT Image CLI 工具链

## 背景

需要在本地稳定调用 `shell.wyzlab.ai` 的 OpenAI 兼容接口生成图片，并形成可维护的 **自包含 Skill** 与过程记录。

**协议（2026-07-17）**：主路径为 **Chat Completions**（`/v1/chat/completions`），不再以 Responses 为 skill 主协议。

## 目标

1. 提供可配置、可重试、可中断的文生图 / 图生图 CLI（Skill）
2. 默认文件化提示词与本地密钥（skill 同级 `.env`）
3. 结果可预测地落盘到 skill 内 `gen-images/`
4. 后续支持尺寸/比例/质量控制（T7，Chat 适配）
## 用户故事

1. 作为开发者，我编辑 `prompt-image.md` 后执行脚本，即可得到 png。
2. 作为开发者，网络/524 失败时脚本自动重试，不必手工循环。
3. 作为开发者，我按 Ctrl+C 应立即停止，而不是继续重试。
4. 作为开发者，我希望指定竖图/方图比例，而不是总是 `auto`。

## 范围

### In

- bash CLI + env（skill 自包含）
- Chat Completions 文生图 / 图生图（`--image`）
- 重试、中断、流式解码 / URL 下载、落盘命名、RESULT
- size / quality / ratio（P2 / T7，第一版）
### Out

- Web UI
- 多模型路由平台化
- 官方计费/用量面板

## 成功指标

- 一次配置后，单命令出图成功率可接受（允许重试）
- 关键失败路径有明确中文错误
- 密钥与大体量响应不进入 git

## 状态

- MVP：已实现
- P2 尺寸控制：待 tasks 实施（T7 · 须 Chat 适配）
- 2026-07-16：图文同传（T11）+ JSON 回退（T13）+ 双 skill 同步（T14）已完成并通过实测
- 2026-07-17：主协议切换 Chat Completions（T16）已完成；文生图/图生图/大参考图实测通过