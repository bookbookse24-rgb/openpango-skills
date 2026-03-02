#!/usr/bin/env python3
"""
messenger.py - Unified Communication Core for OpenPango Agents.

Provides a single interface for agents to send/receive messages across
Email (SMTP/IMAP), Telegram, Discord, and Slack. Falls back to mock mode
when API tokens are not set.
"""

import os
import json
import smtplib
import imaplib
import email
import logging
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Generator, Any
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(name)s] %(levelname)s: %(message)s')
logger = logging.getLogger("Messenger")


class Messenger:
    """Unified messaging interface for all communication channels."""

    SUPPORTED_CHANNELS = ("email", "telegram", "discord", "slack")

    def __init__(self):
        self._config = {
            "email": {
                "smtp_host": os.getenv("SMTP_HOST", ""),
                "smtp_port": int(os.getenv("SMTP_PORT", "587")),
                "smtp_user": os.getenv("SMTP_USER", ""),
                "smtp_pass": os.getenv("SMTP_PASS", ""),
                "imap_host": os.getenv("IMAP_HOST", ""),
                "imap_user": os.getenv("IMAP_USER", os.getenv("SMTP_USER", "")),
                "imap_pass": os.getenv("IMAP_PASS", os.getenv("SMTP_PASS", "")),
            },
            "telegram": {
                "bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
            },
            "discord": {
                "bot_token": os.getenv("DISCORD_BOT_TOKEN", ""),
            },
            "slack": {
                "bot_token": os.getenv("SLACK_BOT_TOKEN", ""),
            },
        }
        self._mock = {}
        for ch in self.SUPPORTED_CHANNELS:
            # A channel is in mock mode if its primary credential is empty
            primary_key = list(self._config[ch].keys())[0]
            is_mock = not bool(self._config[ch][primary_key])
            self._mock[ch] = is_mock
            if is_mock:
                logger.warning(f"[{ch.upper()}] No credentials found. Running in MOCK mode.")

    # ─── SEND ────────────────────────────────────────────────

    def send(self, channel: str, to: str, body: str, subject: str = "", **kwargs) -> Dict[str, Any]:
        """Send a message on a given channel."""
        if channel not in self.SUPPORTED_CHANNELS:
            return {"error": f"Unsupported channel: {channel}"}

        if self._mock[channel]:
            return self._mock_send(channel, to, body, subject)

        dispatch = {
            "email": self._send_email,
            "telegram": self._send_telegram,
            "discord": self._send_discord,
            "slack": self._send_slack,
        }
        return dispatch[channel](to, body, subject, **kwargs)

    def _mock_send(self, channel: str, to: str, body: str, subject: str) -> Dict[str, Any]:
        logger.info(f"[MOCK {channel.upper()}] → To: {to} | Subject: {subject} | Body: {body[:80]}...")
        return {
            "status": "sent_mock",
            "channel": channel,
            "to": to,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ─── EMAIL ───────────────────────────────────────────────

    def _send_email(self, to: str, body: str, subject: str = "", **kwargs) -> Dict:
        cfg = self._config["email"]
        msg = MIMEMultipart()
        msg["From"] = cfg["smtp_user"]
        msg["To"] = to
        msg["Subject"] = subject or "OpenPango Agent Notification"
        msg.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP(cfg["smtp_host"], cfg["smtp_port"]) as server:
                server.starttls()
                server.login(cfg["smtp_user"], cfg["smtp_pass"])
                server.sendmail(cfg["smtp_user"], to, msg.as_string())
            return {"status": "sent", "channel": "email", "to": to}
        except Exception as e:
            logger.error(f"Email send failed: {e}")
            return {"error": str(e)}

    def fetch_emails(self, folder: str = "INBOX", limit: int = 5) -> List[Dict]:
        """Fetch recent emails via IMAP."""
        cfg = self._config["email"]
        if self._mock["email"]:
            logger.info("[MOCK EMAIL] Fetching inbox...")
            return [{"from": "mock@example.com", "subject": "Test", "body": "Mock email body", "date": datetime.now(timezone.utc).isoformat()}]

        try:
            mail = imaplib.IMAP4_SSL(cfg["imap_host"])
            mail.login(cfg["imap_user"], cfg["imap_pass"])
            mail.select(folder)
            _, data = mail.search(None, "ALL")
            ids = data[0].split()
            results = []
            for eid in ids[-limit:]:
                _, msg_data = mail.fetch(eid, "(RFC822)")
                raw = email.message_from_bytes(msg_data[0][1])
                results.append({
                    "from": raw["From"],
                    "subject": raw["Subject"],
                    "date": raw["Date"],
                    "body": raw.get_payload(decode=True).decode("utf-8", errors="ignore")[:500] if not raw.is_multipart() else "[multipart]",
                })
            mail.logout()
            return results
        except Exception as e:
            logger.error(f"IMAP fetch failed: {e}")
            return [{"error": str(e)}]

    # ─── TELEGRAM ────────────────────────────────────────────

    def _send_telegram(self, to: str, body: str, subject: str = "", **kwargs) -> Dict:
        """Send a Telegram message via Bot API."""
        import urllib.request
        token = self._config["telegram"]["bot_token"]
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = json.dumps({"chat_id": to, "text": body, "parse_mode": "Markdown"}).encode()
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            logger.error(f"Telegram send failed: {e}")
            return {"error": str(e)}

    # ─── DISCORD ─────────────────────────────────────────────

    def _send_discord(self, to: str, body: str, subject: str = "", **kwargs) -> Dict:
        """Send a Discord message to a channel via REST API. `to` is a channel ID."""
        import urllib.request
        token = self._config["discord"]["bot_token"]
        url = f"https://discord.com/api/v10/channels/{to}/messages"
        payload = json.dumps({"content": body}).encode()
        req = urllib.request.Request(url, data=payload, headers={
            "Content-Type": "application/json",
            "Authorization": f"Bot {token}",
        })
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            logger.error(f"Discord send failed: {e}")
            return {"error": str(e)}

    # ─── SLACK ───────────────────────────────────────────────

    def _send_slack(self, to: str, body: str, subject: str = "", **kwargs) -> Dict:
        """Send a Slack message to a channel via chat.postMessage. `to` is a channel ID."""
        import urllib.request
        token = self._config["slack"]["bot_token"]
        url = "https://slack.com/api/chat.postMessage"
        payload = json.dumps({"channel": to, "text": body}).encode()
        req = urllib.request.Request(url, data=payload, headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        })
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            logger.error(f"Slack send failed: {e}")
            return {"error": str(e)}

    # ─── LISTEN (Daemon) ────────────────────────────────────

    def listen(self, channel: str, poll_interval: float = 5.0) -> Generator[Dict, None, None]:
        """
        Generator that yields incoming messages for a channel.
        In mock mode, yields a test message then stops.
        """
        if channel not in self.SUPPORTED_CHANNELS:
            yield {"error": f"Unsupported channel: {channel}"}
            return

        if self._mock[channel]:
            logger.info(f"[MOCK {channel.upper()}] Listening for messages...")
            yield {
                "channel": channel,
                "author": "mock_user",
                "content": "Hello from mock listener!",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            return

        # Real listening implementations would use long-poll or websocket here
        logger.info(f"[{channel.upper()}] Starting listener daemon (poll={poll_interval}s)...")
        while True:
            # Placeholder for real polling logic
            time.sleep(poll_interval)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="OpenPango Communication Core")
    sub = parser.add_subparsers(dest="cmd", required=True)

    send_p = sub.add_parser("send")
    send_p.add_argument("--channel", required=True, choices=Messenger.SUPPORTED_CHANNELS)
    send_p.add_argument("--to", required=True)
    send_p.add_argument("--body", required=True)
    send_p.add_argument("--subject", default="")

    fetch_p = sub.add_parser("fetch-email")
    fetch_p.add_argument("--folder", default="INBOX")
    fetch_p.add_argument("--limit", type=int, default=5)

    listen_p = sub.add_parser("listen")
    listen_p.add_argument("--channel", required=True, choices=Messenger.SUPPORTED_CHANNELS)

    args = parser.parse_args()
    m = Messenger()

    if args.cmd == "send":
        result = m.send(channel=args.channel, to=args.to, body=args.body, subject=args.subject)
        print(json.dumps(result, indent=2))
    elif args.cmd == "fetch-email":
        emails = m.fetch_emails(folder=args.folder, limit=args.limit)
        print(json.dumps(emails, indent=2))
    elif args.cmd == "listen":
        for msg in m.listen(channel=args.channel):
            print(json.dumps(msg, indent=2))
