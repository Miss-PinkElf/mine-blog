# Align · 主站壳迁移 + 极简入口保留

- **日期**：2026-07-17
- **状态**：用户已确认

## 结论

1. **主站壳（Shell）**：由 `/preview` 实验版升级为正式壳，落在 `/`、`/profile/`、`/gallery/`、`/contact/`。
2. **极简入口（Classic）**：原 `BaseLayout` 首页迁到 `/classic/`，作为博客向的极简入口，暂时保留。
3. **共用路由与组件**：`/blog/*`、`/tools/*` 只有一套；`PostCard`、`ToolCard`、`JsonFormatter`、文章正文逻辑共用。
4. **阅读区布局**：博客与工具继续用 **BaseLayout（极简）**，减少阅读干扰；Shell 主站用菜单链过去。
5. **删除** 实验命名空间 `/preview/*`（逻辑并入主站）。

## 路由表

| 路径 | 布局 | 说明 |
| --- | --- | --- |
| `/` | Shell | 新主站首页 |
| `/profile/` `/gallery/` `/contact/` | Shell | 原 preview 页 |
| `/classic/` | Base | 原极简首页 |
| `/blog/` `/blog/[slug]/` | Base | 共用文章 |
| `/tools/` `/tools/json/` | Base | 共用工具 |
