# Tasks · gpt-image-cli-tooling

## T1 · 脚本骨架与配置加载

- [x] `generate-image.sh` 可执行
- [x] 自动读取 `scripts/.env`
- [x] `.env.example` 模板
- [x] gitignore 密钥与产物

## T2 · 生图主路径（历史：Responses → 2026-07-17 起 Chat）

- [x] （历史）`POST /responses` + `image_generation` / `action=generate`
- [x] （历史）解析 `output[].result` base64
- [x] 兼容字段探测（失败摘要截断）
- [x] **（现行）`POST /chat/completions` + `messages`**（见 T16）
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

## T7 · 尺寸 / 比例 / 质量（下一轮 Apply · 第一版即可）

- [ ] CLI：`--size`、`--quality`、`--ratio`
- [ ] `.env`：`OPENAI_IMAGE_SIZE` / `OPENAI_IMAGE_QUALITY` / `OPENAI_IMAGE_RATIO`
- [ ] **按 Chat 协议设计写入方式**（不可再写 Responses `tools[0]`；可选：提示词前缀约定 / 网关扩展字段）
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

## T11 · 图文同传（参考图 + 文字）

- [x] CLI：`--image` / `-i PATH`
- [x] 有图：多模态 input + `action=edit`；body 临时文件投递
- [x] 无图：保持 generate 字符串 input
- [x] RESULT：`mode` / `source_image`
- [x] 参考图不存在/不可读时中文报错

## T12 · Skill 文档

- [x] 更新 `.claude/.../SKILL.md`（触发、用法、双路径 `.claude`/`.codex`）
- [x] 更新 `references/notes.md`

## T13 · JSON 工具链回退

- [x] jq → node → python 探测
- [x] 缺全部工具时分平台安装提示
- [x] 禁止大 base64 进 bash 变量

## T14 · 双目录同步 + gitignore

- [x] 同步到 `.codex/skills/gpt-image-generate/`
- [x] gitignore codex skill 的 `.env` / `gen-images/`

## T15 · Verify + mission 收尾

- [x] help / 语法 / 双目录 diff
- [x] 更新 state/workflow/checkpoint（本轮）

## T16 · Chat Completions 协议切换（2026-07-17）

- [x] `run.sh` 端点改为 `POST /chat/completions`
- [x] 请求体：文生图 messages 文本；图生图 text + image_url(data URL)
- [x] 响应：Markdown URL 下载 / data URL base64 解码；codec 三后端一致
- [x] 修 printf RESULT 块；修 has 短 base64
- [x] 同步 `.codex/skills/gpt-image-generate/`
- [x] 实测：文生图、图生图、OC 大参考图
- [x] mission 文档 + handoff 收尾

## 当前建议执行顺序（2026-07-17 更新）

1. **本轮 T16：已完成**（Chat 协议 + 实测 + 收尾）
2. 后续：T7 size/ratio/quality（Chat 适配第一版）→ T8 完整 Verify
3. 可选 backlog：仓库 scripts 迁 Chat / 废弃双轨