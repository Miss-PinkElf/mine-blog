# Tasks · gpt-image-cli-tooling

## T1 · 脚本骨架与配置加载

- [x] `generate-image.sh` 可执行
- [x] 自动读取 `scripts/.env`
- [x] `.env.example` 模板
- [x] gitignore 密钥与产物

## T2 · Responses 生图主路径

- [x] `POST /responses` + `image_generation` / `action=generate`
- [x] 解析 `output[].result` base64
- [x] 兼容字段探测（失败摘要截断）

## T3 · 提示词与落盘

- [x] 默认读 `prompts-images/prompt-image.md`
- [x] 文件不存在/空内容报错
- [x] 输出到 `gen-images/yyyy-mm-dd-hh-mm-ss.png`
- [x] 重名追加随机数

## T4 · 可观察性与可靠性

- [x] loading + 本步/总计耗时
- [x] 最多重试 5 次，递增等待
- [x] 流式解码避免 bash 大变量
- [x] Ctrl+C 立即退出且不重试

## T5 · 调试资产

- [x] `generate-image.http`（**仅本机**；已 untrack + gitignore，勿再提交）
- [x] bug-log 记录 524 / 慢解析 / 中断 / spinner 卡死
## T6 · 过程治理（重型）

- [x] Mission Init（workflow/state/origin/decision）
- [x] Align/Plan 落盘
- [x] proposal / design / tasks 三件套
- [x] 本轮代码与文档提交（`35046b2`）

## T7 · 尺寸 / 比例 / 质量（下一轮 Apply）

- [ ] CLI：`--size`、`--quality`、`--ratio`
- [ ] `.env`：`OPENAI_IMAGE_SIZE` / `OPENAI_IMAGE_QUALITY` / `OPENAI_IMAGE_RATIO`
- [ ] 请求体写入 tools 字段
- [ ] help 与 plan 对齐说明
- [ ] 真实调用验证至少 1:1 与 2:3 各一次

## T8 · Verify

- [ ] 无 key 失败路径
- [ ] 空 prompt 文件失败路径
- [ ] 成功出图路径（或脱敏日志证据）
- [ ] Ctrl+C 中断路径抽检

## T9 · Claude Skill 封装（自包含）

- [x] `.claude/skills/gpt-image-generate/` 完全自包含
- [x] `run.sh` 与 `.env` / `gen-images` / `prompts` 同级
- [x] **不**依赖仓库 `scripts/`、不使用 `REPO_ROOT=../../..`
- [x] 缺 `jq` 时明确提示安装
- [x] 提示词：用户给出或按意图自动扩写
- [x] 成功后汇报：耗时、图片大小、图片路径（`---RESULT---`）
- [x] 默认 model=`gpt-image-2`；Ctrl+C force kill；`CURL_MAX_TIME` 默认 180

## T10 · 本会话收尾

- [x] 更新 state/workflow/checkpoint/handoff/deferred
- [x] NEXT-SESSION-PROMPT
- [x] 提交收尾文档（不含 gitignore/config/tsconfig 的额外要求已遵守）

## 当前建议执行顺序

1. **下轮优先 T7** size/ratio/quality（skill `run.sh` 为主）
2. 再 T8 Verify
3. 延期项见 `deferred/`，勿在本 mission 偷做 Web UI