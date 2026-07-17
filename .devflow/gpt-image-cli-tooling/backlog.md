# Backlog

- 保存无 base64 的 response meta.json（旁路，便于排查）
- 多提示词批量出图
- npm script / make 快捷入口
- skill 与仓库 `scripts/generate-image.sh` 是否长期双轨或只保留 skill（待定）
- **仓库 `scripts/generate-image.sh` / `generate-image.http` 仍为旧 Responses**，是否迁移 Chat 或标注废弃（待定；非 skill 主路径）
- Windows 上 `jq` 安装说明是否写入用户本机文档（可选；skill 已有分平台提示）
- 图文请求默认 `CURL_MAX_TIME` 是否再调大（大图编辑更慢时；OC 1.9MB 约 75s 尚可）
- Chat 协议下 size/quality 是否走网关非标准字段 vs 只写进提示词（并入 T7 讨论）
