"""Static checks (nothing is run against a database).

* no secrets file, virtual environment or compiled Python file is tracked
* no password is written in code (a quoted literal after password / DB_PASSWORD)
* no tracked file or folder name starts or ends with a space
* every SQL file parses as PostgreSQL (sqlglot); every Python file compiles (warnings are errors)
* every README link that points into this repository leads to an existing file
"""
import glob
import os
import re
import subprocess
import sys
import urllib.parse
import warnings

import sqlglot
from sqlglot.errors import ParseError, TokenError

problems = []
tracked = [t.strip('"') for t in subprocess.run(["git", "ls-files"], capture_output=True, text=True, check=True, encoding="utf-8").stdout.splitlines()]

for t in tracked:
    parts = t.split("/")
    if t == ".env" or t.endswith("/.env"):
        problems.append(f"{t}: secrets file is tracked")
    if parts[0] in ("env", "venv", ".venv") or "site-packages" in parts or "__pycache__" in parts or t.endswith(".pyc"):
        problems.append(f"{t}: virtual environment or compiled file is tracked")
    if any(p != p.strip() for p in parts):
        problems.append(f"{t}: a name starts or ends with a space")

py = sorted(t for t in tracked if t.endswith(".py"))
warnings.simplefilter("error", SyntaxWarning)
secret = re.compile(r"""(?i)(password|passwd|pwd)["']?\s*[:=]\s*["'][^"']+["']""")
for f in py:
    with open(f, encoding="utf-8") as fh:
        src = fh.read()
    try:
        compile(src, f, "exec")
    except (SyntaxError, SyntaxWarning) as exc:
        problems.append(f"{f}: does not compile: {exc}")
    for i, line in enumerate(src.splitlines(), 1):
        if secret.search(line):
            problems.append(f"{f}:{i}: a password is written in code (read it from the environment)")

sql = sorted(t for t in tracked if t.endswith(".sql"))
for f in sql:
    with open(f, encoding="utf-8") as fh:
        txt = fh.read()
    if not txt.strip():
        problems.append(f"{f}: empty file")
        continue
    try:
        sqlglot.parse(txt, read="postgres")
    except (ParseError, TokenError) as exc:
        problems.append(f"{f}: PostgreSQL parse error: {str(exc).splitlines()[0][:110]}")

with open("README.md", encoding="utf-8") as fh:
    readme = fh.read()
n_links = 0
for target in re.findall(r"\]\(((?:[^()\s]|\([^)]*\))+)\)", readme):
    if re.match(r"^(https?:|#|mailto:)", target):
        continue
    n_links += 1
    if urllib.parse.unquote(target.split("#")[0]) not in tracked:
        problems.append(f"README: link to a missing file: {target}")

print(f"Checked {len(tracked)} tracked files: {len(sql)} SQL, {len(py)} Python, {n_links} README links, {len(problems)} problem(s)")
for p in problems:
    print("FAIL ", p)
sys.exit(1 if problems else 0)
