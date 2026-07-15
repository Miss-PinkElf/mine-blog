# Handoff · 2026-07-15-001 会话收尾

## 基础信息

- 创建时间：2026-07-15
- mission：`gpt-image-cli-tooling`
- 当前阶段：Close / Handoff（第一版完成，T7/T8 留给下轮）
- handoff 编号：001
- 是否 superseded：否

## 当前目标

维护并演进本地 **GPT Image（Responses）** 工具链；**主入口是自包含 skill**，不是仓库 scripts 反查。

## 当前进度

- 第一版可用：配置 key → 跑 `run.sh` 或触发 skill → 得到 png + 耗时/大小/路径
- 默认 model：`gpt-image-2`
- 重试、中断、超时已热修
- T7（size/ratio/quality）、T8（Verify）未做

## 本轮完成内容

- [x] Responses 生图脚本（仓库 `scripts/generate-image.sh`）
- [x] 自包含 skill `.claude/skills/gpt-image-generate/`
- [x] 默认 `gpt-image-2`；`CURL_MAX_TIME=180`；Ctrl+C force kill
- [x] `---RESULT---` 机器可读结果
- [x] 缺 jq 中文提示
- [x] devflow 重型 mission + spec + bug-log
- [x] `generate-image.http` 本地保留、git untrack
- [x] 核查：用户询问的 `sk-C2h0…` **未进 git 历史**（另一把 `sk-nD7a…` 曾在历史 http 中）

## 关键决策与原因

| 决策 | 备选 | 原因 |
| --- | --- | --- |
| Skill 自包含 | 调用仓库 scripts | 用户要求 env/run 同级、可独立带走 |
| 默认 gpt-image-2 | 默认 gpt-5.4 | 对齐 REST Client / 中转习惯 |
| size/ratio 不做第一版 | 本轮实现 T7 | 先稳定出图；T7 下轮 |
| http 不入库 | 继续跟踪 | 防 key |

## 关键文件 / 产物

| 文件 | 作用 | 相关性 |
| --- | --- | --- |
| `.claude/skills/gpt-image-generate/run.sh` | **主生图入口** | 高 |
| `.claude/skills/gpt-image-generate/SKILL.md` | Agent 触发与流程 | 高 |
| `.claude/skills/gpt-image-generate/.env` | 本机 key（ignore） | 高 |
| `scripts/generate-image.sh` | 旁路脚本（非 skill 依赖） | 中 |
| `scripts/generate-image.http` | 本机 REST 调试（ignore） | 中 |
| `spec/tasks.md` | T7/T8 清单 | 高 |

## 风险 / 阻塞 / 开放问题

- [ ] 中转 524 / 排队：长任务仍可能失败，依赖重试
- [ ] 历史 commit 中若曾含其它 key，远端若已 push 需当暴露处理
- [ ] T7 中转对 `tools[].size/quality` 兼容性需实机验证
- [ ] skill 与 scripts 双轨是否长期保留（backlog）

## 立即下一步

1. 新对话读取 `state.md` + `checkpoints.md` + 本 handoff  
2. 实现 **T7**：`--size` / `--quality` / `--ratio`（改 skill `run.sh` 为主，scripts 可同步）  
3. **T8** 抽检：无 key、空 prompt、成功出图、Ctrl+C  
4. 不要做：站点 UI、异步 task（见 `deferred/`）

## 恢复指引

1. `handoffs/index.md` → 本文件  
2. `state.md`、`checkpoints.md`  
3. `spec/tasks.md`、`spec/design.md`  
4. 从 T7 第 1 条开始  

## 可从活跃上下文移除的内容

- 长 base64 响应样例、逐次 curl 调试日志  
- Java 注解 vs JS 装饰器闲聊（与本 mission 无关）  
