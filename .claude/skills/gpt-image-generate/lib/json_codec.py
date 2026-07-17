#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""JSON 组装 / 抽取回退（无 jq 时由 run.sh 调用）。

协议：OpenAI Chat Completions（POST /v1/chat/completions）
- 文生图：messages 纯文本
- 图生图：messages 多模态 text + image_url（data URL）
- 响应：choices[0].message.content 内 Markdown 图片 / data URL / 数组 image_url
"""
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Optional, Tuple

# Markdown 图片：![alt](url) —— url 可能是 https 或 data:image/...;base64,...
MD_IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
DATA_URL_RE = re.compile(r"^data:image/[^;]+;base64,(.+)$", re.DOTALL | re.IGNORECASE)


def mime_for(path: str) -> str:
    ext = Path(path).suffix.lower()
    mapping = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }
    if ext in mapping:
        return mapping[ext]
    guess, _ = mimetypes.guess_type(path)
    return guess or "image/png"


def cmd_build(args: argparse.Namespace) -> int:
    model = args.model
    prompt = args.prompt
    out = Path(args.out)
    if args.image:
        raw = Path(args.image).read_bytes()
        b64 = base64.b64encode(raw).decode("ascii")
        mime = args.mime or mime_for(args.image)
        body = {
            "model": model,
            "stream": False,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime};base64,{b64}"},
                        },
                    ],
                }
            ],
        }
    else:
        body = {
            "model": model,
            "stream": False,
            "messages": [{"role": "user", "content": prompt}],
        }
    out.write_text(json.dumps(body, ensure_ascii=False), encoding="utf-8")
    return 0


def _strip_data_url(s: str) -> str:
    m = DATA_URL_RE.match(s.strip())
    if m:
        return re.sub(r"\s+", "", m.group(1))
    return re.sub(r"\s+", "", s)


def _from_content_string(content: str) -> Optional[Tuple[str, str]]:
    """从字符串 content 解析出 (kind, value)。kind: url | b64。"""
    if not content or not isinstance(content, str):
        return None
    text = content.strip()
    if not text:
        return None

    # Markdown 图片优先
    m = MD_IMAGE_RE.search(text)
    if m:
        target = m.group(1).strip()
        if target.startswith(("http://", "https://")):
            return ("url", target)
        if target.lower().startswith("data:image/"):
            return ("b64", _strip_data_url(target))
        # 裸 base64 写在 markdown 里（少见）
        if len(target) > 100:
            return ("b64", re.sub(r"\s+", "", target))

    # 整段就是 data URL
    if text.lower().startswith("data:image/"):
        return ("b64", _strip_data_url(text))

    # 整段是 http(s) URL
    if text.startswith(("http://", "https://")) and "\n" not in text and len(text) < 4096:
        return ("url", text)

    return None


def _from_content_array(content: list) -> Optional[Tuple[str, str]]:
    for part in content:
        if not isinstance(part, dict):
            continue
        ptype = part.get("type")
        if ptype in ("image_url", "output_image", "image"):
            iu = part.get("image_url")
            url = None
            if isinstance(iu, dict):
                url = iu.get("url")
            elif isinstance(iu, str):
                url = iu
            if not url:
                url = part.get("url") or part.get("image")
            if isinstance(url, str) and len(url) > 8:
                if url.startswith(("http://", "https://")):
                    return ("url", url)
                if url.lower().startswith("data:image/"):
                    return ("b64", _strip_data_url(url))
                if len(url) > 100:
                    return ("b64", re.sub(r"\s+", "", url))
        if ptype == "text" and isinstance(part.get("text"), str):
            got = _from_content_string(part["text"])
            if got:
                return got
    return None


def find_image_source(obj: Any) -> Optional[Tuple[str, str]]:
    """返回 (kind, value)：kind 为 'url' 或 'b64'。"""
    if not isinstance(obj, dict):
        return None

    # 1) Chat Completions：choices[0].message.content
    choices = obj.get("choices")
    if isinstance(choices, list) and choices:
        msg = choices[0].get("message") if isinstance(choices[0], dict) else None
        if isinstance(msg, dict):
            content = msg.get("content")
            if isinstance(content, str):
                got = _from_content_string(content)
                if got:
                    return got
            elif isinstance(content, list):
                got = _from_content_array(content)
                if got:
                    return got
            # 少数网关：message.images / message.image_url
            for key in ("images", "image_url", "image"):
                extra = msg.get(key)
                if isinstance(extra, str) and len(extra) > 8:
                    if extra.startswith(("http://", "https://")):
                        return ("url", extra)
                    if extra.lower().startswith("data:image/"):
                        return ("b64", _strip_data_url(extra))
                if isinstance(extra, list):
                    got = _from_content_array(
                        [
                            {"type": "image_url", "image_url": x}
                            if isinstance(x, (str, dict))
                            else x
                            for x in extra
                        ]
                    )
                    if got:
                        return got

    # 2) Images API 兼容：data[0].b64_json / url
    data = obj.get("data")
    if isinstance(data, list):
        for item in data:
            if not isinstance(item, dict):
                continue
            for k in ("b64_json", "result", "image_base64"):
                v = item.get(k)
                if isinstance(v, str) and len(v) > 100:
                    return ("b64", re.sub(r"\s+", "", v))
            u = item.get("url")
            if isinstance(u, str) and u.startswith(("http://", "https://")):
                return ("url", u)

    # 3) 旧 Responses 兼容（兜底）
    out = obj.get("output")
    if isinstance(out, list):
        for item in out:
            if not isinstance(item, dict):
                continue
            if item.get("type") == "image_generation_call":
                for k in ("result", "image_base64", "b64_json"):
                    v = item.get(k)
                    if isinstance(v, str) and len(v) > 100:
                        return ("b64", re.sub(r"\s+", "", v))
            content = item.get("content")
            if isinstance(content, list):
                got = _from_content_array(content)
                if got:
                    return got

    return None


def find_b64(obj: Any) -> Optional[str]:
    """仅当源是 base64 时返回；URL 场景返回 None（需走 save/download）。"""
    src = find_image_source(obj)
    if src and src[0] == "b64":
        return src[1]
    return None


def cmd_extract(args: argparse.Namespace) -> int:
    obj = json.loads(Path(args.json).read_text(encoding="utf-8"))
    src = find_image_source(obj)
    if not src:
        return 2
    kind, value = src
    if kind == "b64":
        sys.stdout.write(value)
        return 0
    if kind == "url":
        # 下载后转 base64 流到 stdout（供 run.sh 统一 base64 -d 管线）
        try:
            req = urllib.request.Request(
                value,
                headers={"User-Agent": "gpt-image-generate/1.0"},
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                raw = resp.read()
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            print(f"下载图片失败: {e}", file=sys.stderr)
            return 3
        sys.stdout.write(base64.b64encode(raw).decode("ascii"))
        return 0
    return 2


def cmd_has(args: argparse.Namespace) -> int:
    obj = json.loads(Path(args.json).read_text(encoding="utf-8"))
    src = find_image_source(obj)
    if not src:
        return 1
    kind, value = src
    if kind == "url" and value.startswith(("http://", "https://")):
        return 0
    # 1x1 PNG 的 base64 仅约 96 字符；阈值不宜过高
    if kind == "b64" and len(value) >= 32:
        return 0
    return 1


def cmd_meta(args: argparse.Namespace) -> int:
    """Chat 协议元信息较少；尽量从 content / usage 取。"""
    obj = json.loads(Path(args.json).read_text(encoding="utf-8"))
    field = args.field
    v = ""
    if field == "tool_model":
        v = obj.get("model") or ""
    elif field == "revised_prompt":
        # chat 响应通常无改写提示词
        v = ""
    elif field in ("size", "quality", "output_format"):
        v = ""
    # 旧 responses 字段兼容
    if not v:
        outs = obj.get("output") or []
        ig = next(
            (
                x
                for x in outs
                if isinstance(x, dict) and x.get("type") == "image_generation_call"
            ),
            {},
        ) or {}
        if field == "tool_model":
            tools = obj.get("tools") or []
            if tools and isinstance(tools[0], dict):
                v = tools[0].get("model") or obj.get("model") or ""
        else:
            v = ig.get(field) or ""
    sys.stdout.write("" if v is None else str(v))
    return 0


def cmd_kind(args: argparse.Namespace) -> int:
    """打印 image 源类型：url / b64 / empty（调试用）。"""
    obj = json.loads(Path(args.json).read_text(encoding="utf-8"))
    src = find_image_source(obj)
    if not src:
        sys.stdout.write("empty")
        return 1
    sys.stdout.write(src[0])
    return 0


def main() -> int:
    p = argparse.ArgumentParser(prog="json_codec.py")
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build")
    b.add_argument("--model", required=True)
    b.add_argument("--prompt", required=True)
    b.add_argument("--out", required=True)
    b.add_argument("--image")
    b.add_argument("--mime")
    b.set_defaults(func=cmd_build)

    e = sub.add_parser("extract")
    e.add_argument("--json", required=True)
    e.set_defaults(func=cmd_extract)

    h = sub.add_parser("has")
    h.add_argument("--json", required=True)
    h.set_defaults(func=cmd_has)

    m = sub.add_parser("meta")
    m.add_argument("--json", required=True)
    m.add_argument("--field", required=True)
    m.set_defaults(func=cmd_meta)

    k = sub.add_parser("kind")
    k.add_argument("--json", required=True)
    k.set_defaults(func=cmd_kind)

    args = p.parse_args()
    return int(args.func(args) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
