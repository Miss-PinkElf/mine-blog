# -*- coding: utf-8 -*-
"""Extract GptImageTutorialView documentation strings from SPA bundle."""
from __future__ import annotations

import re
from pathlib import Path

JS = Path(r"C:\Users\Mobius\AppData\Local\Temp\wyzlab-docs\index.js")
OUT = Path(r"C:\Users\Mobius\AppData\Local\Temp\wyzlab-docs\extracted.txt")
OUT_DIR = Path(r"C:\Users\Mobius\AppData\Local\Temp\wyzlab-docs")


def unescape_js(s: str) -> str:
    s = s.replace("\\n", "\n").replace("\\t", "\t").replace("\\r", "\r")
    s = s.replace("\\'", "'").replace('\\"', '"').replace("\\\\", "\\")
    return s


def main() -> None:
    js = JS.read_text(encoding="utf-8", errors="replace")
    idx = js.find("GptImageTutorialView")
    print(f"GptImageTutorialView at {idx}")
    # Tutorial content is mostly BEFORE the component name in the bundle
    start = max(0, idx - 120000)
    end = min(len(js), idx + 30000)
    region = js[start:end]
    print(f"region length {len(region)}")

    keywords = (
        "gpt-image",
        "metadata",
        "image_size",
        "image_url",
        "images/generations",
        "image_quality",
        "image_input",
        "image_moderation",
        "image_partial",
        "image_background",
        "image_output",
        "chat/completions",
        "safety_violations",
        "input_fidelity",
        "partial_images",
        "b64_json",
        "response_format",
        "extra_body",
    )

    parts: list[str] = []
    seen: set[str] = set()

    for pat in (
        r"'((?:\\'|[^']){60,})'",
        r'"((?:\\"|[^"]){60,})"',
        r"`((?:\\`|[^`]){60,})`",
    ):
        for m in re.finditer(pat, region):
            raw = m.group(1)
            dec = unescape_js(raw)
            if not any(k in dec for k in keywords):
                continue
            key = dec[:200]
            if key in seen:
                continue
            seen.add(key)
            parts.append(dec)
            parts.append("\n" + "=" * 60 + "\n")

    OUT.write_text("\n".join(parts), encoding="utf-8")
    print(f"wrote {OUT} size={OUT.stat().st_size} snippets={len(parts)//2}")

    # Also dump parameter tables near image_size definitions
    m = re.search(
        r"image_size[\s\S]{0,8000}?image_partial_images[\s\S]{0,500}",
        region,
    )
    if m:
        (OUT_DIR / "params_region.txt").write_text(m.group(0), encoding="utf-8")
        print("wrote params_region.txt")

    # FAQ array region
    m2 = re.search(r"\{q:\"[^\"]+\",a:\"[\s\S]{20,800}?\"\}", region)
    faqs = re.findall(r'\{q:"((?:\\"|[^"])+)",a:"((?:\\"|[^"])+)"\}', region)
    if faqs:
        lines = []
        for q, a in faqs:
            lines.append(f"Q: {unescape_js(q)}")
            lines.append(f"A: {unescape_js(a)}")
            lines.append("-" * 40)
        (OUT_DIR / "faq.txt").write_text("\n".join(lines), encoding="utf-8")
        print(f"wrote faq.txt count={len(faqs)}")

    # Scene examples id/title/body
    scenes = re.findall(
        r'\{id:"([^"]+)",title:"((?:\\"|[^"])+)",tag:"([^"]+)",color:"[^"]+",body:\'([\s\S]*?)\'\}',
        region,
    )
    if scenes:
        lines = []
        for sid, title, tag, body in scenes:
            lines.append(f"### {sid} | {unescape_js(title)} | {tag}")
            lines.append(unescape_js(body))
            lines.append("=" * 60)
        (OUT_DIR / "scenes.txt").write_text("\n".join(lines), encoding="utf-8")
        print(f"wrote scenes.txt count={len(scenes)}")

    # Param table objects name/type/values/def/desc
    params = re.findall(
        r'\{name:"([^"]+)",type:"([^"]+)",values:"((?:\\"|[^"])*)",def:"((?:\\"|[^"])*)",desc:"((?:\\"|[^"])*)"\}',
        region,
    )
    if params:
        lines = []
        for name, typ, values, default, desc in params:
            lines.append(
                f"| {name} | {typ} | {unescape_js(values)} | {unescape_js(default)} | {unescape_js(desc)} |"
            )
        (OUT_DIR / "param_table.txt").write_text("\n".join(lines), encoding="utf-8")
        print(f"wrote param_table.txt count={len(params)}")


if __name__ == "__main__":
    main()
