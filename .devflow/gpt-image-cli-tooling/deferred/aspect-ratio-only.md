# 延期：仅控制比例（无独立官方字段）

- **状态**：延期（能力并入 T7 的 ratio→size 映射，不做「纯 ratio API」幻想）
- **说明**：OpenAI GPT Image 以 `size: WxH` 表达比例，无单独 aspect_ratio 主参数
- **第一版**：不实现 CLI ratio
- **后续**：T7 用 `--ratio 2:3` 映射到 `1024x1536` 等常用 size
