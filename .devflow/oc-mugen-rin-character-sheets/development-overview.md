# Development Overview · oc-mugen-rin-character-sheets

## 一句话

为个人 OC「无限凛」建立可复用的动漫向角色设定图资产，生图方法对齐 cat-oc-design，工具用仓库自包含 `gpt-image-generate` skill。

## 背景

用户在 `zzz-prompt-debug/origin/OC/` 给出人设文档与参考图需求，并指定参考咖啡馆猫咪 OC 设定图页面的「设定图驱动生成」工作流。

## 阶段脉络

1. **准备（本轮）**：读人设、下 HTML/图、下角色参考、理解版式
2. **生图（阻塞）**：`gpt-image-2` 文生图/图生图均被中转上游 500 挡住
3. **后续**：API 恢复后先出全局设定图 v1，再视需要扩展表情/动作/场景

## 与其它 mission 关系

- 工具链：`gpt-image-cli-tooling`（skill 实现；本 mission 消费 skill，不在此改 T7/T8 范围）
