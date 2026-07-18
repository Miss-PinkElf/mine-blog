# 下次对话提示词 · oc-mugen-rin-character-sheets

直接复制给新对话即可。

---

请用 **devflow** 续作 mission **`oc-mugen-rin-character-sheets`**（重型路径）。

## 恢复读取（热路径）

1. `.devflow/oc-mugen-rin-character-sheets/state.md`
2. `.devflow/oc-mugen-rin-character-sheets/checkpoints.md`
3. `.devflow/oc-mugen-rin-character-sheets/handoffs/2026-07-18-005-grok-session-close.md`

完整过程：`development-overview.md`；延期：`deferred/`；需求：`zzz-prompt-debug/origin/OC/prompt-1.md` + `prompt-2.md` + `人设.md`。

## 当前进度（一句话）

- **主线第一版**在 `zzz-prompt-debug/origin/OC/generated/`（gpt-image-2 设定图 01–04 + 日常/表情包），暂作可用/已接受第一版。
- **Grok 试做**在 `zzz-prompt-debug/origin/OC/grok-images/`（设定图+日常+表情包共 9 张），用户判定**质量一般/偏糊，暂时不管，不定稿**。

## 主线产物（generated/）

| 类型 | 文件 |
| --- | --- |
| 全局/角度/动作/机房 | `rin-01`～`rin-04`*.png |
| 日常 ×3 | `rin-daily-01/02/03`*.png |
| 表情包 | `rin-stickers-01-line-pack.png` |
| 风格参考 | `../ref-style/` ×10 |

## 明确延期

- 设定图级宅家直播 → `deferred/home-stream-scene-rin-05.md`
- 更密全套设定页 → `deferred/full-multi-sheet-suite.md`
- 公开相册 → `deferred/public-gallery-page.md`
- Grok 清晰度重抽 → 未承诺（backlog 一句话）

## 注意

- 默认继续以 **generated/** 为角色锚，不要默认当 Grok 已定稿
- 历史：gpt-image 中转易 524；Grok 清晰度一般
- 不要提交 `.env` / key

## 建议第一步

1. 确认用户新对话目标（新需求 / 重抽 / 延期项）  
2. 未点名则不碰 `grok-images/`  
3. 需要理解过程再读 `development-overview.md`  
