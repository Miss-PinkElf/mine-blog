# 下次对话提示词 · static-blog-github-pages

直接复制到新对话即可。

---

请继续 mission **`static-blog-github-pages`**（無限凜 · GitHub Pages 静态博客+小工具）。

## 恢复读取（Context Budget）

**默认热路径（先读）：**

1. `.devflow/static-blog-github-pages/state.md`
2. `.devflow/static-blog-github-pages/checkpoints.md`

**再读：**

3. `.devflow/static-blog-github-pages/handoffs/index.md` → 最新 handoff  
4. 需要任务清单时：`spec/tasks.md`  
5. 需要延期边界：`deferred/mvp-out-of-scope.md`  
6. 需要完整脉络才读：`development-overview.md`

使用 **devflow**；语言 **简体中文**；未允许不 commit。

## 当前进度

- Align / Plan / Spec / 本地 Apply（T1–T9）**已完成**
- 功能分支：`feat/mugen-rin-astro-mvp`
- 本地：`npm run build` → 7 页，`base: /mine-blog/`
- 站名：**無限凜**；accent：`#39FF14`；首个工具：JSON 格式化
- GitHub：`Miss-PinkElf/mine-blog` → 预期 `https://Miss-PinkElf.github.io/mine-blog/`

## 优先事项（建议顺序）

1. 确认本轮提交是否已在分支上；是否 **merge → main 并 push**
2. 仓库 **Settings → Pages → Source = GitHub Actions**
3. 看 Actions 是否绿；线上点验：首页双入口、博客、JSON 格式化/压缩/错误
4. 可选：`npm run preview` 本地带 base 再验一遍
5. 不要把 `deferred/mvp-out-of-scope.md` 里的项当成本轮默认范围

## 未完成 / 未上线

- [ ] 合并 main + push（若尚未）
- [ ] Pages 上线与 Actions 通过
- [ ] 线上验收清单勾选

## 明确延期（不要当 bug 漏做）

分类标签、关于页、搜索、RSS、评论、主题切换、多工具、自定义域名、SSR、整站 antd、UI 全繁体等 → 见 `deferred/mvp-out-of-scope.md`。

## 技术注意

- 链接必须走 `import.meta.env.BASE_URL`
- 改视觉先读根目录 `DESIGN.md` 与 `src/styles/tokens.css`
- 包管理：npm
- 协作：commit 需用户允许（除非用户当轮明确授权）

## 建议开场白（Agent）

先读 state + checkpoints + 最新 handoff，用三句话汇报：本地是否已提交、远端/Pages 状态、建议的下一步操作（合并或线上验收）。
