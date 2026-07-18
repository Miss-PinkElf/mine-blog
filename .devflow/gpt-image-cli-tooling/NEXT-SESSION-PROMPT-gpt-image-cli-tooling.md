# 下次对话提示词 · gpt-image-cli-tooling

直接复制给新对话即可。

---

请用 **devflow** 续作 mission **`gpt-image-cli-tooling`**（重型路径）。

## 恢复读取（默认热路径）

1. `.devflow/gpt-image-cli-tooling/state.md`
2. `.devflow/gpt-image-cli-tooling/checkpoints.md`
3. 交接：`.devflow/gpt-image-cli-tooling/handoffs/2026-07-18-002-official-docs-explore-close.md`
4. 需要时：`learnings.md`（2026-07-18 续）+ `spec/tasks.md`（T7/T8）

实现基线可补读：`handoffs/2026-07-18-001-python-node-cross-platform-close.md`

## 当前进度（摘要）

### 已完成

- 第一～四版：文生图、图文、Chat 协议、Python/Node 跨平台、多 `-i`、`--prep`
- **2026-07-18 晚 Explore（未改 run.py 业务）**：
  - 官方教程：https://team.wyzlab.ai/tutorial/gpt-image
  - T7 正确写入点：Chat 顶层 **`metadata.image_*`**
  - 图生图官方：`image_url`（示范为 **https URL**）+ **`image_input_fidelity: high`**
  - **多图根因**：不稳 ≈ **data URL 大 body 断连**；HTTPS 双参考 body≈526B 一次 200
  - 多 `image_url` 实测可用，但**官方只示范单参考**，勿写成文档主路径

### 未完成（下轮优先）

#### T7 · 尺寸 / 比例 / 质量（第一版）

- CLI/env：`--size`、`--quality`、`--ratio` → `metadata.image_size` / `image_quality`
- 先 Align 再 plan/apply；至少验证 1:1 与 2:3
- 注意：`1024x1024` 实测像素可能约 1254 边长

#### 建议与 T7 同批讨论（可选）

- `--fidelity` → `image_input_fidelity`
- http(s) `image_url` 直通（不二次 base64）
- 本地大图 / 多图 body 策略（prep 或先上传换 URL）

#### T8 · Verify 补强

- 无 key、空 prompt、成功出图、Ctrl+C 抽检

### 明确延期

- 异步 task、站点 UI、仅 aspect_ratio、内嵌运行时/输出体积治理 → `deferred/`
- **本地大图先上传再 URL** → `deferred/local-upload-then-url.md`
- metadata 全量 CLI（background/format/moderation/partial）→ backlog（T7 第一版不做）
- 仓库 scripts 迁 Chat → backlog

## 注意

- 始终简体中文；相对路径
- 不要提交 `.env`、key、skill 内 `gen-images/`、`_probe_out/` 大图
- 改 skill 后同步 **`.claude` → `.codex`**
- 多图/大本地图：优先控 body；不要再假设「多图协议不可用」
- 默认：`python .claude/skills/gpt-image-generate/run.py ...`

## 建议第一步

做 T7：先 Align CLI→metadata 映射与是否同批带 fidelity/URL 直通，确认后写 plan 再 Apply。
