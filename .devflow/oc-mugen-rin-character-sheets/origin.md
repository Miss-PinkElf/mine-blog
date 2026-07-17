# Origin · 原始输入索引

## 定位

记录本 mission 的原始用户诉求与关键上下文来源。可追加，非冻结文件。

## 来源列表

| 序号 | 来源 | 时间 | 用途 | 吸收状态 |
| --- | --- | --- | --- | --- |
| 1 | `zzz-prompt-debug/origin/OC/prompt-1.md` | 2026-07-17 | 需求：读人设→理解图→对照 HTML→生成人设图 | 已吸收 |
| 2 | `zzz-prompt-debug/origin/OC/人设.md` | 2026-07-17 | 角色「无限凛」性格/外貌/衣着/旧 prompt | 已吸收到计划与提示词草稿 |
| 3 | 人设文档内语雀图（10 张） | 2026-07-17 | 角色视觉参考 | 已下载 `ref-character/char-01..10.png` |
| 4 | https://cafe3310.github.io/chocho-miemie-album/posts/cat-oc-design.html | 2026-07-17 | 设定图方法论与版式参考 | 已下载 `ref-html/` |
| 5 | skill：`.codex/skills/gpt-image-generate/`（`$gpt-image-generate`） | 2026-07-17 | 生图工具 | 已用；出图失败 |
| 6 | 对话：可自行理解图片再结合 skill 出图 | 2026-07-17 | 工作方式 | 已执行（部分） |
| 7 | 对话：先测 skill；模型仅 `gpt-image-2` 可用；其它模型不可行 | 2026-07-17 | 模型约束 | 已记录到 learnings |
| 8 | 对话：怀疑代理；要求不使用代理再试 | 2026-07-17 | 排障 | 已验证本机无系统代理；noproxy 仍 500 |
| 9 | 对话：换 key 测试 | 2026-07-17 | 排障 | 新旧 key 同症状；官方 api.openai.com 拒中转 key |
| 10 | 对话：域名可能挂了；devflow 重型收尾 + 提交相关代码 + 新开对话 | 2026-07-17 | Close/Handoff | 本轮 |

| 11 | 对话：中转恢复，再测 skill；固定 gpt-image-2 | 2026-07-17 | 出图恢复 | 已吸收 |
| 12 | 对话：是否等太短/有无报错 | 2026-07-17 | 排障：524 非本地掐断 | 已吸收 bug-log |
| 13 | 对话：继续补设定图（表情/动作/场景） | 2026-07-17 | 01–04 完成；05 失败 | 已吸收 |
| 14 | 对话：上下文过长，收尾 + **不提交** | 2026-07-17 | Close/Handoff | 本轮 |

## 备注

- API Key 仅本机 skill 同级 `.env`，禁止提交。
- 大体积参考图在 `zzz-prompt-debug/origin/OC/ref-*`；`_preview/` 为可再生成的缩略图，可不提交。
- 勿提交 `gen-images/`、`.env`、测试用临时 key。
