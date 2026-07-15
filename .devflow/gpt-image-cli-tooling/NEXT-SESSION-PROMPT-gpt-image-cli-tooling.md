# 下次对话提示词 · gpt-image-cli-tooling

直接复制给新对话即可。

---

请用 devflow 续作 mission **`gpt-image-cli-tooling`**（重型路径）。

## 恢复读取（默认热路径）

1. `.devflow/gpt-image-cli-tooling/state.md`
2. `.devflow/gpt-image-cli-tooling/checkpoints.md`
3. 需要交接细节时：`.devflow/gpt-image-cli-tooling/handoffs/2026-07-15-001-session-close.md`
4. 实施前：`.devflow/gpt-image-cli-tooling/spec/tasks.md` + `spec/design.md`

完整过程再读 `development-overview.md`；延期项见 `deferred/`。

## 当前进度（摘要）

- **第一版已完成**：自包含 skill `.claude/skills/gpt-image-generate/`（`run.sh` + 同级 `.env`）
- 默认 model：`gpt-image-2`；重试；流式解码；Ctrl+C force kill；`---RESULT---` 汇报
- 仓库 `scripts/generate-image.sh` 为旁路，**skill 不依赖它**
- `scripts/generate-image.http` **仅本机**，已 untrack

## 未完成（优先）

### T7 · 尺寸 / 比例 / 质量（优先做）

- CLI / env：`--size`、`--quality`、`--ratio`
- 写入 Responses `tools[0]` 对应字段
- 验证至少 1:1 与 2:3

### T8 · Verify

- 无 key、空 prompt、成功出图、Ctrl+C 抽检并留证据

## 明确延期（不要本轮偷做）

- 异步 task 轮询 → `deferred/async-image-jobs.md`
- 站点内嵌生图 UI → `deferred/web-ui-image-gen.md`
- 「只有官方 aspect_ratio、不要 size」→ 用 ratio→size 映射在 T7 解决

## 注意

- 始终简体中文；路径用相对路径
- 不要提交 `.env`、key、`gen-images/`、`generate-image.http`
- 硬门禁：有 plan/tasks 再改代码；本 mission 已有 T7 任务可直接 Apply
- 用户未要求时不要 commit；要求时中文 commit message

## 建议第一步

打开 skill 的 `run.sh`，按 `spec/design.md` 为 `image_generation` 工具增加 `size`/`quality`，并支持 `--ratio` 映射表。
