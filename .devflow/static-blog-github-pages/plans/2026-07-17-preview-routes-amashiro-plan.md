# 预览路由（amashiro 版式）Implementation Plan

> **For agentic workers:** 可按任务顺序 inline 实施。Steps 用 checkbox 追踪。

**Goal:** 在 `/preview/*` 提供四页视觉预览（amashiro 版式语言 + 無限凜色系），正式站零改动。

**Architecture:** 独立 `PreviewLayout` + `src/styles/preview/` + `src/components/preview/`；页面放在 `src/pages/preview/`。只 import 现有 `tokens.css`，不修改 `global.css` 对正式站的影响路径（预览布局自行引入 preview 样式）。

**Tech Stack:** Astro 7 SSG、现有 CSS 变量 token、无新依赖。

---

## 文件地图

| 路径 | 职责 |
| --- | --- |
| `src/styles/preview/preview.css` | 预览全局：body 壳、竖排站名、菜单、标题、footer、工具类 |
| `src/layouts/PreviewLayout.astro` | 预览 HTML 壳、引入样式、插槽 |
| `src/components/preview/PreviewChrome.astro` | 角标、返回正式站、汉堡菜单 + 全屏导航、竖排站名 |
| `src/components/preview/PreviewFooter.astro` | 品牌化页脚 |
| `src/pages/preview/index.astro` | 预览首页 |
| `src/pages/preview/profile/index.astro` | 档案页 |
| `src/pages/preview/gallery/index.astro` | 画廊网格 |
| `src/pages/preview/contact/index.astro` | 联系表单皮 |

---

### Task 1: 预览样式与布局壳

**Files:**
- Create: `src/styles/preview/preview.css`
- Create: `src/layouts/PreviewLayout.astro`
- Create: `src/components/preview/PreviewChrome.astro`
- Create: `src/components/preview/PreviewFooter.astro`

- [x] **Step 1:** 写 `preview.css`：重置级局部、预览 body、fixed 菜单按钮（accent 底）、全屏导航、竖排 sitename、page title 底线、footer 抬升面。
- [x] **Step 2:** `PreviewChrome` 用原生 `details/summary` 控制导航展开。
- [x] **Step 3:** `PreviewLayout` 引入 tokens（via preview.css @import）与 chrome/footer。

### Task 2: 四页内容

**Files:**
- Create: `src/pages/preview/index.astro`
- Create: `src/pages/preview/profile/index.astro`
- Create: `src/pages/preview/gallery/index.astro`
- Create: `src/pages/preview/contact/index.astro`

- [x] **Step 1:** 首页：大 hero、入口卡链预览页 + 正式站 blog/tools。
- [x] **Step 2:** profile：STATUS / LIKES / SNS 三区占位。
- [x] **Step 3:** gallery：9 张占位卡网格。
- [x] **Step 4:** contact：表单 UI，`submit` 拦截并文案「预览不发送」。

### Task 3: 验证

- [x] **Step 1:** `npm run build` → 11 page(s)（原 7 + preview 4）。
- [x] **Step 2:** 正式页未改（仅新增 preview 路径与 mission 文档）。

### Task 4: 记录

- [x] 更新 `state.md` / `workflow.md` / `origin.md` / checkpoint。

---

## 验收清单

- [x] `/preview/` `/preview/profile/` `/preview/gallery/` `/preview/contact/` 可访问（build 产物）
- [x] 菜单可开闭并互链
- [x] 「返回正式站」指向 `BASE_URL`
- [x] 色 token 仍为無限凜
- [x] `npm run build` 通过
- [ ] 用户本地 dev 目视（人工）
