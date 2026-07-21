# -*- coding: utf-8 -*-
"""对比：官方风格 HTTPS image_url 多参考 vs data URL 大 body。

用已可公网访问的历史出图 URL 作参考，body 极小，验证「多 image_url 不稳」
是不是其实是 body 太大，而不是协议不支持。
"""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image

ENV = Path(".claude/skills/gpt-image-generate/.env")
OUT = Path(".devflow/gpt-image-cli-tooling/_probe_out")
OUT.mkdir(parents=True, exist_ok=True)


def load_env() -> None:
    for raw in ENV.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v


def post(url: str, key: str, body: dict, timeout: float = 180.0):
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    print(f"body_bytes={len(data)}")
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
            return int(resp.status), json.loads(resp.read().decode("utf-8")), None
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        try:
            return int(e.code), json.loads(raw), None
        except Exception:
            return int(e.code), raw[:500], None
    except Exception as e:
        return 0, None, f"{type(e).__name__}: {e}"


def download(url: str, path: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "gpt-image-probe/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        path.write_bytes(resp.read())


def main() -> None:
    load_env()
    key = os.environ["OPENAI_API_KEY"]
    base = os.environ.get("OPENAI_BASE_URL", "https://shell.wyzlab.ai/v1").rstrip("/")
    model = os.environ.get("OPENAI_MODEL", "gpt-image-2")
    chat = f"{base}/chat/completions"

    # 使用先前探针成功返回的公网图 URL（若失效则本探针会失败，属预期）
    # 优先：今天 probe 里拿到的图；否则从 skill-text / images-api 再文生两张拿 URL
    # 为可重复：先发两张小文生图拿 URL
    urls = []
    for prompt in [
        "simple blue circle icon, white background, flat",
        "simple green square icon, white background, flat",
    ]:
        code, obj, err = post(
            chat,
            key,
            {
                "model": model,
                "stream": False,
                "messages": [{"role": "user", "content": prompt}],
                "metadata": {"image_quality": "low", "image_size": "1024x1024"},
            },
            timeout=120,
        )
        print("seed", code, err)
        if not isinstance(obj, dict):
            print(obj)
            return
        content = ((obj.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
        found = re.findall(r"https?://\S+\.(?:png|jpe?g|webp)", content)
        print("seed urls", found)
        if not found:
            print("no seed url, abort")
            return
        urls.append(found[0])

    # 官方风格：HTTPS 多 image_url + image_input_fidelity
    body = {
        "model": model,
        "stream": False,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Image1 is a blue circle icon. Image2 is a green square icon. "
                            "Combine both shapes into one clean flat icon composition on white."
                        ),
                    },
                    {"type": "image_url", "image_url": {"url": urls[0]}},
                    {"type": "image_url", "image_url": {"url": urls[1]}},
                ],
            }
        ],
        "metadata": {
            "image_input_fidelity": "high",
            "image_quality": "low",
            "image_size": "1024x1024",
        },
    }
    print("\n=== dual HTTPS image_url + fidelity high ===")
    code, obj, err = post(chat, key, body, timeout=180)
    print("HTTP", code, "err", err)
    if err:
        return
    if not isinstance(obj, dict):
        print(obj)
        return
    print("model", obj.get("model"))
    content = ((obj.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
    print("content_head", content[:200].replace("\n", " "))
    out_urls = re.findall(r"https?://\S+\.(?:png|jpe?g|webp)", content)
    print("out_urls", out_urls)
    if out_urls:
        p = OUT / "dual-https-url-refs.png"
        download(out_urls[0], p)
        im = Image.open(p)
        print("saved", p, im.size, p.stat().st_size)


if __name__ == "__main__":
    main()
