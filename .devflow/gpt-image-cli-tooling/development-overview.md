# Development Overview · gpt-image-cli-tooling

## 定位

完整过程总览；默认恢复不读本文件。

## 背景

用户需在本地调用中转站 GPT Image，从 curl / REST Client 演进为可维护脚本，再封装为**自包含 Claude/Codex Skill**，并纳入 devflow 重型治理。  
**2026-07-17 起 skill 主协议为 Chat Completions**（不再以 Responses 为主路径）。

## 已完成阶段（本对话）

1. **联调**：确认 `/v1/responses` + `image_generation`；响应 `output[].result` base64  
2. **脚本 MVP**：env、提示词文件、gen-images、重试、loading  
3. **热修**：流式解码、双计时、Ctrl+C 第一轮、524 说明  
4. **Mission 补录**：重型 skeleton + plan + spec  
5. **T9 Skill**：完全自包含（不依赖 REPO_ROOT / 仓库 scripts）  
6. **对齐 .http 体验**：默认 model=`gpt-image-2`；curl 默认 180s；Ctrl+C force kill  
7. **安全**：`generate-image.http` untrack + ignore；核查 key 是否进历史  

## 关键提交（本对话相关，摘录）

| Commit | 说明 |
| --- | --- |
| `f76cec2` | 脚本 + mission 初版 |
| `e84276d` | 自包含 gpt-image-generate skill |
| `f35d114` | 默认 gpt-image-2、中断/超时、untrack http |

## 第一版 vs 后续

| 类别 | 内容 |
| --- | --- |
| 第一版已交付 | Skill 出图、重试、中断、RESULT、默认 image-2 |
| 下轮优先 | T7 size/ratio/quality；T8 Verify |
| 明确延期 | 异步 task、站点 UI、纯 ratio 官方字段（见 `deferred/`） |

## 推荐读取

- 恢复：`state.md` → `checkpoints.md`
- 续作：`spec/tasks.md` + `handoffs/` 最新 + NEXT-SESSION-PROMPT

## 2026-07-16 增量（第二版）

### 目标

在第一版纯文生图之上，支持「参考图 + 文字」编辑，并提升无 jq 环境可用性；同时让 Codex 与 Claude 两套 skill 目录一致。

### 过程摘要

1. 实测确认多模态图文可用（curl）；Python urllib 曾遇 Cloudflare 1010  
2. Align → Plan → Spec（T11–T15）→ Apply  
3. 实现 `--image`、`lib/json_codec.*`、RESULT 扩展、双目录同步  
4. Verify：无 jq 时 node 回退成功出图（约 74s）  
5. 会话 Close/Handoff，T7/T8 留待下轮；延期项仍见 `deferred/`

### 相关计划

- `plans/2026-07-16-image-text-jq-align.md`
- `plans/2026-07-16-image-text-jq-fallback-plan.md`

## 2026-07-17 增量（第三版 · Chat 协议）

### 目标

按用户要求将 skill 从 Responses 改为 **v1 Chat Completions**，保持文生图 + 图生图能力，并验证真实 OC 大参考图。

### 过程摘要

1. 改造 `run.sh` / `json_codec` 请求体与端点；响应支持 Markdown URL 下载与 data URL 解码  
2. 修复 macOS `printf ---` 与 `has` 短 base64 边界  
3. 实测：文生图 ~20s；小图编辑 ~28s；`rin-01-global-design.png` 图生图 ~75s  
4. 更新 decision/bug/tasks/design；T7 标记须 Chat 适配；scripts 旧协议记入 backlog  
5. 会话 Close/Handoff  

### 产物

- Skill：`.claude/skills/gpt-image-generate/`（同步 `.codex/...`）
- 最新 handoff（当时）：`handoffs/2026-07-17-001-chat-protocol-session-close.md`

## 2026-07-18 增量（第四版 · 跨平台）

### 目标

Win/Mac 可跑：Python 主入口 + Node 兜底；多参考图；输入可压。

### 过程摘要

1. `run.py` / `run.mjs` / 启动器；`--prep`；多 `-i`
2. 双图实测落盘；断连靠重试 + 压 body
3. 明确不做：内嵌运行时、输出体积治理

## 2026-07-18 晚 增量（官方文档 Explore · 无代码业务改动）

### 目标

读透 https://team.wyzlab.ai/tutorial/gpt-image，纠正 T7 与多图理解。

### 关键结论

1. T7 → `metadata.image_size` / `image_quality`（已探针）
2. 图生图官方：`image_input_fidelity` + 示范 https `image_url`
3. 多图不稳 ≈ data URL 大 body，≠ 协议拒绝
4. Images API 可选纯画图路径；skill 仍走 Chat

### 产物

- handoff：`handoffs/2026-07-18-002-official-docs-explore-close.md`
- notes / learnings / design T7 段更新
- 探针目录 `_probe_out/`（本地，默认不提交）
