# Development Overview · gpt-image-cli-tooling

## 定位

完整过程总览；默认恢复不读本文件。

## 背景

用户需在本地调用中转站 GPT Image（Responses 协议），从 curl / REST Client 演进为可维护脚本，再封装为**自包含 Claude Skill**，并纳入 devflow 重型治理。

## 已完成阶段（本对话）

1. **联调**：确认 `/v1/responses` + `image_generation`；响应 `output[].result` base64  
2. **脚本 MVP**：env、提示词文件、gen-images、重试、loading  
3. **热修**：流式解码、双计时、Ctrl+C 第一轮、524 说明  
4. **Mission 补录**：重型 skeleton + plan + spec  
5. **T9 Skill**：完全自包含（不依赖 REPO_ROOT / 仓库 scripts）  
6. **对齐 .http 体验**：默认 model=`gpt-image-2`；curl 默认 180s；Ctrl+C force kill  
7. **安全**：`generate-image.http` untrack + ignore；核查 key 是否进历史  

## 关键提交（本对话相关，摘录）

| Commit | 说明 |
| --- | --- |
| `f76cec2` | 脚本 + mission 初版 |
| `e84276d` | 自包含 gpt-image-generate skill |
| `f35d114` | 默认 gpt-image-2、中断/超时、untrack http |

## 第一版 vs 后续

| 类别 | 内容 |
| --- | --- |
| 第一版已交付 | Skill 出图、重试、中断、RESULT、默认 image-2 |
| 下轮优先 | T7 size/ratio/quality；T8 Verify |
| 明确延期 | 异步 task、站点 UI、纯 ratio 官方字段（见 `deferred/`） |

## 推荐读取

- 恢复：`state.md` → `checkpoints.md`
- 续作：`spec/tasks.md` + `handoffs/` 最新 + NEXT-SESSION-PROMPT
