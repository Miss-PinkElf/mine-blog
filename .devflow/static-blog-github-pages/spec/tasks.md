# Tasks · 無限凜静态博客 + 小工具

> 详细步骤见：`plans/2026-07-15-无限凛-static-blog-plan.md`  
> 约定：不擅自 `git commit` / `git push`。

## 实施任务

- [x] **T1 脚手架** — Astro + React、`base: '/mine-blog/'`、`site` 已配置；build 通过
- [x] **T2 设计系统** — `DESIGN.md` + `tokens.css` + `global.css`；accent `#39ff14`
- [x] **T3 布局导航** — BaseLayout / Header / Footer / favicon
- [x] **T4 博客** — Content Collections + 2 篇示例 + 列表/详情
- [x] **T5 首页** — 双入口 + 最近文章
- [x] **T6 工具** — 工具列表 + JsonFormatter 岛屿
- [x] **T7 404** — `404.astro` → `dist/404.html`
- [x] **T8 部署** — `.github/workflows/deploy-pages.yml`
- [x] **T9 验收** — 2026-07-15 主会话验收通过（见下）

## 验证（T9 结果）

| 项 | 结果 |
| --- | --- |
| `npm run build` | ✅ exit 0，7 pages |
| 路由产物 | ✅ index / blog×3 / tools×2 / 404 |
| base 链接 | ✅ `/mine-blog/...` |
| DESIGN + tokens | ✅ accent `#39ff14` |
| JSON 逻辑冒烟 | ✅ 格式化/压缩/非法错误 |
| 无 antd | ✅ |

## 待用户 / 下会话操作

1. ~~commit 本对话相关代码~~（收尾会话提交）  
2. 是否 merge 到 `main` 并 push（触发 Pages）  
3. 仓库 Settings → Pages → Source = GitHub Actions  
4. 线上点验 JSON 工具与导航  

延期范围见 `deferred/mvp-out-of-scope.md`，勿误当作未做完的 MVP。
