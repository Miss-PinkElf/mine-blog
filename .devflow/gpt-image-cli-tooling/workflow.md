# Workflow · GPT Image CLI 工具链

## 路径

**重型路径（Heavy）**

## 当前阶段

**Close / Handoff（2026-07-18）** → 下轮从 **Apply T7（Chat 适配）** 或 **Verify T8** 恢复

## 目标

本地可用的 GPT Image **文生图 / 图生图（可多参考图）** 工具链（中转 `shell.wyzlab.ai`），以自包含 Skill 为主入口（Claude + Codex 双目录）。

**现行协议**：OpenAI **Chat Completions**（`POST /v1/chat/completions`）。

**现行入口（2026-07-18 起）**：**Python `run.py` 优先**，无 Python 时 **Node `run.mjs`**；不再以 bash 业务逻辑为主。

## 范围

### 已交付

| 版本 | 内容 |
| --- | --- |
| 第一版 | 纯文生图、重试、中断、RESULT、默认 gpt-image-2、自包含 skill |
| 第二版 | `--image` 图文同传；JSON 回退；双目录 |
| 第三版 | 协议切换 Chat Completions；Markdown URL 落盘 |
| **第四版（本轮）** | **跨平台 py/node**；多图；输入 `--prep`；启动器；双图实测落盘 |

### 下轮优先（仍属本 mission，未延期）

- T7：`--size` / `--quality` / `--ratio`（**第一版即可**；Chat 下设计，勿写 `tools[0]`）
- T8：无 key / 空 prompt / Ctrl+C 等抽检

### 明确延期（`deferred/` + 本轮补充）

- 异步 task、站点 UI、仅 aspect_ratio
- skill **内嵌** Python/Node 运行时
- **输出** png 体积/尺寸治理
- 仓库 `scripts/generate-image.sh` 迁 Chat / 废弃双轨（backlog）

### Backlog（轻量）

见 `backlog.md`（含：多图默认 heavy、体积探针笔记、meta.json 旁路等）
