# 自包含 Skill 说明

## 边界

- 配置、脚本、输出、默认提示词 **全部在本 skill 目录内**
- 不依赖仓库 `scripts/generate-image.sh`
- 不依赖 `REPO_ROOT` 或 `../../..` 路径

## 同级文件

与 `run.sh` 同级：

- `.env` / `.env.example`
- `gen-images/`
- `prompts/`
- `SKILL.md`（上一级同一 skill 根目录）

## 接口

- `POST {OPENAI_BASE_URL}/responses`
- `tools: [{ type: "image_generation", action: "generate" }]`
- 图片：`output[].result` base64

## 依赖

- `curl`、`jq`、`base64`
