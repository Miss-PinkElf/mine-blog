# Development Overview · static-blog-github-pages

## 一句话

从空仓对齐并落地 **無限凜** GitHub Pages 静态站 MVP：Astro SSG + React 岛屿，博客与 JSON 工具并重，暗色赛博绿设计系统。

## 时间线

1. **需求**：纯静态博客 + 小工具；参考 awesome-design-md / Open Design。
2. **Align**：并重定位；选 Astro（用户愿学新栈）；暗色极简；骨架 MVP；JSON 工具；站名無限凜；色板采用用户 Mugen Rin 图；DESIGN.md 自写结构参考第三方。
3. **Plan**：九任务实施计划落盘。
4. **Spec**：proposal / design / tasks。
5. **Apply**：功能分支 `feat/mugen-rin-astro-mvp`；subagent（grok-4.5）串行 T1–T8；主会话 T9 验收 build 7 页。
6. **Close**：文档收尾、deferred/backlog、handoff、提交本对话相关代码。

## 关键决策（摘要）

详见 `decision-log.md`。核心：Astro+Pages SSG、不整站 antd、accent `#39FF14`、`base: '/mine-blog/'`、中文 UI + 繁体站名。

## 当前仓库事实

- 源码在分支 `feat/mugen-rin-astro-mvp`（收尾时提交）。
- 远端上线依赖 merge/push + Pages=Actions。
