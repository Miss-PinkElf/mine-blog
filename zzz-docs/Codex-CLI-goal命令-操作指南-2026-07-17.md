# Codex CLI `/goal` 命令操作指南

> 文档类型：操作指南（How-to）  
> 日期：2026-07-17  
> 适用范围：本机已启用 `goals` 特性的 Codex CLI 交互会话（TUI）  
> 相关概念：长期目标（Goal）、会话线程（Thread）、回合（Turn）、令牌预算（Token Budget）

---

## 1. 这是什么

`/goal` 是 Codex **交互会话内部**的斜杠命令（Slash Command），用来给当前会话挂一个**长期目标（Goal）**，并跟踪：

- 目标描述（objective）
- 已用时间（time used）
- 已用 token / 可选 token 预算（token budget）
- 目标状态（status）

它解决的问题：长任务跑着跑着偏航时，你可以**中断 → 提意见 → 改目标 → 再继续**，而不是只能重开聊天从零说。

---

## 2. 重要前提（先看）

### 2.1 不是 shell 子命令

下面这种 **不存在**：

```bash
codex goal ...
```

本机实测会报：

```text
error: unrecognized subcommand 'goal'
```

正确用法：进入 `codex` 交互界面后，输入以 `/` 开头的命令，例如：

```text
/goal
/goal edit
/goal pause
/goal resume
/goal clear
```

### 2.2 特性开关

确认 `goals` 已开启：

```bash
codex features list | rg goals
```

期望类似：

```text
goals    stable    true
```

若未开启：

```bash
codex features enable goals
```

### 2.3 作用范围

- Goal 绑定在**当前会话线程（thread）**上
- 新开一个 chat / 新 session **不会自动继承**旧 goal
- 需要跨会话续做时，应配合 handoff / mission 文档，而不是假设 goal 会跟着走

---

## 3. 状态一览

界面状态文案与含义：

| 状态文案 | 含义 | 常见下一步 |
| --- | --- | --- |
| `Pursuing goal` | 正在推进目标 | 可 `/goal pause`、`/goal edit`、中断后提意见 |
| `Goal paused (/goal resume)` | 已暂停 | `/goal resume` 或 `/goal edit` |
| `Goal blocked (/goal resume)` | 被阻塞（多次无法推进等） | 先补信息/改环境，再 `/goal resume` |
| `Goal hit usage limits (/goal resume)` | 用量/预算触顶 | 调整预算或清 goal 后重建，再 resume |
| `Goal achieved` | 目标已达成 | 可 `/goal clear` 收尾 |
| `Goal abandoned` | 目标已放弃 | 可 `/goal clear` 或重新 `/goal edit` |

状态面板通常还会显示：

- `Objective:` 目标描述
- `Time used:` 已用时间
- `Tokens used:` 已用 token
- `Token budget:` token 预算（若设置）

进行中常见可用命令：

```text
/goal edit, /goal pause, /goal clear
```

暂停后常见可用命令：

```text
/goal edit, /goal resume, /goal clear
```

---

## 4. 命令手册

### 4.1 `/goal`

查看当前 goal 状态、用量、预算，以及当前状态下可用的子命令。

### 4.2 `/goal edit`

新建或修改目标描述（objective）。

典型用法：

```text
/goal edit
```

然后输入，例如：

```text
完成桌宠 Live2D 口型同步，只改 frontend，不要 commit，文本编辑必须用 apply_patch
```

说明：

- 无活跃 goal 时：创建新 goal
- 已有 goal 时：改写 objective（方向纠偏用这个）

### 4.3 `/goal pause`

暂停整个 goal 的推进 / 自动续作。

适合：

- 要先讨论方案，不希望它空闲后继续猛冲
- 要切换大方向，先停再改

### 4.4 `/goal resume`

恢复已暂停 / 阻塞 / 用量受限的 goal。

恢复时可能出现确认项（语义大致如下）：

| 选项 | 含义 |
| --- | --- |
| Resume goal | 立刻恢复推进 |
| Mark it active and continue when idle | 标记为活跃，空闲时再续 |
| Leave paused | 继续暂停，之后手动 `/goal resume` |

### 4.5 `/goal clear`

清除当前 goal，不再按长期目标追踪。

适合：任务已完成、目标作废、想回到普通对话模式。

---

## 5. 推荐工作流：中断 → 提意见 → 再开始

这是最常用、也最符合“人机协作纠偏”的路径。

### 5.1 路径 A：轻量纠偏（只改这一轮做法）

适用：目标还对，但当前执行偏了。

```text
1. /goal edit
   （写清楚目标与约束）

2. Agent 执行中发现偏航
   → 中断当前回合（Turn Interrupt，常见为 Esc，以 /keymap 为准）

3. 直接输入意见，例如：
   先别改后端，只改 frontend 的 Live2D 组件
   不要用 python 写文件，必须 apply_patch

4. 回车发送，让它按新意见继续
```

### 5.2 路径 B：先停自动推进，再聊清楚

适用：要大改方向，或怕它 idle 后又按旧目标自动续跑。

```text
1. /goal pause

2. 充分讨论 / 给约束 / 对齐方案

3. 如目标描述已过时：
   /goal edit

4. /goal resume
```

### 5.3 路径 C：目标本身写错了

```text
/goal edit
（重写 objective）

然后继续对话，或 /goal resume（若处于 pause）
```

---

## 6. 中断 vs 暂停 vs 改目标（别混）

| 动作 | 影响范围 | 典型用途 |
| --- | --- | --- |
| 中断当前回合（Esc / interrupt） | 只停掉**这一轮**模型输出 / 工具调用 | 立刻喊停，马上给新指令 |
| 直接发新消息（steer / 纠偏） | 在中断或空档注入新意见 | “按我刚才说的改” |
| `/goal pause` | 暂停**整个长期目标**推进 | 先讨论，别自动续跑 |
| `/goal resume` | 恢复长期目标 | 讨论完继续干 |
| `/goal edit` | 修改 objective 本身 | 目标描述过时、约束变了 |
| `/goal clear` | 删除 goal | 收尾或不想再跟 goal |

一句话记忆：

- **Esc** = 停这一枪  
- **`/goal pause`** = 整场战役先休整  
- **`/goal edit`** = 改作战目标  
- **`/goal resume`** = 再开打  

---

## 7. 最小可抄示例

```text
# 1. 设目标
/goal edit
实现 xxx 功能，只改 frontend，不要 commit，文本必须 apply_patch

# 2. 跑着发现偏了 → 中断当前 turn
Esc

# 3. 提意见
不要动 backend；Live2D 口型先用假数据

# 4. 若目标描述也过时
/goal edit
只做 frontend Live2D 口型假数据联调，禁止 Shell 黑盒写盘

# 5. 若之前 pause 过
/goal resume

# 6. 做完收尾
/goal clear
```

---

## 8. 与本仓库协作规范的配合建议

在本仓库使用 goal 时，建议把硬约束写进 objective，例如：

```text
/goal edit
完成 <任务名>。
约束：
1) 文本文件优先 apply_patch，禁止 python3<<PY / 重定向黑盒写盘
2) 先 plan 再 apply（devflow 硬门禁）
3) 不自动 commit，完成后先问我
4) 输出与文档默认简体中文，术语中英双语
```

这样即使中断后续跑，模型也更容易“回到同一套规则”。

更完整的文件编辑可见性规则见仓库根目录 `AGENTS.md` 的「文件编辑与变更展示」。

---

## 9. 常见问题（FAQ）

### Q1：为什么 `codex goal` 报错？

因为 **没有** 这个 shell 子命令。请在交互 TUI 里用 `/goal`。

### Q2：中断后 goal 会不会丢？

一般不会。中断的是当前 turn；goal 元数据仍在 thread 上。  
若你执行了 `/goal clear`，才会清掉。

### Q3：暂停和中断哪个更适合“先提意见再继续”？

- 只是这一步做错了：先 **中断 + 直接说意见**  
- 要大范围改方向、先讨论：先 **`/goal pause`**，谈完再 **`/goal resume`**

### Q4：出现 Goal budget reached 怎么办？

表示预算触顶，当前 turn 被停。可：

1. `/goal resume`（若允许继续）  
2. `/goal edit` 调整目标范围，减少无效消耗  
3. `/goal clear` 后重建更小目标  

### Q5：换了一个会话还能 `/goal resume` 吗？

不能指望自动恢复。Goal 是 thread 级。跨会话应使用 handoff / `.devflow/<mission>/` 文档承接上下文。

### Q6：快捷键不是 Esc？

以本机为准，在 TUI 执行：

```text
/keymap
```

查看「interrupt / 中断当前回合」的实际绑定。

---

## 10. 自检清单

开始长任务前：

- [ ] 已进入交互会话（不是只跑一次性 `codex exec`）
- [ ] `goals` 特性为 true
- [ ] 已用 `/goal edit` 写清目标与约束
- [ ] 知道如何中断当前 turn（`/keymap`）
- [ ] 知道何时该 `pause` 而不是只 Esc

纠偏时：

- [ ] 已中断或 pause，避免一边跑一边说空话
- [ ] 意见具体（改哪些目录、禁止什么写法、验收标准）
- [ ] 目标描述过时时已 `/goal edit`
- [ ] 需要续跑时已明确继续或 `/goal resume`

收尾时：

- [ ] 目标达成或作废后考虑 `/goal clear`
- [ ] 跨会话进度落到 handoff / mission 文档

---

## 11. 附录：与 Agent 侧能力的关系（了解即可）

Codex Agent 内部还有 goal 相关工具能力（例如查询当前 goal、在用户/系统明确要求时创建 goal、在完成或阻塞时更新状态）。  
对日常使用而言，**你只需掌握 TUI 的 `/goal` 系列命令**即可；不必、也不应该把它理解成 `codex goal` 这种独立 CLI 子命令。

---

## 12. 变更记录

| 日期 | 说明 |
| --- | --- |
| 2026-07-17 | 初版：整理 `/goal` 用法、中断/暂停/恢复工作流与本仓库协作建议 |
