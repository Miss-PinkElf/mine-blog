# Align · 图文同传 + jq 可用性 + 双 Skill 同步

- **Mission**：`gpt-image-cli-tooling`
- **日期**：2026-07-16
- **阶段**：Align（已确认方向，待用户复核本文后进 Plan）
- **路径**：Heavy

## 1. 背景与实测结论

| 项 | 结论 |
| --- | --- |
| 现有 skill | 仅纯文生图：`input` 为字符串 + `tools[].action=generate` |
| 接口能力 | 支持「参考图 + 文字」：`input_text` + `input_image(data URL)` |
| 实测成功 | curl 多模态请求 HTTP 200；响应 `action=edit`；已出图 |
| urllib | 中转侧可能 Cloudflare `error code: 1010` → **继续用 curl** |
| jq | Mac 主环境通常有；Windows 本机实测可能缺失 |
| 目录 | `.claude/skills/gpt-image-generate/` 与 `.codex/skills/gpt-image-generate/` **都要更新** |

## 2. 本轮范围（In）

### A · 图文同传 / 图生图编辑

- CLI：`--image PATH`，短选项 `-i PATH`
- 无图：保持现有文生图路径
- 有图：多模态 `input`，本地文件 → base64 data URL
- tools：有参考图时 `action: "edit"`；无图时 `action: "generate"`
- mime：按扩展名 `png/jpg/jpeg/webp/gif`
- RESULT：增加 `mode=text|image_edit`，可选 `source_image=`
- 更新 `SKILL.md` 触发词与用法（改图 / 参考图 / 图生图）

### B · jq 可用性

- **正式路径仍依赖 jq**（主环境 Mac，与现架构一致）
- 缺 jq：清晰分平台安装提示（brew / choco / scoop / 官方包）
- **可选回退（轻量，非重写整栈）**：
  - 若存在 `node` 或 `python3`/`python`，可用于 **JSON 抽取 result base64 字符串（stdout 流式）**
  - **解码**仍走系统 `base64 -d`/`-D`/`--decode`（与现逻辑一致）
  - 组装请求体优先 jq；无 jq 时用 node/python 生成 JSON 文件再 curl
  - **不**把纯 bash 正则解析大 JSON 当作正式方案（脆弱且难流式）

### 双目录

- **真相源**：`.claude/skills/gpt-image-generate/`
- **同步目标**：`.codex/skills/gpt-image-generate/`
- 同步：`run.sh`、`SKILL.md`、`prompts/`、`references/`、`.env.example`
- **不同步**：`.env`、`gen-images/`
- gitignore：为 `.codex/.../.env` 与 `gen-images/` 补条目

### Mission 文档

- 更新 `origin` / `state` / `workflow` / `decision-log` / `spec/*` / `NEXT-SESSION-PROMPT`
- 新增任务 T11–T15（见下）；T7/T8 保留后续

## 3. 明确不做（Out / 延期）

- T7 size/quality/ratio（可后续轮次）
- 站点内嵌生图 UI
- 异步 task 轮询
- 用 Python/Node **整文件重写** run.sh（bash 仍为主入口）
- 纯 bash 解析嵌套 JSON 大 base64

## 4. 解析链路说明（回答：bash / JS 能否解析 base64）

生图落盘实际是 **两步**，不要混为一谈：

```text
响应 JSON ──(1) 抽取字段──► base64 文本流 ──(2) base64 解码──► PNG 文件
              jq / node / python              系统 base64 命令
```

| 步骤 | 工具 | 说明 |
| --- | --- | --- |
| (1) 从 JSON 抽出 `output[].result` | **jq（首选）** / **Node 一行脚本** / **Python** | 需要懂 JSON 路径；响应可达数 MB，应 **流式 stdout**，禁止塞进 bash 变量 |
| (2) base64 → 二进制 | **系统 `base64`**（macOS/Linux/Git Bash 均有） | 已有：`base64 -d` / `-D` / `--decode`；**不必用 JS 再解一层** |
| 请求体组装 | **jq -n**（首选）/ node / python 写临时 JSON | 有图时 body 含 data URL，体积大，写文件再 `curl --data-binary @file` |

### Bash

- **解码 base64**：可以，系统自带 `base64`（现 skill 已用）
- **从 JSON 抽 base64**：纯 bash 不现实（嵌套 + 超大字符串）；**不推荐**

### JavaScript（Node）

- **可以**做步骤 (1)，例如流式/`JSON.parse` 后 `process.stdout.write(result)`
- 解码步骤 (2) 仍建议 pipe 给系统 `base64`，或 `Buffer.from(b64,'base64')` 直接写文件（二选一，plan 里定一种，优先与现管道一致：抽出 | base64 -d）

### Python

- 同上，适合当 node 不存在时的第二回退

### 决策（本轮）

1. **首选整链：jq + 系统 base64**（Mac 主路径）
2. **无 jq 时**：node 优先回退 → python 次回退 → 都没有则安装提示并退出
3. **禁止**：`B64="$(jq ...)"` 整段进 bash 变量（历史踩坑）

## 5. 请求体设计（摘要）

### 纯文

```json
{
  "model": "...",
  "input": "<prompt string>",
  "tools": [{ "type": "image_generation", "action": "generate" }]
}
```

### 图文

```json
{
  "model": "...",
  "input": [{
    "role": "user",
    "content": [
      { "type": "input_text", "text": "<prompt>" },
      { "type": "input_image", "image_url": "data:image/png;base64,..." }
    ]
  }],
  "tools": [{ "type": "image_generation", "action": "edit" }]
}
```

## 6. 建议任务切分（进 Plan/Spec 时落 tasks）

| ID | 内容 |
| --- | --- |
| T11 | `run.sh`：`--image`/`-i`、多模态 body、mode 与 RESULT |
| T12 | `SKILL.md` + `references/notes.md` |
| T13 | jq 检测增强 + node/python 轻量回退（JSON 组装/抽取） |
| T14 | 同步 `.codex/skills/...` + gitignore |
| T15 | mission 文档 + 回归/图文 Verify 证据 |

## 7. 验收标准

1. 无 `--image`：纯文生图仍成功（回归）
2. 有 `--image`：参考图+文字可出图，RESULT 含 `mode=image_edit`
3. 无 jq 但有 node 或 python：仍能完成一次纯文或图文（至少一种）
4. 无 jq 且无 node/python：中文安装提示，非黑盒失败
5. `.claude` 与 `.codex` 的 `run.sh`/`SKILL.md` 内容一致（忽略换行差异可接受）
6. 不提交 `.env`、key、`gen-images/`

## 8. 风险

| 风险 | 缓解 |
| --- | --- |
| data URL 使请求体 ~2MB+ | curl 文件投递；适当增大 `CURL_MAX_TIME` 文档说明 |
| 双目录漂移 | Apply 末强制 diff/同步步骤 |
| node/python 实现与 jq 行为不一致 | 共用同一字段探测顺序；小函数封装 |
| 中转对 edit/generate 行为差异 | 有图固定 `edit`（实测更贴切） |

## 9. 用户确认状态

- [x] 范围 A+B
- [x] 方案 2（claude 真相源 + 同步 codex）
- [x] 有图 action=edit
- [x] B 以 jq 为主 + 安装提示；并吸收 **node/python 可选 JSON 回退**
- [ ] 用户复核本 Align 笔记后进入 Plan

---

复核通过后：进入 `superpowers-writing-plans` 写
`.devflow/gpt-image-cli-tooling/plans/2026-07-16-image-text-jq-fallback-plan.md`
再更新 `spec/proposal.md` / `design.md` / `tasks.md`，最后 Apply。
