# -*- coding: utf-8 -*-
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

env = Path(".claude/skills/gpt-image-generate/.env")
for raw in env.read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, _, v = line.partition("=")
    k, v = k.strip(), v.strip().strip('"').strip("'")
    if k and k not in os.environ:
        os.environ[k] = v

base = os.environ.get("OPENAI_BASE_URL", "https://shell.wyzlab.ai/v1").rstrip("/")
key = os.environ["OPENAI_API_KEY"]

for path in ["/images/edits", "/images/variations", "/images/generations"]:
    url = base + path
    req = urllib.request.Request(
        url,
        data=b"{}",
        method="POST",
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print(path, r.status, r.read()[:200])
    except urllib.error.HTTPError as e:
        body = e.read()[:400].decode("utf-8", "replace")
        print(path, "HTTP", e.code, body)
    except Exception as e:
        print(path, "ERR", type(e).__name__, e)
