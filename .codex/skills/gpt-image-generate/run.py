#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gpt-image-generate 主入口（Python）。

协议: POST {BASE_URL}/chat/completions
支持文生图 / 多图参考图生图；输入参考图可按 --prep 档位压缩（默认不固定长边）。
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import platform
import random
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
LIB_DIR = SCRIPT_DIR / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from image_prep import PrepOptions, prepare_image  # noqa: E402
from json_codec import find_image_source  # noqa: E402

ENV_FILE = SCRIPT_DIR / ".env"
GEN_DIR = SCRIPT_DIR / "gen-images"
DEFAULT_PROMPT_FILE = SCRIPT_DIR / "prompts" / "prompt-image.md"


def log(msg: str) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def step(msg: str) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"\n==> [{ts}] {msg}", flush=True)


def load_env_file(path: Path) -> None:
    if not path.is_file():
        return
    log(f"已加载配置: {path}")
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        if key and key not in os.environ:
            os.environ[key] = value


def elapsed_text(start: float) -> str:
    total = int(max(0, time.time() - start))
    m, s = divmod(total, 60)
    if m > 0:
        return f"{m}m{s:02d}s（共 {total}s）"
    return f"{total}s"


def read_prompt_file(path: Path) -> str:
    if not path.is_file():
        raise SystemExit(
            f"错误: 提示词文件不存在: {path}\n"
            f"请创建并写入生图提示词。"
        )
    content = path.read_text(encoding="utf-8").strip()
    if not content:
        raise SystemExit(f"错误: 提示词文件为空: {path}")
    return content


def build_default_output_path(gen_dir: Path) -> Path:
    gen_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    path = gen_dir / f"{stamp}.png"
    if path.exists():
        path = gen_dir / f"{stamp}-{random.randint(0, 9999):04d}.png"
    return path


def resolve_existing_path(p: str) -> Path:
    path = Path(p)
    if path.is_file():
        return path.resolve()
    cand = SCRIPT_DIR / p
    if cand.is_file():
        return cand.resolve()
    raise SystemExit(f"错误: 参考图不存在: {p}")


def build_request_body(
    model: str,
    prompt: str,
    images: List[Tuple[str, bytes]],
) -> Dict[str, Any]:
    """images: list of (mime, raw_bytes)."""
    if not images:
        return {
            "model": model,
            "stream": False,
            "messages": [{"role": "user", "content": prompt}],
        }
    content: List[Dict[str, Any]] = [{"type": "text", "text": prompt}]
    for mime, raw in images:
        b64 = base64.b64encode(raw).decode("ascii")
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:{mime};base64,{b64}"},
            }
        )
    return {
        "model": model,
        "stream": False,
        "messages": [{"role": "user", "content": content}],
    }


def http_post_json(
    url: str,
    api_key: str,
    body: Dict[str, Any],
    connect_timeout: float,
    max_time: float,
) -> Tuple[int, bytes]:
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "gpt-image-generate/2.0",
        },
    )
    # urllib 单一 timeout；用 max_time 作为总超时
    timeout = max(1.0, float(max_time))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return int(resp.status), resp.read()
    except urllib.error.HTTPError as e:
        raw = e.read() if hasattr(e, "read") else b""
        return int(e.code), raw or str(e).encode("utf-8", errors="replace")
    except urllib.error.URLError as e:
        raise RuntimeError(f"网络错误: {e.reason}") from e


def download_url(url: str, timeout: float) -> bytes:
    req = urllib.request.Request(
        url, headers={"User-Agent": "gpt-image-generate/2.0"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def save_image_from_response(obj: Any, out: Path, timeout: float) -> None:
    src = find_image_source(obj)
    if not src:
        raise RuntimeError("响应成功但未解析到图片")
    kind, value = src
    if kind == "url":
        log("响应为图片 URL，开始下载...")
        raw = download_url(value, timeout=timeout)
    else:
        raw = base64.b64decode(value)
    if not raw:
        raise RuntimeError("解码后图片为空")
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(out.suffix + f".tmp.{os.getpid()}")
    tmp.write_bytes(raw)
    tmp.replace(out)


def print_error_body(raw: bytes) -> None:
    text = raw.decode("utf-8", errors="replace")
    try:
        obj = json.loads(text)

        def walk(x: Any) -> Any:
            if isinstance(x, dict):
                return {k: walk(v) for k, v in x.items()}
            if isinstance(x, list):
                return [walk(v) for v in x]
            if isinstance(x, str) and len(x) > 200:
                return x[:80] + f"...<已截断,len={len(x)}>"
            return x

        print(json.dumps(walk(obj), ensure_ascii=False, indent=2)[:4000], file=sys.stderr)
    except Exception:
        print(text[:800], file=sys.stderr)


def open_image(path: Path) -> None:
    system = platform.system()
    try:
        if system == "Windows":
            os.startfile(str(path))  # type: ignore[attr-defined]
        elif system == "Darwin":
            subprocess.run(["open", str(path)], check=False)
        else:
            subprocess.run(["xdg-open", str(path)], check=False)
    except Exception as e:
        log(f"自动打开图片失败: {e}")


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="run.py",
        description="gpt-image-generate：Chat Completions 文生图 / 图生图（Python 主入口）",
    )
    p.add_argument("prompt_parts", nargs="*", help="提示词（可多段拼接）")
    p.add_argument("-o", "--output", help="输出图片路径")
    p.add_argument("-m", "--model", help="模型名")
    p.add_argument("--base-url", help="API Base URL")
    p.add_argument("-p", "--prompt-file", help="提示词文件")
    p.add_argument(
        "-i",
        "--image",
        action="append",
        default=[],
        dest="images",
        help="参考图路径（可重复）",
    )
    p.add_argument("--retries", type=int, default=None, help="最多重试次数（不含首次）")
    p.add_argument("--raw", action="store_true", help="只打印 JSON，不落盘图片")
    p.add_argument("--no-open", action="store_true", help="生成后不自动打开")
    p.add_argument(
        "--prep",
        choices=["off", "light", "medium", "heavy"],
        default=None,
        help="输入参考图压缩档位（默认 medium；off=原样）",
    )
    p.add_argument("--no-prep", action="store_true", help="等价 --prep off")
    p.add_argument("--jpeg-quality", type=int, default=None, help="覆盖 JPEG 质量 1-100")
    p.add_argument("--target-bytes", type=int, default=None, help="单张输入目标体积（字节）")
    p.add_argument(
        "--max-edge",
        type=int,
        default=None,
        help="可选输入长边上限；0=关闭（默认关闭，不固定长边）",
    )
    p.add_argument("--max-images", type=int, default=None, help="最多参考图张数（默认 4）")
    return p.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    start = time.time()
    load_env_file(ENV_FILE)
    args = parse_args(argv)

    base_url = (args.base_url or os.environ.get("OPENAI_BASE_URL") or "https://shell.wyzlab.ai/v1").rstrip("/")
    model = args.model or os.environ.get("OPENAI_MODEL") or "gpt-image-2"
    api_key = os.environ.get("OPENAI_API_KEY") or ""
    connect_timeout = float(os.environ.get("CURL_CONNECT_TIMEOUT") or 20)
    max_time = float(os.environ.get("CURL_MAX_TIME") or os.environ.get("REQUEST_MAX_TIME") or 180)
    max_retries = args.retries if args.retries is not None else int(os.environ.get("GPT_IMAGE_RETRIES") or 5)
    max_images = args.max_images if args.max_images is not None else int(os.environ.get("GPT_IMAGE_MAX_IMAGES") or 4)

    prep = "off" if args.no_prep else (args.prep or os.environ.get("GPT_IMAGE_PREP") or "medium")
    jpeg_quality = args.jpeg_quality
    if jpeg_quality is None and os.environ.get("GPT_IMAGE_JPEG_QUALITY"):
        jpeg_quality = int(os.environ["GPT_IMAGE_JPEG_QUALITY"])
    target_bytes = args.target_bytes
    if target_bytes is None and os.environ.get("GPT_IMAGE_TARGET_BYTES"):
        target_bytes = int(os.environ["GPT_IMAGE_TARGET_BYTES"])
    max_edge = args.max_edge
    if max_edge is None:
        max_edge = int(os.environ.get("GPT_IMAGE_MAX_EDGE") or 0)

    if not api_key or api_key in ("你的key填这里", "sk-xxxx"):
        print("错误: 未配置有效的 OPENAI_API_KEY", file=sys.stderr)
        print(f"请编辑 skill 同级 .env: {ENV_FILE}", file=sys.stderr)
        print(f'可复制: copy "{SCRIPT_DIR / ".env.example"}" "{ENV_FILE}"', file=sys.stderr)
        return 1

    # 提示词
    if args.prompt_parts:
        prompt = " ".join(args.prompt_parts).strip()
        if not prompt:
            print("错误: 命令行提示词为空", file=sys.stderr)
            return 1
        log("提示词来源: 命令行参数")
    else:
        pf = Path(args.prompt_file) if args.prompt_file else DEFAULT_PROMPT_FILE
        if not pf.is_file() and args.prompt_file:
            alt = SCRIPT_DIR / args.prompt_file
            if alt.is_file():
                pf = alt
        prompt = read_prompt_file(pf)
        log(f"提示词来源: {pf}")

    # 参考图
    image_paths: List[Path] = []
    if args.images:
        if len(args.images) > max_images:
            print(
                f"错误: 参考图数量 {len(args.images)} 超过上限 {max_images}",
                file=sys.stderr,
            )
            return 1
        for ip in args.images:
            image_paths.append(resolve_existing_path(ip))

    prep_opt = PrepOptions(
        prep=prep,
        jpeg_quality=jpeg_quality,
        target_bytes=target_bytes,
        max_edge=max_edge or 0,
    )

    prepared: List[Tuple[str, bytes]] = []
    metas: List[Dict[str, Any]] = []
    input_before = 0
    input_after = 0
    source_list: List[str] = []

    if image_paths:
        step("预处理参考图（仅输入，不影响输出尺寸）")
        log(f"prep={prep_opt.prep} jpeg_quality={prep_opt.jpeg_quality} "
            f"target_bytes={prep_opt.target_bytes} max_edge={prep_opt.max_edge}")
        for path in image_paths:
            try:
                mime, raw, meta = prepare_image(str(path), prep_opt)
            except Exception as e:
                print(f"错误: 预处理失败 ({path}): {e}", file=sys.stderr)
                return 1
            prepared.append((mime, raw))
            metas.append(meta)
            input_before += int(meta.get("original_bytes") or 0)
            input_after += int(meta.get("final_bytes") or 0)
            source_list.append(str(path))
            log(
                f"  {path.name}: {meta.get('original_bytes')}B"
                f" → {meta.get('final_bytes')}B"
                f" wh={meta.get('original_wh')}→{meta.get('final_wh')}"
                f" scaled={meta.get('scaled')} q={meta.get('jpeg_quality')} mime={mime}"
            )
        mode = "image_edit"
    else:
        mode = "text"

    step("1/4 准备输出目录")
    GEN_DIR.mkdir(parents=True, exist_ok=True)
    output = Path(args.output).resolve() if args.output else build_default_output_path(GEN_DIR)
    output.parent.mkdir(parents=True, exist_ok=True)
    log(f"目标图片: {output}")
    log(f"主模型:   {model}")
    log(f"Base URL: {base_url}")
    log(f"模式:     {mode}")
    log(f"提示词:   {prompt[:200]}{'…' if len(prompt) > 200 else ''}")
    if source_list:
        log(f"参考图数: {len(source_list)}")

    step("2/4 组装 Chat Completions 请求")
    body = build_request_body(model, prompt, prepared)
    body_bytes = len(json.dumps(body, ensure_ascii=False).encode("utf-8"))
    log(f"请求体已就绪（mode={mode} / bytes={body_bytes} / runtime=python / protocol=chat）")

    endpoint = f"{base_url}/chat/completions"
    total_attempts = max_retries + 1
    step(f"3/4 调用接口（最多 {total_attempts} 次尝试）")
    log(f"POST {endpoint}")
    log(f"超时: connect≈{connect_timeout}s, max-time={max_time}s")

    last_error = ""
    last_raw = b""
    success = False
    resp_obj: Any = None

    for attempt in range(1, total_attempts + 1):
        log(f"---------- 第 {attempt}/{total_attempts} 次尝试 ----------")
        attempt_start = time.time()
        try:
            status, raw = http_post_json(
                endpoint, api_key, body, connect_timeout, max_time
            )
        except Exception as e:
            last_error = str(e)
            log(f"❌ {last_error}")
            if attempt < total_attempts:
                sleep_s = min(30, attempt * 5)
                log(f"将在 {sleep_s}s 后重试...")
                time.sleep(sleep_s)
            continue

        log(f"本次耗时: {int(time.time() - attempt_start)}s | 累计: {elapsed_text(start)}")
        last_raw = raw

        if status == 401:
            last_error = f"HTTP {status}（认证失败，不重试）"
            log(f"❌ {last_error}")
            print_error_body(raw)
            break

        if status < 200 or status >= 300:
            last_error = f"HTTP {status}"
            log(f"❌ 请求失败：{last_error}")
            print_error_body(raw)
            if attempt < total_attempts:
                sleep_s = min(30, attempt * 5)
                log(f"将在 {sleep_s}s 后重试...")
                time.sleep(sleep_s)
            continue

        log(f"HTTP 状态码: {status}（成功）")
        try:
            resp_obj = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            last_error = "响应不是合法 JSON"
            log(f"❌ {last_error}")
            print_error_body(raw)
            if attempt < total_attempts:
                time.sleep(min(30, attempt * 5))
            continue

        if args.raw:
            print(json.dumps(resp_obj, ensure_ascii=False, indent=2))
            log(f"总耗时: {elapsed_text(start)} | raw 模式完成")
            return 0

        step("4/4 解析并保存图片")
        try:
            save_image_from_response(resp_obj, output, timeout=max_time)
        except Exception as e:
            last_error = f"保存图片失败: {e}"
            log(f"❌ {last_error}")
            print_error_body(raw)
            if attempt < total_attempts:
                time.sleep(min(30, attempt * 5))
            continue

        if not output.is_file() or output.stat().st_size <= 0:
            last_error = "输出文件为空"
            log(f"❌ {last_error}")
            if attempt < total_attempts:
                time.sleep(min(30, attempt * 5))
            continue

        success = True
        log(f"✅ 第 {attempt}/{total_attempts} 次尝试成功")
        break

    if not success:
        fail_path = GEN_DIR / f"failed-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.json"
        try:
            if last_raw:
                fail_path.write_bytes(last_raw)
                print(f"最后一次响应已保存: {fail_path}", file=sys.stderr)
        except OSError:
            pass
        print(
            f"错误: 已尝试 {total_attempts} 次仍失败\n"
            f"最后错误: {last_error or 'unknown'}\n"
            f"已用时: {elapsed_text(start)}",
            file=sys.stderr,
        )
        return 1

    file_size = output.stat().st_size
    elapsed_sec = int(max(0, time.time() - start))
    try:
        output_rel = str(output.relative_to(SCRIPT_DIR))
    except ValueError:
        output_rel = str(output)

    log(f"图片已保存: {output}")
    log(f"文件大小:   {file_size} bytes")
    log(f"总耗时:     {elapsed_text(start)}")

    if not args.no_open:
        log("正在打开图片...")
        open_image(output)

    print(f"\n✅ 完成：{output}")
    print(f"⏱  总耗时：{elapsed_text(start)}")
    print(f"📦 文件大小：{file_size} bytes")

    print("\n---RESULT---")
    print("status=ok")
    print(f"path={output}")
    print(f"path_rel={output_rel}")
    print(f"bytes={file_size}")
    print(f"elapsed_seconds={elapsed_sec}")
    print(f"elapsed_text={elapsed_text(start)}")
    print(f"model={model}")
    print(f"mode={mode}")
    print("json_backend=python")
    print("runtime=python")
    print(f"source_images_count={len(source_list)}")
    if source_list:
        print(f"source_image={'|'.join(source_list)}")
    print(f"request_body_bytes={body_bytes}")
    print(f"image_prep={prep_opt.prep}")
    if jpeg_quality is not None:
        print(f"jpeg_quality={jpeg_quality}")
    elif metas and metas[0].get("jpeg_quality") is not None:
        print(f"jpeg_quality={metas[0].get('jpeg_quality')}")
    if target_bytes is not None:
        print(f"target_bytes={target_bytes}")
    print(f"max_edge={max_edge or 0}")
    print(f"input_bytes_before={input_before}")
    print(f"input_bytes_after={input_after}")
    print(f"skill_dir={SCRIPT_DIR}")
    print("---END_RESULT---")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\n[中断] 已退出（不重试）", file=sys.stderr)
        raise SystemExit(130)
