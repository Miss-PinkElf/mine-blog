# Development Overview · oc-mugen-rin-character-sheets

## 一句话

为 OC「无限凛」建立可复用动漫人设设定图；工具为自包含 `gpt-image-generate` skill（`gpt-image-2` + 中转）。

## 阶段脉络

1. **准备**：读人设、下载 HTML/角色参考、理解 cat-oc-design 设定图体系
2. **阻塞**：中转上游 500（非 key/非本机代理）
3. **恢复出图**：smoke 通过；产出全局/表情/动作/JK 场景（01–04）
4. **prompt-2**：下载风格参考；日常 ×3 + 表情包第一版（中转 524 频发，多用文生图简化）
5. **已知问题**：复杂/图生图易 524；用户对日常/表情包观感一般，暂接受第一版
6. **Close**：文档 handoff；提交本 mission 相关产物（不含 skill 无关改动）

## 与其它 mission

- 工具链：`gpt-image-cli-tooling`（skill 能力；本 mission 只消费）
