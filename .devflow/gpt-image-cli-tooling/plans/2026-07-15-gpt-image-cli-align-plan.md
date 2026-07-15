# Plan · GPT Image CLI 工具链（重型）

日期：2026-07-15  
Mission：`gpt-image-cli-tooling`  
路径：Heavy

## Align 结论（已对齐）

### 要解决什么

本地一键调用中转站的 **OpenAI Responses + image_generation**，生成图片并落盘；过程可观察、可重试、可中断。

### 已确认约束

| 项 | 结论 |
| --- | --- |
| Base URL | `https://shell.wyzlab.ai/v1`（可 `.env` 覆盖） |
| 协议 | `POST /responses` + `tools.image_generation` |
| 鉴权 | `OPENAI_API_KEY` 本地 `.env`，不入库 |
| 默认提示词 | `scripts/prompts-images/prompt-image.md` |
| 输出 | `scripts/gen-images/yyyy-mm-dd-hh-mm-ss.png` |
| 重试 | 最多 5 次，含非 524 错误 |
| 中断 | Ctrl+C 立即退出、不重试 |
| 尺寸 | 当前 `auto`；用户希望后续能控比例/尺寸 |

### 非目标

- 不做站点内生图 UI（本 mission）
- 不把密钥或大 JSON 响应提交 git

## 实施顺序（含已完成）

### P0 · 可用脚本 MVP（已完成）

1. bash 脚本 + `.env` 加载
2. Responses 请求体与 base64 解析（`output[].result`）
3. gen-images 落盘与命名
4. loading / 耗时
5. 全错误重试 5 次
6. 流式解码 + Ctrl+C 修复

### P1 · 过程治理（本轮）

1. Mission Init 与 origin/decision/bug 记录
2. 本 plan 落盘
3. Spec 三件套：proposal / design / tasks
4. 代码提交（脚本 + mission 文档，排除密钥与产物）

### P2 · 尺寸与质量可控（下一轮 Apply）

1. CLI / `.env` 支持 `size`、`quality`
2. 可选 `--ratio` 映射到常用 size（1:1 / 2:3 / 3:2 等）
3. 请求体写入 `tools[0].size` / `quality`
4. 文档与 help 更新
5. 真实调用验证竖图/方图

### P3 · 体验增强（Backlog）

- 失败时更结构化错误分类
- 可选保存精简 response meta（不含 base64）
- 若中转支持异步，再评估 task 轮询

## 风险

| 风险 | 缓解 |
| --- | --- |
| 524 超时 | 重试；控制 size/quality；提示词别过长 |
| 中转字段差异 | 保留多路径 jq 抽取 + 失败 JSON 落盘 |
| 密钥泄露 | gitignore `.env`；提交前检查 |

## 成功标准

1. `./scripts/generate-image.sh` 在配置正确时能产出 png
2. 无 key / 空提示词文件时明确失败
3. Ctrl+C 可停且不重试
4. 重型 mission 文档可恢复续作
5. （P2）可显式指定 size 或 ratio

## 下一步门禁

- 本 plan 确认后 → 写 `spec/proposal.md`、`design.md`、`tasks.md`
- Spec 就绪后 → 仅按 tasks 做 P2 Apply
- 禁止无 tasks 直接改脚本
