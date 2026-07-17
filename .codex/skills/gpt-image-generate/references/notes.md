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

## 接口（Chat Completions）

### 端点

- `POST {OPENAI_BASE_URL}/chat/completions`
- **不再使用** `POST .../responses` 与 `tools: image_generation`

### 纯文生图

```json
{
  "model": "gpt-image-2",
  "stream": false,
  "messages": [
    { "role": "user", "content": "提示词" }
  ]
}
```

### 图文（--image）

```json
{
  "model": "gpt-image-2",
  "stream": false,
  "messages": [
    {
      "role": "user",
      "content": [
        { "type": "text", "text": "编辑指令" },
        { "type": "image_url", "image_url": { "url": "data:image/png;base64,..." } }
      ]
    }
  ]
}
```

- curl：`--data-binary @request.json`（避免超大 body 进 argv）

### 响应图片

常见形态（按优先级解析）：

1. `choices[0].message.content` 为 Markdown：`![image](https://...png)` → **curl 下载**
2. 同上 Markdown 内嵌 `data:image/...;base64,...` → 流式 base64 解码
3. `content` 为数组，含 `type=image_url`
4. 兼容：`data[0].b64_json` / 旧 `output[].image_generation_call.result`

解码原则：JSON 工具抽出 base64 **流式** pipe 到系统 `base64 -d`（禁止塞进 bash 变量）；URL 则 `curl -o`。

## JSON 工具优先级

1. `jq`
2. `node` + `lib/json_codec.cjs`
3. `python3`/`python` + `lib/json_codec.py`

## 依赖

- 必需：`curl`、系统 `base64`
- JSON：`jq` 或 `node` 或 `python`
