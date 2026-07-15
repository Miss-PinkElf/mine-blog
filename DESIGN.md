# DESIGN.md — 無限凜（Mugen Rin）

> 本文件是品牌与 UI 的单一设计真相源（Single Source of Truth）。  
> **任何 UI 改动前，Agent 与开发者必须先读本文件与 `src/styles/tokens.css`。**

---

## 1. 品牌与视觉方向（Brand & Visual Direction）

| 项 | 说明 |
| --- | --- |
| 品牌名 | 無限凜（Mugen Rin） |
| 气质 | 开发者向、暗色极简、冷静克制、略带赛博感 |
| 基底 | 纯黑 / 近黑底，少装饰 |
| 强调 | 赛博绿（Cyber Green）作点缀，不作大面积铺色 |
| 信息密度 | 中等偏低；留白优先于堆叠 |
| 情绪 | 专业、可读、略锋利，不幼稚、不花哨 |

一句话：**黑底上的极简开发者博客，用少量荧光绿勾出层级与交互。**

---

## 2. 色板语义（Color Palette Semantics）

所有颜色通过 CSS 变量（CSS Custom Properties）落地，见 `src/styles/tokens.css`。业务与组件只消费语义 token，不写死 hex。

| Token | 值 | 用途 |
| --- | --- | --- |
| `--color-bg` | `#000000` | 页面最底层背景 |
| `--color-bg-elevated` | `#0A0A0A` | 略抬起的区块 / 页壳 |
| `--color-surface` | `#1A1A1A` | 卡片、面板、输入表面 |
| `--color-border` | `#404040` | 边框、分隔线 |
| `--color-accent` | `#39FF14` | **主强调色**（链接、主按钮、焦点环、关键状态） |
| `--color-neon-secondary` | `#00FF00` | 次级霓虹，**极少使用**（仅特殊高亮或装饰像素点） |
| `--color-accent-soft` | `#50C878` | 柔和强调（次要按钮 hover、成功偏柔和态） |
| `--color-highlight` | `#ADFF2F` | 高亮标注、代码内选中倾向 |
| `--color-text` | `#F5F5F5` | 正文主色 |
| `--color-text-muted` | `#A0A0A0` | 次要文案、元信息、占位 |

### 角色色 → UI 映射（已确认）

- **主强调锁定** `#39FF14`（`--color-accent`）。
- 正文、长段落一律使用 `--color-text` / `--color-text-muted`，**禁止**用荧光绿作正文色。
- `#00FF00`（`--color-neon-secondary`）不得大面积铺底或整块填充。

---

## 3. 字体（Typography）

| 角色 | Token / 栈 | 用途 |
| --- | --- | --- |
| Sans | `--font-sans`：系统 UI 栈 | 正文、导航、按钮、UI 标签 |
| Mono | `--font-mono`：等宽栈 | 代码、路径、键盘快捷键、技术标识 |

推荐栈：

```css
--font-sans: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto,
  "Helvetica Neue", Arial, "Noto Sans", "PingFang SC", "Hiragino Sans GB",
  "Microsoft YaHei", sans-serif;
--font-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas,
  "Liberation Mono", "Courier New", monospace;
```

- 正文字号基准约 `1rem`，行高 `1.6–1.75`。
- 标题层级清晰、克制加粗；不堆叠过多字号。
- 中文优先可读性，不强制自定义 Web 字体（首版系统栈即可）。

---

## 4. 组件约定（Components）

### 4.1 按钮（Button）

- **主按钮（Primary）**：`accent` 底 + 深色字，或描边主按钮（`border: accent` + 透明底 + `accent` 字）；hover 略提亮或改用 `accent-soft`。
- **次按钮（Secondary）**：`surface` 底 + `border` 边 + `text` 字。
- **禁用**：降对比、禁止霓虹闪烁动画。
- 圆角小而统一（如 `0.25–0.5rem`）；内边距足够点击（≥ 44px 高度在触控优先场景）。

### 4.2 链接（Link）

- 默认色：`--color-accent`。
- hover：可用 `--color-highlight` 或下划线加粗；visited 不强行变紫，可略降饱和。
- 正文内链接保持可读，不整段染色。

### 4.3 卡片（Card）

- 背景：`--color-surface`。
- 边框：`1px solid var(--color-border)`。
- **少阴影**；层级主要靠边框与背景阶梯（`bg` → `bg-elevated` → `surface`）。
- 内边距统一（如 `1–1.5rem`）。

### 4.4 导航（Nav）

- 暗底，与页壳一致。
- 当前项：`accent` 字色或底边指示条。
- 不拥挤；移动端可折叠，但不强制汉堡花活。

### 4.5 输入（Input）

- 背景：`surface` 或更深；边框 `border`。
- focus：`outline` / `box-shadow` 使用 `accent`（与全局 `focus-visible` 一致）。
- 占位符：`text-muted`。
- 错误态可用柔和红（若引入须写入 tokens，勿临时硬编码乱色）。

---

## 5. 布局（Layout）

| 项 | 约定 |
| --- | --- |
| 内容最大宽 | `max-width ≈ 48rem`（约 768px），水平居中 |
| 页边距 | 两侧 `1rem` 起，宽屏可 `1.5–2rem` |
| 垂直节奏 | 区块间距用一致的间距阶梯（如 0.5 / 1 / 1.5 / 2rem） |
| 主栏 | 单栏优先；侧栏仅在明确需求时出现 |
| 主内容容器 | `main` 居中并受 `max-width` 约束 |

---

## 6. 深度与材质（Depth & Material）

- **靠边框与背景阶梯表达层级**，不用厚重多级阴影。
- 阴影若出现：极轻、单层、低透明度，仅用于浮层/弹层。
- 避免玻璃拟态大面积 blur、渐变彩虹、强发光描边滥用。
- 允许极细 `accent` 边框作为焦点或选中态，不作整站霓虹描边。

---

## 7. 禁忌（Do Not）

1. **正文不用荧光绿** — 长文、段落、列表正文只用 `--color-text` / `--color-text-muted`。
2. **不大面积使用 `#00FF00`** — `--color-neon-secondary` 仅点缀。
3. **不整站引入 Ant Design（antd）** 或其它重型 UI 库皮肤覆盖品牌。
4. 不把 `accent` 当页面大面积背景填充。
5. 不做高饱和彩虹渐变、闪烁动画、赛博故障滤镜作为默认体验。
6. 不在组件内散落硬编码 hex；统一走 tokens。
7. 不破坏现有 `package.json` / Astro 配置来「强行」塞设计系统构建链（首版纯 CSS 即可）。

---

## 8. 响应式（Responsive）

- 移动优先：单栏、可读字号、足够触控目标。
- `main` 在窄屏保留左右 padding，避免贴边。
- 导航在窄屏可纵向堆叠或简化；不出现横向溢出。
- 断点保持简单（例如 ~640px / ~768px），不堆砌过多布局模式。
- 图片与代码块 `max-width: 100%`，防止撑破容器。

---

## 9. Agent / 开发者提示（Agent Notes）

1. **改任何 UI 之前**：先读本文件 + `src/styles/tokens.css`（及 `src/styles/global.css`）。
2. 新增颜色必须先加语义 token，再在组件中引用。
3. 主强调色锁定 **`#39FF14`**（`--color-accent`），未经设计确认不得替换。
4. 组件样式优先复用全局 base（链接色、`focus-visible`、`main` 宽度），避免重复定义。
5. 若与本文件冲突，以本文件与 tokens 为准；PR / 改动说明中写明偏离原因。
6. 本品牌首版目标是 **Astro + 少量 React** 的极简壳，保持 CSS 轻量，避免整站组件库。

---

*最後更新：与 T2（DESIGN.md + CSS tokens）同步。*
