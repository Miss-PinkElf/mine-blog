# 下次对话提示词 · static-blog-github-pages

直接复制到新对话即可。

---

请继续 mission **`static-blog-github-pages`**（無限凜 · GitHub Pages 静态博客+小工具）。

## 恢复读取（Context Budget）

**默认热路径（先读）：**

1. `.devflow/static-blog-github-pages/state.md`
2. `.devflow/static-blog-github-pages/checkpoints.md`

**再读：**

3. `handoffs/index.md` → 最新 handoff（002）
4. 设计回顾：`zzz-prompt-debug/origin/blog/amashiro-design-analysis.md`
5. 延期边界：`deferred/shell-v1-out-of-scope.md` + `deferred/mvp-out-of-scope.md`
6. 完整脉络才读：`development-overview.md`

使用 **devflow**；语言 **简体中文**；未允许不 commit。

## 当前进度

- MVP + **Shell 主站迁移**已完成（本地）
- **Classic** `/classic/`：原极简入口（暂时保留）
- 共用：`/blog/*`、`/tools/*` + `PostCard` / `ToolCard` / `JsonFormatter` / `src/data/tools.ts`
- Shell：`/` `/profile/` `/gallery/` `/contact/`（菜单状态机 + Q 弹）
- `npm run build` → **11 页**
- 设计分析摘要已落盘；参考 amashiro **色系不抄**，accent 仍 `#39FF14`

## 优先事项（建议顺序）

1. `npm run dev` 目视：主站菜单开合、Classic、博客、JSON 工具
2. 确认本轮提交已在分支；是否 **merge → main 并 push**
3. 仓库 **Settings → Pages → Source = GitHub Actions**
4. 线上点验（若已部署）
5. **不要**把 deferred 项当成本轮默认范围

## 未完成 / 未上线

- [ ] Pages 上线与 Actions 通过（若尚未）
- [ ] 线上验收清单
- [ ] Contact 真发送、Gallery 真图等 → 见 deferred

## 明确延期（不要当 bug）

Contact 真通道、Gallery 真图/Modal、展示字体、角色 idle、抄对方素材、下线 Classic、博客改 Shell 壳、分类/搜索/RSS/评论/主题切换/多工具/自定义域名等 → `deferred/*`。

## 技术注意

- 链接：`import.meta.env.BASE_URL`
- 视觉：`DESIGN.md` + `src/styles/tokens.css` + `src/styles/shell/shell.css`
- 包管理：npm；Node 可用 `~/.nvm/versions/node/v24.13.1`
- 协作：commit 需用户允许（本轮收尾用户已授权提交相关文件）

## 建议开场白（Agent）

先读 state + checkpoints + 最新 handoff，用三句话汇报：双入口是否已提交、远端/Pages 状态、建议下一步（目视 polish 或上线）。
