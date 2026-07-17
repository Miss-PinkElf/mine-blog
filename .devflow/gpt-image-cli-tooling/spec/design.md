# Design · GPT Image CLI 工具链

## 架构概览（现行 · Skill 主入口）

```text
CLI 提示词 / prompts/prompt-image.md
        │  可选 --image 参考图
        ▼
.claude/skills/gpt-image-generate/run.sh   （真相源；同步 .codex）
  ├─ load 同级 .env
  ├─ JSON 工具：jq → node(lib/json_codec.cjs) → python(lib/json_codec.py)
  ├─ 组装 Chat Completions JSON（临时文件）
  ├─ curl POST {BASE}/chat/completions  （可后台、可杀）
  ├─ 失败重试（最多 5 次）
  ├─ 解析 choices[0].message.content
  │    ├─ Markdown https URL → curl 下载
  │    └─ data URL / b64 → 流式 base64 解码
  └─ 落盘 gen-images/*.png + ---RESULT---
```

> 仓库 `scripts/generate-image.sh` 仍为历史 Responses 实现，**非** skill 主路径；是否迁移见 backlog。

## 接口约定（2026-07-17 起）

### 请求

- Method：`POST`
- URL：`{OPENAI_BASE_URL}/chat/completions`
- Header：`Authorization: Bearer {OPENAI_API_KEY}`、`Content-Type: application/json`

#### 文生图

```json
{
  "model": "gpt-image-2",
  "stream": false,
  "messages": [
    { "role": "user", "content": "<prompt>" }
  ]
}
```

#### 图生图（--image）

```json
{
  "model": "gpt-image-2",
  "stream": false,
  "messages": [
    {
      "role": "user",
      "content": [
        { "type": "text", "text": "<edit prompt>" },
        {
          "type": "image_url",
          "image_url": { "url": "data:image/png;base64,..." }
        }
      ]
    }
  ]
}
```

### 响应关键路径

1. `choices[0].message.content` 为字符串，含 Markdown 图片：`![...](https://...png)` → **curl 下载**
2. 同上 Markdown 内嵌 `data:image/...;base64,...` → 流式解码
3. `content` 为数组且含 `image_url`
4. 兼容兜底：`data[0].b64_json`、旧 Responses `output[].image_generation_call.result`

### 历史协议（已废弃于 skill 主路径）

- `POST /responses` + `tools: [{type: image_generation, action: generate|edit}]`
- 多模态曾用 `input_text` / `input_image`
- 仅作 codec 兜底与仓库 scripts 对照，**新功能不要依赖**

## 配置优先级

1. CLI 参数（`--model` / `--base-url` / 未来 `--size` 等）
2. 进程环境变量
3. skill 同级 `.env`
4. 脚本默认值（model=`gpt-image-2`，base=`https://shell.wyzlab.ai/v1`）

## 尺寸与比例设计（T7 · 待实现 · Chat 适配）

- Chat 路径**没有**稳定的 `tools[0].size` 写入点
- 第一版建议优先：
  1. 将 ratio/size 写进用户提示词前缀（兼容性最好）
  2. 或探测中转是否接受顶层/扩展字段（需实测）
- 映射表（若最终落到 size 字符串）：

| ratio | size |
| --- | --- |
| `1:1` | `1024x1024` |
| `2:3` | `1024x1536` |
| `3:2` | `1536x1024` |

## 可靠性

- 重试最多 5 次；Ctrl+C 立即退出不重试
- 大 base64 禁止进 bash 变量；请求体 `--data-binary @file`
- 默认 `CURL_MAX_TIME=180`（可 `.env` 覆盖）
- macOS：`printf '%s\n' '---RESULT---'`，勿直接 `printf '---...`

## JSON 工具

| 优先级 | 工具 | 用途 |
| --- | --- | --- |
| 1 | jq | 组装 / 抽取 |
| 2 | node + `lib/json_codec.cjs` | 同上（含 URL 下载再编码） |
| 3 | python + `lib/json_codec.py` | 同上 |
