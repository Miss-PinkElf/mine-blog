# amashiro.com 设计与交互分析摘要

> **整理日期**：2026-07-17  
> **参考站**：https://amashiro.com/（及 `/profile/`、`/gallery/`、`/contact/`）  
> **原始需求**：`prompt-1.md`（分析 CSS/样式并借鉴，色系自用）、`prompt-2.md`（右上角菜单开合逻辑）  
> **用途**：作为無限凜（Mugen Rin）静态站视觉/交互借鉴的单一阅读摘要；**不照搬素材与色板**。

---

## 1. 站点定位与气质

| 项 | 说明 |
| --- | --- |
| 类型 | 插画师 / 角色 **官方站**（WordPress 定制主题 `amashiro_v0`） |
| 气质 | 明亮、日系、插画主导、官方周边感 |
| 信息密度 | 中低；大面积 KV / 装饰图优先于文字 |
| 与無限凜差异 | 参考站白/浅蓝；無限凜为 **暗底 + 赛博绿 `#39FF14`** |

**可借鉴**：版式语言、菜单状态机、缩放阶梯、入场节奏。  
**不可照搬**：色板、插画资源、字体强依赖、WordPress 实现。

---

## 2. 技术与资源结构

### 2.1 栈

- WordPress + 主题 `amashiro_v0`
- 样式：按页分包 CSS  
  - 首页：`.../css/index/style.css`  
  - Profile / Gallery / Contact：各有独立 `style.css`
- 脚本：公共 `lib.js`（含 jQuery 等）+ 各页 `app.bundle.js`  
  - Gallery 另有 `gallery/lib.js`（含 Masonry 等）
- 字体：Google Fonts — `Noto Sans JP`、`M PLUS 1p`、`Montserrat`
- 重置：destyle.css

### 2.2 布局语言

- **大量 `vw` 流体单位**（非 CSS Grid 主导）
- Flex + 绝对定位 + **背景图拼贴**
- 少用 `position: sticky`；菜单层多用 **fixed**

---

## 3. 设计风格（Design Style）

### 3.1 色板（参考站自身，映射时勿直接抄）

| 角色 | 代表色 | 用途 |
| --- | --- | --- |
| 正文 | `#071828` | 深蓝黑文字 |
| 主强调 | `#1abbde` | 菜单钮、交互青 |
| 辅蓝 | `#7a98c9` / `#1464ae` | 标题线、渐变字 |
| 浅底 | `#eef7ff` / `#cce2f1` | Footer、浅色区 |
| 白 | `#fff` | 大面积背景 |

**映射到無限凜（语义对齐，色值不搬）：**

| 参考站角色 | 無限凜 token |
| --- | --- |
| 主强调青 | `--color-accent` `#39FF14` |
| 正文深色 | `--color-text`（暗底上为浅字） |
| 浅底/抬升 | `--color-bg-elevated` / `--color-surface` |
| 边线辅色 | `--color-border` / accent 半透明 |

### 3.2 字体

| 角色 | 参考站 | 無限凜实践 |
| --- | --- | --- |
| 正文 | Noto Sans JP | 系统 UI 栈（`tokens.css`） |
| 展示/英文 UI | Montserrat、M PLUS 1p | 可选后续引入；首版系统栈 |
| 等宽 | monospace | `--font-mono` |

### 3.3 版式与组件气质

1. **强品牌首屏**：大 KV / 大标题，而非纯文档顶栏。  
2. **固定角菜单** + 展开后「像换了一页」的全屏菜单层。  
3. **竖排站名**（`writing-mode: vertical-rl`，低透明度）。  
4. **展示型页标题**：大写英文 + 底线 / 渐变字（`sw-Heading` / `sw-Ttl`）。  
5. **Profile**：STATUS / LIKES / SNS 分区档案卡。  
6. **Gallery**：网格 + 图内缩放 + Modal。  
7. **Footer**：浅色带装饰（脚印/角色），品牌收尾强。  
8. **圆角、字距**：按钮大圆角、`letter-spacing` 偏展示。

### 3.4 信息架构（真页面）

| URL | 内容形态 |
| --- | --- |
| `/` | 全屏 Keyvisual + 官方入口 |
| `/profile/` | 角色档案 |
| `/gallery/` | 图库 + Modal |
| `/contact/` | 表单（CF7 + reCAPTCHA） |

---

## 4. 交互逻辑（Interaction Logic）

### 4.1 核心结论（对应 `prompt-2.md`）

右上角按钮 **不是路由跳转**，而是 **同一 URL 上的全屏菜单 Toggle**：

1. 点击 → 打开菜单层（背景 + 导航），**按钮外观变为关闭态（两线成 X）**  
2. 再点 → 关闭菜单，**回到当前页内容**（不是 `history.back()`）  
3. 菜单内链接（Profile 等）才是 **真·换页**（整页刷新到新 URL）

### 4.2 DOM 三件套（状态机）

| 节点 | 角色 |
| --- | --- |
| `#st-Menu` | 右上角开关（`href="javascript:void(0);"`） |
| `#st-Header_Bg` | 菜单背景 / 插画层 |
| `#st-Header_Nav` | 菜单链接层 |

**状态 class：**

- 默认：`closed`  
- 打开：`opened`  
- JS 布尔量 `isOpen`，三节点 **同步** 加减 class  

伪代码（各页 `app.bundle.js` 同源逻辑）：

```js
let isOpen = false;
menu.addEventListener('click', () => {
  if (isOpen) {
    // opened → closed
    [nav, menu, bg].forEach(/* remove opened, add closed */);
    isOpen = false;
  } else {
    setTimeout(() => {
      // closed → opened（推到下一 macrotask，利于 CSS 过渡）
      [nav, menu, bg].forEach(/* remove closed, add opened */);
      isOpen = true;
    }, 0);
  }
});
```

### 4.3 菜单开合的 CSS 行为要点

| 状态 | 行为 |
| --- | --- |
| **closed** | 菜单项 `translateX(-40px)` + `opacity: 0`；**transition 时长强制 0**（关的时候不倒放长动画） |
| **opened** | 项 `translateX(0)` + `opacity: 1`；**每项 delay 递增**（约 0.2s～0.7s 错峰） |
| 汉堡线 | 打开时两根线旋转成 X 造型；背景 SVG 填色/描边变化 |
| `body.preload` | 首屏/浏览器 `popstate` 时短暂加锁，减少闪烁；`popstate` 时强制关菜单 |

### 4.4 单页内其它「层」逻辑（URL 不变）

| 层 | 触发 | 状态 |
| --- | --- | --- |
| Gallery Modal | 点图 `.js-Img` | `#gallery-Modal` + `is-show`；关闭后延迟清 img |
| YouTube 层 | `.js-Youtube` | 全屏 opacity 动画 + iframe |
| 菜单 | `#st-Menu` | `opened` / `closed` |

### 4.5 各页 load 后入场（class `show`）

**首页：**

```text
load
  → 去掉 body.preload
  → .index-Keyvisual +show
  → +200ms .index-Keyvisual_Img +show   （图 scale 1.2→1）
  → +1400ms .index-Official +show
```

**内页（Profile / Contact 等）：**

```text
.sw-Lower / wrapper +show
  → 延迟 .sw-Ttl +show
  → 再延迟吉祥物 #sw-Hennnyano +show
```

**Gallery 额外：** Masonry 排布；入场 delay 略长。

### 4.6 Profile 特有

- 点击角色图：随机加 `img-1` / `img-2` / `img-3`，约 1.8s 后清除（表情/姿势切换）
- 角色 idle keyframes：`fuwafuwa` / `jump` / `buruburu` / `purupuru` / `bound`（萌系装饰，冷静开发者站可默认不搬）

### 4.7 全局小能力（部分页）

| 能力 | 行为 |
| --- | --- |
| pageTop | 点吉祥物 → anime 位移 + 滚回顶 |
| parallaxHennnyano | 鼠标视差 |
| anchorLink | 页内锚点平滑滚动 |

---

## 5. 动效体系（Motion）

### 5.1 技术取向

- **主路径**：CSS `transition` + `transform`（非 GSAP）
- **几乎不用** 全站 CSS `animation`（Profile 角色 idle 除外）
- JS **只负责 class 切换**；手感在 CSS

### 5.2 核心缓动（Easing）

| 用途 | 曲线 | 时长感 |
| --- | --- | --- |
| **Q 弹 hover/active** | `cubic-bezier(.17, .67, 0, 1.85)` | ~0.3s，略过冲 |
| **入场揭示** | `cubic-bezier(0, .8, .2, 1)` | 0.8s～2.5s，先快后稳 |
| **图内 zoom** | `cubic-bezier(.33, 1, .68, 1)` | ~0.3s，平滑 |
| **菜单背景显现** | `cubic-bezier(.16, 1, .3, 1)` | ~0.5s |

### 5.3 缩放阶梯（Scale Ladder）

| 元素 | hover | active |
| --- | --- | --- |
| 菜单按钮 | `1.07` | `0.95` |
| 导航文字 | `1.015` | `0.98` |
| SNS / 入口卡 | `1.03` | `0.98` |
| Footer 导航 | `1.04` | 回 `1` |
| 分页 | `1.08` | `0.98` |
| Gallery 图 | **img `1.04`**（盒内） | 整项 `0.98` |

**图片规则**：`overflow: hidden` 容器内对 **子元素** `scale`，避免布局抖动。

### 5.4 大图揭示（Keyvisual）

1. 容器先 `opacity: 0` → `.show` 淡入  
2. 图层初始 `scale(1.2)` → `.show` 后 `scale(1)`，约 **2.5s** + delay  
3. 菜单背景插画同一套「1.2 → 1」语言  

### 5.5 无限凜落地时的动效 token（实践）

```css
--ease-pop: cubic-bezier(0.17, 0.67, 0, 1.85);
--ease-reveal: cubic-bezier(0, 0.8, 0.2, 1);
--ease-zoom: cubic-bezier(0.33, 1, 0.68, 1);
/* hover 1.03~1.07 / active 0.95~0.98 / img 1.04 */
```

并尊重 `prefers-reduced-motion`。

---

## 6. 如何分析任意网站 CSS/交互（方法沉淀）

1. **入口**：HTML 的 `link[rel=stylesheet]` / Network → CSS；`script[src]` → JS  
2. **Token**：统计 hex、`font-family`、`border-radius`、间距  
3. **布局语言**：fixed/sticky、max-width、Grid/Flex、`vw`  
4. **组件前缀**：Header / Footer / Card / Modal 选择器  
5. **交互**：搜 `opened`/`closed`/`show`/`click`/`classList`；判断是路由还是层  
6. **映射表**：对方语义 → 自己 token（只映射角色）  
7. **只抄结构与节奏，不抄皮肤与素材**

---

## 7. 与無限凜仓库的对应关系（本对话落地）

| 概念 | 仓库落点（相对路径） |
| --- | --- |
| 主站壳 Shell | `src/layouts/ShellLayout.astro`、`src/styles/shell/shell.css`、`src/components/shell/*` |
| 菜单状态机 | `ShellChrome.astro`（`opened`/`closed` 三节点） |
| 极简入口 | `/classic/` + `BaseLayout` |
| 共用内容 | `/blog/*`、`/tools/*`；`PostCard` / `ToolCard` / `JsonFormatter` |
| 色板真相源 | `DESIGN.md`、`src/styles/tokens.css` |
| 过程记录 | `.devflow/static-blog-github-pages/plans/2026-07-17-*.md` |

### 路由（迁移后）

| 路径 | 布局 |
| --- | --- |
| `/` profile gallery contact | Shell |
| `/classic/` | 极简 Base |
| `/blog/*` `/tools/*` | 极简 Base（共用组件） |

---

## 8. 取舍摘要

| 做 | 不做 |
| --- | --- |
| 全屏菜单状态机、Q 弹缩放、错峰入场 | 照搬白蓝皮与对方插画 |
| 语义 token 映射 accent | 整站抄 WordPress CSS |
| 关菜单 transition 清零 | 角色 idle 全套萌动效（默认） |
| 双入口（Shell + Classic） | 把博客阅读页强行套满装饰壳（阅读区保持极简） |

---

## 9. 相关原始文件

- `zzz-prompt-debug/origin/blog/prompt-1.md` — 参考站列表 + 借鉴诉求  
- `zzz-prompt-debug/origin/blog/prompt-2.md` — 菜单按钮开合描述  
- `zzz-prompt-debug/origin/blog/image.png` / `image-1.png` — 用户附图（按钮/菜单态）  

---

## 10. 一句话总览

> amashiro 是 **白底插画官方站**：用 **fixed 菜单三件套 + opened/closed 状态机** 制造「换页感」，用 **Q 弹 scale 阶梯 + 长入场 decelerate** 做手感；无限凜借其 **壳与节奏**，换 **暗色霓虹 token**，内容区（博客/工具）保持极简与组件共用。
