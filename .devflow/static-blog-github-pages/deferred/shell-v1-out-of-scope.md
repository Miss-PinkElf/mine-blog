# 延期 · Shell / 视觉借鉴（第一版之后）

> 来源：2026-07-17 amashiro 分析与壳迁移。第一版已交付：Shell 主站 + Classic 入口 + 共用 blog/tools + Q 弹/菜单状态机。

## 明确延期（不要当 bug 漏做）

| 项 | 说明 |
| --- | --- |
| Contact 真实发送 | 当前表单仅 UI + preventDefault；需表单服务或外部通道 |
| Gallery 真实插画 / 生成图 | **第一版已落地（2026-07-17）**：`public/gallery/` 四张 OC；**后续可补图**（非本轮默认） |
| Gallery 图压缩 / WebP | 当前 PNG 合计约 8MB；性能优化延期 |
| Gallery Modal 灯箱 | 参考站有 is-show Modal；真图已上，**灯箱明确延期** |
| 自定义展示字体（Montserrat 等） | 第一版系统栈 |
| 角色 idle 动画（fuwafuwa 等） | 偏萌，冷静开发者站默认不做 |
| 菜单全屏插画背景（对方素材） | 用几何/光晕替代，不抄素材 |
| Classic 入口移除或合并 | 用户要求暂时保留；以后再定是否下线 |
| 博客/工具页换用 Shell 壳 | 当前有意保持极简 BaseLayout 阅读区 |
| 把 Shell 动效迁入 BaseLayout 卡片 | 可选统一手感，非必须 |
| 设计分析英文版 | 中文摘要已落盘即可 |

## 仍属 MVP 延期（继承）

见 `deferred/mvp-out-of-scope.md`（分类、搜索、RSS、评论、主题切换、多工具、自定义域名等）。
