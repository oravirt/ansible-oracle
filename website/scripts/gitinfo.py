#!/usr/bin/env python3
"""Write the last commit of each documentation source to data/gitinfo.json.

hugo gives the pages of content/docs/_content.gotmpl the git info of the
content adapter itself. The adapter uses this file for "Last modified" instead.
Keys are the paths below the repository root in lower case, like in the adapter.
"""

import json
import subprocess
import sys
from pathlib import Path

website = Path(__file__).resolve().parent.parent
sources = ["doc", ":(glob)roles/*/README.md"]

log = subprocess.run(
    ["git", "log", "--format=%x1e%H%x1f%h%x1f%cI%x1f%s", "--name-only", "--", *sources],
    cwd=website.parent, check=True, capture_output=True, text=True,
).stdout

info = {}
for entry in log.split("\x1e")[1:]:
    header, _, files = entry.partition("\n")
    full, short, date, subject = header.split("\x1f", 3)
    for name in files.split():
        # git log starts with the newest commit
        info.setdefault(
            name.lower(),
            {"hash": full, "short": short, "date": date, "subject": subject},
        )

target = website / "data" / "gitinfo.json"
target.parent.mkdir(exist_ok=True)
target.write_text(json.dumps(info, indent=1, sort_keys=True) + "\n")
print(f"{target.relative_to(website)}: {len(info)} files", file=sys.stderr)
