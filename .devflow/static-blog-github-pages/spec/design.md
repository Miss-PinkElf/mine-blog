# Design · 無限凜静态博客 + 小工具

## 总体思路

采用 **Astro 默认静态输出（SSG）** 生成全部 HTML，部署到 **GitHub Pages**（仅托管静态文件，不做请求时 SSR）。

- **内容**：Markdown → Content Collections → 博客页  
- **壳层**：Astro 布局 + 站点组件（Header / Footer / 卡片）  
- **交互**：仅 JSON 工具使用 React 岛屿（`client:load`）  
- **视觉**：`DESIGN.md`（品牌契约）→ `tokens.css`（运行时变量）→ 组件只引用变量  

GitHub 仓库：`Miss-PinkElf/mine-blog`  
建议配置：

```js
site: 'https://Miss-PinkElf.github.io',
base: '/mine-blog/',
```

## 结构与边界

```text
content/posts/          内容边界：只存文章
src/pages/              路由边界：SSG 页面
src/components/site/    展示边界：无客户端状态
src/components/react/   交互边界：仅工具
src/styles/             设计边界：token 唯一色值来源
DESIGN.md               文档边界：人与 Agent 的视觉约束
.github/workflows/      部署边界：build → Pages artifact
```

**禁止：** 在业务组件中硬编码 `#39FF14` 等品牌色（tokens 与 DESIGN 除外）。  
**禁止：** 整站引入 antd。

## 数据流与接口

### 博客

```text
content/posts/*.md
  → content.config.ts schema (title, description, pubDate, draft?)
  → getCollection('posts')
  → 列表 / 详情 / 首页「最近文章」
```

Frontmatter 契约：

| 字段 | 类型 | 必填 |
| --- | --- | --- |
| title | string | 是 |
| description | string | 是 |
| pubDate | date | 是 |
| draft | boolean | 否，默认 false |

### JSON 工具

```text
用户输入字符串
  → JSON.parse
  → 成功：JSON.stringify pretty | minify
  → 失败：展示 Error.message
```

无网络请求、无 localStorage（MVP）。

### 链接与 base

所有站内链接使用 `import.meta.env.BASE_URL` 拼接，避免 Project Pages 子路径下资源断裂。

## 复用点

| 复用 | 用途 |
| --- | --- |
| `BaseLayout.astro` | 全页 HTML、样式、Header/Footer |
| `PostCard.astro` | 列表与首页最近文章 |
| `ToolCard.astro` | 工具列表（便于后续加工具） |
| `tokens.css` | 全站颜色/间距/字体 |

## 风险与权衡

| 风险 | 权衡 / 缓解 |
| --- | --- |
| Astro Content Collections API 随版本变化 | 以当前 `astro` 稳定版文档为准；字段契约不变 |
| 霓虹绿可读性 | 正文禁用 accent 作字色；写入 DESIGN 禁忌 |
| Subagent 实现冲突 | 串行任务；禁止并行改同一批文件 |
| 未经允许 commit | 实现可落盘文件，commit 必须问用户 |
| main 上直接开发 | 建议功能分支 `feat/mugen-rin-astro-mvp`，合并前征得用户同意 |

## 与 Plan 对齐

实施任务顺序与粒度以 `plans/2026-07-15-无限凛-static-blog-plan.md` 的 Task 1–9 为准；`tasks.md` 为其可勾选摘要。
