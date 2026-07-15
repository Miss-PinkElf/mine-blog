---
name: gpt-image-generate
description: |
  自包含文生图 skill：在本目录用 OpenAI Responses + image_generation 生成 png。
  用户说「生成图片」「画一张」「文生图」「gpt-image」「出图」或给出画面意图时使用。
  检查 jq、读取同级 .env、执行 run.sh、汇报耗时/大小/路径；提示词可由用户给出或按意图自动扩写。
---

# GPT Image 生成（自包含 Skill）

本 skill **独立完整**，不依赖仓库 `scripts/generate-image.sh`，不向上解析仓库根路径。

## 目录结构（全部在 skill 内）

```text
.claude/skills/gpt-image-generate/
├── SKILL.md
├── run.sh                 # 生图入口（自包含逻辑）
├── .env.example
├── .env                   # 与 run.sh 同级（本地创建，勿提交）
├── gen-images/            # 输出目录（自动创建）
├── prompts/
│   └── prompt-image.md    # 无 CLI 提示词时的默认文件
└── references/
    └── notes.md
```

| 文件 | 说明 |
| --- | --- |
| `run.sh` | 唯一执行入口 |
| `.env` | `OPENAI_API_KEY` / `OPENAI_BASE_URL` / `OPENAI_MODEL`，**与 run.sh 同级** |
| `gen-images/` | 生成的 png，自动建目录 |
| `prompts/prompt-image.md` | 默认提示词文件 |

## 何时使用

- 生成 / 画 / 出图 / gpt-image / 文生图
- 用户给了视觉描述，需要本地 png 路径

## Preflight（必须按序）

### 1. 检查 `jq`

```bash
command -v jq && jq --version
```

若没有：

1. **停止**，不要执行 `run.sh`
2. 明确告诉用户：缺少 `jq`，无法解析 JSON
3. 安装提示：
   - macOS：`brew install jq`
   - 验证：`jq --version`

### 2. 检查同级 `.env`

路径（相对 skill 目录）：

`.claude/skills/gpt-image-generate/.env`

若不存在：

```bash
cp .claude/skills/gpt-image-generate/.env.example \
   .claude/skills/gpt-image-generate/.env
```

提醒用户填入真实 `OPENAI_API_KEY`。  
**不要**把 key 写进 git 或长日志。

### 3. 确认 `run.sh` 可执行

```bash
chmod +x .claude/skills/gpt-image-generate/run.sh
```

## 提示词策略

1. 用户给出完整提示词 → 原样使用  
2. 用户只给意图 → 你扩写成详细文生图提示词  
3. 完全没说画什么 → 先问一句  

## 执行

在任意 cwd 都可，用 skill 内路径调用：

```bash
.claude/skills/gpt-image-generate/run.sh --no-open "最终提示词"
```

或：

```bash
bash .claude/skills/gpt-image-generate/run.sh --no-open "最终提示词"
```

- **不要**再调用 `scripts/generate-image.sh`
- **不要**使用 `REPO_ROOT=../../..` 一类路径拼接
- 目录创建、重试、解码、命名全部由 `run.sh` 完成

## 成功后必须汇报

解析输出中的 `---RESULT---` 块，用中文报告：

1. **耗时**（`elapsed_text` / `elapsed_seconds`）
2. **图片大小**（`bytes`，可换算 KB/MB）
3. **图片路径**（`path_rel` 或 `path`）

模板：

```markdown
已生成图片。

- 耗时：{elapsed_text}
- 大小：{bytes} bytes（约 {human_size}）
- 路径：`{path}` 或 skill 内相对路径 `{path_rel}`

提示词摘要：{一句话}
```

## 失败

| 情况 | 处理 |
| --- | --- |
| 无 jq | 停止 + 安装说明 |
| 无 key / 占位 key | 指向 skill 同级 `.env` |
| 524 / 重试耗尽 | 说明中转超时，建议简化提示词后重试 |
| 其它错误 | 摘录关键行中文解释，不谎称成功 |

## 配置项（.env）

```bash
OPENAI_API_KEY=...
OPENAI_BASE_URL=https://shell.wyzlab.ai/v1
OPENAI_MODEL=gpt-image-2
```

优先级：CLI 参数 > 环境变量 > 同级 `.env` > 脚本默认值。
