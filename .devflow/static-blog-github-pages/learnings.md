# Learnings

## 2026-07-17 · 竖图主视觉与 object-position

- 竖图（约 2:3）塞进宽横幅时，`object-fit: cover` 极易砍头或砍腿。
- 调 `object-position` 时小步试（如 12%→20%），一次跳到 38% 容易整头出框。
- 更稳：略增高框（如 `16/10`→`4/3`）+ 锚点偏上，而不是只猛调百分比。
- 四张 PNG 合计约 8MB，Pages 可先用；后续可压 WebP / 缩略图。

## 2026-07-17 · 参考站分析与迁移顺序

- 先拆 **token / 布局 / 状态机 / 动效**，再做隔离预览路由，最后迁移主站，回退成本低。
- amashiro 菜单是 **class 状态机** 不是换页；Q 弹核心是 `cubic-bezier(.17,.67,0,1.85)` + hover/active scale 阶梯。
- 图片缩放应在 `overflow:hidden` 内对子元素 scale，避免布局抖。
- 关菜单时 transition 清零，避免「倒放」拖沓。

## 2026-07-15 · GitHub Pages 与渲染模型

- Pages **不是** SSR 运行时，只托管静态文件。
- Astro / Next 静态导出本质是 **构建时 SSG**，不是「用户访问时服务端渲染」。
- Project Pages 必须正确配置 `base`（本仓库 `/mine-blog/`），站内链接统一用 `import.meta.env.BASE_URL`。

## 2026-07-15 · DESIGN.md 用法

- awesome-design-md / Open Design：学**结构与约束写法**。
- 品牌色与气质：用無限凜自己的色板（用户提供的 Mugen Rin 体系），**不要**整份复制 Linear/Vercel DESIGN.md。
- 主强调 `#39FF14` 只用于 CTA/链接/焦点；正文禁用荧光绿字色。

## 2026-07-15 · Astro 7 Content Layer

- 使用 `src/content.config.ts` + `glob` loader；文章标识用 `post.id`。
- React 工具页用 `client:load` 岛屿即可，不必整站 CSR。

## 2026-07-15 · Subagent 实施

- 有详细 plan 时，按 Task 串行 subagent（禁止并行改同一批文件）效率可接受。
- 脚手架在非空仓库优先**手工文件**，避免 interactive `create astro` 覆盖协作文档。
