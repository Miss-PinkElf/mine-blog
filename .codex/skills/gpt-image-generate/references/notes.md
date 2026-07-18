# 自包含 Skill 说明

## 边界

- 配置、脚本、输出、默认提示词 **全部在本 skill 目录内**
- 不依赖仓库 `scripts/generate-image.sh`
- 不依赖 `REPO_ROOT`
- Claude / Codex 双目录：以 `.claude/skills/gpt-image-generate/` 为真相源

## 运行时

1. **Python** `run.py`（主）
2. **Node** `run.mjs`（兜底，CLI/RESULT 对齐）
3. 启动器：`run.cmd`（Win）/ `run`（Unix）：py → node
4. `run.sh`：薄封装，不再维护 Bash 业务逻辑

## 接口（Chat Completions）

官方教程：https://team.wyzlab.ai/tutorial/gpt-image

### 端点

- 主路径：`POST {OPENAI_BASE_URL}/chat/completions`（Agent / 图文混合）
- 可选对照：`POST {OPENAI_BASE_URL}/images/generations`（纯画图，官方 Images 字段）
- **不使用** `POST .../responses` 与 `tools: image_generation`

### 纯文生图

```json
{
  "model": "gpt-image-2",
  "stream": false,
  "messages": [{ "role": "user", "content": "提示词" }]
}
```

不带 `metadata` 时默认：size=auto / quality=auto / background=auto / format=png。

### 尺寸 / 质量（官方 metadata · T7 写入点）

Chat 路径用**顶层** `metadata.image_*`（非 tools）：

```json
{
  "model": "gpt-image-2",
  "stream": false,
  "messages": [{ "role": "user", "content": "提示词" }],
  "metadata": {
    "image_size": "1024x1024",
    "image_quality": "high",
    "image_background": "auto",
    "image_output_format": "png",
    "image_moderation": "auto",
    "image_input_fidelity": "high",
    "image_partial_images": 0
  }
}
```

| 键 | 合法值 | 默认 |
| --- | --- | --- |
| `image_size` | `1024x1024` / `1536x1024` / `1024x1536` / `auto` | auto |
| `image_quality` | `low` / `medium` / `high` / `auto` | auto |
| `image_background` | `opaque` / `transparent` / `auto` | auto |
| `image_output_format` | `png` / `jpeg` / `webp` | png |
| `image_output_compression` | 0–100（仅 jpeg/webp） | — |
| `image_moderation` | `auto` / `low` | auto |
| `image_input_fidelity` | `low` / `high`（图生图） | low |
| `image_partial_images` | 0–3（流式） | 0 |

注意：请求 `1024x1024` 时实测输出可能是约 **1254×1254**；`1024x1536` 可精确。

### 单图 / 多图参考

```json
{
  "model": "gpt-image-2",
  "stream": false,
  "messages": [
    {
      "role": "user",
      "content": [
        { "type": "text", "text": "编辑指令；图1=… 图2=…" },
        { "type": "image_url", "image_url": { "url": "data:image/jpeg;base64,..." } },
        { "type": "image_url", "image_url": { "url": "data:image/jpeg;base64,..." } }
      ]
    }
  ],
  "metadata": {
    "image_input_fidelity": "high",
    "image_quality": "high"
  }
}
```

官方示例为单 `image_url`；多 `image_url` 已实测可用。提示词写清图1/图2职责。

### 响应图片

1. `choices[0].message.content` Markdown：`![x](https://...)` → 下载  
2. data URL / 裸 base64 → 解码  
3. content 数组 `image_url`  
4. 兼容 `data[0].b64_json` 等  
5. 响应 `model` 常为 `gpt-5.4`（画图别名），请求仍写 `gpt-image-2`  

## 输入预处理（image_prep）

**只改上传参考图，不改模型输出。**

| 原则 | 说明 |
| --- | --- |
| 质量优先 | 默认 **不** 固定长边缩放 |
| 主手段 | PNG→JPEG 等编码 + quality 阶梯 |
| 缩边 | 仅 `heavy` 体积仍超标，或显式 `--max-edge>0` |
| 档位 | `off` / `light` / `medium`（默认）/ `heavy` |

依赖：Python **Pillow**（`pip install pillow`）。Node 兜底在需要压缩时会尝试调用同机 Python 的 `image_prep`。

## 探针结论（2026-07-18）

### 双图 / 中转

- **多 `image_url` 可用**：小 body 探针 HTTP 200，模型会回复「2 images」并分别描述。
- **`run.py` 双图可落盘**：`zzz-prompt-debug/origin/OC/generated/rin-dual-test-01.png`（人设 preview + style-01，`--prep heavy`，body≈101KB；第 1–2 次断连，第 3 次 200）。
- **断连错误**：`Remote end closed connection without response`（约 60s），无 JSON 错误体 → **不是**「协议拒绝双图」。
- **响应 model**：常为 `gpt-5.4`，请求仍为 `gpt-image-2`（中转改写）。

### 输入压缩量级（经验）

| 场景 | 观察 |
| --- | --- |
| 单图 medium | 约 1.6MB PNG → ~180KB JPEG，宽高可不变 |
| 双图 medium | body 约 377KB 时易断连 |
| 双图 heavy + max_edge 512 | body 约 100KB，可成功出图 |

完整 off/light/medium/heavy 对照表仍可后续补全。  


## 依赖

- 必需：Python 3 **或** Node 18+
- 推荐：Pillow（输入压缩）
- 不再要求：jq、bash 业务逻辑、系统 curl（主路径用语言内置 HTTP）
