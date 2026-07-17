# Handoff · 002 · Shell 迁移与视觉续作收尾

- **时间**：2026-07-17
- **Mission**：`static-blog-github-pages`
- **状态标记**：active（最新）
- **前序**：`2026-07-15-001-mvp-apply-close.md`（superseded 作为历史）

## 当前目标

無限凜静态站已具备 **Shell 主站 + Classic 极简入口 + 共用博客/工具**；下一对话可 polish、上线或扩展内容。

## 当前阶段

Close / 会话交接。本轮视觉分析、实验预览、主站迁移与文档收尾完成。

## 本轮完成内容

1. 分析 amashiro.com：色板、版式、动效（Q 弹 scale）、菜单状态机（非路由）。
2. `/preview/*` 实验 → 用户认可后 **迁移为主站 Shell**。
3. 原极简首页保留为 `/classic/`；`/blog/*` `/tools/*` 共用组件与数据。
4. 动效：`--ease-pop` 等；菜单：btn + bg + nav 的 opened/closed。
5. 设计摘要：`zzz-prompt-debug/origin/blog/amashiro-design-analysis.md`。
6. mission 文档、deferred、handoff、NEXT-SESSION-PROMPT 更新；本轮相关代码提交。

## 关键决策

| 决策 | 原因 |
| --- | --- |
| Shell + Classic 双入口 | 迁移新壳且暂留原入口 |
| blog/tools 用 BaseLayout | 阅读/工具区保持极简 |
| 菜单状态机同构 amashiro | 开合不换 URL |
| 色系不抄参考站 | 用户锁定無限凜 token |

## 关键文件 / 产物

```text
src/layouts/ShellLayout.astro
src/components/shell/*
src/styles/shell/shell.css
src/pages/index.astro          # Shell 首页
src/pages/classic/index.astro
src/pages/profile|gallery|contact/
src/data/tools.ts
src/components/site/Header.astro / Footer.astro
zzz-prompt-debug/origin/blog/* # prompt + 分析 + 附图
.devflow/static-blog-github-pages/**  # 本轮文档
```

## 第一版已交付 vs 延期

**第一版已交付：**

- Shell 主站壳（菜单状态机 + Q 弹）
- Classic 极简入口
- 共用博客列表/详情、工具列表/JSON
- Profile / Gallery / Contact 壳页（占位内容可接受）
- 设计分析文档

**明确延期：** 见 `deferred/shell-v1-out-of-scope.md` 与 `deferred/mvp-out-of-scope.md`  
（Contact 真发送、Gallery 真图与 Modal、展示字体、角色 idle、Pages 自定义域名等）

## 风险与注意

1. 链接必须走 `import.meta.env.BASE_URL`。
2. 改视觉：`DESIGN.md` + `tokens.css` + `styles/shell/shell.css`。
3. 勿把 `zzz-prompt-debug/origin/OC/**` 等其它 mission 产物误提交。
4. Pages 若未开 Actions，线上仍可能不可用。

## 立即下一步

1. 新对话读 `state.md` + `checkpoints.md`。
2. `npm run dev` 点验：`/` 菜单、`/classic/`、blog、tools。
3. 可选：merge/push + Pages 线上验收。
4. 勿默认做 deferred 列表项。

## 恢复指引

```text
1. state.md
2. checkpoints.md
3. handoffs/index.md → 本文件
4. 设计回顾：zzz-prompt-debug/origin/blog/amashiro-design-analysis.md
5. 延期：deferred/shell-v1-out-of-scope.md
6. 完整脉络：development-overview.md
```

粘贴：`NEXT-SESSION-PROMPT-static-blog-github-pages.md`
