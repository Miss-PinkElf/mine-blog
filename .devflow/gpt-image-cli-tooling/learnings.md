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
