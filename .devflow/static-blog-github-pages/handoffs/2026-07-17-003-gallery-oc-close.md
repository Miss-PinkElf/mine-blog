# Handoff · 003 · Gallery OC 真图与 Profile 立绘收尾

- **时间**：2026-07-17
- **Mission**：`static-blog-github-pages`
- **状态标记**：active（最新）
- **前序**：`2026-07-17-002-shell-migrate-close.md`（superseded 作为历史）

## 当前目标

無限凜静态站在 Shell/Classic 双入口之上，**Gallery 第一版真图 + Profile 立绘**已落地；下一对话可 polish、上线或扩展内容。

## 当前阶段

Close / 会话交接。本轮内容接入与文档收尾完成。

## 本轮完成内容

1. 恢复 mission 上下文（state / checkpoints / NEXT-SESSION-PROMPT）。
2. 理解 4 张 OC 图：
   - `rin-01` 全身设定（三视图/配件/配色/便装）
   - `rin-02` 角度与表情
   - `rin-03` 动作四联
   - `rin-04` 机房 JK 主视觉（竖图）
3. 复制到 `public/gallery/`；Gallery 页：主视觉通栏 + 三设定表。
4. Profile：左侧 `rin-04` 立绘 + 右侧 STATUS/LIKES/SNS。
5. 首页 Gallery 卡片文案改为「無限凜设定与插画」。
6. 主视觉裁切：用户反馈「往下」→ 一度砍头 → 改为 `aspect-ratio: 4/3` + `object-position: center 12%`。
7. `npm run build` 11 页通过；mission 文档更新。

## 关键决策

| 决策 | 原因 |
| --- | --- |
| 真图进 `public/gallery/` | 站点可访问；源图保留在 prompt-debug 区 |
| Gallery 第一版无灯箱 | 用户本轮只要放图；Modal 明确延期 |
| Profile 复用 rin-04 | 机房立绘最适合档案页 |
| 主视觉优先露头 | 竖图 cover 易裁切；锚点偏上 + 框略高 |

## 第一版已交付 vs 延期

**本轮第一版已交付：**

- Gallery 四张真图网格（主视觉 + 设定表）
- Profile 立绘双栏
- 主视觉裁切调优
- 首页入口文案

**明确延期（不要当 bug）：** 见 `deferred/shell-v1-out-of-scope.md` 与 `deferred/mvp-out-of-scope.md`

- Gallery Modal 灯箱
- Gallery 补图 / PNG→WebP
- Contact 真发送
- Classic 下线、博客换 Shell 壳、分类/搜索/RSS/评论/主题切换/多工具/自定义域名等

## 关键文件 / 产物

```text
public/gallery/rin-01-global-design.png
public/gallery/rin-02-angles-expressions.png
public/gallery/rin-03-actions.png
public/gallery/rin-04-jk-server-room.png
src/pages/gallery/index.astro
src/pages/profile/index.astro
src/pages/index.astro
src/styles/shell/shell.css
.devflow/static-blog-github-pages/**  # 本轮文档
```

## 风险与注意

1. 链接必须走 `import.meta.env.BASE_URL`（含图片 `src`）。
2. 四张 PNG 约 8MB，首次打开 Gallery 可能偏慢。
3. 勿把 `zzz-prompt-debug/origin/OC/**` 调试源与其它 mission 无关改动误提交。
4. 主视觉裁切再调只改 `shell.css` 中 featured 相关规则。

## 立即下一步

1. 新对话读 `state.md` + `checkpoints.md` + 本 handoff。
2. 可选：`npm run dev` 再目视 Gallery/Profile。
3. 可选：push + Pages 线上验收。
4. 勿默认做 deferred（灯箱、Contact 真发送、压图等）。

## 恢复指引

```text
1. state.md
2. checkpoints.md
3. handoffs/index.md → 003（本文件）
4. deferred/shell-v1-out-of-scope.md（边界）
5. 需要完整脉络再读 development-overview.md
```
