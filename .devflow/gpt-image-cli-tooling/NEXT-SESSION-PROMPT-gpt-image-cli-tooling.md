# 下次对话提示词 · gpt-image-cli-tooling

直接复制给新对话即可。

---

请用 **devflow** 续作 mission **`gpt-image-cli-tooling`**（重型路径）。

## 恢复读取（默认热路径）

1. `.devflow/gpt-image-cli-tooling/state.md`
2. `.devflow/gpt-image-cli-tooling/checkpoints.md`
3. 需要交接细节：`.devflow/gpt-image-cli-tooling/handoffs/2026-07-16-001-image-text-session-close.md`
4. 实施前：`.devflow/gpt-image-cli-tooling/spec/tasks.md` + `spec/design.md`

完整过程再读 `development-overview.md`；延期见 `deferred/` 与 `backlog.md`。

## 当前进度（摘要）

### 已完成

- **第一版**：自包含文生图 skill（重试、中断、RESULT、默认 `gpt-image-2`）
- **第二版（2026-07-16）**：
  - `--image` / `-i` 图文同传（`action=edit`）
  - JSON：`jq` → `node` + `lib/json_codec.cjs` → `python` + `lib/json_codec.py`
  - 双目录：`.claude/skills/gpt-image-generate/`（真相源）与 `.codex/skills/gpt-image-generate/` 同步
  - 实测：无 jq 时用 node 成功出图

### 未完成（下轮优先，非延期）

#### T7 · 尺寸 / 比例 / 质量（优先）

- CLI / env：`--size`、`--quality`、`--ratio`
- 写入 Responses `tools[0]`；验证至少 1:1 与 2:3

#### T8 · Verify 补强

- 无 key、空 prompt、成功出图、Ctrl+C 抽检并留证据

### 明确延期（不要本轮偷做）

- 异步 task 轮询 → `deferred/async-image-jobs.md`
- 站点内嵌生图 UI → `deferred/web-ui-image-gen.md`
- 「只有官方 aspect_ratio、不要 size」→ T7 用 ratio→size 映射；见 `deferred/aspect-ratio-only.md`

## 注意

- 始终简体中文；路径用相对路径
- 不要提交 `.env`、key、`gen-images/`
- 改 skill 后同步 **`.claude` → `.codex`**
- 硬门禁：有 plan/tasks 再改代码；用户未要求不要 commit（或按其要求）
- 大 base64 禁止进 bash 变量；图文 body 用临时文件 + curl `@file`

## 建议第一步

打开 skill `run.sh`，按 `spec/design.md` / tasks **T7** 增加 size/quality/ratio。
