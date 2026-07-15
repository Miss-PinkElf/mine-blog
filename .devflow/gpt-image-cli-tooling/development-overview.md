# Development Overview · gpt-image-cli-tooling

## 定位

完整过程总览；默认恢复不读本文件。

## 背景

用户需要本地调用中转站 GPT Image（Responses 协议），从 curl / REST Client 演进为可维护 bash 工具，并纳入 devflow 重型治理。

## 已完成阶段

1. **探索与联调**：确认 `/v1/responses` + `image_generation`；真实 JSON 含 `output[0].result`
2. **脚本 MVP**：env、提示词文件、落盘、重试、loading
3. **热修**：流式解码、中断退出、双计时
4. **Mission 补录**：重型骨架 + plan + spec

## 关键决策

见 `decision-log.md`。

## 当前开放问题

- 中转对 `tools[].size/quality` 的兼容性需实机验证
- 524 是否可升级为异步接口

## 推荐读取

- 恢复：`state.md` → `checkpoints.md`
- 续作 Apply：`spec/tasks.md` + `spec/design.md`
