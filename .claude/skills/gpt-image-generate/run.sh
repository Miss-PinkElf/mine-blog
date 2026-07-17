#!/usr/bin/env bash
# gpt-image-generate skill 自包含生图脚本（OpenAI Chat Completions：/v1/chat/completions）
# 本文件与 .env / gen-images / prompts 同级，不依赖仓库其它脚本。
#
# 协议说明:
#   POST {BASE_URL}/chat/completions
#   文生图: messages=[{role:user, content: 提示词}]
#   图生图: messages content 数组 text + image_url(data URL)
#   响应: choices[0].message.content 中 Markdown 图片 URL / data URL（兼容部分 b64 字段）
#
# 目录约定（均相对本脚本所在目录）:
#   .env                  API Key / Base URL / Model
#   gen-images/           输出图片（自动创建）
#   prompts/prompt-image.md  默认提示词（无 CLI 提示词时使用）
#
# 配置优先级:
#   1. 命令行参数  2. 已 export 环境变量  3. 同级 .env  4. 内置默认
#
# 用法:
#   1) 编辑与本脚本同级的 .env，填入 OPENAI_API_KEY
#   2) ./run.sh "提示词"
#   ./run.sh --no-open "提示词"
#   ./run.sh --image ref.png "编辑指令"
#   ./run.sh -i ref.png --no-open "编辑指令"
#   ./run.sh            # 读 prompts/prompt-image.md
#
# 失败自动重试（默认最多 5 次）
# JSON: jq 优先，否则 lib/json_codec（node/python）；解码用系统 base64

set -euo pipefail

# 全部路径只相对本 skill 目录，不向上找仓库根
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${SCRIPT_DIR}/.env"
GEN_DIR="${SCRIPT_DIR}/gen-images"
DEFAULT_PROMPT_FILE="${SCRIPT_DIR}/prompts/prompt-image.md"

# 最多重试次数（不含首次）；总尝试次数 = MAX_RETRIES + 1
MAX_RETRIES=5
# 重试基础等待秒数（第 n 次重试等待 n * RETRY_BASE_SLEEP 秒，上限 30 秒）
RETRY_BASE_SLEEP=5
# 单次 curl 超时在 load_env 之后再套默认（见下方），避免 .env 被抢先写死

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

elapsed_seconds() {
  printf '%s' "$(( $(date +%s) - START_TS ))"
}

elapsed_text() {
  local total
  total="$(elapsed_seconds)"
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
JSON_BACKEND=""
REQUEST_BODY_FILE=""
IMAGE_PATH=""
IMAGE_MIME=""
MODE="text"
SOURCE_IMAGE=""
LIB_DIR="${SCRIPT_DIR}/lib"
PY_CODEC="${LIB_DIR}/json_codec.py"
JS_CODEC="${LIB_DIR}/json_codec.cjs"
PYTHON_BIN=""


# 判断是否为用户中断（Ctrl+C 等）导致的退出码
is_interrupt_exit() {
  local code="${1:-0}"
  # 130=SIGINT, 143=SIGTERM, 129=SIGHUP, 131=SIGQUIT
  [[ "$code" -eq 130 || "$code" -eq 143 || "$code" -eq 129 || "$code" -eq 131 ]]
}

# 强制结束子进程：TERM → 短暂等待 → KILL，避免 wait 永久挂死
# （旧版 spinner 忽略了 TERM，会导致 Ctrl+C 后卡在 wait 上）
force_kill_pid() {
  local pid="${1:-}"
  [[ -z "$pid" ]] && return 0
  kill -TERM "$pid" 2>/dev/null || true
  local i=0
  while kill -0 "$pid" 2>/dev/null && [[ "$i" -lt 5 ]]; do
    # 0.1s * 5 = 最多约 0.5s
    sleep 0.1 2>/dev/null || sleep 1
    i=$((i + 1))
  done
  if kill -0 "$pid" 2>/dev/null; then
    kill -KILL "$pid" 2>/dev/null || true
  fi
  wait "$pid" 2>/dev/null || true
}

stop_loading() {
  local step_cost=0
  if [[ "${LOADING_STEP_START:-0}" -gt 0 ]]; then
    step_cost=$(( $(date +%s) - LOADING_STEP_START ))
  fi
  if [[ -n "${LOADING_PID}" ]]; then
    force_kill_pid "$LOADING_PID"
  fi
  LOADING_PID=""
  LOADING_STEP_START=0
  # 清掉 loading 行 + 换行，避免残影盖住后续日志
  printf '\r%*s\r' 100 '' 2>/dev/null || true
  LAST_STEP_COST="$step_cost"
}

kill_curl_if_running() {
  if [[ -n "${CURL_PID}" ]]; then
    force_kill_pid "$CURL_PID"
    CURL_PID=""
  fi
}

# Ctrl+C / kill 时立刻退出，绝不进入重试、绝不卡在 wait
on_interrupt() {
  # 防止重复进入
  if [[ "$INTERRUPTED" -eq 1 ]]; then
    kill -KILL "$$" 2>/dev/null || exit 130
  fi
  INTERRUPTED=1
  printf '\n' >&2
  log "收到中断信号（Ctrl+C），正在强制停止子进程..."
  # 先杀 curl 再杀 spinner，避免继续占连接
  kill_curl_if_running
  stop_loading >/dev/null 2>&1 || true
  printf '\r%*s\r' 100 '' 2>/dev/null || true
  echo "[中断] 已退出（不重试）" >&2
  # 临时文件由 EXIT trap 清理
  exit 130
}

start_loading() {
  LOADING_MSG="${1:-处理中}"
  LOADING_STEP_START="$(date +%s)"
  (
    # 仅忽略 INT，避免和父进程抢信号；必须能响应 TERM/KILL（否则 Ctrl+C 会卡死）
    trap '' INT
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

# 自动读取与 run.sh 同级的 .env（若存在）
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


# ---------- JSON 工具：jq → node(json_codec.cjs) → python(json_codec.py) ----------

print_json_tool_help() {
  cat >&2 <<'EOF'
错误: 未检测到可用的 JSON 工具（需要 jq，或 Node，或 Python 3）。

用途：组装请求体、从响应抽取图片 base64（流式，不进 bash 变量）。
图片二进制解码仍使用系统 `base64`。

安装其一：
  • jq (推荐)  macOS: brew install jq
               Windows: scoop install jq  或  choco install jq
               验证: jq --version
  • Node.js    需可执行 node（将使用 skill 内 lib/json_codec.cjs）
  • Python 3   需可执行 python3 或 python（将使用 lib/json_codec.py）
EOF
}

resolve_python_bin() {
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
    return 0
  fi
  if command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
    return 0
  fi
  PYTHON_BIN=""
  return 1
}

detect_json_backend() {
  if command -v jq >/dev/null 2>&1; then
    JSON_BACKEND="jq"
    return 0
  fi
  if command -v node >/dev/null 2>&1 && [[ -f "$JS_CODEC" ]]; then
    JSON_BACKEND="node"
    return 0
  fi
  if resolve_python_bin && [[ -f "$PY_CODEC" ]]; then
    JSON_BACKEND="python"
    return 0
  fi
  JSON_BACKEND=""
  return 1
}

mime_for_image() {
  local path="$1"
  local ext
  ext="$(printf '%s' "${path##*.}" | tr 'A-Z' 'a-z')"
  case "$ext" in
    jpg|jpeg) printf 'image/jpeg' ;;
    png) printf 'image/png' ;;
    webp) printf 'image/webp' ;;
    gif) printf 'image/gif' ;;
    *) printf 'image/png' ;;
  esac
}

build_request_body_file() {
  local out_file="$1"
  if [[ -n "$IMAGE_PATH" ]]; then
    MODE="image_edit"
  else
    MODE="text"
  fi

  case "$JSON_BACKEND" in
    jq)
      if [[ -n "$IMAGE_PATH" ]]; then
        local data_url_file b64_tmp
        data_url_file="$(mktemp -t gpt-data-url.XXXXXX)"
        b64_tmp="$(mktemp -t gpt-img-b64.XXXXXX)"
        if base64 --help 2>&1 | grep -q -- '-w'; then
          base64 -w 0 "$IMAGE_PATH" >"$b64_tmp"
        else
          base64 <"$IMAGE_PATH" | tr -d '\n\r' >"$b64_tmp"
        fi
        {
          printf 'data:%s;base64,' "$IMAGE_MIME"
          cat "$b64_tmp"
        } >"$data_url_file"
        rm -f "$b64_tmp"
        # Chat Completions 多模态：text + image_url
        jq -n \
          --arg model "$MODEL" \
          --arg prompt "$PROMPT" \
          --rawfile data_url "$data_url_file" \
          '{
            model: $model,
            stream: false,
            messages: [
              {
                role: "user",
                content: [
                  { type: "text", text: $prompt },
                  { type: "image_url", image_url: { url: ($data_url | sub("\n$";"")) } }
                ]
              }
            ]
          }' >"$out_file"
        rm -f "$data_url_file"
      else
        # Chat Completions 纯文生图
        jq -n \
          --arg model "$MODEL" \
          --arg prompt "$PROMPT" \
          '{
            model: $model,
            stream: false,
            messages: [
              { role: "user", content: $prompt }
            ]
          }' >"$out_file"
      fi
      ;;
    node)
      if [[ -n "$IMAGE_PATH" ]]; then
        node "$JS_CODEC" build --model "$MODEL" --prompt "$PROMPT" --out "$out_file" --image "$IMAGE_PATH" --mime "$IMAGE_MIME"
      else
        node "$JS_CODEC" build --model "$MODEL" --prompt "$PROMPT" --out "$out_file"
      fi
      ;;
    python)
      if [[ -n "$IMAGE_PATH" ]]; then
        "$PYTHON_BIN" "$PY_CODEC" build --model "$MODEL" --prompt "$PROMPT" --out "$out_file" --image "$IMAGE_PATH" --mime "$IMAGE_MIME"
      else
        "$PYTHON_BIN" "$PY_CODEC" build --model "$MODEL" --prompt "$PROMPT" --out "$out_file"
      fi
      ;;
    *)
      echo "错误: JSON_BACKEND 无效" >&2
      return 1
      ;;
  esac
  [[ -s "$out_file" ]]
}

stream_image_b64() {
  local json_path="$1"
  case "$JSON_BACKEND" in
    jq) jq -r "$IMAGE_B64_JQ" "$json_path" | tr -d '\n\r ' ;;
    node) node "$JS_CODEC" extract --json "$json_path" ;;
    python) "$PYTHON_BIN" "$PY_CODEC" extract --json "$json_path" ;;
    *) return 1 ;;
  esac
}

json_meta_get() {
  local json_path="$1"
  local field="$2"
  case "$JSON_BACKEND" in
    jq)
      case "$field" in
        # Chat 协议通常无 size/quality/revised_prompt；尽量从 model 取
        size|quality|output_format|revised_prompt) printf '' ;;
        tool_model) jq -r '.model // empty' "$json_path" 2>/dev/null || true ;;
      esac
      ;;
    node) node "$JS_CODEC" meta --json "$json_path" --field "$field" ;;
    python) "$PYTHON_BIN" "$PY_CODEC" meta --json "$json_path" --field "$field" ;;
  esac
}


# jq：从 Chat Completions（及兼容字段）抽出图片源字符串
# - Markdown: ![x](https://... 或 data:image/...;base64,...)
# - content 数组 image_url
# - data[0].b64_json / 旧 responses result（兜底）
IMAGE_SRC_JQ='
  def md_url:
    if type == "string" then
      (capture("!\\[[^\\]]*\\]\\((?<u>[^)]+)\\)") | .u) // empty
    else empty end;
  def content_src:
    if type == "string" then
      md_url
      // (if test("^data:image/"; "i") then . else empty end)
      // (if (test("^https?://") and length < 8192 and (contains("\n") | not)) then . else empty end)
    elif type == "array" then
      ([.[]?
        | select(.type == "image_url" or .type == "output_image" or .type == "image")
        | (.image_url.url? // .image_url? // .url? // .image? // empty)
      ] | map(select(type == "string" and length > 8)) | .[0] // empty)
    else empty end;
  (.choices[0].message.content? | content_src)
  // (.choices[0].message.image_url? // empty)
  // .data[0].url?
  // .data[0].b64_json?
  // ([.output[]? | select(.type == "image_generation_call") | .result? // .image_base64? // .b64_json?][0] // empty)
  // empty
'

# jq 抽取图片 base64 的表达式（仅当源本身是 b64 / data URL 时用；URL 走 curl 下载）
IMAGE_B64_JQ='
  ('"$IMAGE_SRC_JQ"') as $src
  | if ($src | type) != "string" then empty
    elif ($src | test("^https?://")) then empty
    elif ($src | test("^data:image/"; "i")) then ($src | sub("^data:image/[^;]+;base64,"; ""))
    else $src
    end
  | gsub("[\\n\\r ]"; "")
'

# 是否存在可落盘的图片源（URL 或 base64；不把大 base64 灌进 shell）
has_image_b64() {
  local json_path="$1"
  case "$JSON_BACKEND" in
    jq)
      jq -e '
        def md_ok:
          type == "string" and (
            test("!\\[[^\\]]*\\]\\((https?://|data:image/)[^)]+\\)")
            or test("^data:image/"; "i")
            or (test("^https?://") and length < 8192)
          );
        def arr_ok:
          type == "array" and any(
            .[]?;
            (.type == "image_url" or .type == "output_image" or .type == "image")
            and (
              (.image_url.url? // .image_url? // .url? // "")
              | type == "string" and length > 8
            )
          );
        (
          (.choices[0].message.content? | (md_ok or arr_ok))
          or ((.data[0].b64_json? | type == "string" and length > 100))
          or ((.data[0].url? | type == "string" and test("^https?://")))
          or (
            ([.output[]? | select(.type == "image_generation_call") | .result][0]
            | type == "string" and length > 100)
          )
        )
      ' "$json_path" >/dev/null 2>&1
      ;;
    node)
      node "$JS_CODEC" has --json "$json_path"
      ;;
    python)
      "$PYTHON_BIN" "$PY_CODEC" has --json "$json_path"
      ;;
    *) return 1 ;;
  esac
}


# 从 JSON 落盘图片：
# - Chat content 里是 https URL → curl 下载
# - data URL / 裸 base64 → 流式 base64 解码（禁止塞进 bash 变量）
# - node/python 的 extract 已统一输出 base64（URL 会先下载再编码）
save_image_from_json() {
  local json_path="$1"
  local out="$2"
  local tmp_out="${out}.tmp.$$"

  if [[ "$JSON_BACKEND" == "jq" ]]; then
    local src_kind src_url
    # 仅探测类型：url / b64 / empty（短字段，安全）
    src_kind="$(jq -r '
      ('"$IMAGE_SRC_JQ"') as $src
      | if ($src | type) != "string" or ($src | length) == 0 then "empty"
        elif ($src | test("^https?://")) then "url"
        else "b64"
        end
    ' "$json_path" 2>/dev/null || echo empty)"

    if [[ "$src_kind" == "url" ]]; then
      src_url="$(jq -r "($IMAGE_SRC_JQ)" "$json_path" 2>/dev/null || true)"
      if [[ -z "$src_url" || ! "$src_url" =~ ^https?:// ]]; then
        rm -f "$tmp_out"
        return 1
      fi
      log "响应为图片 URL，开始下载..."
      if ! curl -fsSL --connect-timeout "${CURL_CONNECT_TIMEOUT}" --max-time "${CURL_MAX_TIME}" \
        -A "gpt-image-generate/1.0" -o "$tmp_out" "$src_url"; then
        rm -f "$tmp_out"
        return 1
      fi
    elif [[ "$src_kind" == "b64" ]]; then
      if base64 --help 2>&1 | grep -q -- '-d'; then
        jq -r "$IMAGE_B64_JQ" "$json_path" | tr -d '\n\r ' | base64 -d >"$tmp_out"
      else
        jq -r "$IMAGE_B64_JQ" "$json_path" | tr -d '\n\r ' | base64 -D >"$tmp_out" 2>/dev/null \
          || jq -r "$IMAGE_B64_JQ" "$json_path" | tr -d '\n\r ' | base64 --decode >"$tmp_out"
      fi
    else
      rm -f "$tmp_out"
      return 1
    fi
  else
    # node / python：extract 统一吐 base64（含 URL 下载后编码）
    if base64 --help 2>&1 | grep -q -- '-d'; then
      stream_image_b64 "$json_path" | base64 -d >"$tmp_out"
    else
      stream_image_b64 "$json_path" | base64 -D >"$tmp_out" 2>/dev/null \
        || stream_image_b64 "$json_path" | base64 --decode >"$tmp_out"
    fi
  fi

  if [[ ! -s "$tmp_out" ]]; then
    rm -f "$tmp_out"
    return 1
  fi

  local magic
  magic="$(head -c 8 "$tmp_out" | xxd -p 2>/dev/null || true)"
  if [[ ! "$magic" =~ ^(89504e470d0a1a0a|ffd8|52494646) ]]; then
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
  if [[ "${JSON_BACKEND:-}" == "jq" ]] && jq -e . "$json_path" >/dev/null 2>&1; then
    jq '
      walk(
        if type == "string" and length > 200 then
          (.[0:80] + "...<已截断,len=" + (length|tostring) + ">")
        else . end
      )
    ' "$json_path" 2>/dev/null | head -n 80 >&2 || head -c 500 "$json_path" >&2
  else
    head -c 800 "$json_path" >&2
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
  ./run.sh [选项] [提示词]

默认提示词:
  与本脚本同级: prompts/prompt-image.md
  文件不存在、为空、或只有空白字符时会报错退出

选项:
  -o, --output PATH        自定义输出图片路径（默认写入同级 gen-images/）
  -m, --model NAME         Chat Completions 模型（默认: gpt-image-2）
  --base-url URL           API Base URL（默认: https://shell.wyzlab.ai/v1）
  -p, --prompt-file PATH   指定提示词文件（默认: prompts/prompt-image.md）
  -i, --image PATH         参考图路径（图文同传 / 图生图编辑）
  --retries N              最多重试次数（默认 5，不含首次）
  --raw                    只打印完整 JSON，不解码图片
  --no-open                生成后不自动打开图片
  -h, --help               帮助

配置:
  与本脚本同级的 .env（OPENAI_API_KEY / OPENAI_BASE_URL / OPENAI_MODEL）

提示词优先级:
  1. 命令行直接传入的提示词
  2. --prompt-file 指定的文件
  3. 默认文件 prompts/prompt-image.md

默认输出:
  gen-images/yyyy-mm-dd-hh-mm-ss.png（与 run.sh 同级）

示例:
  ./run.sh "一只在樱花树下喝茶的橘猫，插画风格"
  ./run.sh --no-open "赛博朋克城市"
  ./run.sh --image ./ref.png "把头发改成黑长直，整体变暗"
  ./run.sh -i ./ref.png --no-open "衣服换成暗色系"
EOF
}

# ---------- 读配置 / 参数 ----------

load_env_file "$ENV_FILE"

BASE_URL="${OPENAI_BASE_URL:-https://shell.wyzlab.ai/v1}"
MODEL="${OPENAI_MODEL:-gpt-image-2}"
API_KEY="${OPENAI_API_KEY:-}"
# 读完 .env 后再给超时默认值
CURL_CONNECT_TIMEOUT="${CURL_CONNECT_TIMEOUT:-20}"
CURL_MAX_TIME="${CURL_MAX_TIME:-180}"
OUTPUT=""
RAW_ONLY=0
AUTO_OPEN=1
PROMPT=""
PROMPT_FILE="${DEFAULT_PROMPT_FILE}"
PROMPT_FROM_CLI=0
IMAGE_PATH=""

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
    -i|--image)
      IMAGE_PATH="${2:-}"
      if [[ -z "$IMAGE_PATH" ]]; then
        echo "错误: --image 需要指定图片路径" >&2
        exit 1
      fi
      shift 2
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
  echo "请编辑与 run.sh 同级的 .env，填入真实 key" >&2
  echo "  文件路径: ${ENV_FILE}" >&2
  echo "  可复制: cp \"${SCRIPT_DIR}/.env.example\" \"${ENV_FILE}\"" >&2
  exit 1
fi

# 提示词：命令行优先；否则读 skill 内 prompts/prompt-image.md
if [[ "$PROMPT_FROM_CLI" -eq 1 ]]; then
  PROMPT="${PROMPT#"${PROMPT%%[![:space:]]*}"}"
  PROMPT="${PROMPT%"${PROMPT##*[![:space:]]}"}"
  if [[ -z "$PROMPT" ]]; then
    echo "错误: 命令行提示词为空" >&2
    exit 1
  fi
  log "提示词来源: 命令行参数"
else
  if [[ "$PROMPT_FILE" != /* && ! -f "$PROMPT_FILE" && -f "${SCRIPT_DIR}/${PROMPT_FILE}" ]]; then
    PROMPT_FILE="${SCRIPT_DIR}/${PROMPT_FILE}"
  fi
  PROMPT="$(read_prompt_file "$PROMPT_FILE")"
  log "提示词来源: ${PROMPT_FILE}"
fi


# 参考图（可选）
if [[ -n "$IMAGE_PATH" ]]; then
  if [[ "$IMAGE_PATH" != /* && ! -f "$IMAGE_PATH" && -f "${SCRIPT_DIR}/${IMAGE_PATH}" ]]; then
    IMAGE_PATH="${SCRIPT_DIR}/${IMAGE_PATH}"
  fi
  if [[ ! -f "$IMAGE_PATH" ]]; then
    echo "错误: 参考图不存在: ${IMAGE_PATH}" >&2
    exit 1
  fi
  if [[ ! -s "$IMAGE_PATH" ]]; then
    echo "错误: 参考图为空文件: ${IMAGE_PATH}" >&2
    exit 1
  fi
  IMAGE_MIME="$(mime_for_image "$IMAGE_PATH")"
  SOURCE_IMAGE="$IMAGE_PATH"
  MODE="image_edit"
  log "参考图: ${IMAGE_PATH} (mime=${IMAGE_MIME})"
else
  MODE="text"
  SOURCE_IMAGE=""
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "错误: 需要 curl" >&2
  exit 1
fi

if ! detect_json_backend; then
  print_json_tool_help
  exit 127
fi
log "JSON 工具: ${JSON_BACKEND}"

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
  [[ -n "${REQUEST_BODY_FILE:-}" && -f "$REQUEST_BODY_FILE" ]] && rm -f "$REQUEST_BODY_FILE"
}

# 统一信号处理：Ctrl+C 必须立刻退出，不能当失败去重试
trap cleanup_all EXIT
trap on_interrupt INT TERM

log "目标图片: ${OUTPUT}"
log "主模型:   ${MODEL}"
log "Base URL: ${BASE_URL}"
log "提示词:   ${PROMPT}"
log "模式:     ${MODE}"
[[ -n "$SOURCE_IMAGE" ]] && log "参考图:   ${SOURCE_IMAGE}"
log "提示: 按 Ctrl+C 可立即停止（不会继续重试）"

# ---------- 组装请求 ----------

step "2/4 组装 Chat Completions 请求"
REQUEST_BODY_FILE="$(mktemp -t generate-image-body.XXXXXX.json)"
if ! build_request_body_file "$REQUEST_BODY_FILE"; then
  echo "错误: 组装请求体失败" >&2
  exit 1
fi
BODY_BYTES="$(wc -c < "$REQUEST_BODY_FILE" | tr -d ' ')"
log "请求体已就绪（mode=${MODE} / bytes=${BODY_BYTES} / json=${JSON_BACKEND} / protocol=chat）"

# ---------- 发起请求（带 loading + 失败重试） ----------

TOTAL_ATTEMPTS=$((MAX_RETRIES + 1))
step "3/4 调用接口生成图片（最多 ${TOTAL_ATTEMPTS} 次尝试，失败最多重试 ${MAX_RETRIES} 次）"
log "POST ${BASE_URL}/chat/completions"
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

  start_loading "等待服务端生成图片（第 ${attempt}/${TOTAL_ATTEMPTS} 次，单次最长 ${CURL_MAX_TIME}s）"
  log "curl 超时: connect=${CURL_CONNECT_TIMEOUT}s, max-time=${CURL_MAX_TIME}s（可用 .env 的 CURL_MAX_TIME 调整）"
  set +e
  # curl 放到后台，便于 Ctrl+C 时强制杀掉
  curl -sS -o "$JSON_PATH" -w "%{http_code}" \
    --connect-timeout "${CURL_CONNECT_TIMEOUT}" \
    --max-time "${CURL_MAX_TIME}" \
    -X POST "${BASE_URL}/chat/completions" \
    -H "Authorization: Bearer ${API_KEY}" \
    -H "Content-Type: application/json" \
    --data-binary @"${REQUEST_BODY_FILE}" \
    >"$HTTP_CODE_FILE" &
  CURL_PID=$!
  # wait 被信号打断时可能返回 >128；随后 on_interrupt 会 exit
  wait "$CURL_PID"
  CURL_EXIT=$?
  # 若中断处理已在跑，CURL_PID 可能已被清空
  if [[ -n "${CURL_PID}" ]]; then
    CURL_PID=""
  fi
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
      if [[ "$JSON_BACKEND" == "jq" ]]; then
        jq . "$JSON_PATH"
      else
        cat "$JSON_PATH"
      fi
      log "总耗时: $(elapsed_text) | 成功尝试: ${attempt}/${TOTAL_ATTEMPTS}"
      printf '\n✅ raw 模式完成（第 %s 次尝试成功）\n' "$attempt"
      printf '⏱  总耗时：%s\n' "$(elapsed_text)"
      exit 0
    fi

    # 3) 解析并保存图片（流式解码，避免大 base64 进 bash 变量）
    step "4/4 本地解析并保存图片（通常几秒内完成；loading 里的「总计」含前面等接口时间）"
    log "说明: 接口已返回；本步只做 JSON→PNG 解码落盘，不是再次请求模型"

    # 先打元信息（轻量字段，几乎瞬时）
    META_SIZE="$(json_meta_get "$JSON_PATH" size)"
    META_QUALITY="$(json_meta_get "$JSON_PATH" quality)"
    META_FORMAT="$(json_meta_get "$JSON_PATH" output_format)"
    META_PROMPT="$(json_meta_get "$JSON_PATH" revised_prompt)"
    TOOL_MODEL="$(json_meta_get "$JSON_PATH" tool_model)"
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
ELAPSED_SEC="$(elapsed_seconds)"
# 相对 skill 目录（run.sh 同级）的路径
OUTPUT_REL="$OUTPUT"
case "$OUTPUT" in
  "${SCRIPT_DIR}"/*) OUTPUT_REL="${OUTPUT#"${SCRIPT_DIR}"/}" ;;
esac

log "图片已保存: ${OUTPUT}"
log "文件大小:   ${FILE_SIZE} bytes"
log "总耗时:     $(elapsed_text)（其中绝大部分通常是等待接口生图）"

if [[ "$AUTO_OPEN" -eq 1 && "$(uname -s)" == "Darwin" ]] && command -v open >/dev/null 2>&1; then
  log "正在打开图片..."
  open "$OUTPUT" || true
fi

printf '\n✅ 完成：%s\n' "$OUTPUT"
printf '⏱  总耗时：%s\n' "$(elapsed_text)"
printf '📦 文件大小：%s bytes\n' "$FILE_SIZE"

# 机器可读结果块（供 skill 汇报：耗时 / 大小 / 路径）
# 注意：macOS printf 会把以 --- 开头的 format 当成选项，必须用 %s 包一层
printf '\n%s\n' '---RESULT---'
printf 'status=ok\n'
printf 'path=%s\n' "$OUTPUT"
printf 'path_rel=%s\n' "$OUTPUT_REL"
printf 'bytes=%s\n' "$FILE_SIZE"
printf 'elapsed_seconds=%s\n' "$ELAPSED_SEC"
printf 'elapsed_text=%s\n' "$(elapsed_text)"
printf 'model=%s\n' "$MODEL"
printf 'mode=%s\n' "$MODE"
printf 'json_backend=%s\n' "$JSON_BACKEND"
if [[ -n "$SOURCE_IMAGE" ]]; then
  printf 'source_image=%s\n' "$SOURCE_IMAGE"
fi
printf 'skill_dir=%s\n' "$SCRIPT_DIR"
printf '%s\n' '---END_RESULT---'

