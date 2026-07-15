# Handoff · 2026-07-16-001 · 图文同传会话收尾

## 元信息

- **Mission**：`gpt-image-cli-tooling`
- **时间**：2026-07-16
- **原因**：上下文过长，新开对话继续；本轮 T11–T15 已完成并 Verify

## 本轮完成了什么

1. 实测确认 Responses **图文同传**可用（curl；urllib 可能 CF 1010）
2. Align / Plan / Spec（T11–T15）并 Apply
3. Skill 增强：
   - `--image` / `-i` → `action=edit` 多模态请求
   - `lib/json_codec.py` + `lib/json_codec.cjs`（无 jq 回退）
   - RESULT：`mode` / `json_backend` / `source_image`
4. 同步 `.codex/skills/gpt-image-generate/`
5. 实测：`JSON 工具: node`，HTTP 200，约 74s，出图成功

## 代码入口

| 角色 | 路径 |
| --- | --- |
| 真相源 | `.claude/skills/gpt-image-generate/` |
| Codex 副本 | `.codex/skills/gpt-image-generate/` |
| 主脚本 | `run.sh` |
| JSON 回退 | `lib/json_codec.cjs` / `lib/json_codec.py` |

## 未完成（下轮）

| ID | 内容 | 性质 |
| --- | --- | --- |
| T7 | size / quality / ratio | **优先做**（第一版未做的能力扩展） |
| T8 | 失败路径正式 Verify | **优先做** |

## 明确延期（勿偷做）

- `deferred/async-image-jobs.md`
- `deferred/web-ui-image-gen.md`
- `deferred/aspect-ratio-only.md`（用 T7 映射表替代）

## 决策摘要

- 有图固定 `edit`；无图 `generate`
- JSON 首选 jq；node/python 为正式轻量回退，不重写整栈为 Node
- 双目录以 `.claude` 为真相源

## 恢复建议

1. 读 `state.md` + `checkpoints.md`
2. 读本 handoff（可选）
3. 读 `NEXT-SESSION-PROMPT-gpt-image-cli-tooling.md`
4. Apply **T7**

## 风险 / 注意

- 勿提交 `.env` / `gen-images/` / key
- 改 skill 必须双目录同步
- 大图编辑请求慢，注意 `CURL_MAX_TIME`
