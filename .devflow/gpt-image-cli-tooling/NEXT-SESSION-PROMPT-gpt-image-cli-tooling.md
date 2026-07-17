# 下次对话提示词 · gpt-image-cli-tooling

直接复制给新对话即可。

---

请用 **devflow** 续作 mission **`gpt-image-cli-tooling`**（重型路径）。

## 恢复读取（默认热路径）

1. `.devflow/gpt-image-cli-tooling/state.md`
2. `.devflow/gpt-image-cli-tooling/checkpoints.md`
3. 需要交接细节：`.devflow/gpt-image-cli-tooling/handoffs/2026-07-17-001-chat-protocol-session-close.md`
4. 实施前：`.devflow/gpt-image-cli-tooling/spec/tasks.md` + `spec/design.md`

完整过程再读 `development-overview.md`；延期见 `deferred/` 与 `backlog.md`。

## 当前进度（摘要）

### 已完成

- **第一版**：自包含文生图 skill（重试、中断、RESULT、默认 `gpt-image-2`）
- **第二版（2026-07-16）**：`--image` 图文同传；jq/node/python JSON 回退；双目录同步
- **第三版（2026-07-17）**：
  - 主协议改为 **Chat Completions**（`POST /v1/chat/completions`）
  - **不再**使用 `/responses` + `image_generation`
  - 响应：Markdown 图片 URL 下载 / data URL 解码
  - 实测：文生图、图生图、OC 大图 `zzz-prompt-debug/origin/OC/generated/rin-01-global-design.png` 成功

### 未完成（下轮优先，非延期）

#### T7 · 尺寸 / 比例 / 质量（优先 · 第一版即可）

- CLI / env：`--size`、`--quality`、`--ratio`
- **必须按 Chat 协议设计**，不要写 Responses `tools[0]`
- 建议先讨论：提示词前缀 vs 网关扩展字段，再落 plan/apply
- 验证至少 1:1 与 2:3 各一次

#### T8 · Verify 补强

- 无 key、空 prompt、成功出图、Ctrl+C 抽检并留证据

### 明确延期（不要本轮偷做）

- 异步 task 轮询 → `deferred/async-image-jobs.md`
- 站点内嵌生图 UI → `deferred/web-ui-image-gen.md`
- 「只有官方 aspect_ratio、不要 size」→ `deferred/aspect-ratio-only.md`
- 仓库 `scripts/generate-image.sh` 迁 Chat / 废弃双轨 → backlog（可选，非 T7 阻塞）

## 注意

- 始终简体中文；路径用相对路径
- 不要提交 `.env`、key、`gen-images/`
- 改 skill 后同步 **`.claude` → `.codex`**
- 硬门禁：有 plan/tasks 再改代码（用户另有要求除外）
- 大 base64 禁止进 bash 变量；图文 body 用临时文件 + curl `@file`
- macOS：`printf '%s\n' '---RESULT---'`，勿 `printf '---...'`

## 建议第一步

打开 `spec/design.md` 中「尺寸与比例设计（T7）」一节，先定 Chat 下 size/ratio 写入策略，再写 plan 并 Apply。
