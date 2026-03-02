---
name: comms
description: "Native communication integrations for email (IMAP/SMTP), Telegram, Discord, and Slack — enabling agents to send, receive, and respond to messages autonomously."
version: "1.0.0"
user-invocable: true
metadata:
  capabilities:
    - comms/email
    - comms/telegram
    - comms/discord
    - comms/slack
  author: "Antigravity (OpenPango Core)"
  license: "MIT"
---

# Communication Core Skill

Enables OpenPango agents to interact with the world through native messaging protocols. Instead of relying on browser automation to check email or respond on Slack, agents use direct API and protocol integrations for speed and reliability.

## Supported Channels

| Channel  | Protocol            | Send | Receive | Listen (Daemon) |
|----------|---------------------|------|---------|-----------------|
| Email    | IMAP / SMTP         | ✅   | ✅      | ✅              |
| Telegram | Bot HTTP API        | ✅   | ✅      | ✅              |
| Discord  | Bot Gateway / REST  | ✅   | ✅      | ✅              |
| Slack    | Bot Events API      | ✅   | ✅      | ✅              |

## Usage

```python
from skills.comms.messenger import Messenger

m = Messenger()

# Send an email
m.send(channel="email", to="ceo@example.com",
       subject="Weekly Agent Report", body="All 12 bounties shipped.")

# Send a Telegram message
m.send(channel="telegram", to="@openpango_alerts", body="PR #60 merged.")

# Listen for incoming messages on Discord (blocking daemon)
for msg in m.listen(channel="discord"):
    print(f"[{msg['author']}]: {msg['content']}")
```

## Environment Variables

| Variable              | Required For |
|-----------------------|-------------|
| `SMTP_HOST`           | Email       |
| `SMTP_USER`           | Email       |
| `SMTP_PASS`           | Email       |
| `IMAP_HOST`           | Email       |
| `TELEGRAM_BOT_TOKEN`  | Telegram    |
| `DISCORD_BOT_TOKEN`   | Discord     |
| `SLACK_BOT_TOKEN`     | Slack       |

All tokens are read from the environment at runtime. In mock mode (no tokens), all operations simulate success and log to stdout.
