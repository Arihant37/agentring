"""OMMM -> agentring alerts (run every 15 min). Calls the owner for P0 problems, messages for the rest.
Read-only checks; never uploads, publishes or deletes. Needs the `agentring` CLI (paired) on PATH.
    python ommm/ommm_alerts.py            # check once and alert
    python ommm/ommm_alerts.py --dry      # print what it would send
"""
import datetime as dt
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

PRIYA = Path(r"C:\Users\ariha\Downloads\priya")
STATE = Path.home() / ".agentring" / "ommm_alerts_state.json"  # remembers what was already sent
QUIET = (23, 7)  # no calls 23:00-07:00 except P0


def checks():
    out = []
    now = dt.datetime.now()
    import re  # agy stuck: no 'agy' line in the team log for > 3 h (lane log files are rarely rewritten)
    log = PRIYA / "automation_team" / "log.md"
    if log.exists():
        stamps = re.findall(r"^- (\d\d \w{3} \d\d:\d\d) agy", log.read_text(encoding="utf-8", errors="ignore"), re.M)
        if stamps:
            last = dt.datetime.strptime(f"{stamps[-1]} {now.year}", "%d %b %H:%M %Y")
            hrs = (now - last).total_seconds() / 3600
            if hrs > 3:
                out.append(("P0", "agy", f"Antigravity has written nothing for {hrs:.0f} hours; it may be stuck."))
    try:  # Jarvis down
        urllib.request.urlopen("http://127.0.0.1:8770/", timeout=5)
    except Exception:
        out.append(("P1", "jarvis", "Jarvis is not responding on port 8770."))
    for tok in sorted((PRIYA / "youtube_mcp").glob("token_*.json")):  # expired YouTube login
        if "expired" in tok.name:
            continue
        try:
            exp = json.loads(tok.read_text()).get("expiry", "")
            if exp and dt.datetime.fromisoformat(exp.replace("Z", "+00:00")).replace(tzinfo=None) < now - dt.timedelta(days=6):
                out.append(("P1", tok.stem, f"YouTube login {tok.stem.replace('token_', '')} may have expired; re-run --add-channel."))
        except Exception:
            pass
    try:  # approvals waiting
        a = json.load(urllib.request.urlopen("http://127.0.0.1:8770/api/approvals", timeout=10)).get("summary", {})
        if a.get("videos", 0) + a.get("asks", 0) > 0:
            out.append(("P2", "approvals", f"{a.get('videos', 0)} videos and {a.get('asks', 0)} questions wait for your approval in Jarvis."))
    except Exception:
        pass
    return out


def main(dry=False):
    sent = json.loads(STATE.read_text()) if STATE.exists() else {}
    today = dt.date.today().isoformat()
    quiet = dt.datetime.now().hour >= QUIET[0] or dt.datetime.now().hour < QUIET[1]
    for prio, key, text in checks():
        if sent.get(key) == today:  # one alert per problem per day
            continue
        if prio == "P0":  # P0 calls even in quiet hours
            cmd = ["agentring", "call", text, "--ai"]
        elif prio == "P1" and not quiet:
            cmd = ["agentring", "call", text, "--ai"]
        else:
            cmd = ["agentring", "msg", text]
        print(prio, " ".join(cmd))
        if not dry:
            subprocess.run(cmd, check=False)
            sent[key] = today
    if not dry:
        STATE.parent.mkdir(exist_ok=True)
        STATE.write_text(json.dumps(sent))


if __name__ == "__main__":
    main(dry="--dry" in sys.argv)
