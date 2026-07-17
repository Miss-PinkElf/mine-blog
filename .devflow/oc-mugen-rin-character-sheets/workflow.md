# Workflow · 无限凛 OC 人设设定图

## 路径

**重型路径（Heavy）**

## 当前阶段

**Close / Handoff（2026-07-17 · prompt-2 第一版）** → 下轮从 **质量重抽 / 可选补图 / 细验收** 恢复

## 目标

产出可复用的「无限凛」人设设定图 + 日常切片/表情包（设定图驱动，对齐 cat-oc-design）。

## 第一版范围（已落地）

| 类型 | 产物 | 状态 |
| --- | --- | --- |
| 全局设定 | `generated/rin-01-global-design.png` | 完成 |
| 角度/表情 | `generated/rin-02-angles-expressions.png` | 完成 |
| 动作 | `generated/rin-03-actions.png` | 完成 |
| 场景（JK/机房） | `generated/rin-04-jk-server-room.png` | 完成 |
| 场景（宅家直播设定） | rin-05 | **延期** |
| 风格参考本地 | `ref-style/` ×10 | 完成 |
| 日常切片 ×3 | `rin-daily-01/02/03` | 完成（第一版；用户观感一般） |
| 表情包 | `rin-stickers-01-line-pack.png` | 完成（第一版） |

## 方法要点

1. 先本地参考图 + HTML 方法，再出图
2. 模型固定 `gpt-image-2`；skill：`.claude/skills/gpt-image-generate/run.sh`（或 `.codex` 同步）
3. 大设定图 `image_edit` 易 524；日常可用 **文生图 + 角色锚点写进 prompt**
4. 单次建议 `--retries 0` + `CURL_MAX_TIME=300`；失败简化 prompt 另起一轮
5. 风格参考用于画风/构图气质，**不改角色设计**

## 里程碑

| 里程碑 | 状态 |
| --- | --- |
| 素材与方法理解 | 完成 |
| 设定图套件 01–04 | 完成 |
| prompt-2 日常 + 表情包第一版 | 完成 |
| 宅家场景 05 / 质量重抽 | 延期/可选 |
| 本会话 Close/Handoff + commit | 完成 |
