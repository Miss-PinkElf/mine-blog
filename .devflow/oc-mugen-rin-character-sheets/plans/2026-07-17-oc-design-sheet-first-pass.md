# Plan · 无限凛全局设定图第一版

## 目标

在 API 可用前提下，生成至少 1 张专业向 anime character design sheet。

## 前置条件

1. `GET {BASE}/models` 含 `gpt-image-2`
2. 极简文生图 smoke test 成功（如「red apple on white」）
3. skill：`.codex/skills/gpt-image-generate/run.sh`（或 `.claude` 真相源）

## 步骤

1. **Smoke**
   ```bash
   .codex/skills/gpt-image-generate/run.sh --no-open -m gpt-image-2 \
     -o zzz-prompt-debug/origin/OC/generated/smoke-text.png \
     "a red apple on white background, simple photo"
   ```
2. **准备参考图**：优先 `_preview/char-02.png`（或 char-04），长边约 800
3. **全局设定图（图生图）**
   - 输出：`zzz-prompt-debug/origin/OC/generated/rin-01-global-design.png`
   - 内容：正/侧/背全身 JK；脸部特写（异色瞳+∞）；色板；衔尾蛇配件；小私服卫衣 bust
   - 风格：赛璐珞、干净线稿、浅灰底生产向设定板
4. **可选第二张**：表情/角度 sheet（若第一张脸稳定）
5. **Verify**：目视脸一致性、色板、∞ 瞳孔、无乱码水印

## 提示词要点（摘要）

- Same girl as reference；black + neon cyber-green hair
- Heterochromia；green eye ∞ pupil
- Custom JK：dark gray blazer、black-green plaid skirt、ouroboros pin
- Casual：oversized black hoodie、mismatched black/green thigh-highs、headphones

## 非目标（本 plan）

- 全套动作/场景
- 修改 skill 功能（T7/T8 属 `gpt-image-cli-tooling`）
