# Bug Log · oc-mugen-rin-character-sheets

## BUG-001 · 中转上游生图失败（HTTP 500 / do_request_failed）

- **现象**：
  - `POST https://shell.wyzlab.ai/v1/responses`（skill 文生图 / 图生图）返回 HTTP 500
  - `POST .../images/generations` + `gpt-image-2` 同样 500
  - `POST .../chat/completions` 也 500
  - `GET .../models` 仍 200，且列表含 `gpt-image-2`
  - 错误体：`upstream error: do request failed (request id: ...)`，`type=new_api_error`
- **原因**：
  - 中转站鉴权与路由可用，**上游推理/生图服务失败**
  - 已排除：本机系统代理（无 proxy 环境变量；`--noproxy '*'` 仍失败）
  - 已排除：单把 key 失效（新旧 key 同症状）
  - 用户提供的中转 key 对官方 `api.openai.com` 为 401（非官方 key，属预期）
- **解决方案 / 状态**：
  - **待外部恢复**：等 `shell.wyzlab.ai` 上游恢复，或更换可用 `OPENAI_BASE_URL`
  - 恢复后先用极简 prompt 做 smoke test，再继续人设图
  - **状态**：阻塞中（2026-07-17 下午）→ **已恢复可用**（2026-07-17 晚间复测 smoke + 设定图成功）

## BUG-002 · 偶发 HTTP 524（网关超时）

- **现象**：长请求等待后出现 `error code: 524`
- **原因**：Cloudflare/网关等待源站超时（与 `gpt-image-cli-tooling` BUG-001 同类）
- **方案**：`CURL_MAX_TIME` 可调；减小参考图；简化 prompt；依赖 skill 重试
- **状态**：已知；本轮主阻塞为 500 而非 524

## NOTE · 排障记录（非代码 bug）

- 大体积角色原图（数 MB）做 `--image` 时请求体可达 ~8MB，不利于中转稳定性；优先用 `_preview`（长边约 800）。


## BUG-003 · 多格/复杂设定图易 HTTP 524

- **现象**：`rin-02` 等请求约 2 分钟返回 `error code: 524`；不是本地提前掐断
- **原因**：Cloudflare/网关等待上游生图超时；复杂 multi-panel 更易触发
- **方案**：skill 自动重试（`--retries`）；简化面板；单场景优先；总等待需覆盖「多次 ~2min 524 + 最终成功」（如 rin-02 总耗时 ~8m38s）
- **状态**：已知；rin-02 重试成功；rin-05 四次仍 524
