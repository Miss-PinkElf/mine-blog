# Backlog

## 已并入 T7 / 下轮讨论（勿再当悬空问题）

- ~~Chat size/quality 写提示词还是扩展字段~~ → **已确认 `metadata.image_*`**（T7）
- 多图时 SKILL 默认建议 `--prep heavy` / 控 body（策略文档）
- `references/notes.md` 体积/断连探针对照表（官方对齐后已有部分；可补全）

## 第一版之后 / 轻量后续

- metadata 全量 CLI：`image_background` / `image_output_format` / `image_moderation` / `image_partial_images`（T7 第一版不做）
- `--fidelity` 与 http(s) 参考图直通（可与 T7 同批，非必须）
- 本地大图「先上传再 URL」管线（明确延期倾向，见 deferred 或单独立项）
- 保存无 base64 的 response meta.json（旁路排查）
- 多提示词批量出图
- npm script / make 快捷入口
- skill 与仓库 `scripts/generate-image.sh` 是否长期双轨或只保留 skill（待定）
- **仓库 `scripts/generate-image.sh` / `generate-image.http` 仍为旧 Responses**，是否迁移 Chat 或标注废弃（待定；非 skill 主路径）
- 图文请求默认 `CURL_MAX_TIME` 是否再调大
- Node 侧纯 JS 图像压缩（当前依赖 Python+Pillow）
- medium 压缩对已很小的 JPEG 可能「越压越大」——「仅当变小才替换」
