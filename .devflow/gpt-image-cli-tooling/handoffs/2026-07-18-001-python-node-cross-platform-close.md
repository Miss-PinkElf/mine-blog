# Handoff · 2026-07-18-001 · Python 主入口 + Node 兜底收尾

## 当前目标

跨平台稳定运行 gpt-image skill：文生图 / 单图与多图图生图；输入可调压缩；不依赖 bash 主路径。

## 当前阶段

Close / Handoff（第四版交付完成）

## 当前进度

- T17 已完成并实测
- T7 / T8 仍未做
- 仓库 `scripts/generate-image.sh` 仍为旧协议（双轨）

## 本轮完成内容

1. Align + Plan：`plans/2026-07-18-python-node-cross-platform-plan.md`
2. 实现：
   - `run.py`、`run.mjs`、`lib/image_prep.py`
   - `run.cmd` / `run`；`run.sh` 薄封装
   - 多 `-i`；`--prep` 档位
   - 同步 `.codex/skills/gpt-image-generate/`
3. 验证：
   - 文生图、单图图生图
   - **双图** HTTP 200 + 落盘 `zzz-prompt-debug/origin/OC/generated/rin-dual-test-01.png`
4. 结论：双图协议可用；断连 ≠ 组包错误；响应 model 常被改写为 `gpt-5.4`

## 关键决策与原因

| 决策 | 原因 |
| --- | --- |
| py 主 / node 兜底 | Win/Mac 有 py；至少一个脚本运行时 |
| 不内嵌运行时 | 体积与维护；见 deferred |
| 输入压、输出不压 | 成功率 vs 出图质量职责分离 |
| 默认不固定长边 | 质量优先编码；Agent 用 `--prep` 判断 |

## 关键文件 / 产物

- Skill 真相源：`.claude/skills/gpt-image-generate/`（`run.py` 等）
- Codex 镜像：`.codex/skills/gpt-image-generate/`
- Plan / mission 文档：`.devflow/gpt-image-cli-tooling/`
- 双图样张：`zzz-prompt-debug/origin/OC/generated/rin-dual-test-01.png`

## 风险 / 阻塞 / 开放问题

- 中转偶发断连；大 body 更易挂
- 请求 model 与响应 model 不一致
- Node 无 Pillow/py 时 prep 能力弱
- T7 仍须按 Chat 重新设计

## 立即下一步

1. 新对话读 `state.md` + `checkpoints.md` + 本 handoff
2. 优先 T7（size/ratio/quality 第一版）或 T8 抽检
3. 多图出图默认建议 `--prep heavy`

## 恢复指引

- 热路径：`state.md` → `checkpoints.md` → 本 handoff
- 完整过程：`development-overview.md`（本轮未大改）
- 延期：`deferred/` + `backlog.md`
