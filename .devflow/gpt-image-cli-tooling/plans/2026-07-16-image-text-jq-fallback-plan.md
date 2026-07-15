# 图文同传 + jq 回退 Implementation Plan

> **For agentic workers:** 按 tasks 顺序实现；完成后同步 `.codex` skill。

**Goal:** skill 支持参考图+文字编辑，并在无 jq 时用 node/python 轻量回退；双目录同步。

**Architecture:** 以 `.claude/skills/gpt-image-generate/run.sh` 为真相源。有 `--image` 时组装多模态 Responses body（action=edit），请求体写临时文件后 curl 投递；JSON 组装/抽取优先 jq，其次 node、python；图片二进制解码始终用系统 base64 流式管道。完成后同步到 `.codex/skills/gpt-image-generate/`。

**Tech Stack:** bash、curl、jq/node/python、OpenAI Responses `image_generation`

**Align 依据:** `.devflow/gpt-image-cli-tooling/plans/2026-07-16-image-text-jq-align.md`

---

## 文件映射

| 路径 | 动作 |
| --- | --- |
| `.claude/skills/gpt-image-generate/run.sh` | 改：CLI、body、回退、RESULT |
| `.claude/skills/gpt-image-generate/SKILL.md` | 改：触发/用法/双路径 |
| `.claude/skills/gpt-image-generate/references/notes.md` | 改：协议说明 |
| `.codex/skills/gpt-image-generate/*` | 同步（非 .env/gen-images） |
| `.gitignore` | 补 codex skill ignore |
| `.devflow/gpt-image-cli-tooling/spec/*` | 更新 |
| `.devflow/gpt-image-cli-tooling/state.md` 等 | Apply 后更新 |

## Task 清单

### T11 · run.sh 图文 + RESULT

- [ ] `--image` / `-i PATH`
- [ ] 无图：`input` 字符串 + `action=generate`
- [ ] 有图：多模态 content + `action=edit`；body 写临时文件
- [ ] RESULT：`mode` / `source_image`

### T12 · 文档

- [ ] SKILL.md 触发词与示例
- [ ] references/notes.md

### T13 · JSON 工具回退

- [ ] 探测顺序：jq → node → python3/python
- [ ] 无可用工具：分平台安装提示
- [ ] 抽取/组装均走同一探测结果

### T14 · 双目录 + gitignore

- [ ] 同步到 `.codex/skills/gpt-image-generate/`
- [ ] ignore `.codex/.../.env` 与 `gen-images/`

### T15 · Verify + mission 文档

- [ ] 语法检查 / help 检查
- [ ] 有条件时真实调用或记录本地证据
- [ ] 更新 tasks/state/checkpoint

## 验收

1. `./run.sh --help` 含 `--image`
2. 无 image 路径逻辑仍存在
3. 双目录 run.sh / SKILL.md 一致
4. gitignore 覆盖 codex skill 产物

## 执行说明

用户要求：**写 plan 后直接 Apply**（本会话 inline 执行，不另开 subagent）。
