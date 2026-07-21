# -*- coding: utf-8 -*-
"""Probe image_input_fidelity via Chat Completions multimodal."""
from __future__ import annotations

import base64
import json
import os
import re
import urllib.request
from pathlib import Path

from PIL import Image

SKILL = Path(__file__).resolve().parents[2] / ".claude" / "skills" / "gpt-image-generate"
ENV = SKILL / ".env"
REF = (
    Path(__file__).resolve().parents[2]
    / "zzz-prompt-debug"
    / "origin"
    / "OC"
    / "_preview"
    / "char-01.png"
)
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


def main() -> None:
    load_env(ENV)
    key = os.environ["OPENAI_API_KEY"]
    base = os.environ.get("OPENAI_BASE_URL", "https://shell.wyzlab.ai/v1").rstrip("/")
    model = os.environ.get("OPENAI_MODEL", "gpt-image-2")

    # compress ref lightly with pillow to keep body small
    im = Image.open(REF).convert("RGB")
    im.thumbnail((512, 512))
    from io import BytesIO

    buf = BytesIO()
    im.save(buf, format="JPEG", quality=70)
    raw = buf.getvalue()
    b64 = base64.b64encode(raw).decode("ascii")
    print(f"ref bytes={len(raw)} wh={im.size}")

    body = {
        "model": model,
        "stream": False,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Turn into flat vector illustration, preserve pose and face",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                    },
                ],
            }
        ],
        "metadata": {
            "image_input_fidelity": "high",
            "image_quality": "low",
            "image_size": "1024x1024",
        },
    }
    data = json.dumps(body).encode("utf-8")
    print("body bytes", len(data))
    req = urllib.request.Request(
        f"{base}/chat/completions",
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "User-Agent": "gpt-image-probe/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        obj = json.loads(resp.read().decode("utf-8"))
        print("HTTP", resp.status, "model", obj.get("model"))
    content = ((obj.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
    print("content_head", content[:160].replace("\n", " "))
    urls = re.findall(r"https?://\S+\.(?:png|jpe?g|webp)", content)
    print("urls", urls)
    if urls:
        p = OUT / "chat-fidelity-high.png"
        r = urllib.request.Request(urls[0], headers={"User-Agent": "gpt-image-probe/1.0"})
        with urllib.request.urlopen(r, timeout=60) as resp:
            p.write_bytes(resp.read())
        im2 = Image.open(p)
        print("saved", p, p.stat().st_size, "dim", im2.size)


if __name__ == "__main__":
    main()
