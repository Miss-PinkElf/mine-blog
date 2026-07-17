# 下次对话提示词 · oc-mugen-rin-character-sheets

直接复制给新对话即可。

---

请用 **devflow** 续作 mission **`oc-mugen-rin-character-sheets`**（重型路径）。

## 恢复读取（热路径）

1. `.devflow/oc-mugen-rin-character-sheets/state.md`
2. `.devflow/oc-mugen-rin-character-sheets/checkpoints.md`
3. `.devflow/oc-mugen-rin-character-sheets/handoffs/2026-07-17-002-design-sheets-v1-close.md`

完整过程：`development-overview.md`；延期：`deferred/`；原始需求：`zzz-prompt-debug/origin/OC/prompt-1.md` + `人设.md`。

## 当前进度

### 第一版已完成（已出图）

| ID | 文件 |
| --- | --- |
| 全局 | `zzz-prompt-debug/origin/OC/generated/rin-01-global-design.png` |
| 角度/表情 | `.../rin-02-angles-expressions.png` |
| 动作 | `.../rin-03-actions.png` |
| JK 场景 | `.../rin-04-jk-server-room.png` |

### 明确延期 / 可选

- **rin-05 宅家直播**：4×HTTP 524 → `deferred/home-stream-scene-rin-05.md`
- 更密全套设定页、公开相册 → 其它 `deferred/`

### 未讨论完议题

- 无开放产品争议；仅余验收与是否补 05 / 是否 commit

## 注意

- 模型 **只用 `gpt-image-2`**
- 524 是网关超时，不是「没报错」；复杂图要长等 + retries
- 不要提交 `.env` / key
- 上一会话用户要求 **先不 commit**；新会话若要入库需用户明确

## 建议第一步

1. 目视打开 01–04，列不满意点  
2. 按需重抽单张，或重试 05  
3. 用户同意后再 git 提交 generated + 更新的 `.devflow/oc-mugen-rin-character-sheets/`
