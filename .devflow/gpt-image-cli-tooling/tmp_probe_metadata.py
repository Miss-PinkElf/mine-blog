# -*- coding: utf-8 -*-
"""Probe Chat Completions metadata.image_* against shell.wyzlab.ai.

不打印 API Key；只打印 status / 关键响应字段 / 是否解析到图 URL。
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2] / ".claude" / "skills" / "gpt-image-generate"
ENV = SKILL / ".env"


def load_env(path: Path) -> None:
    if not path.is_file():
        raise SystemExit(f"missing .env: {path}")
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v


def post(url: str, key: str, body: dict, timeout: float = 180.0) -> tuple[int, dict | str]:
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "User-Agent": "gpt-image-probe/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            code = int(resp.status)
    except urllib.error.HTTPError as e:
        raw = e.read() if hasattr(e, "read") else b""
        code = int(e.code)
    except Exception as e:
        return 0, f"ERR: {type(e).__name__}: {e}"

    text = raw.decode("utf-8", errors="replace")
    try:
        return code, json.loads(text)
    except json.JSONDecodeError:
        return code, text[:500]


def summarize(label: str, code: int, obj) -> None:
    print(f"\n=== {label} ===")
    print(f"HTTP {code}")
    if isinstance(obj, str):
        print(obj[:400])
        return
    print("model:", obj.get("model"))
    choices = obj.get("choices") or []
    if choices:
        content = (choices[0].get("message") or {}).get("content")
        if isinstance(content, str):
            print("content_head:", content[:180].replace("\n", " "))
            urls = re.findall(r"https?://\S+\.(?:png|jpe?g|webp)", content)
            print("image_urls:", urls[:3] if urls else None)
        else:
            print("content_type:", type(content).__name__, str(content)[:180])
    err = obj.get("error")
    if err:
        print("error:", err)


def main() -> None:
    load_env(ENV)
    key = os.environ.get("OPENAI_API_KEY") or ""
    base = (os.environ.get("OPENAI_BASE_URL") or "https://shell.wyzlab.ai/v1").rstrip("/")
    model = os.environ.get("OPENAI_MODEL") or "gpt-image-2"
    if not key:
        raise SystemExit("no OPENAI_API_KEY")

    chat_url = f"{base}/chat/completions"
    images_url = f"{base}/images/generations"

    # 1) Chat 文生图 + metadata size/quality
    body1 = {
        "model": model,
        "stream": False,
        "messages": [
            {
                "role": "user",
                "content": "simple flat icon of a red apple, white background, minimal",
            }
        ],
        "metadata": {
            "image_size": "1024x1024",
            "image_quality": "low",
            "image_output_format": "png",
        },
    }
    code, obj = post(chat_url, key, body1)
    summarize("chat+metadata low 1:1", code, obj)

    # 2) Chat 竖版 ratio via image_size
    body2 = {
        "model": model,
        "stream": False,
        "messages": [
            {
                "role": "user",
                "content": "vertical poster of a blue mountain at dusk, minimal illustration",
            }
        ],
        "metadata": {
            "image_size": "1024x1536",
            "image_quality": "low",
        },
    }
    code, obj = post(chat_url, key, body2)
    summarize("chat+metadata 2:3", code, obj)

    # 3) Images API 对照
    body3 = {
        "model": model,
        "prompt": "simple flat icon of a green pear, white background, minimal",
        "size": "1024x1024",
        "quality": "low",
        "n": 1,
    }
    code, obj = post(images_url, key, body3)
    summarize("images/generations low 1:1", code, obj)

    print("\nDONE")


if __name__ == "__main__":
    main()
