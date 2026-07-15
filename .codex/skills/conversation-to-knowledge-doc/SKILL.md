---
name: conversation-to-knowledge-doc
description: Use when the user asks Codex to review the current conversation, summarize a discussion, extract useful knowledge points, write a knowledge document, or turn a conversation plus explicitly referenced files into a structured Markdown document under zzz-docs.
---

# 对话转知识文档

## 核心原则

只整理当前对话和用户明确引用的文件（explicit referenced files）。不要默认扫描全仓库、历史文档、`.devflow/` 或 `zzz-docs/`。

如果用户要求读取额外材料，先确认路径是用户明确给出的；仓库内路径用相对路径表达。

## 固定流程

1. 如果用户没有明确指定输出模式（output mode），先询问用户选择模式。
2. 支持四种模式：复盘型知识文档、教程型文章、项目沉淀文档、自适应结构。
3. 根据模式读取对应 `references/` 文件。
4. 先给出大纲（outline），等待用户确认。
5. 用户确认后写入 `zzz-docs/`。
6. 文件名使用 `主题-类型-日期.md`，例如 `写作技能体系-复盘型知识文档-2026-07-09.md`。
7. 写入后报告相对路径和关键内容摘要。

除非用户在同一轮请求中明确说“不要问，直接写”，否则不要跳过大纲确认。

## 输出模式路由

- 复盘型知识文档（review knowledge doc）：读取 `references/review-knowledge-doc.md`。
- 教程型文章（tutorial-style article）：读取 `references/tutorial-article.md`。
- 项目沉淀文档（project knowledge note）：读取 `references/project-knowledge-note.md`。
- 自适应结构（adaptive structure）：读取 `references/adaptive-structure.md`。

如果用户已经明确指定模式，直接读取对应参考文件；如果用户没有指定，询问：

```text
请选择输出模式：
1. 复盘型知识文档
2. 教程型文章
3. 项目沉淀文档
4. 自适应结构
```

## 通用质量要求

- 必须包含例子说明（examples）：抽象概念、关键决策或重要流程至少配一个具体例子。
- 必须包含取舍分析（trade-off analysis）：说明为什么这么做、为什么不那么做。
- 必须包含适度知识延伸（knowledge extension）：每篇 1-3 个强相关关联点。
- 知识延伸方向由当前主题决定，不能套固定模板。
- 不做百科式罗列；延伸点要服务当前文档主题。
- 不编造对话中没有出现、用户没有明确引用、也无法从明确引用文件中得到的事实。

## 写入规则

- 目录：`zzz-docs/`
- 文件名：`主题-类型-日期.md`
- 主题：从对话主线中提炼，优先使用用户用词。
- 类型：使用输出模式的中文名称，例如 `复盘型知识文档`。
- 日期：使用当前日期，格式为 `YYYY-MM-DD`。

写入前确保 `zzz-docs/` 存在。写入后只报告相对路径，不使用绝对路径。
