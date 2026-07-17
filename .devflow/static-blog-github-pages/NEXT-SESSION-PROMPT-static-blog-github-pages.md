# 下次对话提示词 · static-blog-github-pages

直接复制到新对话即可。

---

请继续 mission **`static-blog-github-pages`**（無限凜 · GitHub Pages 静态博客+小工具）。

## 恢复读取（Context Budget）

**默认热路径（先读）：**

1. `.devflow/static-blog-github-pages/state.md`
2. `.devflow/static-blog-github-pages/checkpoints.md`

**再读：**

3. `handoffs/index.md` → 最新 handoff（**003**）
4. 延期边界：`deferred/shell-v1-out-of-scope.md` + `deferred/mvp-out-of-scope.md`
5. 完整脉络才读：`development-overview.md`

使用 **devflow**；语言 **简体中文**；未允许不 commit。

## 当前进度

- MVP + **Shell 主站** + **Classic** 双入口已完成
- 共用：`/blog/*`、`/tools/*` + 卡片/JSON 工具
- Shell：`/` `/profile/` `/gallery/` `/contact/`（菜单状态机 + Q 弹）
- **Gallery 第一版真图**：`public/gallery/rin-01`～`rin-04`（主视觉 + 三设定表）
- **Profile**：机房立绘双栏（复用 rin-04）
- 主视觉裁切：`4/3` + `object-position: center 12%`（优先露头）
- `npm run build` → **11 页**
- accent 仍 `#39FF14`；参考 amashiro **色系不抄**

## 优先事项（建议顺序）

1. `npm run dev` 目视：Gallery 主视觉/三格、Profile 立绘、菜单
2. 确认本轮提交已在分支；是否 **push / Pages**
3. 仓库 **Settings → Pages → Source = GitHub Actions**（若尚未）
4. 线上点验（若已部署）
5. **不要**把 deferred 项当成本轮默认范围

## 未完成 / 未上线

- [ ] Pages 上线与 Actions 通过（若尚未）
- [ ] 线上验收清单
- [ ] Contact 真发送、Gallery 灯箱等 → 见 deferred

## 第一版已交付（本轮）

- Gallery 四张真图（非占位色块）
- Profile 立绘布局
- 主视觉裁切调优

## 明确延期（不要当 bug）

Gallery **Modal 灯箱**、Gallery **补图/WebP 压缩**、Contact 真通道、展示字体、角色 idle、抄对方素材、下线 Classic、博客改 Shell 壳、分类/搜索/RSS/评论/主题切换/多工具/自定义域名等 → `deferred/*`。

## 技术注意

- 链接与图片：`import.meta.env.BASE_URL`（例：`${base}gallery/rin-04-...png`）
- 视觉：`DESIGN.md` + `src/styles/tokens.css` + `src/styles/shell/shell.css`
- 主视觉再调：`.shell-gallery__item--featured` 与 `object-position`
- 包管理：npm；Node 可用 `~/.nvm/versions/node/v24.13.1`
- 协作：commit 需用户允许（收尾轮用户已授权提交本对话相关文件）

## 建议开场白（Agent）

先读 state + checkpoints + handoff 003，用三句话汇报：Gallery/Profile 真图是否已提交、远端/Pages 状态、建议下一步（polish 或上线；勿默认灯箱）。
