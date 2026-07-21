# -*- coding: utf-8 -*-
from datetime import datetime
from pathlib import Path
import subprocess

hist = Path(".devflow/gpt-image-cli-tooling/state-history.md")
old = subprocess.check_output(
    ["git", "show", "HEAD:.devflow/gpt-image-cli-tooling/state.md"],
    text=True,
    encoding="utf-8",
    errors="replace",
)
marker = "第四版 Close 快照"
text = hist.read_text(encoding="utf-8", errors="replace") if hist.exists() else "# State History · gpt-image-cli-tooling\n"
if marker in text:
    print("already present")
else:
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    sep = f"\n\n## {stamp} · 收尾前归档（{marker}）\n\n"
    hist.write_text(text.rstrip() + sep + old.strip() + "\n", encoding="utf-8")
    print("appended")
