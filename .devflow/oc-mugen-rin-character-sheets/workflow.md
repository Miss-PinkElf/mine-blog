# Workflow · 无限凛 OC 人设设定图

## 路径

**重型路径（Heavy）**

## 当前阶段

**Close / Handoff（2026-07-17）** → 下轮从 **目视验收 / 可选补图** 恢复

## 目标

产出可复用的「无限凛」人设设定图资产（设定图驱动，对齐 cat-oc-design）。

## 第一版范围（本轮已落地）

| 类型 | 产物 | 状态 |
| --- | --- | --- |
| 全局设定 | `zzz-prompt-debug/origin/OC/generated/rin-01-global-design.png` | 完成 |
| 角度/表情 | `.../rin-02-angles-expressions.png` | 完成（含 524 重试） |
| 动作 | `.../rin-03-actions.png` | 完成 |
| 场景（JK/机房） | `.../rin-04-jk-server-room.png` | 完成 |
| 场景（宅家直播） | rin-05 | **未交付**（524×4，已记延期） |

## 方法要点

1. 先本地参考图 + HTML 方法，再出图
2. 模型固定 `gpt-image-2`；skill：`.codex/skills/gpt-image-generate/run.sh`
3. 图生图用缩略参考（`_preview/char-02.png` 等），避免超大 body
4. 每次尽量带回角色锚点；复杂 multi-panel 易 524，需 `--retries` 与足够等待

## 里程碑

| 里程碑 | 状态 |
| --- | --- |
| 素材与方法理解 | 完成 |
| 中转恢复后 smoke | 完成 |
| 第一版设定图套件 01–04 | 完成 |
| 宅家场景 05 | 延期/可选 |
| 本会话 Close/Handoff | 完成 |

## 下一步（新会话）

1. 读 `state.md` + `checkpoints.md` + 最新 handoff
2. 目视验收 01–04；不满意再针对性重抽
3. 可选：重试 rin-05 或补其它场景
4. **不要**默认开全套表情包/公开相册（已 deferred）
