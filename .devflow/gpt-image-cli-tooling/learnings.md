# Learnings · gpt-image-cli-tooling

## 2026-07-15

1. **Responses 默认 model 与中转习惯要对齐**  
   文档里的「主模型 gpt-5.x + image tool」在中转上可能更慢；本环境直接 `gpt-image-2` 与 REST Client 体验更接近。

2. **Bash 大 base64 不能进变量**  
   `B64="$(jq ...)"` 对数 MB 字符串极慢；应 `jq | base64 -d` 流式落盘。

3. **Ctrl+C 卡死的隐藏原因**  
   后台 spinner 若 `trap '' TERM`，父进程 `wait` 会永久挂起；必须允许 TERM/KILL，并 force kill。

4. **loading「已用时」必须区分本步/总计**  
   否则用户会把等接口的时间误当成解析时间。

5. **密钥文件不要进 git**  
   `.http` / `.env` 易粘贴真 key；应 ignore + untrack；历史里若进过 key 需轮换。

6. **524 是网关超时**  
   不是 curl 语法错误；需重试 + 控制单次 max-time。
