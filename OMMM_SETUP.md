# agentring for the OMMM agency (fork of mutonby/agentring)

## Review (Claude, 5 Nov 2026)
- Apache-2.0, ~284 stars, active (last commit 5 Nov 2026), CI + Android e2e tests, documented threat model.
- Daemon runs agent commands with `create_subprocess_exec` (argv list, no shell) - fine.
- Risk to manage: on a call the voice AI acts on what it hears -> give it read-only tools only
  (status, logs, "what is stuck"), never upload/publish/delete commands.
- Data: messages + call reasons stored on our relay (SQLite); push text is readable by Google FCM;
  call audio goes to the chosen voice AI (Gemini free tier may be used by Google). Never speak passwords on a call.

## Our setup plan
| Step | Who | Notes |
|---|---|---|
| Relay + LiveKit on the laptop (docker-compose.local.yml) | Claude, after owner installs Docker Desktop | phone reaches it over Tailscale (already installed) |
| Firebase project (free) + google-services / service account | owner (login) | docs/firebase.md |
| Gemini API key in ~/.agentring/.env | owner types it | never in files we commit |
| Daemon: `pip install ./daemon[voice]`, `agentring init`, `agentring pair` | Claude + owner scans QR | |
| App on the vivo phone (Google Play) | owner | allow "display over lock screen", battery: no restrictions (docs/troubleshooting-oem.md) |
| `claude mcp add agentring -- agentring mcp` | Claude | |

## OMMM customisations (planned)
- Call the owner when: an agy lane is stuck > 1 h, a YouTube token expires, uploads fail, QA fails twice, an approval waits > 12 h.
- Message (not call) for: morning report, e-book/video batch finished.
- Voice AI tools (read-only): `team_check.py` status, last 10 log lines, list approvals waiting.
- Quiet hours 23:00-07:00 except P0.
