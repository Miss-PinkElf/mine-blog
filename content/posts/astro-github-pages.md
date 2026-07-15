---
title: 用 Astro 部署到 GitHub Pages
description: 记录本站使用 Astro 静态构建，并通过 GitHub Pages 发布的基本思路。
pubDate: 2026-07-10
---

本站基于 **Astro** 构建，部署目标是 **GitHub Pages**。

## 关键配置

- `site`：仓库对应的 GitHub Pages 域名
- `base`：子路径 `/mine-blog/`，避免资源与链接在子目录下 404

## 构建与产物

本地执行：

```bash
npm run build
```

会在 `dist/` 生成静态 HTML / CSS / JS。将产物发布到 `gh-pages` 分支（或 Actions 指定目录）即可。

## 内容管理

文章放在 `content/posts/`，通过 Content Collections 校验 frontmatter，并生成列表页与详情页。

后续若增加标签、草稿预览等能力，也会建立在同一套 Content Layer 之上。
