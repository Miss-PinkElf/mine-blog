# Python 主入口 + Node 兜底跨平台生图 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers-subagent-driven-development（推荐）或 executing-plans 按 task 实现。步骤用 checkbox（`- [ ]`）跟踪。

**Goal:** 将 `gpt-image-generate` skill 从「Bash 主入口 + jq 优先」升级为「**Python 主实现 + Node 完整兜底**」的跨平台生图工具，支持多张参考图与发送前输入图压缩，提高图生图成功率；**不治理输出图体积**。

**Architecture:** 以 `.claude/skills/gpt-image-generate/` 为真相源。`run.py` 承担完整流水线（`.env`、CLI、多图预处理、Chat Completions、重试、落盘、`---RESULT---`）。无 Python 时由 `run.mjs` 提供能力对齐（parity）的兜底。可选薄启动器 `run` / `run.cmd` 仅做运行时探测。`run.sh` 降级为转调 Python 或文档备用，不再作为 Win 主路径。协议保持 `POST {BASE_URL}/chat/completions`。完成后同步到 `.codex/skills/gpt-image-generate/`（不同步 `.env`、`gen-images/`）。

**Tech Stack:** Python 3 标准库（`urllib`/`json`/`base64`/`pathlib`/`argparse`）；可选 Pillow 做输入图压缩；Node 18+（`fs`/`https`/`http`/`path`）；可选不引入 sharp 时 Node 端用「缩放降级策略 + 原样/质量阶梯」与 py 对齐接口契约；OpenAI 兼容 Chat Completions。

**Align 依据（本会话讨论）:**

- 主：Python；兜底：Node（完整写，能力对齐）
- 环境前提：Win/Mac 有 py；且 py 与 node **至少一个**
- **不**在 skill 内嵌 Python 发行版
- 输出 png 体积 **暂不管**
- 输入参考图需预处理，解决大图 body（约 2.5MB）+ 180s 超时反复重试
- 多图：多次 `--image` / `-i`
- 去 jq 作为主依赖

**默认拍板（2026-07-18 修订 · 压缩策略）:**

| 项 | 默认 |
| --- | --- |
| 多图 CLI | 可重复 `-i/--image PATH`，顺序即 messages content 中图片顺序 |
| 多图上限 | **4** 张（`GPT_IMAGE_MAX_IMAGES` / `--max-images`） |
| **输入压缩哲学** | **质量优先的编码压缩**；**禁止**默认「固定长边等比缩放到 1536」作为主策略 |
| **谁决定压多狠** | **Agent / 调用方** 通过 CLI 参数选档或精细参数；脚本只执行、打日志，不替业务猜死尺寸 |
| 压缩档位 `--prep` | `off` / `light` / `medium`（默认）/ `heavy`（见下表） |
| 精细覆盖 | `--jpeg-quality`、`--target-bytes`、可选 `--max-edge`（**仅兜底**，默认 **不启用**） |
| 默认行为 | **不缩放分辨率**；PNG→高质 JPEG/WebP 等编码手段逼近体积；仅 heavy 或显式 `--max-edge` 才等比缩边 |
| 输出图 | **不压缩、不改尺寸**（与输入预处理完全分离） |
| 压缩依赖 | Python：Pillow 可选；无 Pillow 且需要 prep≠off 时：大文件明确失败并提示安装 |
| Node | 与 py **同一套 CLI 档位名**；实现能力对齐 |
| 启动器 | `run.cmd` / `run`：优先 py，否则 node |
| `run.sh` | 薄封装转调 `run.py` |
| 超时 | 默认仍 180s；靠输入体积与 Agent 选档提高成功率 |
| 经验数据 | Apply 后做一次 **输入体积探针**（见 Task 探针），把结论写进 `references/notes.md`，供 Agent 选档；**不**在未测时写死「必须 <X KB」 |

### 输入压缩档位（给 Agent 用，只作用于参考图）

| `--prep` | 意图 | 典型手段（实现可微调，须写进 help） |
| --- | --- | --- |
| `off` | 原样上传 | 不转码、不缩边 |
| `light` | 尽量不影响观感 | 仅去可剥离元数据 / 高质转码（如 q≈92），**不缩边** |
| `medium`（默认） | 保质与体积平衡 | 高质 JPEG/WebP，quality 阶梯降至约 80，目标单张约 600–800KB 量级，**默认不缩边** |
| `heavy` | 优先稳过中转 | 更低 quality + **必要时**等比缩边（仅当体积仍超标）；缩边是最后手段 |

说明：

1. **「固定长边」不是默认产品行为**；`--max-edge` 仅高级/兜底，默认 `0`=关闭。  
2. **等比缩边** ≠ 压缩的唯一形式；主路径是 **编码质量（quality）与格式选择**。  
3. **输出** `gpt-image-2` 生成图大小由模型/接口决定，脚本 **不**用这些参数去改输出。  
4. SKILL.md 指导 Agent：参考图很大或曾 524/超时 → 升 `heavy` 或降 `--jpeg-quality` / 设 `--target-bytes`；人设脸部细节关键 → `light` 或 `medium`。

---

## 核心思路（给人读的摘要）

```text
Agent/用户
  → run.cmd / run / 直接 python|node
  → 优先 run.py，否则 run.mjs
  → 读 skill 同级 .env
  → 解析提示词 + 0..N 张 --image
  → 按 --prep / 精细参数做【输入】编码压缩（默认可不缩边）
  → messages: [text, image_url×N]
  → POST /chat/completions（重试 + 退避）
  → 解析 → 写入 gen-images/*.png（输出不压）
  → ---RESULT---（含 prep 档位、原/后体积，供 Agent 复盘）
```

**要解决的三个痛点：**

1. **Win 不好跑 sh** → 脚本语言入口  
2. **大图超时** → 可调的**输入**压缩；**由 AI/调用方选强度**，不是写死长边  
3. **只要单图** → 多次 `--image` 组多模态 content  

**不要做的：** 内嵌 Python、异步任务、站点 UI、输出体积治理、强制 jq、默认固定长边缩放。

---

## 文件映射

| 路径 | 动作 | 职责 |
| --- | --- | --- |
| `.claude/skills/gpt-image-generate/run.py` | **新建** | Python 主入口：全流程 |
| `.claude/skills/gpt-image-generate/run.mjs` | **新建** | Node 兜底：与 run.py 契约对齐 |
| `.claude/skills/gpt-image-generate/lib/image_prep.py` | **新建** | 输入图按档位/参数做编码压缩（Pillow 可选；默认不固定长边） |
| `.claude/skills/gpt-image-generate/lib/json_codec.py` | 改或内聚 | 可被 run.py 直接 import；保留 CLI 子命令兼容可选 |
| `.claude/skills/gpt-image-generate/lib/json_codec.cjs` | 改 | 支持 **多图** build；extract/has/meta 与现 Chat 协议一致 |
| `.claude/skills/gpt-image-generate/run` | **新建** | Unix 薄启动器：py → node |
| `.claude/skills/gpt-image-generate/run.cmd` | **新建** | Windows 薄启动器：py/py -3 → node |
| `.claude/skills/gpt-image-generate/run.sh` | **改** | 薄封装：`exec python3/python run.py "$@"` 或提示 |
| `.claude/skills/gpt-image-generate/SKILL.md` | **改** | Preflight、双运行时、多图示例、压缩说明 |
| `.claude/skills/gpt-image-generate/references/notes.md` | **改** | 协议、多 image_url、预处理策略 |
| `.claude/skills/gpt-image-generate/.env.example` | **改** | 可选：`GPT_IMAGE_PREP` / `GPT_IMAGE_JPEG_QUALITY` / `GPT_IMAGE_TARGET_BYTES` / `GPT_IMAGE_MAX_IMAGES` / `REQUEST_MAX_TIME`（`MAX_EDGE` 仅高级可选） |
| `.codex/skills/gpt-image-generate/*` | **同步** | 与真相源一致（排除 `.env`、`gen-images/`） |
| `.devflow/gpt-image-cli-tooling/state.md` 等 | Apply 后更新 | 进度与决策 |

**不修改：** 仓库根 `scripts/generate-image.sh`（旧轨，另案废弃）；输出 png 后处理。

---

## CLI 契约（py / node 必须一致）

```text
run.py | run.mjs [选项] [提示词...]

选项:
  -o, --output PATH
  -m, --model NAME
  --base-url URL
  -p, --prompt-file PATH
  -i, --image PATH          # 可重复
  --retries N
  --raw
  --no-open
  # ----- 仅影响【输入参考图】预处理；不影响输出 png -----
  --prep off|light|medium|heavy   # 默认 medium；off=原样
  --no-prep                       # 等价 --prep off
  --jpeg-quality 1-100            # 覆盖档位内 JPEG/WebP 质量（有则优先）
  --target-bytes N                # 单张输入目标体积（字节）；编码阶梯逼近
  --max-edge N                    # 可选兜底：长边上限，0=关闭（默认 0，不启用固定长边）
  --max-images N                  # 默认 4
  -h, --help
```

优先级：CLI 精细参数 > `--prep` 档位预设 > `.env` > 内置默认。

提示词优先级：CLI 参数 > `--prompt-file` > `prompts/prompt-image.md`。

退出码：`0` 成功；`1` 业务/请求失败；`127` 无可用运行时（仅启动器）；`130` 中断。

**Agent 选档指引（写入 SKILL.md）：**

| 场景 | 建议 |
| --- | --- |
| 参考图很小 / 要像素级一致 | `--prep off` 或 `light` |
| 常规图生图（默认） | `--prep medium` |
| 曾出现 524、body 过大、多图 | `--prep heavy` 或 `--target-bytes 400000` |
| 需要可复现实验 | 显式 `--jpeg-quality` + 日志中的 before/after bytes |

---

## `---RESULT---` 契约（扩展，保持旧字段）

```text
---RESULT---
status=ok
path=...
path_rel=...
bytes=...
elapsed_seconds=...
elapsed_text=...
model=...
mode=text|image_edit
json_backend=python|node
runtime=python|node
source_image=...          # 多图时用 | 拼接，或 source_images_count=N
source_images_count=N
request_body_bytes=...
image_prep=off|light|medium|heavy
jpeg_quality=...
target_bytes=...
max_edge=0
input_bytes_before=...
input_bytes_after=...
skill_dir=...
---END_RESULT---
```

Agent 汇报：耗时 / 输出路径与大小 / 模式 / **输入压缩档位与 before→after**；用这些信息决定下次是否加重/减轻 prep。

---

## 请求体形状（多图）

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
  ]
}
```

无图时 `content` 仍为纯字符串（与现网兼容）。

---

## Chunk 1: Python 主路径

### Task 1 · `lib/image_prep.py` 输入预处理（档位 + 参数，非固定长边）

**Files:**
- Create: `.claude/skills/gpt-image-generate/lib/image_prep.py`

- [ ] **Step 1: 实现接口**

```python
# 职责：本地参考图 → (mime, raw_bytes, meta)
# meta: original_bytes, final_bytes, original_wh, final_wh, prep, jpeg_quality, scaled(bool)

@dataclass
class PrepOptions:
    prep: str = "medium"          # off|light|medium|heavy
    jpeg_quality: int | None = None
    target_bytes: int | None = None
    max_edge: int = 0             # 0 = 不启用固定长边；>0 才允许等比缩边兜底

def prepare_image(path: str, opt: PrepOptions) -> tuple[str, bytes, dict]:
    ...
```

规则（必须遵守）：

1. `prep=off` 或等价 → **原样**，不转码不缩边  
2. **默认不修改像素宽高**；主路径 = 格式/质量编码（Pillow 存 JPEG/WebP）  
3. quality：CLI/`jpeg_quality` 优先，否则按档位（light≈92，medium 阶梯 90→80，heavy 阶梯 85→65）  
4. `target_bytes`：在**不缩边**前提下用 quality 阶梯逼近；仍超标且 `prep=heavy` 或 `max_edge>0` 时才 **等比**缩边（保持宽高比），缩边是最后手段  
5. `max_edge==0`（默认）→ **永不**因「默认 1536」缩边  
6. 无 Pillow 且 prep≠off：无法编码压缩则错误退出并提示 `pip install pillow`（可对已很小的 JPEG 原样放行）  
7. 返回 mime + bytes + meta（供 RESULT / 日志）

- [ ] **Step 2: 本地手测（无网络）**

对同一大图分别 `--prep off/light/medium/heavy`（或直接调 `prepare_image`），确认：

- off：字节不变  
- light/medium：体积下降且宽高默认不变  
- heavy：体积更小；仅在需要时 scaled=true  

- [ ] **Step 3: 不单独 commit**（用户允许再 commit）

---

### Task 2 · `run.py` 全流程

**Files:**
- Create: `.claude/skills/gpt-image-generate/run.py`
- Modify/reuse: `.claude/skills/gpt-image-generate/lib/json_codec.py`（extract/has 逻辑可 import，避免复制粘贴分叉）

- [ ] **Step 1: 骨架**

  - `SCRIPT_DIR`、加载同级 `.env`（不覆盖已 export）  
  - argparse：上表 CLI（`-i` action=`append`）  
  - 校验 `OPENAI_API_KEY`  
  - 读提示词  

- [ ] **Step 2: 多图与预处理**

  - 解析多 path；张数 > max → 错误退出  
  - 组装 `PrepOptions`（`--prep` / quality / target-bytes / max-edge）  
  - 逐张 `prepare_image`，日志：`prep=… before=… after=… wh=… scaled=…`  
  - `mode=image_edit` if any images else `text`  

- [ ] **Step 3: 组装 body + HTTP**

  - 标准库 `urllib.request` POST JSON  
  - Header: `Authorization: Bearer` + `Content-Type: application/json`  
  - timeout = connect + max_time（与现 .env 名兼容：`CURL_MAX_TIME` 读作请求总超时）  
  - 重试：默认 5，指数/线性退避上限 30s；401 可不重试  

- [ ] **Step 4: 解析与落盘**

  - 复用 `json_codec` 的 `find_image_source` / extract 逻辑（URL 下载或 b64 解码）  
  - 默认输出 `gen-images/yyyy-mm-dd-hh-mm-ss.png`  
  - 魔数校验可保留 warning  
  - `--raw` 打印 JSON  
  - 成功打印 `---RESULT---`  
  - `--no-open`；否则 Win `os.startfile`，Mac `open`，Linux `xdg-open`  

- [ ] **Step 5: 验证**

```text
cd .claude/skills/gpt-image-generate
python run.py --help
python run.py --no-open "一只橘猫，简笔画"
# 有 key 时；无 key 时期望明确错误指向 .env
```

Expected: help 含 `--image` 可重复说明；无 key 时非 0 退出且中文错误。

---

## Chunk 2: Node 兜底 + 启动器

### Task 3 · 扩展 `json_codec.cjs` 多图 build

**Files:**
- Modify: `.claude/skills/gpt-image-generate/lib/json_codec.cjs`

- [ ] **Step 1:** `build` 支持多次 `--image`（或 `--images` 列表 + 重复 flag 解析在 run.mjs）

  content 数组：`[{type:text},{type:image_url},...]`

- [ ] **Step 2:** `extract` / `has` / `meta` 保持 Chat 协议兼容（已有则回归测一眼）

---

### Task 4 · `run.mjs` 能力对齐

**Files:**
- Create: `.claude/skills/gpt-image-generate/run.mjs`

- [ ] **Step 1:** CLI 与 `run.py` 相同 flag（可用手工 parse 或 `util.parseArgs`）  
- [ ] **Step 2:** 读 `.env`、组 body、`https`/`http` request、重试、落盘、RESULT  
- [ ] **Step 3:** 实现与 py 相同的 `--prep` / `--jpeg-quality` / `--target-bytes` / `--max-edge`；无图像库时 prep≠off 给出明确提示  
- [ ] **Step 4:**

```text
node run.mjs --help
node run.mjs --no-open "测试文生图"
```

Expected: 行为与 py 一致（同一 .env）。

---

### Task 5 · 薄启动器 + 降级 `run.sh`

**Files:**
- Create: `.claude/skills/gpt-image-generate/run`
- Create: `.claude/skills/gpt-image-generate/run.cmd`
- Modify: `.claude/skills/gpt-image-generate/run.sh`

- [ ] **`run`（Unix）伪逻辑**

```bash
#!/usr/bin/env bash
DIR="$(cd "$(dirname "$0")" && pwd)"
if command -v python3 >/dev/null; then exec python3 "$DIR/run.py" "$@"
elif command -v python >/dev/null; then exec python "$DIR/run.py" "$@"
elif command -v node >/dev/null; then exec node "$DIR/run.mjs" "$@"
else echo "需要 Python3 或 Node"; exit 127
fi
```

- [ ] **`run.cmd`（Windows）**

```bat
@echo off
setlocal
set DIR=%~dp0
where py >nul 2>&1 && py -3 "%DIR%run.py" %* && exit /b %ERRORLEVEL%
where python >nul 2>&1 && python "%DIR%run.py" %* && exit /b %ERRORLEVEL%
where node >nul 2>&1 && node "%DIR%run.mjs" %* && exit /b %ERRORLEVEL%
echo 需要 Python3 或 Node
exit /b 127
```

- [ ] **`run.sh`**：改为转调 `run.py`（找不到 python 再尝试 node），避免再维护千行 bash 业务逻辑。

---

## Chunk 3: 文档 + 同步 + 验收

### Task 6 · SKILL.md + notes + .env.example

**Files:**
- Modify: `.claude/skills/gpt-image-generate/SKILL.md`
- Modify: `.claude/skills/gpt-image-generate/references/notes.md`
- Modify: `.claude/skills/gpt-image-generate/.env.example`

- [ ] Preflight：优先 py，否则 node；安装说明  
- [ ] 执行示例：`run.py` / `run.cmd`；多图；**`--prep` 选档表**（Agent 自行判断）  
- [ ] 明确：压缩参数 **只影响输入参考图**；输出不管；**默认不固定长边**  
- [ ] `references/notes.md`：预处理算法 +（有条件时）探针结论  
- [ ] 目录结构与同步清单更新  

---

### Task 7 · 同步 `.codex` + mission 状态

**Files:**
- Sync: `.codex/skills/gpt-image-generate/`（脚本与文档，排除 `.env`、`gen-images/`）
- Update: `.devflow/gpt-image-cli-tooling/state.md`、`decision-log.md`（Apply 完成时）

- [ ] 复制/对齐真相源文件  
- [ ] 确认 `.gitignore` 已忽略 codex 侧 `.env` 与 `gen-images/`（已有则跳过）  

---

### Task 8 · 验证清单（Apply 时勾选）

- [ ] `python run.py --help` / `node run.mjs --help`：含 `--prep`、`--jpeg-quality`、`--target-bytes`、`--max-edge`（默认 0）  
- [ ] 无 API key → 中文错误、指向 skill 同级 `.env`  
- [ ] 文生图（有 key）：成功 + RESULT  
- [ ] 同一参考图：`prep=off` vs `medium` → after bytes 变化符合预期，**medium 默认宽高不变**  
- [ ] 双图：`--image a --image b` body 含两个 `image_url`  
- [ ] Win：`run.cmd` 能进 py  
- [ ] 双目录同步一致  

### Task 9 · 输入体积探针（可选但推荐，有 key 时）

目的：弄清 **什么输入体积/档位更容易超时**，写成经验而不是拍脑袋固定长边。

- [ ] 选 1 张真实大参考图（如 OC 人设图）  
- [ ] 分别用 `--prep off` / `light` / `medium` / `heavy` 跑图生图（可 `--no-open`）  
- [ ] 记录：输入 before/after bytes、request_body_bytes、HTTP 结果、耗时  
- [ ] 写入 `references/notes.md` 小节「探针结论（日期）」+ SKILL 里一句话建议  
- [ ] **不**据此把默认改回固定 1536；只更新 Agent 选档建议与默认 `medium` 的 target 量级  

若无 key / 中转不稳：跳过 Task 9，文档写「待补探针」。

**不做：** 全局 ESLint；输出 png 体积断言；默认强制等比缩到固定长边。

---

## 验收标准（Definition of Done）

1. Win/Mac 均可：`python run.py` 或启动器完成生图  
2. 无 py 有 node：`node run.mjs` 完成同等 CLI 生图  
3. 多参考图（≤4）可请求  
4. 输入压缩 **可调档 + 精细参数**；默认质量优先、**不固定长边**；RESULT 暴露 before/after 供 Agent 判断  
5. 输出图不强制压缩  
6. SKILL 指导 Agent 如何选 `--prep`  
7. 文档与 `.codex` 同步；可选探针结论  
8. 不再要求 jq 才能跑主路径  

---

## 风险与缓解

| 风险 | 缓解 |
| --- | --- |
| py/node 双实现漂移 | 同一 CLI/RESULT/请求体契约；改协议同 PR 改两边 |
| 无 Pillow 无法编码压 | prep≠off 时提示安装；或 `--prep off` 自行承担超时风险 |
| 默认档过狠伤细节 | 默认 medium + 不缩边；脸部场景文档建议 light |
| 固定长边误伤 | 默认 max_edge=0；缩边仅 heavy 兜底或显式参数 |
| 中转对多图支持差 | 先 2 张实测；失败记 bug-log，上限可调 |
| `run.sh` 破坏旧习惯 | 薄封装保留 argv 转发 |

---

## 明确不在本次

- skill 内嵌 Python/Node 运行时  
- 输出图片大小/质量治理  
- 异步 job / Web UI  
- T7 size/ratio 官方字段（另 plan；Chat 协议需单独设计）  
- 废弃仓库 `scripts/generate-image.sh`（可 backlog）  

---

## 执行说明

- **Plan 落盘路径:** `.devflow/gpt-image-cli-tooling/plans/2026-07-18-python-node-cross-platform-plan.md`  
- **真相源:** `.claude/skills/gpt-image-generate/`  
- **Commit:** 仅在用户明确允许后；信息用中文  
- **实现顺序:** Task 1→2→3→4→5→6→7→8  

用户确认 plan 后，可选：

1. **本会话 Inline Apply**（按 task 推进）  
2. **Subagent-Driven**（每 task 子代理 + 审查）  
