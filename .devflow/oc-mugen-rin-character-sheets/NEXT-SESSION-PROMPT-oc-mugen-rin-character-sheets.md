# 下次对话提示词 · oc-mugen-rin-character-sheets

直接复制给新对话即可。

---

请用 **devflow** 续作 mission **`oc-mugen-rin-character-sheets`**（重型路径）。

## 恢复读取（热路径）

1. `.devflow/oc-mugen-rin-character-sheets/state.md`
2. `.devflow/oc-mugen-rin-character-sheets/checkpoints.md`
3. `.devflow/oc-mugen-rin-character-sheets/handoffs/2026-07-17-003-prompt2-daily-sticker-close.md`

完整过程：`development-overview.md`；延期：`deferred/`；需求：`zzz-prompt-debug/origin/OC/prompt-1.md` + `prompt-2.md` + `人设.md` + `风格参考图.md`。

## 当前进度

### 第一版已完成（已入库/或已落盘）

**设定图**

| ID | 文件 |
| --- | --- |
| 全局 | `zzz-prompt-debug/origin/OC/generated/rin-01-global-design.png` |
| 角度/表情 | `.../rin-02-angles-expressions.png` |
| 动作 | `.../rin-03-actions.png` |
| JK 场景 | `.../rin-04-jk-server-room.png` |

**prompt-2 日常 + 表情包（第一版；用户观感一般，暂接受）**

| ID | 文件 |
| --- | --- |
| 风格参考 | `ref-style/` ×10 |
| 日常 01 | `generated/rin-daily-01-home-code.png`（宅家写代码，锚点较好） |
| 日常 02 | `generated/rin-daily-02-convenience-jk.png` |
| 日常 03 | `generated/rin-daily-03-live-stream.png`（实为卧室刷手机，非真直播） |
| 表情包 | `generated/rin-stickers-01-line-pack.png`（6 格） |

### 明确延期

- **rin-05 真·宅家直播** → `deferred/home-stream-scene-rin-05.md`（daily-03 不算完成此项）
- 更密全套设定页 → `deferred/full-multi-sheet-suite.md`
- 公开相册页 → `deferred/public-gallery-page.md`

### 未讨论完议题

- 无开放产品争议；余项为质量重抽与是否补真直播

## 注意

- 模型 **只用 `gpt-image-2`**
- 单次建议 `--retries 0` + `CURL_MAX_TIME=300`；失败简化再试
- 大设定图 image_edit 易 524；日常可用文生图 + 角色锚点
- 风格参考只借画风/动作，不改人设
- 不要提交 `.env` / key

## 建议第一步

1. 目视打开 daily/stickers，列具体不满意点（脸、瞳、服装、画风）  
2. 按点重抽单张，或以 `rin-01` 为锚点小图再试 image_edit  
3. 可选补真直播构图（rin-05 / 替换 daily-03）
