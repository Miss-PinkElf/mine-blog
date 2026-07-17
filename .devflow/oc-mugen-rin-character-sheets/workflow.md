# Workflow · 无限凛 OC 人设设定图

## 路径

**重型路径（Heavy）**

## 当前阶段

**Close / Handoff（2026-07-17）** → 下轮从 **Apply（生图）** 恢复（先 Verify 中转可用性）

## 目标

产出可稳定复用的「无限凛」人设设定图，支持后续场景/表情/构图重绘时角色一致。

## 方法（对齐 cat-oc-design）

1. 提供全面设定图（全局、角度/表情、动作、场景）
2. 每次生成都带回原始设定图，避免链式 A→B→C 漂移
3. 先理解角色与风格，再写 prompt；图生图用 `--image`

## 范围

### 本轮（第一版准备）

| 项 | 状态 |
| --- | --- |
| 读人设 + 理解角色 | 完成 |
| 下载 HTML + 图库 | 完成 |
| 下载人设参考图 | 完成 |
| skill 可用性探测 | 完成（上游失败） |
| 生成全局设定图 | **阻塞** |
| 表情/动作/场景设定图 | 未开始（可第一版后做） |

### 第一版目标（恢复后）

- 至少 1 张「全局设定图」（三视图 + 脸部特写 + 色板 + JK/私服要点）
- 输出目录建议：`zzz-prompt-debug/origin/OC/generated/`
- 模型固定：`gpt-image-2`；Base URL 待中转恢复或替换

### 明确延期

- 见 `deferred/`（全套多页设定、相册页等）

## 里程碑

| 里程碑 | 状态 |
| --- | --- |
| 素材与方法理解 | 完成 |
| 中转生图可用 | **阻塞** |
| 全局设定图 v1 | 未开始 |
| 表情/角度扩展 | 延期/后续 |
| 本会话 Close/Handoff | 完成 |

## 关键路径

| 类型 | 路径 |
| --- | --- |
| 需求 | `zzz-prompt-debug/origin/OC/prompt-1.md` |
| 人设 | `zzz-prompt-debug/origin/OC/人设.md` |
| 角色参考图 | `zzz-prompt-debug/origin/OC/ref-character/` |
| HTML 方法与示例图 | `zzz-prompt-debug/origin/OC/ref-html/` |
| 计划 | `plans/2026-07-17-oc-design-sheet-first-pass.md` |
| Skill | `.codex/skills/gpt-image-generate/run.sh`（真相源 `.claude/...`） |
| 生图输出（计划） | `zzz-prompt-debug/origin/OC/generated/` |

## 下一步（新会话）

1. 读 `state.md` + `checkpoints.md` + 最新 handoff
2. 用极简 prompt 测 `gpt-image-2` 是否恢复
3. 恢复后按 plan 生成 `rin-01-global-design.png`（图生图 + 角色参考）
