# 無限凜 · GitHub Pages 静态博客 + 小工具 · Align 设计说明

> 状态：Align 已确认；Plan/Spec/Apply 已完成（本地 MVP）；收尾于 2026-07-15  
> Mission：`static-blog-github-pages`  
> 下一阶段：合并/push 与 GitHub Pages 线上验收（见 handoff）

---

## 1. 目标

在 GitHub Pages 上部署 **纯静态** 个人站点 **無限凜**：

- **博客** 与 **小工具** 信息架构并重（首页并列入口）
- 视觉为 **开发者暗色极简**，品牌色来自「无限凛 / Mugen Rin」角色标准色彩体系
- 技术上采用 **Astro SSG + 局部 React 岛屿**，便于学习新栈并服务双模块

## 2. 成功标准（MVP 完成定义）

- [ ] 本地可访问：首页、博客列表、文章详情、工具列表、JSON 工具
- [ ] 暗色主题 + 主强调色 `#39FF14`；无整站 Ant Design 默认皮肤
- [ ] 仓库内存在 `DESIGN.md` 与 `src/styles/tokens.css`，组件消费 CSS 变量而非散落魔法色
- [ ] JSON 工具：格式化、压缩、非法 JSON 错误提示；纯前端
- [ ] `astro build` 成功；GitHub Actions 可部署到 Pages
- [ ] 在 Project Pages 的 `base` 路径下资源与链接正确

## 3. 范围

### 3.1 本轮包含（MVP · 骨架优先）

| 模块 | 内容 |
| --- | --- |
| 品牌与壳层 | 站名 **無限凜**（繁体）；导航/正文 **简体中文**；顶栏 + 页脚 |
| 首页 | 短介绍 + 博客/工具双入口卡片；可选最近文章摘要 |
| 博客 | 列表 + 详情；Content Collections；1～2 篇示例 Markdown |
| 工具 | 列表页；首个工具 **JSON 格式化**（`/tools/json`） |
| 设计系统 | 自写 `DESIGN.md`（结构参考 awesome-design-md）+ tokens |
| 部署 | Astro 静态导出 + GitHub Actions → GitHub Pages |

### 3.2 明确延后（非本轮）

标签/分类归档、关于页、搜索、RSS、亮暗主题切换、评论、多工具、antd 局部引入、自定义域名、请求时 SSR。

## 4. 关键决策摘要

| 主题 | 决策 |
| --- | --- |
| 定位 | 博客 + 工具并重 |
| 技术栈 | Astro（SSG）+ React 岛屿；非 Next/Umi 主栈 |
| 渲染模型 | 构建时 SSG；GitHub Pages 仅静态托管（非请求时 SSR） |
| 视觉 | 开发者暗色极简 + Mugen Rin 色板 |
| 主强调色 | `#39FF14`（赛博绿）；`#00FF00` 为次级霓虹（少用） |
| DESIGN.md | 参考 awesome-design-md / Open Design 的**结构与写法**；内容按無限凜自写，不整份复制 Linear/Vercel |
| MVP 工具 | JSON 格式化 / 压缩 / 校验提示 |
| 语言 | 中文优先（界面简体；品牌名繁体無限凜） |
| 实现路径 | 方案 1：Content Collections + 自研 tokens + React 岛屿 |

色板附件：`.devflow/static-blog-github-pages/mugen-rin-color-system.jpg`

## 5. 信息架构

```text
/                 首页
/blog             文章列表
/blog/[slug]      文章详情
/tools            工具列表
/tools/json       JSON 格式化
404               简单未找到页
```

导航：首页 · 博客 · 工具。顶栏左侧为站名 **無限凜**。

## 6. 设计系统

### 6.1 策略

- **格式**：对齐 awesome-design-md / Stitch 常见章节（氛围、色板、字体、组件、布局、深度、禁忌、响应式、Agent 提示）
- **内容**：無限凜品牌 + 用户色板图，不照搬第三方品牌 token 全文
- **工程映射**：`DESIGN.md` → `src/styles/tokens.css` → 布局/组件只引用变量

### 6.2 语义色（已确认）

| 语义 | 值 | 说明 |
| --- | --- | --- |
| bg | `#000000` / `#0A0A0A` | 页面背景 |
| surface | `#1A1A1A` | 卡片/表面 |
| border / muted surface | `#404040` | 边框、次级面 |
| accent | `#39FF14` | 主 CTA、链接悬停、焦点 |
| neon-secondary | `#00FF00` | 装饰/代码点缀，少用 |
| accent-soft | `#50C878` | 次强调/成功感 |
| highlight | `#ADFF2F` | 高光点缀 |
| text | 近白（如 `#F5F5F5`） | 正文 |
| text-muted | 中灰 | 次要信息 |

**硬规则：**

- 长文、正文 **禁止** 使用荧光绿作为字色
- 荧光绿仅用于：按钮、链接、激活态、小标签、焦点环
- 大面积背景保持黑/近黑

### 6.3 字体（建议，Plan 可微调）

- 无衬线：系统栈或 Inter / Geist 一类现代 sans（最终在 DESIGN.md 写死）
- 等宽：工具区、JSON 编辑区使用 mono

## 7. 内容模型（博客）

`content/posts/*.md` frontmatter：

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `title` | 是 | 标题 |
| `description` | 是 | 列表摘要 |
| `pubDate` | 是 | 发布日期 |
| `draft` | 否 | `true` 时构建排除 |

MVP：1～2 篇简体中文示例文。

## 8. JSON 工具

| 项 | 约定 |
| --- | --- |
| 路径 | `/tools/json` |
| 实现 | `src/components/react/JsonFormatter.tsx`，Astro 中 `client:load` 或 `client:visible` |
| 能力 | 格式化（pretty）、压缩（minify）、`JSON.parse` 失败时展示错误 |
| 边界 | 无后端、无持久化（刷新清空可接受） |

## 9. 目录结构（目标态）

```text
mine-blog/
├── DESIGN.md
├── package.json
├── astro.config.mjs
├── tsconfig.json
├── public/
├── content/posts/
├── src/
│   ├── content.config.ts
│   ├── layouts/BaseLayout.astro
│   ├── components/site/          # Nav、Footer、卡片等 Astro 组件
│   ├── components/react/         # JsonFormatter.tsx
│   ├── pages/
│   │   ├── index.astro
│   │   ├── blog/index.astro
│   │   ├── blog/[...slug].astro
│   │   ├── tools/index.astro
│   │   ├── tools/json.astro
│   │   └── 404.astro
│   └── styles/tokens.css
│       global.css
└── .github/workflows/deploy-pages.yml
```

既有协作文件（`AGENTS.md`、`.devflow/` 等）保留，与站点源码并列。

## 10. 部署

| 项 | 约定 |
| --- | --- |
| 托管 | GitHub Pages（静态文件） |
| 形态 | Project Pages：`https://<owner>.github.io/mine-blog/` |
| `base` | `/mine-blog/`（若改为用户站根路径再调） |
| 构建 | `astro build` → `dist/` |
| CI | `main` push → GitHub Actions 构建并发布 |
| 仓库设置 | Pages source = GitHub Actions |

说明：GitHub Pages **不是** SSR 运行时；Astro 默认静态构建，与托管模型一致。

## 11. 架构要点

```text
Markdown (content) ──SSG──► 博客 HTML
Astro 布局/页面 ──SSG──► 壳层 HTML
React 岛屿 ──按需水合──► JSON 工具交互
DESIGN.md + tokens.css ──约束──► 全站视觉
build 产物 ──托管──► GitHub Pages
```

单元边界：

- **内容层**：只关心文章 frontmatter 与正文
- **展示层（Astro）**：路由、布局、列表渲染
- **交互层（React）**：仅工具页需要的状态与事件
- **设计层**：token 单一来源，禁止业务组件硬编码品牌色（除 tokens 定义处）

## 12. 风险与约束

| 风险 | 缓解 |
| --- | --- |
| `base` 配错导致 CSS/链接 404 | 配置 `base` + 本地用 preview 验；CI 后检查 Pages URL |
| 霓虹绿对比度/可读性 | DESIGN.md 硬规则；正文不用 accent 作字色 |
| 范围膨胀 | 严格按 §3.2 延后项；加工具另开任务 |
| Astro 学习成本 | MVP 页面少；React 仅一处岛屿 |

## 13. 验收清单（可测试）

1. `npm/pnpm install && dev`：五类页面可导航  
2. 打开示例文章：标题、日期、正文样式正常  
3. JSON 工具：输入合法 JSON → 格式化/压缩结果正确；输入 `{"a":` → 有错误提示  
4. `build` 无错误；`preview` 下带 base 路径可浏览  
5. Actions 部署后，线上首页与工具页可打开且样式加载成功  

## 14. 参考

- 用户需求与色板：`.devflow/static-blog-github-pages/origin.md`、同目录色板图  
- 决策记录：`.devflow/static-blog-github-pages/decision-log.md`  
- [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md)（DESIGN.md 结构参考）  
- Open Design / DESIGN.md 品牌契约思路（写法参考，非照搬其桌面产品）

---

## Self-Review（落盘自检）

| 检查项 | 结果 |
| --- | --- |
| 占位符 TBD/TODO | 无未决 TBD；字体具体家族允许 Plan 微调 |
| 内部一致性 | 路由、色板、栈、MVP 范围与对话确认一致 |
| 范围 | 单 mission 单 MVP，无需再拆子系统 |
| 歧义 | `base` 默认 `/mine-blog/`；包管理器未强绑，Plan 中固定为 npm 或 pnpm 其一 |

**结论：** Align 文档可提交用户审阅；通过后进入 `superpowers-writing-plans` 写实施计划。
