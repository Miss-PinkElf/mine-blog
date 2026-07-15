# Design · GPT Image CLI 工具链

## 架构概览

```text
prompt-image.md / CLI 提示词
        │
        ▼
generate-image.sh
  ├─ load scripts/.env
  ├─ 组装 Responses JSON
  ├─ curl POST {BASE}/responses  （可后台、可杀）
  ├─ 失败重试（最多 5 次）
  ├─ jq 抽取 image_generation_call.result
  └─ 流式 base64 解码 → gen-images/*.png
```

## 接口约定

### 请求

- Method：`POST`
- URL：`{OPENAI_BASE_URL}/responses`
- Header：`Authorization: Bearer {OPENAI_API_KEY}`
- Body（MVP）：

```json
{
  "model": "gpt-5.4",
  "input": "<prompt>",
  "tools": [
    {
      "type": "image_generation",
      "action": "generate"
    }
  ]
}
```

### P2 扩展 Body

在 `tools[0]` 增加（若中转兼容）：

```json
{
  "type": "image_generation",
  "action": "generate",
  "size": "1024x1536",
  "quality": "medium"
}
```

### 响应关键路径

- `status == completed`
- `output[]` 中 `type == image_generation_call`
- 图片：`output[].result`（base64 PNG）
- 元信息：`size` / `quality` / `revised_prompt` / `tools[0].model`

实测样例模型名：`gpt-image-2-codex`。

## 配置优先级

1. CLI 参数（`--model` / `--base-url` / `--size` / `--ratio` 等）
2. 进程环境变量
3. `scripts/.env`
4. 脚本默认值

## 尺寸与比例设计（P2）

- 主参数：`size`（`WxH` 或 `auto`）
- 便捷参数：`ratio` → 映射表（可覆盖 size）

建议映射：

| ratio | size |
| --- | --- |
| `1:1` | `1024x1024` |
| `2:3` | `1024x1536` |
| `3:2` | `1536x1024` |
| `9:16` | `1152x2048`（需验证中转） |
| `16:9` | `1536x864` 或 `2048x1152` |

说明：官方无单独 `aspect_ratio` 字段；比例通过 size 表达。

## 错误与重试

| 类型 | 行为 |
| --- | --- |
| 配置错误（无 key / 空提示词） | 立即失败，不重试 |
| curl 非中断失败 | 重试 |
| HTTP 非 2xx（含 524） | 重试 |
| 无 base64 / 解码失败 | 重试 |
| Ctrl+C / exit 130 等 | 立即退出，不重试 |

## 安全

- `scripts/.env` gitignore
- `scripts/gen-images/`、`Response-*.json` gitignore
- 日志不打印完整 API Key

## 文件清单

| 路径 | 职责 |
| --- | --- |
| `scripts/generate-image.sh` | 主 CLI |
| `scripts/.env.example` | 配置模板 |
| `scripts/prompts-images/prompt-image.md` | 默认提示词 |
| `scripts/generate-image.http` | REST Client |
| `scripts/gen-images/` | 输出（本地） |

## 2026-07-16 增量设计 · 图文同传与 JSON 回退

### Skill 主入口（更新）

```text
.claude/skills/gpt-image-generate/run.sh   # 真相源
        │ 同步
        ▼
.codex/skills/gpt-image-generate/run.sh    # Codex 调用副本
```

### 图文请求

- CLI：`--image` / `-i`
- Body：`input` 为 user content 数组；`tools[0].action = "edit"`
- `image_url`：`data:<mime>;base64,<...>`
- curl：`--data-binary @request.json`（避免超大 argv）

### JSON 工具

| 优先级 | 用途 |
| --- | --- |
| jq | 组装 body、抽取 result、摘要错误 |
| node | 无 jq 时回退 |
| python3/python | 无 jq/node 时回退 |
| 系统 base64 | 仅解码二进制 |

### 模式

- `mode=text`：纯文生图
- `mode=image_edit`：参考图编辑
