"""Read-only status for the voice AI ('call agent' -> 'what is going on?'). Prints a short plain summary.
Registered in ~/.agentring/agents.yaml as the 'ommm' agent. Never changes anything.
"""
import json
import urllib.request
from pathlib import Path

PRIYA = Path(r"C:\Users\ariha\Downloads\priya")
lines = []
log = PRIYA / "automation_team" / "log.md"
if log.exists():
    lines.append("Last team log lines: " + " | ".join(l[:120] for l in log.read_text(encoding="utf-8", errors="ignore").splitlines()[-5:]))
qa = list((PRIYA / "ebooks_store" / "books_v3").glob("*_qa.json"))
ok = sum(1 for f in qa if json.loads(f.read_text())["pass"])
lines.append(f"E-books ready: {ok} of 21.")
try:
    a = json.load(urllib.request.urlopen("http://127.0.0.1:8770/api/approvals", timeout=10)).get("summary", {})
    lines.append(f"Waiting for approval: {a.get('videos', 0)} videos, {a.get('drafts', 0)} drafts, {a.get('asks', 0)} questions.")
except Exception:
    lines.append("Jarvis is not responding.")
print("\n".join(lines))
