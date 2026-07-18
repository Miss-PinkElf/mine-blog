# Learnings · gpt-image-cli-tooling

## 2026-07-15

1. **Responses 默认 model 与中转习惯要对齐**  
   文档里的「主模型 gpt-5.x + image tool」在中转上可能更慢；本环境直接 `gpt-image-2` 与 REST Client 体验更接近。

2. **Bash 大 base64 不能进变量**  
   `B64="$(jq ...)"` 对数 MB 字符串极慢；应 `jq | base64 -d` 流式落盘。

3. **Ctrl+C 卡死的隐藏原因**  
   后台 spinner 若 `trap '' TERM`，父进程 `wait` 会永久挂起；必须允许 TERM/KILL，并 force kill。

4. **loading「已用时」必须区分本步/总计**  
   否则用户会把等接口的时间误当成解析时间。

5. **密钥文件不要进 git**  
   `.http` / `.env` 易粘贴真 key；应 ignore + untrack；历史里若进过 key 需轮换。

6. **524 是网关超时**  
   不是 curl 语法错误；需重试 + 控制单次 max-time。

## 2026-07-16

1. **图文同传协议**：Responses 多模态 `input_text` + `input_image(data URL)` + `tools.image_generation`；有参考图时用 `action=edit` 更贴切。
2. **请求体体积**：参考图 base64 可达 ~2MB，必须 `curl --data-binary @file`，避免塞进 shell 变量 / 过大 argv。
3. **JSON 工具分层**：抽 JSON 字段用 jq/node/python；**解码**只用系统 `base64` 流式管道。纯 bash 解析大 JSON 不可行。
4. **urllib 可能被中转 CF 1010 拦截**；脚本路径继续用 curl。
5. **双目录**：Codex 读 `.codex/skills/`，Claude 读 `.claude/skills/`；以 claude 为真相源，改完必须同步 codex。
6. **Windows 注意**：shebang/`env bash` 与 CRLF 会导致「No such file」；脚本宜 LF；用 `bash run.sh` 更稳。

## 2026-07-17

1. **Chat 生图响应常见是 Markdown URL**，不一定是 base64：`choices[0].message.content` ≈ `![image](https://...png)`，需 curl 下载再落盘。
2. **协议字段彻底不同**：Chat 用 `messages` + `image_url`；旧 Responses 的 `input` / `input_text` / `image_generation` / `action` 不应再作为 skill 主路径。
3. **macOS printf 坑**：`printf '---xxx---\n'` 可能被当成选项；固定用 `printf '%s\n' '---xxx---'`。
4. **`has` 阈值**：不能用过大的 base64 长度门槛；极小 PNG 合法 base64 可 <100。
5. **大参考图可行**：约 1.9MB OC 立绘 data URL（请求体约 2.5MB）+ Chat 图生图实测约 75s 成功；body 仍必须 `@file`。
6. **T7 不可照搬旧 design**：Chat 无 `tools[0].size` 写入点；下轮 size/ratio 需重新设计（提示词约定 / 网关扩展字段 / 或另开 images API）。

## 2026-07-18

1. **跨平台主路径用 Python，Node 作完整兜底**；skill 不内嵌解释器；Win 用 `run.cmd` / `python run.py`。
2. **输入压缩 ≠ 固定长边**：默认编码压体积（JPEG quality）；缩边仅 heavy 兜底或显式 `--max-edge`；**输出不管**。
3. **双图协议可用**：`content` 多 `image_url`；模型会认张数；`run.py` 可落盘。失败多为断连，不是 4xx。
4. **请求 model 与响应 model 可能不一致**：请求 `gpt-image-2`，响应常 `gpt-5.4`（中转改写）。
5. **多图 body 建议压到约 100KB 量级更稳**；medium 双图 ~377KB 易 60s 断连；heavy 后 ~100KB 可成功。
6. **Node 压缩可复用 Python image_prep**（子进程），避免双份图像算法分叉。

## 2026-07-18（续）· 官方教程 + 实测

来源：https://team.wyzlab.ai/tutorial/gpt-image（SPA 内容在 `assets/index-*.js`）

### 双协议（官方）

| 路径 | 端点 | 适用 |
| --- | --- | --- |
| Chat Completions | `POST /v1/chat/completions` | Agent / 文字+图混合；本 skill 主路径 |
| Images API | `POST /v1/images/generations` | 纯画图；字段贴近 OpenAI 官方 SDK |

### Chat 侧尺寸/质量（T7 关键发现）

- **正确写入点是顶层 `metadata.image_*`，不是 `tools[0]`，也不必只靠提示词前缀。**
- 官方字段：

| metadata 键 | 合法值 | 默认 | 说明 |
| --- | --- | --- | --- |
| `image_size` | `1024x1024` / `1536x1024` / `1024x1536` / `auto` | auto | 画幅 |
| `image_quality` | `low` / `medium` / `high` / `auto` | auto | 质量/耗时/费用 |
| `image_background` | `opaque` / `transparent` / `auto` | auto | 透明底 |
| `image_output_format` | `png` / `jpeg` / `webp` | png | 输出格式 |
| `image_output_compression` | 0–100 | — | 仅 jpeg/webp |
| `image_moderation` | `auto` / `low` | auto | 审核；误杀时用 low |
| `image_input_fidelity` | `low` / `high` | low | **图生图还原度** |
| `image_partial_images` | 0–3 | 0 | 流式渐进预览 |

- 优先级：`metadata.image_*` > 服务端默认；空字符串/null 的 size 会跳过走 auto。
- OpenAI Python SDK 写 metadata 用 `extra_body={"metadata": {...}}`。

### Images API 字段（对照）

- `size` / `quality` / `background` / `output_format` / `output_compression` / `moderation` / `n` / `response_format`（`url`|`b64_json`）
- `n=1..10` 内部串行；Chat 路径一次只出 1 张，多张需并发 N 次。

### 响应约定（官方 + 实测）

- Chat：`choices[0].message.content` 常为 `![image](https://...png)`；响应 `model` 恒显示 `gpt-5.4`（画图别名）。
- Images：`data[0].url` 或 `b64_json`。

### 图生图 / 多参考图

- 官方场景示例：单参考图 = `content: [text, image_url]` + `metadata.image_input_fidelity: high`。
- 文档**未单独写「多参考图」示例**；本 skill 用多个 `image_url` 已多次实测成功（含 2026-07-18 双图）。
- 提示词需标明「图1=… 图2=…」。

### 本轮探针证据（`.devflow/gpt-image-cli-tooling/_probe_out/`）

| 用例 | 结果 | 备注 |
| --- | --- | --- |
| Chat + `image_size=1024x1024` quality=low | HTTP 200 | 落盘约 **1254×1254**（非严格 1024） |
| Chat + `image_size=1024x1536` | HTTP 200 | 落盘 **1024×1536** 精确 |
| Images API size=1024x1024 quality=low | HTTP 200 | 落盘约 **1254×1254** |
| Chat img2img + `image_input_fidelity=high` | HTTP 200 | 小 body 约 40KB 即成功 |
| skill 文生图 | 200 / 28s | `skill-text.png` 1254×1254 |
| skill 单图 heavy | 200 / 51s | body≈120KB；`skill-img2img-single.png` |
| skill 双图 heavy | 200 / 第3次 | body≈254KB；前两次断连；`skill-img2img-dual.png` |

### 对 T7 的含义

1. CLI 应映射：`--size`/`--ratio`/`--quality` → `metadata.image_size` / `image_quality`（Chat 路径）。
2. 可选后续：`--fidelity` → `image_input_fidelity`；`--format` → `image_output_format`；审核误杀 `--moderation low`。
3. `1024x1024` 实测可能变成 1254 边长，写文档时别写死「像素严格等于枚举值」。
4. 多图仍建议控 body；body 越大越容易 60s 断连，与「多 image_url 协议」无关。

### 多图根因纠正（同日晚间）

| 输入方式 | body | 结果 |
| --- | --- | --- |
| 双图 data URL（skill `--prep heavy`） | ~254KB | 易断连，靠重试 |
| 双图 **HTTPS URL** + `image_input_fidelity=high` | ~526B | **一次 200** |

官方图生图示范是 **公网 URL + fidelity**，不是本地大图 base64。  
skill 的 data URL 是本地文件工程路径；大参考图不稳应优先改输入载体/body，而不是判定多图不可用。
