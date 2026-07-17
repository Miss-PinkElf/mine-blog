# 下次对话提示词 · oc-mugen-rin-character-sheets

直接复制给新对话即可。

---

请用 **devflow** 续作 mission **`oc-mugen-rin-character-sheets`**（重型路径）。

## 恢复读取（默认热路径）

1. `.devflow/oc-mugen-rin-character-sheets/state.md`
2. `.devflow/oc-mugen-rin-character-sheets/checkpoints.md`
3. 交接细节：`.devflow/oc-mugen-rin-character-sheets/handoffs/2026-07-17-001-api-blocked-session-close.md`
4. 计划：`.devflow/oc-mugen-rin-character-sheets/plans/2026-07-17-oc-design-sheet-first-pass.md`

完整过程再读 `development-overview.md`；延期见 `deferred/` 与 `backlog.md`。

原始需求与素材：

- `zzz-prompt-debug/origin/OC/prompt-1.md`
- `zzz-prompt-debug/origin/OC/人设.md`
- `zzz-prompt-debug/origin/OC/ref-character/`
- `zzz-prompt-debug/origin/OC/ref-html/`

## 当前进度（摘要）

### 已完成

- 人设理解（无限凛 / URO：黑客、三无傲娇傻萌、黑+赛博绿、异色瞳∞、JK/卫衣）
- HTML 方法下载与理解（设定图驱动）
- 角色参考图本地化
- skill 探测：当前中转 **不可用**

### 未完成（下轮优先，非延期）

1. **先** 极简 smoke test：`gpt-image-2` 是否恢复
2. 生成 **全局设定图** `zzz-prompt-debug/origin/OC/generated/rin-01-global-design.png`
   - 参考图用 `_preview/char-02.png` 或同级缩略图
   - 模型：`gpt-image-2` only
3. 目视验收：脸、色板、∞ 瞳孔、JK 要点

### 明确延期（不要本轮偷做）

- 全套多页设定（表情/动作/场景全集）→ `deferred/full-multi-sheet-suite.md`
- 公开相册页 → `deferred/public-gallery-page.md`
- skill 的 T7/T8 尺寸能力 → 属 mission `gpt-image-cli-tooling`，勿混做

## 注意

- 始终简体中文；路径用相对路径
- 不要提交 `.env`、key、`gen-images/`
- 本机无系统代理；若仍 500 是中转上游问题
- 大图先缩再 `--image`；`CURL_MAX_TIME` 可调高
- 硬门禁：按 plan 执行；用户未要求不要随意扩大范围

## 建议第一步

```bash
.codex/skills/gpt-image-generate/run.sh --no-open -m gpt-image-2 \
  -o zzz-prompt-debug/origin/OC/generated/smoke-text.png \
  "a red apple on white background, simple photo"
```

成功后再按 plan 做 `rin-01-global-design.png`。
