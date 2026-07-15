#!/usr/bin/env bash
# 通过 OpenAI Responses 协议调用图像生成
# Base URL: https://shell.wyzlab.ai/v1
#
# 配置优先级（从高到低）:
#   1. 命令行参数（如 -m / --base-url / -o）
#   2. 当前 shell 已 export 的环境变量
#   3. scripts/.env 文件
#   4. 脚本内置默认值
#
# 默认提示词文件: scripts/prompts-images/prompt-image.md
#   - 文件不存在或内容为空：直接报错退出
#   - 可用命令行参数覆盖提示词；可用 --prompt-file 指定其它文件
#
# 默认图片输出: scripts/gen-images/yyyy-mm-dd-hh-mm-ss.png
# 若文件名重名，则追加随机数: yyyy-mm-dd-hh-mm-ss-<随机数>.png
#
# 用法:
#   1) 编辑 scripts/.env，填入 OPENAI_API_KEY
#   2) 编辑 scripts/prompts-images/prompt-image.md，写入提示词
#   3) ./scripts/generate-image.sh
#   ./scripts/generate-image.sh --raw
#   ./scripts/generate-image.sh --no-open
#   ./scripts/generate-image.sh --prompt-file ./other.md
#   ./scripts/generate-image.sh "命令行提示词会覆盖默认文件"
#
# 失败会自动重试（默认最多重试 5 次，含首次共 6 次尝试）
# 覆盖范围：网络/curl 失败、HTTP 非 2xx（含 524）、解析/解码失败等

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${SCRIPT_DIR}/.env"
GEN_DIR="${SCRIPT_DIR}/gen-images"
DEFAULT_PROMPT_FILE="${SCRIPT_DIR}/prompts-images/prompt-image.md"

# 最多重试次数（不含首次）；总尝试次数 = MAX_RETRIES + 1
MAX_RETRIES=5
# 重试基础等待秒数（第 n 次重试等待 n * RETRY_BASE_SLEEP 秒，上限 30 秒）
RETRY_BASE_SLEEP=5

# 全程计时（bash 内置秒表）
SECONDS=0
START_TS="$(date +%s)"

# ---------- 工具函数 ----------

log() {
  printf '[%s] %s\n' "$(date +%H:%M:%S)" "$*"
}

step() {
  printf '\n==> [%s] %s\n' "$(date +%H:%M:%S)" "$*"
}

elapsed_text() {
  local total=$(( $(date +%s) - START_TS ))
  local m=$(( total / 60 ))
  local s=$(( total % 60 ))
  if [[ "$m" -gt 0 ]]; then
    printf '%dm%02ds（共 %ds）' "$m" "$s" "$total"
  else
    printf '%ds' "$total"
  fi
}

# 后台 loading：显示旋转动画
# 用法: start_loading "文案"; ... ; stop_loading
# 展示：本步耗时 + 总计耗时（避免误以为当前步骤跑了几百秒）
LOADING_PID=""
LOADING_MSG=""
LOADING_STEP_START=0
CURL_PID=""
HTTP_CODE_FILE=""
INTERRUPTED=0
LAST_STEP_COST=0

# 判断是否为用户中断（Ctrl+C 等）导致的退出码
is_interrupt_exit() {
  local code="${1:-0}"
  # 130=SIGINT, 143=SIGTERM, 129=SIGHUP, 131=SIGQUIT
  [[ "$code" -eq 130 || "$code" -eq 143 || "$code" -eq 129 || "$code" -eq 131 ]]
}

stop_loading() {
  local step_cost=0
  if [[ "${LOADING_STEP_START:-0}" -gt 0 ]]; then
    step_cost=$(( $(date +%s) - LOADING_STEP_START ))
  fi
  if [[ -n "${LOADING_PID}" ]]; then
    kill "$LOADING_PID" 2>/dev/null || true
    # 杀掉 spinner 的子进程（sleep 等）
    kill -- -"$LOADING_PID" 2>/dev/null || true
    wait "$LOADING_PID" 2>/dev/null || true
  fi
  LOADING_PID=""
  LOADING_STEP_START=0
  # 清掉 loading 行
  printf '\r%*s\r' 100 '' 2>/dev/null || true
  LAST_STEP_COST="$step_cost"
}

kill_curl_if_running() {
  if [[ -n "${CURL_PID}" ]]; then
    kill "$CURL_PID" 2>/dev/null || true
    wait "$CURL_PID" 2>/dev/null || true
    CURL_PID=""
  fi
}

# Ctrl+C / kill 时立刻退出，绝不进入重试
on_interrupt() {
  INTERRUPTED=1
  printf '\n' >&2
  log "收到中断信号（Ctrl+C），正在停止..."
  stop_loading >/dev/null 2>&1 || true
  kill_curl_if_running
  # 临时文件由 EXIT trap 清理
  exit 130
}

start_loading() {
  LOADING_MSG="${1:-处理中}"
  LOADING_STEP_START="$(date +%s)"
  (
    # 子进程里忽略多余噪音；父进程负责真正退出
    trap '' INT TERM
    local frames=('|' '/' '-' '\')
    local i=0
    local step_used=0
    local total_used=0
    local step_start="$LOADING_STEP_START"
    local start_ts="$START_TS"
    while true; do
      step_used=$(( $(date +%s) - step_start ))
      total_used=$(( $(date +%s) - start_ts ))
      printf '\r    [loading] %s %s  本步 %ss | 总计 %ss   ' \
        "$LOADING_MSG" "${frames[$((i % 4))]}" "$step_used" "$total_used"
      i=$((i + 1))
      sleep 0.2
    done
  ) &
  LOADING_PID=$!
  # 注意：不要在这里覆盖 EXIT/INT trap，统一由主流程注册
}

# 可被 Ctrl+C 打断的 sleep（避免重试等待时按中断没反应）
interruptible_sleep() {
  local sec="$1"
  local i=0
  while [[ "$i" -lt "$sec" ]]; do
    if [[ "$INTERRUPTED" -eq 1 ]]; then
      exit 130
    fi
    sleep 1
    i=$((i + 1))
  done
}

# 自动读取 scripts/.env（若存在）
# 不覆盖当前 shell 里已经 export 过的变量
load_env_file() {
  local file="$1"
  [[ -f "$file" ]] || return 0

  log "已加载配置: ${file}"
  while IFS= read -r line || [[ -n "$line" ]]; do
    [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
    line="${line#"${line%%[![:space:]]*}"}"
    line="${line%"${line##*[![:space:]]}"}"
    [[ "$line" != *=* ]] && continue

    local key="${line%%=*}"
    local value="${line#*=}"
    key="${key%"${key##*[![:space:]]}"}"
    key="${key#"${key%%[![:space:]]*}"}"

    if [[ "$value" =~ ^\".*\"$ ]]; then
      value="${value:1:${#value}-2}"
    elif [[ "$value" =~ ^\'.*\'$ ]]; then
      value="${value:1:${#value}-2}"
    fi

    if [[ -z "${!key+x}" ]]; then
      export "$key=$value"
    fi
  done < "$file"
}

# 从文件读取提示词；文件不存在或内容为空则报错退出
# 会去掉首尾空白；忽略仅空白的文件
read_prompt_file() {
  local file="$1"

  if [[ ! -f "$file" ]]; then
    echo "错误: 提示词文件不存在: ${file}" >&2
    echo "请创建该文件并写入生图提示词，例如:" >&2
    echo "  mkdir -p \"$(dirname "$file")\"" >&2
    echo "  echo '一只在樱花树下喝茶的橘猫，插画风格' > \"${file}\"" >&2
    exit 1
  fi

  if [[ ! -s "$file" ]]; then
    echo "错误: 提示词文件为空: ${file}" >&2
    echo "请写入非空的生图提示词后再执行脚本。" >&2
    exit 1
  fi

  # 读取全文，去掉首尾空白（保留中间换行）
  local content
  content="$(<"$file")"
  # 去尾部空白/换行
  content="${content%"${content##*[![:space:]]}"}"
  # 去头部空白/换行
  content="${content#"${content%%[![:space:]]*}"}"

  if [[ -z "$content" ]]; then
    echo "错误: 提示词文件内容为空（仅空白字符）: ${file}" >&2
    echo "请写入非空的生图提示词后再执行脚本。" >&2
    exit 1
  fi

  printf '%s' "$content"
}

# 生成默认输出路径：gen-images/yyyy-mm-dd-hh-mm-ss.png
# 重名则追加随机数
build_default_output_path() {
  local dir="$1"
  mkdir -p "$dir"

  local stamp
  stamp="$(date +%Y-%m-%d-%H-%M-%S)"
  local path="${dir}/${stamp}.png"

  if [[ -e "$path" ]]; then
    local rand
    rand="$(printf '%04d' $((RANDOM % 10000)))"
    path="${dir}/${stamp}-${rand}.png"
    # 极端情况下仍冲突再试几次
    local i=0
    while [[ -e "$path" && "$i" -lt 20 ]]; do
      rand="$(printf '%04d' $((RANDOM % 10000)))"
      path="${dir}/${stamp}-${rand}.png"
      i=$((i + 1))
    done
  fi

  printf '%s' "$path"
}

# jq 抽取图片 base64 的表达式（流式管道复用，避免塞进 bash 变量）
IMAGE_B64_JQ='
  (
    [.output[]? | select(.type == "image_generation_call") | .result][0]
  )
  // (
    [.output[]? | select(.type == "image_generation_call") | .result? // .image_base64? // .b64_json?][0]
  )
  // .data[0].b64_json?
  // (
    [.output[]? | .content[]? | .image_url? // .b64_json? // .image_base64?][0]
  )
  // empty
'

# 是否存在可解码的图片字段（只判断类型/长度，不把整段 base64 灌进 shell）
has_image_b64() {
  local json_path="$1"
  jq -e '
    (
      [.output[]? | select(.type == "image_generation_call") | .result][0]
      // .data[0].b64_json?
      // empty
    ) | type == "string" and length > 100
  ' "$json_path" >/dev/null 2>&1
}

# 流式：jq 抽出 base64 -> base64 解码 -> 写文件
# 关键点：不要 B64="$(jq ...)"，几 MB 字符串进 bash 变量会非常慢且占内存
save_image_from_json() {
  local json_path="$1"
  local out="$2"
  local tmp_out="${out}.tmp.$$"

  # macOS / Linux base64 参数不同
  if base64 --help 2>&1 | grep -q -- '-d'; then
    # GNU
    jq -r "$IMAGE_B64_JQ" "$json_path" \
      | tr -d '\n\r ' \
      | base64 -d > "$tmp_out"
  else
    # BSD (macOS)
    jq -r "$IMAGE_B64_JQ" "$json_path" \
      | tr -d '\n\r ' \
      | base64 -D > "$tmp_out" 2>/dev/null \
      || jq -r "$IMAGE_B64_JQ" "$json_path" \
           | tr -d '\n\r ' \
           | base64 --decode > "$tmp_out"
  fi

  if [[ ! -s "$tmp_out" ]]; then
    rm -f "$tmp_out"
    return 1
  fi

  # 简单校验 PNG/JPEG/WEBP 文件头
  local magic
  magic="$(head -c 8 "$tmp_out" | xxd -p 2>/dev/null || true)"
  # PNG: 89504e470d0a1a0a / JPEG: ffd8 / WEBP: 52494646...
  if [[ ! "$magic" =~ ^(89504e470d0a1a0a|ffd8|52494646) ]]; then
    # 不强制失败，只告警（有的实现可能包装了其它容器）
    log "警告: 输出文件头不像常见图片格式（magic=${magic:-unknown}），仍将保存"
  fi

  mv -f "$tmp_out" "$out"
}

# 打印失败响应摘要（截断，避免超大 base64 刷屏）
print_error_body() {
  local json_path="$1"
  if [[ ! -f "$json_path" ]]; then
    echo "(无响应体)" >&2
    return
  fi
  # 优先尝试 JSON；否则原文前 500 字符
  if jq -e . "$json_path" >/dev/null 2>&1; then
    # 若含超长 result，抹掉后再打印
    jq '
      walk(
        if type == "string" and length > 200 then
          (.[0:80] + "...<已截断,len=" + (length|tostring) + ">")
        else . end
      )
    ' "$json_path" 2>/dev/null | head -n 80 >&2 || head -c 500 "$json_path" >&2
  else
    head -c 500 "$json_path" >&2
    echo >&2
  fi
}

# 计算重试等待秒数
retry_sleep_seconds() {
  local retry_index="$1" # 第几次重试（1..MAX_RETRIES）
  local sec=$(( retry_index * RETRY_BASE_SLEEP ))
  if [[ "$sec" -gt 30 ]]; then
    sec=30
  fi
  printf '%s' "$sec"
}

usage() {
  cat <<'EOF'
用法:
  ./scripts/generate-image.sh [选项] [提示词]

默认提示词:
  读取脚本同级目录: prompts-images/prompt-image.md
  文件不存在、为空、或只有空白字符时会报错退出

选项:
  -o, --output PATH        自定义输出图片路径（默认写入 scripts/gen-images/）
  -m, --model NAME         Responses 主模型（默认: gpt-5.4）
  --base-url URL           API Base URL（默认: https://shell.wyzlab.ai/v1）
  -p, --prompt-file PATH   指定提示词文件（默认: prompts-images/prompt-image.md）
  --retries N              最多重试次数（默认 5，不含首次）
  --raw                    只打印完整 JSON，不解码图片
  --no-open                生成后不自动打开图片
  -h, --help               帮助

提示词优先级:
  1. 命令行直接传入的提示词
  2. --prompt-file 指定的文件
  3. 默认文件 prompts-images/prompt-image.md

失败重试:
  默认最多重试 5 次（共 6 次尝试）
  覆盖：curl 失败、HTTP 非 2xx（含 524）、无图片数据、解码失败等
  重试间隔：5s / 10s / 15s / 20s / 25s（上限 30s）

默认输出:
  scripts/gen-images/yyyy-mm-dd-hh-mm-ss.png
  若重名: scripts/gen-images/yyyy-mm-dd-hh-mm-ss-<随机数>.png

示例:
  # 编辑默认提示词文件后直接跑
  ./scripts/generate-image.sh

  # 临时用命令行提示词覆盖文件
  ./scripts/generate-image.sh "一只在樱花树下喝茶的橘猫，插画风格"

  # 指定其它提示词文件
  ./scripts/generate-image.sh --prompt-file ./prompts-images/other.md
EOF
}

# ---------- 读配置 / 参数 ----------

load_env_file "$ENV_FILE"

BASE_URL="${OPENAI_BASE_URL:-https://shell.wyzlab.ai/v1}"
MODEL="${OPENAI_MODEL:-gpt-5.4}"
API_KEY="${OPENAI_API_KEY:-}"
OUTPUT=""
RAW_ONLY=0
AUTO_OPEN=1
PROMPT=""
PROMPT_FILE="${DEFAULT_PROMPT_FILE}"
PROMPT_FROM_CLI=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    -o|--output)
      OUTPUT="${2:-}"
      shift 2
      ;;
    -m|--model)
      MODEL="${2:-}"
      shift 2
      ;;
    --base-url)
      BASE_URL="${2:-}"
      shift 2
      ;;
    -p|--prompt-file)
      PROMPT_FILE="${2:-}"
      if [[ -z "$PROMPT_FILE" ]]; then
        echo "错误: --prompt-file 需要指定文件路径" >&2
        exit 1
      fi
      shift 2
      ;;
    --retries)
      MAX_RETRIES="${2:-}"
      if [[ -z "$MAX_RETRIES" || ! "$MAX_RETRIES" =~ ^[0-9]+$ ]]; then
        echo "错误: --retries 需要非负整数" >&2
        exit 1
      fi
      shift 2
      ;;
    --raw)
      RAW_ONLY=1
      shift
      ;;
    --no-open)
      AUTO_OPEN=0
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    -*)
      echo "未知参数: $1" >&2
      usage >&2
      exit 1
      ;;
    *)
      PROMPT_FROM_CLI=1
      if [[ -n "$PROMPT" ]]; then
        PROMPT="$PROMPT $1"
      else
        PROMPT="$1"
      fi
      shift
      ;;
  esac
done

if [[ -z "$API_KEY" || "$API_KEY" == "你的key填这里" || "$API_KEY" == "sk-xxxx" ]]; then
  echo "错误: 未配置有效的 OPENAI_API_KEY" >&2
  echo "请编辑 scripts/.env，把 OPENAI_API_KEY 改成你的真实 key" >&2
  echo "  文件路径: ${ENV_FILE}" >&2
  exit 1
fi

# 提示词：命令行优先；否则读文件（默认 prompts-images/prompt-image.md）
if [[ "$PROMPT_FROM_CLI" -eq 1 ]]; then
  # 去掉首尾空白
  PROMPT="${PROMPT#"${PROMPT%%[![:space:]]*}"}"
  PROMPT="${PROMPT%"${PROMPT##*[![:space:]]}"}"
  if [[ -z "$PROMPT" ]]; then
    echo "错误: 命令行提示词为空" >&2
    exit 1
  fi
  log "提示词来源: 命令行参数"
else
  # 相对路径按当前工作目录解析；绝对路径原样使用
  # 若用户传的是相对路径且不存在，再尝试相对脚本目录
  if [[ "$PROMPT_FILE" != /* && ! -f "$PROMPT_FILE" && -f "${SCRIPT_DIR}/${PROMPT_FILE}" ]]; then
    PROMPT_FILE="${SCRIPT_DIR}/${PROMPT_FILE}"
  fi
  PROMPT="$(read_prompt_file "$PROMPT_FILE")"
  log "提示词来源: ${PROMPT_FILE}"
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "错误: 需要 curl" >&2
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "错误: 需要 jq（macOS: brew install jq）" >&2
  exit 1
fi

# ---------- 准备输出路径 ----------

step "1/4 准备输出目录"
mkdir -p "$GEN_DIR"
log "图片目录: ${GEN_DIR}"

if [[ -z "$OUTPUT" ]]; then
  OUTPUT="$(build_default_output_path "$GEN_DIR")"
fi
# 若用户自定义 -o 路径，确保父目录存在
mkdir -p "$(dirname "$OUTPUT")"

JSON_PATH="$(mktemp -t generate-image.XXXXXX.json)"
HTTP_CODE_FILE="$(mktemp -t generate-image-http.XXXXXX.txt)"

cleanup_all() {
  # EXIT 时统一清理：spinner / curl / 临时文件
  stop_loading >/dev/null 2>&1 || true
  kill_curl_if_running >/dev/null 2>&1 || true
  [[ -n "${JSON_PATH:-}" && -f "$JSON_PATH" ]] && rm -f "$JSON_PATH"
  [[ -n "${HTTP_CODE_FILE:-}" && -f "$HTTP_CODE_FILE" ]] && rm -f "$HTTP_CODE_FILE"
}

# 统一信号处理：Ctrl+C 必须立刻退出，不能当失败去重试
trap cleanup_all EXIT
trap on_interrupt INT TERM

log "目标图片: ${OUTPUT}"
log "主模型:   ${MODEL}"
log "Base URL: ${BASE_URL}"
log "提示词:   ${PROMPT}"
log "提示: 按 Ctrl+C 可立即停止（不会继续重试）"

# ---------- 组装请求 ----------

step "2/4 组装 Responses 请求"
REQUEST_BODY="$(jq -n \
  --arg model "$MODEL" \
  --arg prompt "$PROMPT" \
  '{
    model: $model,
    input: $prompt,
    tools: [
      {
        type: "image_generation",
        action: "generate"
      }
    ]
  }')"
log "请求体已就绪（tools: image_generation / action: generate）"

# ---------- 发起请求（带 loading + 失败重试） ----------

TOTAL_ATTEMPTS=$((MAX_RETRIES + 1))
step "3/4 调用接口生成图片（最多 ${TOTAL_ATTEMPTS} 次尝试，失败最多重试 ${MAX_RETRIES} 次）"
log "POST ${BASE_URL}/responses"
log "重试策略: 任意请求/解析失败都会重试；间隔 ${RETRY_BASE_SLEEP}s 起递增，上限 30s"

B64=""
HTTP_CODE="000"
CURL_EXIT=0
LAST_ERROR=""
SUCCESS=0

for ((attempt=1; attempt<=TOTAL_ATTEMPTS; attempt++)); do
  if [[ "$INTERRUPTED" -eq 1 ]]; then
    exit 130
  fi

  ATTEMPT_START="$(date +%s)"
  log "---------- 第 ${attempt}/${TOTAL_ATTEMPTS} 次尝试 ----------"
  : > "$JSON_PATH"
  : > "$HTTP_CODE_FILE"

  start_loading "等待服务端生成图片（第 ${attempt}/${TOTAL_ATTEMPTS} 次）"
  set +e
  # curl 放到后台，便于 Ctrl+C 时精确杀掉，避免「中断后被当成失败继续重试」
  curl -sS -o "$JSON_PATH" -w "%{http_code}" \
    --connect-timeout 30 \
    --max-time 600 \
    -X POST "${BASE_URL}/responses" \
    -H "Authorization: Bearer ${API_KEY}" \
    -H "Content-Type: application/json" \
    -d "$REQUEST_BODY" \
    >"$HTTP_CODE_FILE" &
  CURL_PID=$!
  wait "$CURL_PID"
  CURL_EXIT=$?
  CURL_PID=""
  set -e
  stop_loading

  # 用户中断：立即退出，不重试
  if [[ "$INTERRUPTED" -eq 1 ]] || is_interrupt_exit "$CURL_EXIT"; then
    log "已中断（curl exit=${CURL_EXIT}），退出且不重试"
    exit 130
  fi

  HTTP_CODE="$(tr -d '[:space:]' <"$HTTP_CODE_FILE" 2>/dev/null || true)"
  [[ -z "$HTTP_CODE" ]] && HTTP_CODE="000"

  ATTEMPT_COST=$(( $(date +%s) - ATTEMPT_START ))
  log "本次耗时: ${ATTEMPT_COST}s | 累计: $(elapsed_text)"

  # 1) curl 自身失败（网络中断、超时等）
  if [[ "$CURL_EXIT" -ne 0 ]]; then
    LAST_ERROR="curl 失败，exit=${CURL_EXIT}"
    log "❌ ${LAST_ERROR}"
  # 2) HTTP 非 2xx（含 524/502/500/429/401 等，统一重试）
  elif [[ ! "$HTTP_CODE" =~ ^[0-9]+$ ]] || [[ "$HTTP_CODE" -lt 200 || "$HTTP_CODE" -ge 300 ]]; then
    LAST_ERROR="HTTP ${HTTP_CODE}"
    log "❌ 请求失败：${LAST_ERROR}"
    echo "响应摘要:" >&2
    print_error_body "$JSON_PATH"
  else
    log "HTTP 状态码: ${HTTP_CODE}（成功）"

    if [[ "$RAW_ONLY" -eq 1 ]]; then
      step "原始 JSON 输出"
      jq . "$JSON_PATH"
      log "总耗时: $(elapsed_text) | 成功尝试: ${attempt}/${TOTAL_ATTEMPTS}"
      printf '\n✅ raw 模式完成（第 %s 次尝试成功）\n' "$attempt"
      printf '⏱  总耗时：%s\n' "$(elapsed_text)"
      exit 0
    fi

    # 3) 解析并保存图片（流式解码，避免大 base64 进 bash 变量）
    step "4/4 本地解析并保存图片（通常几秒内完成；loading 里的「总计」含前面等接口时间）"
    log "说明: 接口已返回；本步只做 JSON→PNG 解码落盘，不是再次请求模型"

    # 先打元信息（轻量字段，几乎瞬时）
    META_SIZE="$(jq -r '[.output[]? | select(.type=="image_generation_call") | .size][0] // empty' "$JSON_PATH" 2>/dev/null || true)"
    META_QUALITY="$(jq -r '[.output[]? | select(.type=="image_generation_call") | .quality][0] // empty' "$JSON_PATH" 2>/dev/null || true)"
    META_FORMAT="$(jq -r '[.output[]? | select(.type=="image_generation_call") | .output_format][0] // empty' "$JSON_PATH" 2>/dev/null || true)"
    META_PROMPT="$(jq -r '[.output[]? | select(.type=="image_generation_call") | .revised_prompt][0] // empty' "$JSON_PATH" 2>/dev/null || true)"
    TOOL_MODEL="$(jq -r '.tools[0].model // empty' "$JSON_PATH" 2>/dev/null || true)"
    [[ -n "$TOOL_MODEL" ]] && log "实际图像模型: ${TOOL_MODEL}"
    [[ -n "$META_SIZE" ]] && log "尺寸: ${META_SIZE}"
    [[ -n "$META_QUALITY" ]] && log "质量: ${META_QUALITY}"
    [[ -n "$META_FORMAT" ]] && log "格式: ${META_FORMAT}"
    [[ -n "$META_PROMPT" ]] && log "改写提示词: ${META_PROMPT}"

    if ! has_image_b64 "$JSON_PATH"; then
      LAST_ERROR="响应成功但未解析到图片 base64"
      log "❌ ${LAST_ERROR}"
      echo "响应摘要:" >&2
      print_error_body "$JSON_PATH"
    else
      set +e
      start_loading "流式解码并写入本地文件"
      save_image_from_json "$JSON_PATH" "$OUTPUT"
      DECODE_EXIT=$?
      stop_loading
      set -e

      if [[ "$INTERRUPTED" -eq 1 ]] || is_interrupt_exit "$DECODE_EXIT"; then
        log "解码阶段被中断，退出且不重试"
        exit 130
      fi

      log "本步解码落盘耗时: ${LAST_STEP_COST:-?}s（总计仍为 $(elapsed_text)）"

      if [[ "$DECODE_EXIT" -ne 0 || ! -s "$OUTPUT" ]]; then
        LAST_ERROR="base64 解码失败或输出文件为空"
        log "❌ ${LAST_ERROR}"
        rm -f "$OUTPUT" 2>/dev/null || true
      else
        SUCCESS=1
        log "✅ 第 ${attempt}/${TOTAL_ATTEMPTS} 次尝试成功"
        break
      fi
    fi
  fi

  # 还有重试次数则等待后继续
  if [[ "$attempt" -lt "$TOTAL_ATTEMPTS" ]]; then
    if [[ "$INTERRUPTED" -eq 1 ]]; then
      exit 130
    fi
    RETRY_NO=$((attempt)) # 第几次重试（即将进行）
    SLEEP_SEC="$(retry_sleep_seconds "$RETRY_NO")"
    log "将进行第 ${RETRY_NO}/${MAX_RETRIES} 次重试，${SLEEP_SEC}s 后开始...（Ctrl+C 可取消）"
    start_loading "重试倒计时（${SLEEP_SEC}s）"
    interruptible_sleep "$SLEEP_SEC"
    stop_loading
  fi
done

if [[ "$SUCCESS" -ne 1 ]]; then
  FAIL_JSON="${GEN_DIR}/failed-$(date +%Y-%m-%d-%H-%M-%S).json"
  if [[ -f "$JSON_PATH" ]]; then
    cp "$JSON_PATH" "$FAIL_JSON" 2>/dev/null || true
  fi
  echo >&2
  echo "错误: 已尝试 ${TOTAL_ATTEMPTS} 次（最多重试 ${MAX_RETRIES} 次）仍失败" >&2
  echo "最后错误: ${LAST_ERROR:-unknown}" >&2
  echo "已用时: $(elapsed_text)" >&2
  if [[ -f "$FAIL_JSON" ]]; then
    echo "最后一次响应已保存: ${FAIL_JSON}" >&2
  fi
  exit 1
fi

FILE_SIZE="$(wc -c < "$OUTPUT" | tr -d ' ')"
log "图片已保存: ${OUTPUT}"
log "文件大小:   ${FILE_SIZE} bytes"
log "总耗时:     $(elapsed_text)（其中绝大部分通常是等待接口生图）"

if [[ "$AUTO_OPEN" -eq 1 && "$(uname -s)" == "Darwin" ]] && command -v open >/dev/null 2>&1; then
  log "正在打开图片..."
  open "$OUTPUT" || true
fi

printf '\n✅ 完成：%s\n' "$OUTPUT"
printf '⏱  总耗时：%s\n' "$(elapsed_text)"

