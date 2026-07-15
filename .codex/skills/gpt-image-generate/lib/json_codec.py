#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""JSON 组装 / 抽取回退（无 jq 时由 run.sh 调用）。流式输出 base64，避免进 shell 变量。"""
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import re
import sys
from pathlib import Path


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
            "input": [
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {
                            "type": "input_image",
                            "image_url": f"data:{mime};base64,{b64}",
                        },
                    ],
                }
            ],
            "tools": [{"type": "image_generation", "action": "edit"}],
        }
    else:
        body = {
            "model": model,
            "input": prompt,
            "tools": [{"type": "image_generation", "action": "generate"}],
        }
    out.write_text(json.dumps(body, ensure_ascii=False), encoding="utf-8")
    return 0


def find_b64(obj):
    if isinstance(obj, list):
        for x in obj:
            r = find_b64(x)
            if r:
                return r
        return None
    if not isinstance(obj, dict):
        return None
    if obj.get("type") == "image_generation_call":
        for k in ("result", "image_base64", "b64_json"):
            v = obj.get(k)
            if isinstance(v, str) and len(v) > 100:
                return v
    out = obj.get("output")
    if isinstance(out, list):
        for item in out:
            if not isinstance(item, dict):
                continue
            if item.get("type") == "image_generation_call":
                for k in ("result", "image_base64", "b64_json"):
                    v = item.get(k)
                    if isinstance(v, str) and len(v) > 100:
                        return v
            content = item.get("content")
            if isinstance(content, list):
                for c in content:
                    if not isinstance(c, dict):
                        continue
                    for k in ("image_url", "b64_json", "image_base64", "result"):
                        v = c.get(k)
                        if isinstance(v, str) and len(v) > 100:
                            if v.startswith("data:") and "," in v:
                                v = v.split(",", 1)[1]
                            return v
    data = obj.get("data")
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                for k in ("b64_json", "result", "image_base64"):
                    v = item.get(k)
                    if isinstance(v, str) and len(v) > 100:
                        return v
    return None


def cmd_extract(args: argparse.Namespace) -> int:
    obj = json.loads(Path(args.json).read_text(encoding="utf-8"))
    b64 = find_b64(obj)
    if not b64:
        return 2
    sys.stdout.write(re.sub(r"\s+", "", b64))
    return 0


def cmd_has(args: argparse.Namespace) -> int:
    obj = json.loads(Path(args.json).read_text(encoding="utf-8"))
    b64 = find_b64(obj)
    return 0 if (isinstance(b64, str) and len(b64) > 100) else 1


def cmd_meta(args: argparse.Namespace) -> int:
    obj = json.loads(Path(args.json).read_text(encoding="utf-8"))
    field = args.field
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
        v = ""
        if tools and isinstance(tools[0], dict):
            v = tools[0].get("model") or ""
    else:
        v = ig.get(field) or ""
    sys.stdout.write("" if v is None else str(v))
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

    args = p.parse_args()
    return int(args.func(args) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
