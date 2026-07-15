# 自包含 Skill 说明

## 边界

- 配置、脚本、输出、默认提示词、JSON 回退工具 **全部在本 skill 目录内**
- 不依赖仓库 `scripts/generate-image.sh`
- 不依赖 `REPO_ROOT` 或 `../../..` 路径
- Claude / Codex 双目录：以 `.claude/skills/gpt-image-generate/` 为真相源，同步到 `.codex/skills/gpt-image-generate/`

## 同级文件

- `.env` / `.env.example`
- `gen-images/`
- `prompts/`
- `lib/json_codec.py` / `lib/json_codec.cjs`
- `run.sh` / `SKILL.md`

## 接口

### 纯文

- `POST {OPENAI_BASE_URL}/responses`
- `input`: 字符串
- `tools: [{ type: "image_generation", action: "generate" }]`

### 图文（--image）

- `input`: user content 数组，`input_text` + `input_image`（data URL）
- `tools: [{ type: "image_generation", action: "edit" }]`
- curl：`--data-binary @request.json`（避免超大 body 进 argv）

### 响应图片

- `output[].type == image_generation_call` → `result` base64
- 解码：JSON 工具抽出 base64 **流式** pipe 到系统 `base64 -d`（禁止塞进 bash 变量）

## JSON 工具优先级

1. `jq`
2. `node` + `lib/json_codec.cjs`
3. `python3`/`python` + `lib/json_codec.py`

## 依赖

- 必需：`curl`、系统 `base64`
- JSON：`jq` 或 `node` 或 `python`
