# State · gpt-image-cli-tooling

- **阶段**：Close / Handoff（2026-07-18 晚 · 官方文档 Explore 收尾）
- **路径**：Heavy
- **本轮（Explore，未改 run.py 业务）**：
  - 官方教程全 tab 对齐（Chat `metadata.image_*` / Images API / 图生图 fidelity）
  - 文生图、单图、双图 skill 实测；HTTPS 双参考一次成功
  - **多图根因纠正**：不稳 ≈ data URL 大 body 断连，≠ 协议不支持多 `image_url`
- **实现基线仍有效（handoff 004）**：`run.py` / `run.mjs` / 多 `-i` / `--prep`
- **下轮优先（第一版即可）**：
  1. T7 Align→Plan→Apply：`--size/--ratio/--quality` → `metadata.image_*`
  2. T8 失败路径抽检
- **可选同批**：`--fidelity`、http(s) URL 直通、多图 body 策略写 SKILL
- **明确延期（本轮补充）**：`deferred/local-upload-then-url.md`；metadata 全量 CLI 进 backlog
- **阻塞**：无
- **最新 handoff**：`handoffs/2026-07-18-002-official-docs-explore-close.md`
- **下次入口**：`NEXT-SESSION-PROMPT-gpt-image-cli-tooling.md`
