# Workflow · GPT Image CLI 工具链

## 路径

**重型路径（Heavy）**

## 当前阶段

**Close / Handoff（2026-07-18 晚 · 官方文档 Explore）** → 下轮从 **Align/Plan T7（metadata）** 恢复，再 Apply

## 目标

本地可用的 GPT Image **文生图 / 图生图（可多参考图）** 工具链（中转 `shell.wyzlab.ai`），以自包含 Skill 为主入口（Claude + Codex 双目录）。

**现行协议**：OpenAI **Chat Completions**（`POST /v1/chat/completions`）。  
**官方对照**：https://team.wyzlab.ai/tutorial/gpt-image（另有 Images API `/v1/images/generations` 纯画图路径）。

**现行入口（2026-07-18 起）**：**Python `run.py` 优先**，无 Python 时 **Node `run.mjs`**；不再以 bash 业务逻辑为主。

## 范围

### 已交付

| 版本 | 内容 |
| --- | --- |
| 第一版 | 纯文生图、重试、中断、RESULT、默认 gpt-image-2、自包含 skill |
| 第二版 | `--image` 图文同传；JSON 回退；双目录 |
| 第三版 | 协议切换 Chat Completions；Markdown URL 落盘 |
| 第四版 | 跨平台 py/node；多图；输入 `--prep`；启动器；双图实测落盘 |
| **Explore（文档轮）** | 官方教程对齐；确认 `metadata.image_*`；多图根因=大 body data URL；探针落盘（未改 run.py 业务） |

### 下轮优先 · 第一版即可（未延期）

- **T7**：`--size` / `--quality` / `--ratio` → Chat **`metadata.image_size` / `image_quality`**（勿写 `tools[0]`）
- **T8**：无 key / 空 prompt / Ctrl+C 等抽检

### 建议下轮同批讨论、可只做第一版切片

- `--fidelity` → `image_input_fidelity`（图生图官方推荐 high）
- http(s) `image_url` 直通（不二次 base64）
- 多图默认 body 策略写进 SKILL（如建议 heavy）

### 明确延期（`deferred/` + backlog）

- 异步 task、站点 UI、仅 aspect_ratio
- skill **内嵌** Python/Node 运行时
- **输出** png 体积/尺寸治理
- 本地大图「先上传再 URL」管线（当前用 prep + data URL）
- metadata 全量 CLI（background / format / moderation / partial_images）——第一版不做，进 backlog
- 仓库 `scripts/generate-image.sh` 迁 Chat / 废弃双轨（backlog）

### Backlog（轻量）

见 `backlog.md`
