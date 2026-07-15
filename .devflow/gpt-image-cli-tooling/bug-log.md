# Bug Log

## BUG-001 · HTTP 524 网关超时

- **现象**：`POST /v1/responses` 约 100s+ 后返回 `error code: 524`
- **原因**：Cloudflare/网关等待源站生图超时；非脚本参数错误
- **方案**：最多重试 5 次 + 递增等待；提示简化/减小 size 可辅助
- **状态**：已缓解（重试）；根因在中转侧

## BUG-002 · 解析阶段「看似」极慢

- **现象**：4/4 步骤 loading 显示已用时数百秒
- **原因**：
  1. loading 用的是脚本总耗时（含等接口）
  2. 旧实现把数 MB base64 塞进 bash 变量
- **方案**：本步/总计双计时；`jq | base64 -d` 流式落盘
- **状态**：已修复

## BUG-003 · Ctrl+C 无法停止脚本

- **现象**：中断后脚本继续倒计时并重试
- **原因**：`set +e` 下 curl 收到 SIGINT 返回 130，被当成普通失败进入重试循环
- **方案**：`trap INT TERM`；中断 exit 码不重试；curl 后台 PID 可杀
- **状态**：已修复（第一轮）

## BUG-004 · Ctrl+C 后卡死 / loading 不停

- **现象**：已打印「收到中断信号」但 loading 继续转，需连按多次 ^C
- **原因**：spinner 使用 `trap '' INT TERM` **忽略 SIGTERM**；`stop_loading` 里 `wait $LOADING_PID` 永久阻塞
- **方案**：spinner 仅忽略 INT；`force_kill_pid`（TERM→KILL）；中断时先杀 curl 再杀 spinner
- **状态**：已修复

## BUG-005 · 单次请求干等过久

- **现象**：本步 400s+ 仍在等
- **原因**：`curl --max-time 600`（最长 10 分钟）+ 中转生图慢/挂起
- **方案**：默认 `CURL_MAX_TIME=180`，可用 `.env` 覆盖
- **状态**：已调整
