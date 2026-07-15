# Proposal · 無限凜静态博客 + 小工具

## 背景

仓库 `mine-blog` 几乎为空，需要基于 GitHub Pages 搭建纯静态个人站。站点品牌为 **無限凜**，同时承载博客与浏览器端小工具；视觉需遵循自有 `DESIGN.md`（结构参考 awesome-design-md / Open Design），色板来自「无限凛 / Mugen Rin」角色标准色彩体系。

Align 与 Plan 已确认，见：

- `.devflow/static-blog-github-pages/plans/2026-07-15-无限凛-static-blog-align.md`
- `.devflow/static-blog-github-pages/plans/2026-07-15-无限凛-static-blog-plan.md`

## 目标

交付可部署到 GitHub Pages 的 MVP 静态站：

1. 首页：博客 / 工具并列入口  
2. 博客：列表 + 详情 + 1～2 篇示例文  
3. 工具：列表 + JSON 格式化（格式化 / 压缩 / 错误提示）  
4. 设计系统：`DESIGN.md` + CSS tokens（主强调 `#39FF14`）  
5. CI：GitHub Actions 构建并发布 Pages  

## 范围

| 包含 | 说明 |
| --- | --- |
| 技术栈 | Astro SSG + `@astrojs/react` 岛屿；npm |
| 部署 | Project Pages，`base: '/mine-blog/'` |
| 语言 | 界面/正文简体中文；品牌名繁体 **無限凜** |
| 页面 | `/`、`/blog`、`/blog/[slug]`、`/tools`、`/tools/json`、404 |

## 非目标

- 请求时 SSR、服务端 API  
- 整站 Ant Design / Umi / Next 主栈  
- 标签分类、搜索、RSS、评论、主题切换、关于页  
- 多个小工具、数据持久化、自定义域名（可后续）  

## 边界场景

| 场景 | 期望 |
| --- | --- |
| 非法 JSON | 工具展示错误信息，不白屏 |
| `draft: true` 文章 | 构建产物中不出现 |
| 错误 `base` | 本地 preview 与线上 CSS/链接可能 404 → 验收必须带 base 检查 |
| 空工具列表以外 | MVP 固定至少 1 个 JSON 工具 |

## 开放问题

| 项 | 状态 |
| --- | --- |
| GitHub 用户名用于 `site` | Apply 时从 `git remote` / `gh` 解析 |
| 是否立即 push 触发 Pages | 需用户允许 push；仓库需将 Pages source 设为 Actions |
| 包管理器 | 已定 npm（关闭） |
