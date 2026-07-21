# -*- coding: utf-8 -*-
from pathlib import Path
import re

js = Path(r"C:\Users\Mobius\AppData\Local\Temp\wyzlab-docs\index.js").read_text(encoding="utf-8")
region = js[1087000:1099000]


def unesc(s: str) -> str:
    return (
        s.replace("\\n", "\n")
        .replace("\\t", "\t")
        .replace('\\"', '"')
        .replace("\\'", "'")
        .replace("\\\\", "\\")
    )


faqs = re.findall(r'\{q:"((?:\\"|[^"])+)",a:"((?:\\"|[^"])+)"\}', region)
print(f"FAQ count in region: {len(faqs)}")
for q, a in faqs:
    print("Q:", unesc(q))
    print("A:", unesc(a))
    print("-" * 50)

# any multi-image related text near tutorial
for m in re.finditer(r".{0,60}(多张|多图|多个 image|image_url|参考图|还原度).{0,100}", region):
    print("CTX:", unesc(m.group(0))[:220])
    print("---")
