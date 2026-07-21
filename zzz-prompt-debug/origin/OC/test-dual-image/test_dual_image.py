#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""独立双图测试：不修改 gpt-image-generate skill。

协议：
  1) POST {BASE}/chat/completions  （多模态 image_url）
  2) POST {BASE}/responses          （input_text + input_image）

只读借用 skill 目录 .env 的 OPENAI_API_KEY / OPENAI_BASE_URL / OPENAI_MODEL。
"""
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
REPO = HERE
# 向上找到 mine-blog 根（含 .codex/skills）
for p in [HERE, *HERE.parents]:
    if (p / ".codex" / "skills" / "gpt-image-generate" / ".env").is_file():
        REPO = p
        break

SKILL_ENV = REPO / ".codex" / "skills" / "gpt-image-generate" / ".env"
OUT_DIR = HERE / "out"
DEFAULT_CHAR = (
    REPO
    / "zzz-prompt-debug"
    / "origin"
    / "OC"
    / "generated"
    / "rin-01-global-design.png"
)
DEFAULT_STYLE = (
    REPO / "zzz-prompt-debug" / "origin" / "OC" / "ref-style" / "style-05.jpg"
)

MD_IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
DATA_URL_RE = re.compile(r"^data:image/[^;]+;base64,(.+)$", re.DOTALL | re.IGNORECASE)


def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def load_env_file(path: Path) -> Dict[str, str]:
    env: Dict[str, str] = {}
    if not path.is_file():
        raise SystemExit(f"找不到 skill .env（只读借用）: {path}")
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k, v = k.strip(), v.strip()
        if (v.startswith('"') and v.endswith('"')) or (
            v.startswith("'") and v.endswith("'")
        ):
            v = v[1:-1]
        if k:
            env[k] = v
    return env


def mime_for(path: Path) -> str:
    ext = path.suffix.lower()
    mapping = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }
    if ext in mapping:
        return mapping[ext]
    guess, _ = mimetypes.guess_type(str(path))
    return guess or "image/png"


def maybe_downscale_jpeg(path: Path, max_edge: int = 1536, quality: int = 88) -> Tuple[bytes, str]:
    """大图压到 JPEG 以降低中转超时概率；小图原样。"""
    raw = path.read_bytes()
    mime = mime_for(path)
    if len(raw) <= 700_000 and path.suffix.lower() in {".jpg", ".jpeg"}:
        return raw, mime
    try:
        from PIL import Image  # type: ignore
        import io

        im = Image.open(path)
        im = im.convert("RGB")
        w, h = im.size
        edge = max(w, h)
        if edge > max_edge:
            scale = max_edge / float(edge)
            im = im.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=quality, optimize=True)
        out = buf.getvalue()
        log(f"  压缩 {path.name}: {len(raw):,} -> {len(out):,} bytes, size={im.size}")
        return out, "image/jpeg"
    except Exception as e:
        log(f"  未压缩（Pillow 不可用或失败: {e}），原样上传 {len(raw):,} bytes")
        return raw, mime


def data_url(mime: str, raw: bytes) -> str:
    return f"data:{mime};base64,{base64.b64encode(raw).decode('ascii')}"


def http_post_json(
    url: str,
    api_key: str,
    body: Dict[str, Any],
    timeout: float,
) -> Tuple[int, bytes, float]:
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    log(f"POST {url}  body={len(data):,} bytes  timeout={timeout:.0f}s")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "oc-dual-image-probe/1.0",
        },
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            code = getattr(resp, "status", 200) or 200
            return int(code), raw, time.time() - t0
    except urllib.error.HTTPError as e:
        raw = e.read() if e.fp else b""
        return int(e.code), raw, time.time() - t0
    except Exception as e:
        return 0, str(e).encode("utf-8", errors="replace"), time.time() - t0


def _strip_data_url(s: str) -> str:
    m = DATA_URL_RE.match(s.strip())
    if m:
        return re.sub(r"\s+", "", m.group(1))
    return re.sub(r"\s+", "", s)


def find_image_source(obj: Any) -> Optional[Tuple[str, str]]:
    """返回 (kind, value)，kind in url|b64。尽量兼容 chat / responses 多种形状。"""

    def from_str(text: str) -> Optional[Tuple[str, str]]:
        if not text or not isinstance(text, str):
            return None
        t = text.strip()
        m = MD_IMAGE_RE.search(t)
        if m:
            target = m.group(1).strip()
            if target.startswith(("http://", "https://")):
                return ("url", target)
            if target.lower().startswith("data:image/"):
                return ("b64", _strip_data_url(target))
        if t.lower().startswith("data:image/"):
            return ("b64", _strip_data_url(t))
        if t.startswith(("http://", "https://")) and "\n" not in t and len(t) < 8192:
            return ("url", t)
        # 很长的裸 base64
        if len(t) > 500 and re.fullmatch(r"[A-Za-z0-9+/=\s]+", t or ""):
            return ("b64", re.sub(r"\s+", "", t))
        return None

    def walk(node: Any, depth: int = 0) -> Optional[Tuple[str, str]]:
        if depth > 12 or node is None:
            return None
        if isinstance(node, str):
            return from_str(node)
        if isinstance(node, dict):
            # 常见 Images API 形状
            if isinstance(node.get("b64_json"), str) and node["b64_json"]:
                return ("b64", re.sub(r"\s+", "", node["b64_json"]))
            if isinstance(node.get("url"), str) and node["url"].startswith("http"):
                # 排除非图片 url 的误伤：仍返回，保存时再验证
                if any(k in node for k in ("b64_json", "revised_prompt")) or str(
                    node.get("url", "")
                ).lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                    return ("url", node["url"])
            # chat content / responses output
            for key in ("content", "text", "output_text", "result"):
                if key in node:
                    hit = walk(node[key], depth + 1)
                    if hit:
                        return hit
            if "image_url" in node:
                iu = node["image_url"]
                if isinstance(iu, str):
                    hit = from_str(iu)
                    if hit:
                        return hit
                if isinstance(iu, dict) and isinstance(iu.get("url"), str):
                    hit = from_str(iu["url"])
                    if hit:
                        return hit
            # responses: output[].content[].type == output_image / image
            t = str(node.get("type") or "")
            if t in {"output_image", "image", "input_image"}:
                for k in ("image_url", "url", "b64_json", "data"):
                    if k in node:
                        hit = walk(node[k], depth + 1)
                        if hit:
                            return hit
            for v in node.values():
                hit = walk(v, depth + 1)
                if hit:
                    return hit
        if isinstance(node, list):
            for item in node:
                hit = walk(item, depth + 1)
                if hit:
                    return hit
        return None

    return walk(obj)


def save_image(src: Tuple[str, str], out: Path, timeout: float) -> None:
    kind, value = src
    out.parent.mkdir(parents=True, exist_ok=True)
    if kind == "b64":
        raw = base64.b64decode(value)
        out.write_bytes(raw)
        log(f"  已写 b64 -> {out} ({len(raw):,} bytes)")
        return
    req = urllib.request.Request(value, headers={"User-Agent": "oc-dual-image-probe/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
    out.write_bytes(raw)
    log(f"  已下载 url -> {out} ({len(raw):,} bytes)")


def build_chat_body(model: str, prompt: str, images: List[Tuple[str, bytes]]) -> Dict[str, Any]:
    content: List[Dict[str, Any]] = [{"type": "text", "text": prompt}]
    for mime, raw in images:
        content.append(
            {"type": "image_url", "image_url": {"url": data_url(mime, raw)}}
        )
    return {
        "model": model,
        "stream": False,
        "messages": [{"role": "user", "content": content}],
    }


def build_responses_body(
    model: str, prompt: str, images: List[Tuple[str, bytes]]
) -> Dict[str, Any]:
    # OpenAI Responses API 多模态常见形状
    content: List[Dict[str, Any]] = [{"type": "input_text", "text": prompt}]
    for mime, raw in images:
        content.append(
            {
                "type": "input_image",
                "image_url": data_url(mime, raw),
            }
        )
    return {
        "model": model,
        "input": [{"role": "user", "content": content}],
    }


def run_protocol(
    name: str,
    url: str,
    api_key: str,
    body: Dict[str, Any],
    out_png: Path,
    raw_json: Path,
    timeout: float,
) -> Dict[str, Any]:
    code, raw, elapsed = http_post_json(url, api_key, body, timeout)
    raw_json.parent.mkdir(parents=True, exist_ok=True)
    # 限制落盘体积：若超大则截断标记
    try:
        text = raw.decode("utf-8", errors="replace")
    except Exception:
        text = ""
    if len(raw) > 8_000_000:
        raw_json.write_text(
            json.dumps(
                {
                    "note": "response too large, truncated meta only",
                    "http_status": code,
                    "bytes": len(raw),
                    "head": text[:2000],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
    else:
        raw_json.write_bytes(raw)

    result: Dict[str, Any] = {
        "protocol": name,
        "http_status": code,
        "elapsed_sec": round(elapsed, 2),
        "response_bytes": len(raw),
        "raw_json": str(raw_json),
        "output_png": None,
        "ok": False,
        "error": None,
        "preview": text[:500],
    }
    if code != 200:
        result["error"] = f"HTTP {code}"
        log(f"  FAIL {name}: HTTP {code}  elapsed={elapsed:.1f}s")
        log(f"  body head: {text[:400]}")
        return result

    try:
        obj = json.loads(text)
    except Exception as e:
        result["error"] = f"JSON parse failed: {e}"
        log(f"  FAIL {name}: JSON parse: {e}")
        return result

    src = find_image_source(obj)
    if not src:
        result["error"] = "no image found in response"
        log(f"  FAIL {name}: 响应 200 但未解析到图片")
        # 打印 keys 辅助诊断
        if isinstance(obj, dict):
            log(f"  top keys: {list(obj.keys())}")
        return result

    try:
        save_image(src, out_png, timeout=min(timeout, 120))
        result["output_png"] = str(out_png)
        result["ok"] = True
        log(f"  OK {name}: {out_png}  elapsed={elapsed:.1f}s")
    except Exception as e:
        result["error"] = f"save failed: {e}"
        log(f"  FAIL {name}: save: {e}")
    return result


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="双图参考测试（chat / responses）")
    ap.add_argument("--char", type=Path, default=DEFAULT_CHAR, help="人设参考图")
    ap.add_argument("--style", type=Path, default=DEFAULT_STYLE, help="风格参考图")
    ap.add_argument(
        "--protocol",
        choices=["chat", "responses", "both"],
        default="both",
        help="测试协议",
    )
    ap.add_argument("--timeout", type=float, default=300.0)
    ap.add_argument("--max-edge", type=int, default=1536)
    ap.add_argument("--model", default=None)
    ap.add_argument("--base-url", default=None)
    args = ap.parse_args(argv)

    env = load_env_file(SKILL_ENV)
    api_key = os.environ.get("OPENAI_API_KEY") or env.get("OPENAI_API_KEY") or ""
    base_url = (
        args.base_url
        or os.environ.get("OPENAI_BASE_URL")
        or env.get("OPENAI_BASE_URL")
        or ""
    ).rstrip("/")
    model = args.model or os.environ.get("OPENAI_MODEL") or env.get("OPENAI_MODEL") or "gpt-image-2"

    if not api_key:
        raise SystemExit("缺少 OPENAI_API_KEY")
    if not base_url:
        raise SystemExit("缺少 OPENAI_BASE_URL")
    if not args.char.is_file():
        raise SystemExit(f"人设图不存在: {args.char}")
    if not args.style.is_file():
        raise SystemExit(f"风格图不存在: {args.style}")

    stamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    log(f"skill env: {SKILL_ENV} (只读)")
    log(f"base_url: {base_url}")
    log(f"model: {model}")
    log(f"char:  {args.char} ({args.char.stat().st_size:,} bytes)")
    log(f"style: {args.style} ({args.style.stat().st_size:,} bytes)")
    log(f"key:   ***{api_key[-4:]}")

    # 顺序：图1=风格，图2=人设（与官方习惯一致）
    style_raw, style_mime = maybe_downscale_jpeg(args.style, max_edge=args.max_edge)
    char_raw, char_mime = maybe_downscale_jpeg(args.char, max_edge=args.max_edge)
    images = [(style_mime, style_raw), (char_mime, char_raw)]

    prompt = (
        "Image 1 is the STYLE reference only: match its art style, color grading, "
        "lighting, brushwork, and atmosphere. Do NOT copy Image 1 composition or characters.\n"
        "Image 2 is the CHARACTER design sheet: preserve this exact character identity — "
        "black hair with neon green streaks, green infinity-symbol eyes, school blazer + "
        "green plaid skirt, mismatched green/black thigh-highs, headphones, ouroboros earring.\n"
        "Task: generate ONE new full-body scene of the character from Image 2, standing on a "
        "rainy neon night street, cinematic three-quarter view, looking toward camera.\n"
        "Priority: identity from Image 2 first; visual style from Image 1 second.\n"
        "No text, no watermarks, no extra panels, no character sheet layout."
    )

    results: List[Dict[str, Any]] = []

    if args.protocol in ("chat", "both"):
        log("=== protocol: chat/completions ===")
        body = build_chat_body(model, prompt, images)
        r = run_protocol(
            "chat",
            f"{base_url}/chat/completions",
            api_key,
            body,
            OUT_DIR / f"{stamp}-chat.png",
            OUT_DIR / f"{stamp}-chat.raw.json",
            args.timeout,
        )
        results.append(r)

    if args.protocol in ("responses", "both"):
        log("=== protocol: responses ===")
        body = build_responses_body(model, prompt, images)
        r = run_protocol(
            "responses",
            f"{base_url}/responses",
            api_key,
            body,
            OUT_DIR / f"{stamp}-responses.png",
            OUT_DIR / f"{stamp}-responses.raw.json",
            args.timeout,
        )
        results.append(r)

    summary_path = OUT_DIR / f"{stamp}-summary.json"
    summary_path.write_text(
        json.dumps(
            {
                "stamp": stamp,
                "base_url": base_url,
                "model": model,
                "char": str(args.char),
                "style": str(args.style),
                "results": results,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    log(f"summary: {summary_path}")

    print("\n======== SUMMARY ========")
    for r in results:
        status = "OK" if r.get("ok") else "FAIL"
        print(
            f"[{status}] {r['protocol']}: http={r['http_status']} "
            f"elapsed={r['elapsed_sec']}s err={r.get('error')} out={r.get('output_png')}"
        )

    # 任一成功即 0
    return 0 if any(r.get("ok") for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
