"""Google Calendar integration."""
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

class GoogleCalendar:
    def __init__(self, credentials_path: str = ""):
        self.creds_path = credentials_path or os.getenv("GOOGLE_CREDS_PATH", "credentials.json")

    def _get_service(self):
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            creds = Credentials.from_authorized_user_file(self.creds_path)
            return build("calendar", "v3", credentials=creds)
        except Exception as e:
            raise RuntimeError(f"Google auth failed: {e}")

    def list_events(self, days: int = 7) -> List[Dict]:
        svc = self._get_service()
        now = datetime.utcnow().isoformat() + "Z"
        end = (datetime.utcnow() + timedelta(days=days)).isoformat() + "Z"
        result = svc.events().list(calendarId="primary", timeMin=now, timeMax=end, singleEvents=True, orderBy="startTime").execute()
        return result.get("items", [])

    def create_event(self, title: str, start: str, end: str, description: str = "") -> Dict[str, Any]:
        svc = self._get_service()
        event = {"summary": title, "description": description, "start": {"dateTime": start}, "end": {"dateTime": end}}
        return svc.events().insert(calendarId="primary", body=event).execute()
