import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from skills.comms.messenger import Messenger


class TestMessengerMockMode(unittest.TestCase):
    """All tests run in mock mode (no real API tokens)."""

    def setUp(self):
        # Ensure no real tokens are set
        for key in ["SMTP_HOST", "TELEGRAM_BOT_TOKEN", "DISCORD_BOT_TOKEN", "SLACK_BOT_TOKEN"]:
            os.environ.pop(key, None)
        self.m = Messenger()

    def test_all_channels_in_mock_mode(self):
        for ch in Messenger.SUPPORTED_CHANNELS:
            self.assertTrue(self.m._mock[ch], f"{ch} should be in mock mode")

    def test_send_email_mock(self):
        result = self.m.send(channel="email", to="test@example.com", body="Hello", subject="Test")
        self.assertEqual(result["status"], "sent_mock")
        self.assertEqual(result["channel"], "email")

    def test_send_telegram_mock(self):
        result = self.m.send(channel="telegram", to="12345", body="Hello Telegram")
        self.assertEqual(result["status"], "sent_mock")

    def test_send_discord_mock(self):
        result = self.m.send(channel="discord", to="999", body="Hello Discord")
        self.assertEqual(result["status"], "sent_mock")

    def test_send_slack_mock(self):
        result = self.m.send(channel="slack", to="#general", body="Hello Slack")
        self.assertEqual(result["status"], "sent_mock")

    def test_unsupported_channel(self):
        result = self.m.send(channel="fax", to="1234", body="Hello Fax")
        self.assertIn("error", result)

    def test_fetch_emails_mock(self):
        emails = self.m.fetch_emails()
        self.assertEqual(len(emails), 1)
        self.assertEqual(emails[0]["from"], "mock@example.com")

    def test_listen_mock(self):
        msgs = list(self.m.listen(channel="telegram"))
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0]["author"], "mock_user")


if __name__ == "__main__":
    unittest.main()
