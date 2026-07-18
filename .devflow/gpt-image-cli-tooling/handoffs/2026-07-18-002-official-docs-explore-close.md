# Handoff · 2026-07-18-002 · 官方教程对齐 + 多图根因澄清收尾

## 当前目标

对齐 wyzlab 官方 gpt-image 教程，搞清文生图 / 图生图 / 多参考图真实调用方式；为 T7（size/quality）与多图稳定性定方向。本轮**不实现代码业务**，只 Explore + 实测 + 记录。

## 当前阶段

Close / Handoff（Explore 收束；T7 未开 Plan/Apply）

## 当前进度

- 官方教程 6 tab 已读透（SPA 从 `team.wyzlab.ai` JS bundle 抽取）
- 文生图 / 单图 / 双图 skill 实测过
- **多图“不稳”根因已纠正**：主要是 data URL 大 body 断连，不是协议拒绝多图
- T7 写入点明确为 Chat 顶层 `metadata.image_*`
- **未改** `run.py` 组包逻辑（仍无 metadata / 仍无 fidelity / 本地图仍 base64）

## 本轮完成内容

1. 恢复 mission：`state` + handoff 004 + skill 现状
2. 读官方文档：https://team.wyzlab.ai/tutorial/gpt-image
   - 基础调用 / 参数矩阵 / 场景示例 / Images API / SDK / FAQ
3. 探针与 skill 实测（产物在 `_probe_out/`）
4. 纠正多图结论：HTTPS 双 `image_url` body≈526B 一次 200；data URL 双图 body≈254KB 易断连重试
5. 更新 `learnings.md`、`origin.md`、`notes.md`（.claude + .codex 同步 notes）

## 关键决策与原因

| 决策 / 结论 | 原因 |
| --- | --- |
| T7 用 `metadata.image_*`，不用 tools / 纯提示词硬猜 | 官方参数矩阵明文；已探针 1:1 与 2:3 |
| 图生图应对齐 `image_input_fidelity` | 官方场景示例必写 high |
| 多图不标成“官方主路径” | 教程只示范单参考 HTTPS URL |
| “多图不稳”改为“大 body data URL 不稳” | 同为双图：URL 稳、base64 不稳 |
| 本轮不改 run.py | 用户要求先理解与测试；实现走下轮 Align→Plan |

## 关键文件 / 产物

- 记录：`learnings.md`（2026-07-18 续）、`state.md`、`checkpoints.md`、`origin.md`
- Skill 文档：`.claude/skills/gpt-image-generate/references/notes.md`（已 sync `.codex`）
- 探针输出：`.devflow/gpt-image-cli-tooling/_probe_out/`
  - `skill-text.png` / `skill-img2img-single.png` / `skill-img2img-dual.png`
  - `chat-meta-1x1.png` / `chat-meta-2x3.png` / `images-api-star.png`
  - `dual-https-url-refs.png`（HTTPS 双参考，body 极小一次成功）
  - `chat-fidelity-high.png`
- 临时脚本（可下轮清理）：`tmp_probe_*.py`、`tmp_extract_*.py`、`tmp_dig_*.py`

## 风险 / 阻塞 / 开放问题

- 本地大图仍走 data URL 时，多图/大图会继续偶发断连；需下轮设计 URL 或更强压缩策略
- skill 尚未发送 `metadata` / `image_input_fidelity`
- `1024x1024` 实测像素可能约 1254×1254，勿写死严格相等
- `_probe_out/` 与 tmp 脚本：**不提交**（探针产物/临时脚本）

## 第一版 vs 延期（收尾核对）

| 类别 | 项 |
| --- | --- |
| 下轮第一版 | T7 metadata size/quality/ratio；T8 抽检 |
| 可选同批 | fidelity CLI；http(s) 直通；SKILL 多图 body 策略 |
| 明确延期 | 上传换 URL（`deferred/local-upload-then-url.md`）；内嵌运行时；输出体积；async/UI/仅 ratio；metadata 全量 CLI |

## 立即下一步（新对话）

1. 读 `state.md` + `checkpoints.md` + 本 handoff
2. **T7 Align → Plan**：CLI `--size/--ratio/--quality` → `metadata.image_*`
3. 可选同批：`--fidelity`；支持 http(s) `image_url` 直通；多图 body 策略写进 SKILL
4. 不要把“多图协议不可用”当前提

## 恢复指引

- 热路径：`state.md` → `checkpoints.md` → 本 handoff
- 官方字段与探针表：`learnings.md` 2026-07-18 续
- 实现真相源：`.claude/skills/gpt-image-generate/`
- 入口提示：`NEXT-SESSION-PROMPT-gpt-image-cli-tooling.md`
