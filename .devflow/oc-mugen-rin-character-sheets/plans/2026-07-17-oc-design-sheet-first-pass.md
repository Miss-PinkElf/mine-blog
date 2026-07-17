# Plan · 无限凛设定图第一版（收尾态）

## 目标

第一版可复用设定图套件（对齐 cat-oc-design 的全局/角度表情/动作/场景）。

## 结果（2026-07-17）

| 步骤 | 结果 |
| --- | --- |
| Smoke 文/图 | 成功 |
| rin-01 全局 | 成功 |
| rin-02 角度表情 | 成功（2×524 后成功，总 ~8m） |
| rin-03 动作 | 成功（~70s） |
| rin-04 JK 场景 | 成功（~102s） |
| rin-05 宅家 | 失败 4×524 → **延期** |

## 模型与工具

- `gpt-image-2` only
- `.codex/skills/gpt-image-generate/run.sh`
- 参考：`zzz-prompt-debug/origin/OC/_preview/char-02.png`（或全局设定缩略）

## 下轮若补 05

```bash
export CURL_MAX_TIME=420
.codex/skills/gpt-image-generate/run.sh --no-open --retries 4 -m gpt-image-2 \
  --image zzz-prompt-debug/origin/OC/_preview/char-02.png \
  -o zzz-prompt-debug/origin/OC/generated/rin-05-home-stream.png \
  "Same girl as reference... home gaming chair scene..."
```
