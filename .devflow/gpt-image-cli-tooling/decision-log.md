# Decision Log · 决策记录

## 2026-07-15 · 启用独立 mission + 重型路径

- **决策**：新建 mission `gpt-image-cli-tooling`，走 devflow 重型路径
- **原因**：用户明确要求「用 devflow 记录 + 重型流程」；能力会持续扩展（尺寸/比例/质量/可能异步）
- **状态**：已生效

## 2026-07-15 · 协议选型：Responses + image_generation 工具

- **决策**：不优先走 `/v1/images/generations`，而走 `/v1/responses` + `tools: [{type:"image_generation", action:"generate"}]`
- **原因**：用户指定接口协议为 OpenAI Responses；中转实测返回标准 `image_generation_call`
- **状态**：已生效

## 2026-07-15 · 配置与提示词输入

- **决策**：
  - Key/BaseURL/Model：`scripts/.env` 自动加载，shell export 可覆盖
  - 默认提示词：`scripts/prompts-images/prompt-image.md`（不存在/空则失败）
- **状态**：已生效

## 2026-07-15 · 落盘与命名

- **决策**：输出到 `scripts/gen-images/`；文件名 `yyyy-mm-dd-hh-mm-ss.png`；重名追加随机数
- **状态**：已生效

## 2026-07-15 · 可靠性：全错误重试 + 可中断

- **决策**：最多重试 5 次（共 6 次尝试）；curl/HTTP/解析/解码失败均重试；Ctrl+C 立即退出且不重试
- **原因**：中转常见 524；同时避免「中断被当成失败继续重试」
- **状态**：已生效

## 2026-07-15 · 大图解码策略

- **决策**：禁止 `B64="$(jq ...)"` 整段进 bash；改为 `jq | base64 -d` 流式落盘
- **原因**：base64 数 MB 时 shell 变量极慢；用户误解为解析卡死
- **状态**：已生效

## 2026-07-15 · 尺寸控制（待实现）

- **决策（方向）**：官方无独立 ratio-only 参数；用 `size: "宽x高"` 表达比例；`auto` 为当前默认
- **状态**：待 Spec / Apply

## 2026-07-15 · 封装为 Claude Skill（自包含）

- **决策**：`.claude/skills/gpt-image-generate/` **完全自包含**；`run.sh` 与 `.env`/`gen-images` 同级；**不**依赖仓库 `scripts/generate-image.sh`
- **要点**：
  - 缺 `jq` 必须提示安装
  - 提示词：用户给出或 agent 扩写
  - 成功汇报：耗时、大小、路径（`---RESULT---`）
- **状态**：已生效

## 2026-07-15 · 默认模型 gpt-image-2

- **决策**：`MODEL="${OPENAI_MODEL:-gpt-image-2}"`（skill + 仓库脚本一致）
- **原因**：与用户 REST Client / 中转习惯一致；比默认 gpt-5.4 调度路径更直观
- **状态**：已生效

## 2026-07-15 · generate-image.http 仅本机

- **决策**：从 git 取消跟踪并 ignore；本地文件保留
- **原因**：易含 API Key；用户已禁用相关 key
- **状态**：已生效
