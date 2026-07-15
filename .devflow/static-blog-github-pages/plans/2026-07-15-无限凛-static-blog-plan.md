# 無限凜 · 静态博客 + 小工具 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers-subagent-driven-development（推荐）或 executing-plans，按任务逐步实施。步骤使用 checkbox（`- [ ]`）追踪。  
> **仓库约定：** 未经用户明确允许不得 `git commit`；任务中的「提交」步骤一律改为「向用户确认是否提交」。  
> **Align 依据：** `.devflow/static-blog-github-pages/plans/2026-07-15-无限凛-static-blog-align.md`

**Goal:** 用 Astro SSG + React 岛屿搭建可部署到 GitHub Pages 的「無限凜」纯静态站：博客与工具并重、暗色赛博绿设计系统、JSON 格式化工具 MVP。

**Architecture:** 构建时静态生成全部页面；博客来自 Content Collections（Markdown）；站点壳层为 Astro 组件；JSON 工具为单一 React 岛屿；`DESIGN.md` 定义视觉契约并映射为 `tokens.css`；GitHub Actions 将 `dist/` 发布到 Project Pages（`base: '/mine-blog/'`）。

**Tech Stack:** Astro（最新稳定版）、`@astrojs/react`、React 18+、TypeScript、GitHub Pages + Actions；包管理器 **npm**（本机亦有 pnpm，CI 与文档统一 npm）。

---

## 文件结构总览（将创建/修改）

| 路径 | 职责 |
| --- | --- |
| `package.json` | 依赖与 scripts |
| `astro.config.mjs` | `site`、`base`、React 集成、静态输出 |
| `tsconfig.json` | TS 配置 |
| `DESIGN.md` | 無限凜视觉契约 |
| `src/styles/tokens.css` | CSS 变量（唯一色值来源） |
| `src/styles/global.css` | 全局排版与基础元素 |
| `src/content.config.ts` | posts collection schema |
| `content/posts/*.md` | 示例文章 |
| `src/layouts/BaseLayout.astro` | HTML 壳、引入样式、slot |
| `src/components/site/Header.astro` | 顶栏导航 |
| `src/components/site/Footer.astro` | 页脚 |
| `src/components/site/PostCard.astro` | 文章列表项 |
| `src/components/site/ToolCard.astro` | 工具列表项 |
| `src/components/react/JsonFormatter.tsx` | JSON 工具岛屿 |
| `src/pages/index.astro` | 首页 |
| `src/pages/blog/index.astro` | 博客列表 |
| `src/pages/blog/[...slug].astro` | 文章详情 |
| `src/pages/tools/index.astro` | 工具列表 |
| `src/pages/tools/json.astro` | JSON 工具页 |
| `src/pages/404.astro` | 404 |
| `public/favicon.svg` | 站点图标 |
| `.github/workflows/deploy-pages.yml` | 构建与部署 |
| `.gitignore` | 补充 `node_modules`、`dist`、`.astro` |

**不修改：** `AGENTS.md`、`.devflow/**`（过程记录可另更 mission 状态，不在本 plan 业务任务内强制）。

---

### Task 1: 脚手架 Astro + React

**Files:**
- Create: `package.json`、`astro.config.mjs`、`tsconfig.json`、`src/env.d.ts`
- Modify: `.gitignore`

- [ ] **Step 1: 在仓库根初始化 Astro 项目文件**

因仓库已有 `AGENTS.md` 等文件，**不要**在空目录乱覆盖协作文档。在仓库根执行：

```bash
npm create astro@latest . -- --template minimal --install=no --typescript=strict --git=false --yes
```

若 CLI 因非空目录拒绝，则改为**手工创建**下列最小文件（优先手工，避免 interactive）：

`package.json`：

```json
{
  "name": "mine-blog",
  "type": "module",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "astro dev",
    "build": "astro build",
    "preview": "astro preview"
  },
  "dependencies": {
    "astro": "^5.0.0",
    "@astrojs/react": "^4.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
  },
  "devDependencies": {
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "typescript": "^5.7.0"
  }
}
```

（实施时用 `npm info astro version` 核对并锁定合理最新兼容版本，避免故意装过旧包。）

`astro.config.mjs`：

```js
import { defineConfig } from 'astro/config';
import react from '@astrojs/react';

// Project Pages：仓库名 mine-blog
// 若日后改为 username.github.io 用户站，将 base 改为 '/'
export default defineConfig({
  site: 'https://example.github.io',
  base: '/mine-blog/',
  integrations: [react()],
  // 默认静态输出，无需 adapter
});
```

说明：`site` 在 Apply 时改为真实 GitHub 用户名对应域名（可用 `gh api user -q .login` 或询问用户）。临时用占位亦可，SEO 绝对 URL 非 MVP 阻塞。

`tsconfig.json`：

```json
{
  "extends": "astro/tsconfigs/strict",
  "compilerOptions": {
    "jsx": "react-jsx",
    "jsxImportSource": "react"
  },
  "include": [".astro/types.d.ts", "**/*"],
  "exclude": ["dist"]
}
```

`src/env.d.ts`：

```ts
/// <reference path="../.astro/types.d.ts" />
/// <reference types="astro/client" />
```

- [ ] **Step 2: 更新 `.gitignore`**

确保包含：

```gitignore
node_modules/
dist/
.astro/
.DS_Store
*.log
```

- [ ] **Step 3: 安装依赖**

```bash
npm install
```

Expected: 生成 `package-lock.json`，无 peer 致命错误。

- [ ] **Step 4: 放置占位首页并验证 dev**

临时 `src/pages/index.astro`：

```astro
---
const title = '無限凜';
---
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title}</title>
  </head>
  <body>
    <h1>{title}</h1>
    <p>脚手架 OK</p>
  </body>
</html>
```

```bash
npm run dev
```

Expected: 本地可打开，标题为無限凜。Ctrl+C 结束。

- [ ] **Step 5: 向用户确认是否提交**

示例说明（**仅在用户同意后执行**）：

```bash
git add package.json package-lock.json astro.config.mjs tsconfig.json src .gitignore
git commit -m "chore: 初始化 Astro 与 React 岛屿脚手架"
```

---

### Task 2: DESIGN.md + CSS tokens

**Files:**
- Create: `DESIGN.md`、`src/styles/tokens.css`、`src/styles/global.css`

- [ ] **Step 1: 编写 `DESIGN.md`（中文，九段结构）**

必须覆盖：

1. 视觉主题与氛围：开发者暗色极简；品牌 **無限凜**；黑底 + 赛博绿  
2. 色板与语义角色（与 Align 一致）：  
   - bg `#000000` / `#0A0A0A`  
   - surface `#1A1A1A`  
   - border `#404040`  
   - accent `#39FF14`  
   - neon-secondary `#00FF00`（少用）  
   - accent-soft `#50C878`  
   - highlight `#ADFF2F`  
   - text `#F5F5F5`、text-muted `#A0A0A0`  
3. 字体：sans 系统栈 + mono（工具区）  
4. 组件：按钮、链接、卡片、导航、输入框（暗色态）  
5. 布局：内容最大宽 ~48rem、间距刻度  
6. 深度：少阴影，靠边框分层  
7. 禁忌：正文不用荧光绿；不大面积铺 `#00FF00`；不整站 antd 默认皮肤  
8. 响应式：窄屏导航可换行/简化  
9. Agent 提示：改 UI 必须先读本文件与 `tokens.css`

- [ ] **Step 2: 编写 `src/styles/tokens.css`**

```css
:root {
  --color-bg: #000000;
  --color-bg-elevated: #0a0a0a;
  --color-surface: #1a1a1a;
  --color-border: #404040;
  --color-accent: #39ff14;
  --color-neon-secondary: #00ff00;
  --color-accent-soft: #50c878;
  --color-highlight: #adff2f;
  --color-text: #f5f5f5;
  --color-text-muted: #a0a0a0;

  --font-sans: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto,
    "PingFang SC", "Noto Sans SC", "Microsoft YaHei", sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;

  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-5: 1.5rem;
  --space-6: 2rem;
  --space-8: 3rem;

  --radius: 8px;
  --max-width: 48rem;
  --header-height: 3.5rem;
}
```

- [ ] **Step 3: 编写 `src/styles/global.css`**

```css
@import "./tokens.css";

*,
*::before,
*::after {
  box-sizing: border-box;
}

html {
  color-scheme: dark;
}

body {
  margin: 0;
  min-height: 100vh;
  font-family: var(--font-sans);
  background: var(--color-bg);
  color: var(--color-text);
  line-height: 1.6;
}

a {
  color: var(--color-accent);
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

main {
  width: min(100% - 2rem, var(--max-width));
  margin-inline: auto;
  padding-block: var(--space-6);
}

h1,
h2,
h3 {
  line-height: 1.25;
  font-weight: 600;
}

code,
pre {
  font-family: var(--font-mono);
}

:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}
```

- [ ] **Step 4: 自检**

确认无正文色设为 `#39ff14` / `#00ff00`。  
（本任务无需跑测试框架；后续布局引入 global 后目视验证。）

- [ ] **Step 5: 征得用户同意后再提交**

```bash
git add DESIGN.md src/styles
# git commit -m "feat: 添加無限凜 DESIGN.md 与 CSS tokens"
```

---

### Task 3: 布局与导航壳层

**Files:**
- Create: `src/layouts/BaseLayout.astro`、`src/components/site/Header.astro`、`src/components/site/Footer.astro`、`public/favicon.svg`
- Modify: `src/pages/index.astro`（先接到布局）

- [ ] **Step 1: `Header.astro`**

```astro
---
import { base } from "astro:config/client";
// 若 base 在组件中不便取，使用 import.meta.env.BASE_URL
const baseUrl = import.meta.env.BASE_URL;
const pathname = Astro.url.pathname;

const links = [
  { href: baseUrl, label: "首页" },
  { href: `${baseUrl}blog/`, label: "博客" },
  { href: `${baseUrl}tools/`, label: "工具" },
];

function isActive(href: string) {
  if (href === baseUrl) return pathname === baseUrl || pathname === `${baseUrl}`.replace(/\/$/, "") || pathname === "/";
  return pathname.startsWith(href);
}
---
<header class="site-header">
  <div class="inner">
    <a class="brand" href={baseUrl}>無限凜</a>
    <nav aria-label="主导航">
      {
        links.map((l) => (
          <a href={l.href} class:list={[{ active: isActive(l.href) }]}>
            {l.label}
          </a>
        ))
      }
    </nav>
  </div>
</header>

<style>
  .site-header {
    border-bottom: 1px solid var(--color-border);
    background: var(--color-bg-elevated);
    position: sticky;
    top: 0;
    z-index: 10;
  }
  .inner {
    width: min(100% - 2rem, var(--max-width));
    margin-inline: auto;
    height: var(--header-height);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-4);
  }
  .brand {
    font-weight: 700;
    color: var(--color-text);
    letter-spacing: 0.04em;
  }
  .brand:hover {
    color: var(--color-accent);
    text-decoration: none;
  }
  nav {
    display: flex;
    gap: var(--space-4);
  }
  nav a {
    color: var(--color-text-muted);
    font-size: 0.95rem;
  }
  nav a.active,
  nav a:hover {
    color: var(--color-accent);
    text-decoration: none;
  }
</style>
```

注意：`isActive` 在带 `base` 时容易误判，实施时以 `import.meta.env.BASE_URL` 为准实测修正。

- [ ] **Step 2: `Footer.astro`**

```astro
---
const year = new Date().getFullYear();
---
<footer class="site-footer">
  <div class="inner">
    <span>© {year} 無限凜</span>
    <span class="muted">博客 · 小工具</span>
  </div>
</footer>

<style>
  .site-footer {
    border-top: 1px solid var(--color-border);
    margin-top: auto;
  }
  .inner {
    width: min(100% - 2rem, var(--max-width));
    margin-inline: auto;
    padding-block: var(--space-5);
    display: flex;
    justify-content: space-between;
    gap: var(--space-3);
    color: var(--color-text-muted);
    font-size: 0.875rem;
  }
  .muted {
    opacity: 0.85;
  }
</style>
```

- [ ] **Step 3: `BaseLayout.astro`**

```astro
---
import Header from "../components/site/Header.astro";
import Footer from "../components/site/Footer.astro";
import "../styles/global.css";

interface Props {
  title?: string;
  description?: string;
}

const {
  title = "無限凜",
  description = "無限凜 — 博客与小工具",
} = Astro.props;

const fullTitle = title === "無限凜" ? title : `${title} · 無限凜`;
---
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="description" content={description} />
    <link rel="icon" type="image/svg+xml" href={`${import.meta.env.BASE_URL}favicon.svg`} />
    <title>{fullTitle}</title>
  </head>
  <body class="layout">
    <Header />
    <main>
      <slot />
    </main>
    <Footer />
  </body>
</html>

<style>
  .layout {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }
</style>
```

- [ ] **Step 4: 简易 `public/favicon.svg`**

黑底 + 绿色小块或「∞」示意即可，例如：

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect width="32" height="32" fill="#000"/>
  <circle cx="16" cy="16" r="8" fill="none" stroke="#39FF14" stroke-width="2"/>
</svg>
```

- [ ] **Step 5: 首页改用布局并 `npm run dev` 验收**

```astro
---
import BaseLayout from "../layouts/BaseLayout.astro";
---
<BaseLayout title="無限凜" description="無限凜 — 博客与小工具">
  <h1>無限凜</h1>
  <p>脚手架布局验收</p>
</BaseLayout>
```

Expected: 顶栏有無限凜与三导航，背景黑、强调绿链接。

- [ ] **Step 6: 征得同意后提交**

```bash
# git commit -m "feat: 添加 BaseLayout 与站点导航壳层"
```

---

### Task 4: 博客 Content Collections + 示例文

**Files:**
- Create: `src/content.config.ts`、`content/posts/welcome.md`、`content/posts/astro-github-pages.md`  
- Create: `src/components/site/PostCard.astro`  
- Create: `src/pages/blog/index.astro`、`src/pages/blog/[...slug].astro`

- [ ] **Step 1: `src/content.config.ts`（Astro 5 写法）**

```ts
import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

const posts = defineCollection({
  loader: glob({ pattern: "**/*.{md,mdx}", base: "./content/posts" }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    draft: z.boolean().optional().default(false),
  }),
});

export const collections = { posts };
```

若当前 Astro 小版本 loader API 不同，按官方「Content Collections」文档调整，但 **字段保持一致**。

- [ ] **Step 2: 两篇示例 Markdown**

`content/posts/welcome.md`：

```markdown
---
title: 欢迎来到無限凜
description: 站点上线说明：博客与小工具并重的静态空间。
pubDate: 2026-07-15
---

这里是 **無限凜** 的第一篇文章。

本站使用 Astro 静态生成，部署在 GitHub Pages：适合写笔记，也承载纯前端小工具。
```

`content/posts/astro-github-pages.md`：

```markdown
---
title: 为什么用 Astro 做 GitHub Pages
description: 构建时生成 HTML，托管方只负责发文件。
pubDate: 2026-07-14
---

GitHub Pages 不是 SSR 服务器。Astro 默认在构建阶段输出 HTML，与静态托管一致。

需要交互时，用 React 岛屿局部水合——例如本站的 JSON 工具。
```

- [ ] **Step 3: `PostCard.astro`**

```astro
---
interface Props {
  title: string;
  description: string;
  pubDate: Date;
  href: string;
}
const { title, description, pubDate, href } = Astro.props;
const date = pubDate.toLocaleDateString("zh-CN", {
  year: "numeric",
  month: "long",
  day: "numeric",
});
---
<article class="card">
  <h2><a href={href}>{title}</a></h2>
  <time datetime={pubDate.toISOString()}>{date}</time>
  <p>{description}</p>
</article>

<style>
  .card {
    border: 1px solid var(--color-border);
    background: var(--color-surface);
    border-radius: var(--radius);
    padding: var(--space-5);
  }
  .card h2 {
    margin: 0 0 var(--space-2);
    font-size: 1.15rem;
  }
  .card h2 a {
    color: var(--color-text);
  }
  .card h2 a:hover {
    color: var(--color-accent);
    text-decoration: none;
  }
  time {
    color: var(--color-text-muted);
    font-size: 0.85rem;
  }
  p {
    margin: var(--space-3) 0 0;
    color: var(--color-text-muted);
  }
</style>
```

- [ ] **Step 4: 博客列表页**

```astro
---
import { getCollection } from "astro:content";
import BaseLayout from "../../layouts/BaseLayout.astro";
import PostCard from "../../components/site/PostCard.astro";

const posts = (await getCollection("posts", ({ data }) => !data.draft)).sort(
  (a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf(),
);
const base = import.meta.env.BASE_URL;
---
<BaseLayout title="博客" description="無限凜的文章列表">
  <h1>博客</h1>
  <ul class="list">
    {
      posts.map((post) => (
        <li>
          <PostCard
            title={post.data.title}
            description={post.data.description}
            pubDate={post.data.pubDate}
            href={`${base}blog/${post.id}/`}
          />
        </li>
      ))
    }
  </ul>
</BaseLayout>

<style>
  h1 {
    margin-top: 0;
  }
  .list {
    list-style: none;
    padding: 0;
    margin: var(--space-5) 0 0;
    display: grid;
    gap: var(--space-4);
  }
</style>
```

说明：`post.id` / `post.slug` 随 Astro 版本而异；实施时 `console` 或文档确认列表链接与详情 `getStaticPaths` 使用同一标识。

- [ ] **Step 5: 文章详情页**

```astro
---
import { getCollection, render } from "astro:content";
import BaseLayout from "../../layouts/BaseLayout.astro";

export async function getStaticPaths() {
  const posts = await getCollection("posts", ({ data }) => !data.draft);
  return posts.map((post) => ({
    params: { slug: post.id },
    props: { post },
  }));
}

const { post } = Astro.props;
const { Content } = await render(post);
const date = post.data.pubDate.toLocaleDateString("zh-CN", {
  year: "numeric",
  month: "long",
  day: "numeric",
});
---
<BaseLayout title={post.data.title} description={post.data.description}>
  <article class="prose">
    <h1>{post.data.title}</h1>
    <time datetime={post.data.pubDate.toISOString()}>{date}</time>
    <div class="body">
      <Content />
    </div>
  </article>
</BaseLayout>

<style>
  .prose h1 {
    margin-bottom: var(--space-2);
  }
  time {
    color: var(--color-text-muted);
    font-size: 0.9rem;
  }
  .body {
    margin-top: var(--space-6);
  }
  .body :global(a) {
    color: var(--color-accent);
  }
  .body :global(p) {
    color: var(--color-text);
  }
  .body :global(code) {
    background: var(--color-surface);
    padding: 0.1em 0.35em;
    border-radius: 4px;
  }
</style>
```

路由文件名：`src/pages/blog/[...slug].astro` 或 `[slug].astro`，与 `params.slug` 一致。若 `post.id` 含路径，优先 `[...slug]`。

- [ ] **Step 6: 验证**

```bash
npm run dev
```

打开 `/mine-blog/blog/`（dev 下 base 是否带前缀以 Astro 行为为准；本地常见为 `http://localhost:4321/mine-blog/blog/`）。

Expected: 两篇文章列表；点进详情正文可读。

- [ ] **Step 7: 征得同意后提交**

```bash
# git commit -m "feat: 博客 Content Collections 与示例文章"
```

---

### Task 5: 首页双入口

**Files:**
- Modify: `src/pages/index.astro`

- [ ] **Step 1: 实现首页**

```astro
---
import { getCollection } from "astro:content";
import BaseLayout from "../layouts/BaseLayout.astro";
import PostCard from "../components/site/PostCard.astro";

const base = import.meta.env.BASE_URL;
const posts = (await getCollection("posts", ({ data }) => !data.draft))
  .sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf())
  .slice(0, 2);
---
<BaseLayout>
  <section class="hero">
    <p class="eyebrow">Mugen Rin</p>
    <h1>無限凜</h1>
    <p class="lead">中文优先的静态小站：写博客，也放纯前端小工具。</p>
  </section>

  <section class="entries" aria-label="主要入口">
    <a class="entry" href={`${base}blog/`}>
      <h2>博客</h2>
      <p>笔记与长文</p>
    </a>
    <a class="entry" href={`${base}tools/`}>
      <h2>工具</h2>
      <p>浏览器内小工具</p>
    </a>
  </section>

  {
    posts.length > 0 && (
      <section class="recent">
        <h2>最近文章</h2>
        <ul>
          {posts.map((post) => (
            <li>
              <PostCard
                title={post.data.title}
                description={post.data.description}
                pubDate={post.data.pubDate}
                href={`${base}blog/${post.id}/`}
              />
            </li>
          ))}
        </ul>
      </section>
    )
  }
</BaseLayout>

<style>
  .hero {
    margin-bottom: var(--space-8);
  }
  .eyebrow {
    color: var(--color-accent);
    font-family: var(--font-mono);
    font-size: 0.85rem;
    letter-spacing: 0.08em;
    margin: 0 0 var(--space-2);
  }
  .hero h1 {
    margin: 0 0 var(--space-3);
    font-size: clamp(2rem, 5vw, 2.75rem);
  }
  .lead {
    color: var(--color-text-muted);
    margin: 0;
    max-width: 36rem;
  }
  .entries {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(14rem, 1fr));
    gap: var(--space-4);
    margin-bottom: var(--space-8);
  }
  .entry {
    display: block;
    border: 1px solid var(--color-border);
    background: var(--color-surface);
    border-radius: var(--radius);
    padding: var(--space-5);
    color: inherit;
    text-decoration: none;
    transition: border-color 0.15s ease;
  }
  .entry:hover {
    border-color: var(--color-accent);
    text-decoration: none;
  }
  .entry h2 {
    margin: 0 0 var(--space-2);
    color: var(--color-text);
  }
  .entry p {
    margin: 0;
    color: var(--color-text-muted);
  }
  .recent h2 {
    font-size: 1.1rem;
    color: var(--color-text-muted);
  }
  .recent ul {
    list-style: none;
    padding: 0;
    display: grid;
    gap: var(--space-4);
  }
</style>
```

- [ ] **Step 2: 目视验收** — 博客/工具两卡并列；最近文章最多 2 条。

- [ ] **Step 3: 征得同意后提交**

```bash
# git commit -m "feat: 首页博客与工具双入口"
```

---

### Task 6: 工具列表 + JSON 格式化岛屿

**Files:**
- Create: `src/components/site/ToolCard.astro`、`src/components/react/JsonFormatter.tsx`、`src/components/react/JsonFormatter.module.css`（可选，也可用内联 style 或全局类）  
- Create: `src/pages/tools/index.astro`、`src/pages/tools/json.astro`

- [ ] **Step 1: 工具元数据（可内联在 tools/index）**

```ts
// 写在 tools/index.astro 的 frontmatter
const base = import.meta.env.BASE_URL;
const tools = [
  {
    slug: "json",
    title: "JSON 格式化",
    description: "格式化、压缩与语法校验，数据仅在浏览器内处理。",
  },
];
```

- [ ] **Step 2: `ToolCard.astro`**

与 PostCard 类似：标题链接、描述；样式用 surface + border，hover 边框 accent。

- [ ] **Step 3: `tools/index.astro`**

列出 `tools` 数组，链接到 `${base}tools/${slug}/`。

- [ ] **Step 4: 实现 `JsonFormatter.tsx`**

```tsx
import { useMemo, useState } from "react";

const sample = '{\n  "hello": "無限凜"\n}';

export default function JsonFormatter() {
  const [input, setInput] = useState(sample);
  const [output, setOutput] = useState(sample);
  const [error, setError] = useState<string | null>(null);

  const status = useMemo(() => (error ? "error" : "ok"), [error]);

  function format() {
    try {
      const parsed = JSON.parse(input);
      setOutput(JSON.stringify(parsed, null, 2));
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "JSON 解析失败");
    }
  }

  function minify() {
    try {
      const parsed = JSON.parse(input);
      setOutput(JSON.stringify(parsed));
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "JSON 解析失败");
    }
  }

  function copyOutput() {
    void navigator.clipboard.writeText(output);
  }

  return (
    <div className="json-tool">
      <div className="actions">
        <button type="button" onClick={format}>
          格式化
        </button>
        <button type="button" onClick={minify}>
          压缩
        </button>
        <button type="button" onClick={copyOutput}>
          复制结果
        </button>
      </div>
      {error ? (
        <p className="error" role="alert">
          {error}
        </p>
      ) : (
        <p className="hint" data-status={status}>
          JSON 有效
        </p>
      )}
      <label className="field">
        <span>输入</span>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          spellCheck={false}
          rows={12}
        />
      </label>
      <label className="field">
        <span>输出</span>
        <textarea value={output} readOnly spellCheck={false} rows={12} />
      </label>
    </div>
  );
}
```

配套样式（可放在同文件底部由父页 scoped，或 `JsonFormatter.css` 在组件内 `import "./JsonFormatter.css"`）：

- 按钮：背景 surface、边框 border、文字 text；hover 边框/文字 accent  
- textarea：mono 字体、surface 背景、border  
- error：可用柔和红或 `accent-soft` 以外的醒目色；**不要**用大面积 neon 绿显示错误  

- [ ] **Step 5: `tools/json.astro`**

```astro
---
import BaseLayout from "../../layouts/BaseLayout.astro";
import JsonFormatter from "../../components/react/JsonFormatter";
---
<BaseLayout title="JSON 格式化" description="浏览器内 JSON 格式化与压缩">
  <h1>JSON 格式化</h1>
  <p class="desc">数据只在本地处理，不会上传服务器。</p>
  <JsonFormatter client:load />
</BaseLayout>

<style>
  .desc {
    color: var(--color-text-muted);
    margin-top: 0;
  }
</style>
```

- [ ] **Step 6: 手动验收**

1. 格式化 sample → 缩进正确  
2. 压缩 → 单行  
3. 输入 `{"a":` → 显示错误，不崩溃  
4. `npm run build` 中该页成功产出  

- [ ] **Step 7: 征得同意后提交**

```bash
# git commit -m "feat: 工具列表与 JSON 格式化岛屿"
```

---

### Task 7: 404 页

**Files:**
- Create: `src/pages/404.astro`

- [ ] **Step 1: 简单 404**

```astro
---
import BaseLayout from "../layouts/BaseLayout.astro";
const base = import.meta.env.BASE_URL;
---
<BaseLayout title="未找到" description="页面不存在">
  <h1>404</h1>
  <p>这个页面不存在。</p>
  <p><a href={base}>返回首页</a></p>
</BaseLayout>
```

- [ ] **Step 2: build 确认生成 `404.html`（GitHub Pages 可识别）**

```bash
npm run build
ls dist/404.html
```

Expected: 文件存在。

---

### Task 8: GitHub Pages 工作流与 site 配置

**Files:**
- Create: `.github/workflows/deploy-pages.yml`
- Modify: `astro.config.mjs`（写入真实 `site`）

- [ ] **Step 1: 确认 GitHub 用户名 / 仓库名**

```bash
git remote -v
# 若可用：
gh api user -q .login
```

将 `astro.config.mjs` 的 `site` 设为 `https://<login>.github.io`，`base` 保持 `'/mine-blog/'`（与仓库名一致；若仓库改名则同步改 base）。

- [ ] **Step 2: 工作流文件**

`.github/workflows/deploy-pages.yml`：

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "22"
          cache: npm
      - name: Install
        run: npm ci
      - name: Build
        run: npm run build
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: dist

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy
        id: deployment
        uses: actions/deploy-pages@v4
```

- [ ] **Step 3: 本地生产预览**

```bash
npm run build
npm run preview
```

在 preview URL 下点遍导航与 JSON 工具，确认 **带 base 路径** 时 CSS/链接不 404。

- [ ] **Step 4: 提醒用户仓库设置**

用户需在 GitHub：Settings → Pages → Source = **GitHub Actions**。  
合并/推送 `main` 后看 Actions 是否绿。

- [ ] **Step 5: 征得同意后提交工作流与配置**

```bash
# git commit -m "ci: 添加 GitHub Pages 部署工作流"
```

---

### Task 9: 端到端验收（Verification）

对照 Align 成功标准，全部勾选：

- [ ] **Step 1: 本地路由**

| 路径（含 base） | 期望 |
| --- | --- |
| `/mine-blog/` | 雙入口 + 最近文章 |
| `/mine-blog/blog/` | 2 篇文章 |
| `/mine-blog/blog/<id>/` | 正文 |
| `/mine-blog/tools/` | JSON 工具卡片 |
| `/mine-blog/tools/json/` | 格式化/压缩/错误 |

- [ ] **Step 2: 视觉**

暗色背景、accent 链接/按钮、正文非荧光绿、无 antd。

- [ ] **Step 3: 产物**

```bash
npm run build
```

Expected: exit 0；`dist/` 含 index、blog、tools、404。

- [ ] **Step 4: 更新 mission 状态（Apply 收尾时）**

更新 `.devflow/static-blog-github-pages/state.md`：阶段 → Verify/Close 相关描述；勾选 align 中成功标准。

- [ ] **Step 5: 询问用户是否 commit / push**

禁止擅自 push 到 origin。

---

## 实施顺序与依赖

```text
Task 1 脚手架
  → Task 2 DESIGN/tokens
  → Task 3 布局导航
  → Task 4 博客
  → Task 5 首页
  → Task 6 工具+JSON
  → Task 7 404
  → Task 8 Pages CI
  → Task 9 验收
```

Tasks 5 依赖 3+4；Task 6 依赖 3；Task 8 依赖 build 全绿。

## 包管理器与 Node

- 本地与 CI 统一 **npm** + `package-lock.json`  
- Node 建议 22 LTS（与 workflow 一致）

## Plan Self-Review

| 检查 | 结果 |
| --- | --- |
| Align §3.1 覆盖 | 壳层、首页、博客、工具、DESIGN、部署均有 Task |
| Align 延后项 | 未写入实现任务 |
| 色板/主强调 | Task 2 固定 `#39FF14` |
| base 路径 | Task 1/8 明确 `/mine-blog/` |
| 占位符 | 无 TBD；`site` 域名在 Task 8 用 remote/gh 解析 |
| commit 策略 | 符合 AGENTS：须用户允许 |

---

## 执行交接

Plan 已保存至：

`.devflow/static-blog-github-pages/plans/2026-07-15-无限凛-static-blog-plan.md`

**执行方式二选一：**

1. **Subagent-Driven（推荐）** — 每任务独立推进并在任务间审查  
2. **Inline Execution** — 本会话按任务连续实施，关键节点停顿验收  

你更想用哪一种？确认后进入 Apply（重型路径下通常还需 `openspec-propose` 生成 proposal/design/tasks；若你希望 **轻量加速：plan 已足够细则直接 Apply**，请明确说「跳过正式 spec 三件套，按 plan 实施」，我再按你的选择推进）。
