# Origin · 原始输入索引

## 定位

记录本 mission 的原始用户诉求与关键上下文来源。可追加，非冻结文件。

## 来源列表

| 序号 | 来源 | 时间 | 用途 | 吸收状态 |
| --- | --- | --- | --- | --- |
| 1 | 对话：对比 Java 注解 vs JS 装饰器 | 2026-07-15 | 无关背景 | 不吸收 |
| 2 | 对话：curl 调用 gpt-image-2 | 2026-07-15 | 明确 Images/Responses 方向 | 已吸收到脚本 |
| 3 | 对话：REST Client image.http | 2026-07-15 | 调试手段 | 已吸收 `generate-image.http` |
| 4 | 对话：Base URL `https://shell.wyzlab.ai/v1` + Responses 协议 + 自备 key | 2026-07-15 | 接口约定 | 已吸收 |
| 5 | 对话：脚本读环境变量 / 建 `.env` | 2026-07-15 | 配置方式 | 已吸收 |
| 6 | 文件：`Response-1784102441750.json` | 2026-07-15 | 真实响应结构样例 | 已吸收解析逻辑（`output[].result`） |
| 7 | 对话：默认读 `prompts-images/prompt-image.md` | 2026-07-15 | 提示词输入 | 已吸收 |
| 8 | 对话：loading/耗时/gen-images/重名随机数/时间戳文件名 | 2026-07-15 | UX 与落盘规则 | 已吸收 |
| 9 | 对话：失败最多重试 5 次（含非 524） | 2026-07-15 | 可靠性 | 已吸收 |
| 10 | 对话：解析慢、Ctrl+C 停不掉 | 2026-07-15 | 性能与信号处理 | 已吸收（流式解码 + 中断退出） |
| 11 | 对话：图片 size 如何定、能否只控比例 | 2026-07-15 | 后续能力 | 待 Spec 任务 |
| 12 | 对话：提交 + 启用 devflow 重型流程 | 2026-07-15 | 过程治理 | 本 mission 启动 |
| 13 | 对话：skill 自包含，env 与 run.sh 同级 | 2026-07-15 | Skill 边界 | 已吸收 |
| 14 | 对话：默认 model 改为 gpt-image-2 | 2026-07-15 | 默认值 | 已吸收 |
| 15 | 对话：收尾 / 新开对话 / 记录延期 | 2026-07-15 | Close+Handoff | 本轮 |
| 16 | 本地：`scripts/generate-image.http`（含 key 调试） | 2026-07-15 | 仅本机 | 已 untrack，勿提交 |
| 17 | 对话：测试图文同传 + 优化 skill | 2026-07-15/16 | 参考图+文字（A）+ jq 可用性（B）+ mission 文档 | 本轮 Align |
| 18 | 实测图文编辑成功（curl + multimodal input） | 2026-07-15 | 协议与失败面证据 | 已吸收 |
| 19 | 用户确认 A+B；Mac 主环境有 jq；完整 devflow | 2026-07-16 | 范围与流程 | 本轮 |
| 20 | 对话：上下文过长，收尾 + commit + handoff | 2026-07-16 | Close 本轮；记录延期/下轮 | 本轮 |

| 17 | 对话：测试图文同传 + 优化 skill | 2026-07-15/16 | 参考图+文字；A+B；完善 mission 文档 | 本轮 Align |
| 18 | 实测：zzz-prompt-debug/origin/优化生成图片脚本/image.png 图文编辑成功 | 2026-07-15 | 协议：input_text+input_image(data URL)；curl 可用；Python urllib 遇 CF 1010 | 已吸收待落地 |
| 19 | 对话：范围 A+B；主环境 Mac（有 jq）；走完整 devflow | 2026-07-16 | 路径：重型；本轮非仅 T7 | 本轮 |
| 20 | 对话：上下文过长，收尾 + commit + handoff | 2026-07-16 | Close 本轮；记录延期/下轮 | 本轮 |
| 21 | 对话：修正 skill，使用 v1 chat 协议，不用 responses | 2026-07-17 | 协议切换 | 已吸收 skill |
| 22 | 对话：先测试再变更；`has` 阈值与 printf 修复 | 2026-07-17 | 质量门禁 | 已吸收 |
| 23 | 参考图：`zzz-prompt-debug/origin/OC/generated/rin-01-global-design.png` | 2026-07-17 | 真实 OC 图生图验证 | 已验证通过 |
| 24 | 对话：上下文过长，收尾 + commit + handoff（本轮） | 2026-07-17 | Close 第三版 | 本轮 |

## 备注

- API Key 仅本机 `.env` / 可选本地 `.http`，禁止提交。
- Skill：`.claude/skills/gpt-image-generate/.env`
- 大体积 `Response-*.json` 与 `gen-images/` 已 gitignore。
