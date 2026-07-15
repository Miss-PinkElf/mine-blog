---
name: gpt-image-generate
description: |
  自包含文生图 / 图生图 skill：在本目录用 OpenAI Responses + image_generation 生成 png。
  用户说「生成图片」「画一张」「文生图」「gpt-image」「出图」「改图」「参考图」「图生图」
  或给出画面意图 / 提供本地参考图时使用。
  检查 JSON 工具（jq 优先，否则 node/python）、读取同级 .env、执行 run.sh、汇报耗时/大小/路径；
  提示词可由用户给出或按意图自动扩写；支持 --image 图文同传。
---

# GPT Image 生成（自包含 Skill）

本 skill **独立完整**，不依赖仓库 `scripts/generate-image.sh`，不向上解析仓库根路径。

## 双路径（Claude / Codex）

| 场景 | 路径 |
| --- | --- |
| Claude Code / 历史文档 | `.claude/skills/gpt-image-generate/` |
| Codex | `.codex/skills/gpt-image-generate/` |

**真相源**：`.claude/skills/gpt-image-generate/`  
改完后需同步到 `.codex/skills/gpt-image-generate/`（同步 `run.sh`、`SKILL.md`、`lib/`、`prompts/`、`references/`、`.env.example`；**不同步** `.env`、`gen-images/`）。

## 目录结构（全部在 skill 内）

```text
gpt-image-generate/
├── SKILL.md
├── run.sh                 # 生图入口
├── lib/
│   ├── json_codec.py      # 无 jq 时 Python 回退
│   └── json_codec.cjs     # 无 jq 时 Node 回退
├── .env.example
├── .env                   # 本地创建，勿提交
├── gen-images/            # 输出目录（自动创建）
├── prompts/
│   └── prompt-image.md
└── references/
    └── notes.md
```

## 何时使用

- 生成 / 画 / 出图 / gpt-image / 文生图
- **改图 / 参考图 / 图生图 / image edit**
- 用户给了视觉描述或本地参考图路径，需要本地 png

## Preflight（必须按序）

### 1. JSON 工具

优先 `jq`；否则 `node` + `lib/json_codec.cjs`；否则 `python3`/`python` + `lib/json_codec.py`。

```bash
command -v jq || true
command -v node || true
command -v python3 || command -v python || true
```

若三者都没有：

1. **停止**，不要执行 `run.sh`
2. 提示安装 jq（推荐）或 Node / Python 3
   - macOS：`brew install jq`
   - Windows：`scoop install jq` 或 `choco install jq`

### 2. 检查同级 `.env`

```bash
# Claude
.claude/skills/gpt-image-generate/.env
# Codex
.codex/skills/gpt-image-generate/.env
```

若不存在，从 `.env.example` 复制并填入 `OPENAI_API_KEY`。  
**不要**把 key 写进 git 或长日志。

### 3. 确认 `run.sh` 可执行

```bash
chmod +x .claude/skills/gpt-image-generate/run.sh
# 或
chmod +x .codex/skills/gpt-image-generate/run.sh
```

## 提示词策略

1. 用户给出完整提示词 → 原样使用  
2. 用户只给意图 → 你扩写成详细提示词  
3. 用户给了参考图 + 修改意图 → 使用 `--image`，提示词描述**要改什么**（保持脸/构图等可写进 prompt）  
4. 完全没说画什么 → 先问一句  

## 执行

### 纯文生图

```bash
.claude/skills/gpt-image-generate/run.sh --no-open "最终提示词"
# 或 Codex：
.codex/skills/gpt-image-generate/run.sh --no-open "最终提示词"
```

### 图文同传 / 图生图编辑

```bash
.claude/skills/gpt-image-generate/run.sh --no-open \
  --image "path/to/ref.png" \
  "保持人物五官与构图，把头发改成黑长直，衣服换成暗色系，整体风格变暗"
```

短选项：`-i path/to/ref.png`

- **不要**再调用 `scripts/generate-image.sh`
- 目录创建、重试、解码、命名全部由 `run.sh` 完成
- 有参考图时请求 `action=edit`；无图时 `action=generate`

## 成功后必须汇报

解析输出中的 `---RESULT---` 块，用中文报告：

1. **耗时**（`elapsed_text` / `elapsed_seconds`）
2. **图片大小**（`bytes`）
3. **图片路径**（`path_rel` 或 `path`）
4. 若有：`mode`（`text` / `image_edit`）、`source_image`、`json_backend`

模板：

```markdown
已生成图片。

- 耗时：{elapsed_text}
- 大小：{bytes} bytes（约 {human_size}）
- 路径：`{path}`
- 模式：{mode}（json 工具：{json_backend}）

提示词摘要：{一句话}
```

## 失败

| 情况 | 处理 |
| --- | --- |
| 无 jq/node/python | 停止 + 安装说明 |
| 无 key / 占位 key | 指向 skill 同级 `.env` |
| 参考图不存在 | 检查 `--image` 路径 |
| 524 / 重试耗尽 | 说明中转超时，可简化提示词后重试 |
| 其它错误 | 摘录关键行中文解释，不谎称成功 |

## 配置项（.env）

```bash
OPENAI_API_KEY=...
OPENAI_BASE_URL=https://shell.wyzlab.ai/v1
OPENAI_MODEL=gpt-image-2
# CURL_CONNECT_TIMEOUT=20
# CURL_MAX_TIME=180
```

优先级：CLI 参数 > 环境变量 > 同级 `.env` > 脚本默认值。
