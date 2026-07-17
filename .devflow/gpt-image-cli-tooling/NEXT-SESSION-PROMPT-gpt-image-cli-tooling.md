# 下次对话提示词 · gpt-image-cli-tooling

直接复制给新对话即可。

---

请用 **devflow** 续作 mission **`gpt-image-cli-tooling`**（重型路径）。

## 恢复读取（默认热路径）

1. `.devflow/gpt-image-cli-tooling/state.md`
2. `.devflow/gpt-image-cli-tooling/checkpoints.md`
3. 交接：`.devflow/gpt-image-cli-tooling/handoffs/2026-07-18-001-python-node-cross-platform-close.md`
4. 实施前：`spec/tasks.md`（T7/T8）+ 需要时 `spec/design.md`

完整过程再读 `development-overview.md`；延期见 `deferred/` 与 `backlog.md`。

## 当前进度（摘要）

### 已完成

- 第一～三版：文生图、图文、Chat Completions、双目录
- **第四版（2026-07-18）**：
  - 主入口 **`run.py`**，兜底 **`run.mjs`**，`run.cmd` / `run`
  - 多图 `-i`（可重复）、输入 `--prep`（默认不固定长边）
  - **双图实测成功**：`zzz-prompt-debug/origin/OC/generated/rin-dual-test-01.png`
  - 断连靠重试 + 压 body；**不是**协议不支持双图

### 未完成（下轮优先，非延期）

#### T7 · 尺寸 / 比例 / 质量（第一版即可）

- CLI/env：`--size`、`--quality`、`--ratio`
- **必须按 Chat 协议设计**，不要写 Responses `tools[0]`
- 先讨论再 plan/apply；至少验证 1:1 与 2:3

#### T8 · Verify 补强

- 无 key、空 prompt、成功出图、Ctrl+C 抽检

### 可选

- notes 体积/断连对照表
- 多图默认建议 heavy 写进 SKILL 更醒目

### 明确延期（不要本轮偷做）

- 异步 task → `deferred/async-image-jobs.md`
- 站点 UI → `deferred/web-ui-image-gen.md`
- 仅 aspect_ratio → `deferred/aspect-ratio-only.md`
- **内嵌运行时 / 输出体积治理** → `deferred/no-bundled-runtime-and-output-size.md`
- 仓库 scripts 迁 Chat / 废弃双轨 → backlog

## 注意

- 始终简体中文；相对路径
- 不要提交 `.env`、key、skill 内 `gen-images/`
- 改 skill 后同步 **`.claude` → `.codex`**
- 多图/大参考图：优先 `--prep heavy` 控 body
- 响应 `model` 可能是 `gpt-5.4`，请求仍可写 `gpt-image-2`
- 默认：`python .claude/skills/gpt-image-generate/run.py ...`

## 建议第一步

若做 T7：先对齐 Chat 下 size/ratio 写入策略（提示词 vs 扩展字段），再写 plan 后 Apply。  
若只验证稳定性：补 T8 失败路径证据即可。
