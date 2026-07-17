# Handoff · Chat 协议切换会话收尾

## 基础信息

- 创建时间：2026-07-17
- mission：`gpt-image-cli-tooling`
- 当前阶段：Close / Handoff
- handoff 编号：2026-07-17-001
- 是否 superseded：否

## 当前目标

维护本地可用的 GPT Image 文生图 / 图生图 skill；本轮完成 **Chat Completions 主路径切换** 并验证。

## 当前进度

- 第三版（Chat）已交付并通过实测
- T7 / T8 未做（下轮）
- 仓库 `scripts/generate-image.sh` 仍为旧 Responses（非 skill 主路径）

## 本轮完成内容

- [x] Skill 端点改为 `POST /v1/chat/completions`
- [x] 文生图 messages 文本；图生图 text + image_url(data URL)
- [x] 响应 Markdown URL 下载 / data URL 解码；jq/node/python 一致
- [x] 修 printf RESULT；修 has 短 base64
- [x] 双目录同步 `.claude` → `.codex`
- [x] 实测文生图、图生图、OC 参考图 `zzz-prompt-debug/origin/OC/generated/rin-01-global-design.png`
- [x] mission 文档 / handoff / NEXT-SESSION-PROMPT 更新

## 关键决策与原因

| 决策 | 备选方案 | 原因 |
| --- | --- | --- |
| 主协议用 Chat Completions | 继续 Responses；或 `/images/generations` | 用户明确要求 v1 chat、不用 responses |
| 响应优先 Markdown URL | 仅 base64 | 中转实测 chat 常返回 `![image](https://...)` |
| 本轮不迁 scripts | 同步改仓库脚本 | skill 为真相源；scripts 双轨记 backlog |
| T7 下轮做、须 Chat 适配 | 照搬 tools[0].size | Chat 无稳定 tools 写入点 |

## 关键文件 / 产物

| 文件 | 作用 | 相关性 |
| --- | --- | --- |
| `.claude/skills/gpt-image-generate/run.sh` | 生图入口 | 高 |
| `.claude/skills/gpt-image-generate/lib/json_codec.*` | JSON 组装/解析 | 高 |
| `.claude/skills/gpt-image-generate/SKILL.md` / `references/notes.md` | skill 文档 | 高 |
| `.codex/skills/gpt-image-generate/*` | Codex 同步副本 | 高 |
| `.devflow/gpt-image-cli-tooling/**` | mission 真相源文档 | 高 |

## 风险 / 阻塞项 / 开放问题

- [ ] T7 第一版 size/ratio 如何写进 Chat（提示词 vs 扩展字段）尚未拍板
- [ ] `scripts/generate-image.sh` 与 skill 协议不一致，新人易踩坑
- [ ] 中转 524 仍可能出现（重试缓解；本轮 chat 实测较稳）

## 立即下一步

1. 新对话读 `state.md` + `checkpoints.md` + 本 handoff
2. 实施 **T7**（Chat 适配第一版 size/quality/ratio）
3. 实施 **T8** 失败路径抽检
4. 可选：处理 scripts 双轨（迁移或标注废弃）

## 恢复指引

1. 先读取 `handoffs/index.md`
2. 再读取本 handoff
3. 然后读取 `state.md` 与 `checkpoints.md`
4. 实施前读 `spec/tasks.md` + `spec/design.md`
5. 从「立即下一步」第 1 条继续

## 可从活跃上下文移除的内容

- 旧 Responses 请求体细节（仅历史）
- 本轮 loading 刷屏日志
- 已成功的中间失败 524 样本（gen-images/failed-* 本机 ignore）
