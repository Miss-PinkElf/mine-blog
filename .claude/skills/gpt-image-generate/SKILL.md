---
name: gpt-image-generate
description: |
  自包含文生图 / 图生图 skill：在本目录用 OpenAI Chat Completions（/v1/chat/completions）生成 png。
  用户说「生成图片」「画一张」「文生图」「gpt-image」「出图」「改图」「参考图」「图生图」
  或给出画面意图 / 提供本地参考图时使用。
  优先 python run.py，否则 node run.mjs；支持多 --image、--prep 输入压缩档位；
  汇报耗时/大小/路径；提示词可由用户给出或按意图自动扩写。
---

# GPT Image 生成（自包含 Skill）

本 skill **独立完整**，不依赖仓库 `scripts/generate-image.sh`，不向上解析仓库根路径。

## 双路径（Claude / Codex）

| 场景 | 路径 |
| --- | --- |
| Claude Code / 历史文档 | `.claude/skills/gpt-image-generate/` |
| Codex | `.codex/skills/gpt-image-generate/` |

**真相源**：`.claude/skills/gpt-image-generate/`  
改完后需同步到 `.codex/skills/gpt-image-generate/`（同步脚本与文档；**不同步** `.env`、`gen-images/`）。

## 目录结构

```text
gpt-image-generate/
├── SKILL.md
├── run.py                 # 主入口（Python）
├── run.mjs                # 兜底入口（Node）
├── run.cmd                # Windows 启动器：py → node
├── run                    # Unix 启动器：python → node
├── run.sh                 # 旧入口薄封装 → run.py
├── lib/
│   ├── image_prep.py      # 输入参考图预处理
│   ├── json_codec.py
│   └── json_codec.cjs
├── .env.example
├── .env                   # 本地创建，勿提交
├── gen-images/
├── prompts/prompt-image.md
└── references/notes.md
```

## 何时使用

- 生成 / 画 / 出图 / gpt-image / 文生图
- **改图 / 参考图 / 图生图 / image edit**（可多张参考图）
- 用户给了视觉描述或本地参考图路径，需要本地 png

## Preflight（必须按序）

### 1. 运行时（优先 Python，否则 Node）

```bash
python --version || python3 --version || py -3 --version
node --version
```

| 优先级 | 运行时 | 入口 |
| --- | --- | --- |
| 1 | Python 3 | `run.py` |
| 2 | Node 18+ | `run.mjs` |

都没有则 **停止**，提示安装：

- Windows：`winget install Python.Python.3.12` 或 Node LTS  
- macOS：`brew install python` 或 `brew install node`

输入压缩（`--prep` 非 off）建议安装 **Pillow**：`pip install pillow`。

### 2. 检查同级 `.env`

```text
.claude/skills/gpt-image-generate/.env
# 或
.codex/skills/gpt-image-generate/.env
```

不存在则从 `.env.example` 复制并填入 `OPENAI_API_KEY`。**不要**把 key 写进 git 或长日志。

### 3. 启动方式

Windows 推荐：

```bat
.claude\skills\gpt-image-generate\run.cmd --no-open "提示词"
```

或直接：

```bash
python .claude/skills/gpt-image-generate/run.py --no-open "提示词"
```

## 提示词策略

1. 用户给出完整提示词 → 原样使用  
2. 用户只给意图 → 你扩写成详细提示词  
3. 参考图 + 修改意图 → 使用 `-i/--image`，提示词写清**改什么 / 保留什么**  
4. 多张参考图 → 多次 `-i`，提示词写明「图1=… 图2=…」  
5. 完全没说画什么 → 先问一句  

## 输入压缩（只影响参考图，不影响输出）

**默认不固定长边。** 主手段是编码质量；缩边仅 `heavy` 兜底或显式 `--max-edge`。

| `--prep` | 场景 |
| --- | --- |
| `off` / `--no-prep` | 原样上传；小图或要最大保真 |
| `light` | 尽量不影响观感 |
| `medium`（默认） | 常规图生图 |
| `heavy` | 大图、多图、曾 524/超时 |

精细参数：`--jpeg-quality`、`--target-bytes`、`--max-edge`（默认 0=关闭）。

Agent 应根据参考图体积与历史失败自行选档；RESULT 中有 `input_bytes_before/after` 可复盘。

## 执行

### 纯文生图

```bash
python .claude/skills/gpt-image-generate/run.py --no-open "最终提示词"
```

### 单图 / 多图图生图

```bash
python .claude/skills/gpt-image-generate/run.py --no-open \
  -i "path/to/ref.png" \
  --prep medium \
  "保持人物五官与构图，把头发改成黑长直，衣服换成暗色系"

python .claude/skills/gpt-image-generate/run.py --no-open \
  -i "face.png" -i "outfit.png" \
  --prep heavy \
  "图1是脸与人设，图2是服装参考；合成统一暗色系插画"
```

Node 兜底：

```bash
node .claude/skills/gpt-image-generate/run.mjs --no-open "提示词"
```

- 协议固定：`POST {BASE_URL}/chat/completions`
- 有参考图：`messages` 多模态 `text` + 多个 `image_url`
- **不要**再调用 `scripts/generate-image.sh`
- **输出 png 不做体积治理**

## 成功后必须汇报

解析 `---RESULT---`，用中文报告：

1. **耗时**（`elapsed_text`）  
2. **图片大小**（`bytes`）  
3. **图片路径**（`path` / `path_rel`）  
4. `mode`、`runtime`、`image_prep`、输入 before/after（若有）

```markdown
已生成图片。

- 耗时：{elapsed_text}
- 大小：{bytes} bytes
- 路径：`{path}`
- 模式：{mode}（runtime={runtime}，prep={image_prep}）

提示词摘要：{一句话}
```

## 失败

| 情况 | 处理 |
| --- | --- |
| 无 python/node | 停止 + 安装说明 |
| 无 key | 指向 skill 同级 `.env` |
| 参考图不存在 | 检查 `-i` 路径 |
| 要压缩但无 Pillow | 提示 `pip install pillow` 或 `--prep off` |
| 524 / 重试耗尽 | 升 `--prep heavy` 或降 `--target-bytes` 后重试 |
| 其它错误 | 摘录关键行中文解释，不谎称成功 |

## 配置项（.env）

```bash
OPENAI_API_KEY=...
OPENAI_BASE_URL=https://shell.wyzlab.ai/v1
OPENAI_MODEL=gpt-image-2
# CURL_MAX_TIME=180
# GPT_IMAGE_PREP=medium
# GPT_IMAGE_MAX_IMAGES=4
```

优先级：CLI > 环境变量 > 同级 `.env` > 脚本默认值。
