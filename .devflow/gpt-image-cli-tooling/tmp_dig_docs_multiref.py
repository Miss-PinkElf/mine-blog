# -*- coding: utf-8 -*-
from pathlib import Path
import re

region = Path(r"C:\Users\Mobius\AppData\Local\Temp\wyzlab-docs\region.txt").read_text(
    encoding="utf-8"
)
js = Path(r"C:\Users\Mobius\AppData\Local\Temp\wyzlab-docs\index.js").read_text(
    encoding="utf-8"
)


def unesc(s: str) -> str:
    return (
        s.replace("\\n", "\n")
        .replace("\\t", "\t")
        .replace('\\"', '"')
        .replace("\\'", "'")
        .replace("\\\\", "\\")
    )


keywords = [
    "images/edits",
    "image_url",
    "input_fidelity",
    "参考",
    "多图",
    "多张",
    "data:image",
    "base64",
    "MB",
    "文件",
    "上限",
    "体积",
    "压缩",
    "edit",
    "mask",
    "image[]",
    "images",
    "fidelity",
    "detail",
]

print("=== search whole js for gpt-image tutorial adjacent multi-ref ===")
# Find all FAQ entries more broadly
faqs = re.findall(r'\{q:"((?:\\"|[^"])+)",a:"((?:\\"|[^"])+)"\}', js)
print(f"total FAQ objects in whole bundle: {len(faqs)}")
for q, a in faqs:
    qa = unesc(q) + " " + unesc(a)
    if any(
        k in qa
        for k in [
            "图",
            "image",
            "gpt",
            "size",
            "metadata",
            "chat",
            "参考",
            "编辑",
            "edit",
            "URL",
            "url",
            "base64",
            "压缩",
            "断",
            "超时",
            "body",
            "多",
        ]
    ):
        print("Q:", unesc(q))
        print("A:", unesc(a)[:500])
        print("---")

print("\n=== images/edits mentions near tutorial ===")
for m in re.finditer(r".{0,100}images/edits.{0,200}", js):
    s = m.group(0)
    if m.start() > 1000000:  # near tutorial
        print(unesc(s)[:300])
        print("---")

print("\n=== all img2img / image_url bodies in tutorial region ===")
for m in re.finditer(
    r"image_url[\s\S]{0,400}",
    region,
):
    print(unesc(m.group(0))[:350])
    print("---")

print("\n=== HTML template text about 图生图 / 参考 ===")
# extract Chinese UI strings
for pat in [
    r"图生图[^\"']{0,200}",
    r"参考图[^\"']{0,200}",
    r"多[^\"']{0,80}图[^\"']{0,80}",
    r"https://example.com[^\"']{0,80}",
    r"data:image[^\"']{0,40}",
    r"上传[^\"']{0,120}",
    r"公网[^\"']{0,120}",
    r"URL[^\"']{0,120}",
]:
    hits = re.findall(pat, region)
    if hits:
        print("PAT", pat, "count", len(hits))
        for h in hits[:8]:
            print(" ", unesc(h)[:200])
