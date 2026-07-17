# Development Overview · static-blog-github-pages

## 一句话

从空仓对齐并落地 **無限凜** GitHub Pages 静态站 MVP：Astro SSG + React 岛屿，博客与 JSON 工具并重，暗色赛博绿设计系统。

## 时间线

1. **需求**：纯静态博客 + 小工具；参考 awesome-design-md / Open Design。
2. **Align**：并重定位；选 Astro；暗色极简；骨架 MVP；JSON 工具；站名無限凜；Mugen Rin 色板；DESIGN.md。
3. **Plan / Spec / Apply MVP**：T1–T9；本地 build 7 页。
4. **2026-07-17 视觉续作**：分析 amashiro.com（色/版式/动效/菜单逻辑）→ `/preview` 实验 → Q 弹与状态机菜单 → **Shell 迁移主站** + **Classic 极简入口** + 共用 blog/tools。
5. **分析落盘**：`zzz-prompt-debug/origin/blog/amashiro-design-analysis.md`。
6. **Close**：文档与 handoff；提交本对话相关代码。

## 关键决策（摘要）

详见 `decision-log.md`。核心：Astro+Pages SSG、accent `#39FF14`、`base: '/mine-blog/'`、**Shell+Classic 双入口**、菜单状态机、借鉴不抄色。

## 当前仓库事实

- 本地 `npm run build` **11 页**（Shell 主站 + classic + blog/tools + 404）。
- 远端上线仍依赖 merge/push + Pages=Actions（若尚未完成）。
