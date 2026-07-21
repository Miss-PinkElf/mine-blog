# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2] / ".claude" / "skills" / "gpt-image-generate"
ENV = SKILL / ".env"
OUT = Path(__file__).resolve().parent / "_probe_out"
OUT.mkdir(exist_ok=True)


def load_env(path: Path) -> None:
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v


def post(url: str, key: str, body: dict, timeout: float = 180.0):
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
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return int(resp.status), json.loads(resp.read().decode("utf-8"))


def download(url: str, path: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "gpt-image-probe/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        path.write_bytes(resp.read())


def main() -> None:
    load_env(ENV)
    key = os.environ["OPENAI_API_KEY"]
    base = os.environ.get("OPENAI_BASE_URL", "https://shell.wyzlab.ai/v1").rstrip("/")
    model = os.environ.get("OPENAI_MODEL", "gpt-image-2")

    code, obj = post(
        f"{base}/images/generations",
        key,
        {
            "model": model,
            "prompt": "simple flat icon of a yellow star, white background",
            "size": "1024x1024",
            "quality": "low",
            "n": 1,
        },
    )
    print("HTTP", code)
    print(json.dumps(obj, ensure_ascii=False, indent=2)[:1500])

    data = obj.get("data") or []
    if data:
        item = data[0]
        if item.get("url"):
            p = OUT / "images-api-star.png"
            download(item["url"], p)
            print("saved", p, p.stat().st_size)
        elif item.get("b64_json"):
            import base64

            p = OUT / "images-api-star.png"
            p.write_bytes(base64.b64decode(item["b64_json"]))
            print("saved b64", p, p.stat().st_size)

    # download previous chat metadata images if still reachable
    # re-gen 2:3 and save locally for dim check
    code2, obj2 = post(
        f"{base}/chat/completions",
        key,
        {
            "model": model,
            "stream": False,
            "messages": [
                {
                    "role": "user",
                    "content": "vertical blue mountain poster, minimal illustration, solid colors",
                }
            ],
            "metadata": {
                "image_size": "1024x1536",
                "image_quality": "low",
            },
        },
    )
    print("\nchat 2:3 HTTP", code2, "model", obj2.get("model"))
    content = ((obj2.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
    import re

    urls = re.findall(r"https?://\S+\.(?:png|jpe?g|webp)", content)
    print("urls", urls)
    if urls:
        p = OUT / "chat-meta-2x3.png"
        download(urls[0], p)
        print("saved", p, p.stat().st_size)

    code3, obj3 = post(
        f"{base}/chat/completions",
        key,
        {
            "model": model,
            "stream": False,
            "messages": [
                {
                    "role": "user",
                    "content": "square red apple icon, white background, flat",
                }
            ],
            "metadata": {
                "image_size": "1024x1024",
                "image_quality": "low",
            },
        },
    )
    content = ((obj3.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
    urls = re.findall(r"https?://\S+\.(?:png|jpe?g|webp)", content)
    if urls:
        p = OUT / "chat-meta-1x1.png"
        download(urls[0], p)
        print("saved", p, p.stat().st_size)

    # report dimensions
    try:
        from PIL import Image

        for name in ["images-api-star.png", "chat-meta-2x3.png", "chat-meta-1x1.png"]:
            fp = OUT / name
            if fp.is_file():
                im = Image.open(fp)
                print(f"DIM {name}: {im.size} mode={im.mode}")
    except Exception as e:
        print("dim check failed", e)


if __name__ == "__main__":
    main()
