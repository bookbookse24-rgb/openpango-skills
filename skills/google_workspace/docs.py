"""Google Docs integration."""
import os
from typing import Dict, Any

class GoogleDocs:
    def __init__(self, credentials_path: str = ""):
        self.creds_path = credentials_path or os.getenv("GOOGLE_CREDS_PATH", "credentials.json")

    def _get_service(self):
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        creds = Credentials.from_authorized_user_file(self.creds_path)
        return build("docs", "v1", credentials=creds)

    def create(self, title: str) -> Dict[str, Any]:
        svc = self._get_service()
        return svc.documents().create(body={"title": title}).execute()

    def read(self, doc_id: str) -> str:
        svc = self._get_service()
        doc = svc.documents().get(documentId=doc_id).execute()
        text = ""
        for el in doc.get("body", {}).get("content", []):
            for pe in el.get("paragraph", {}).get("elements", []):
                text += pe.get("textRun", {}).get("content", "")
        return text

    def append(self, doc_id: str, text: str) -> Dict[str, Any]:
        svc = self._get_service()
        return svc.documents().batchUpdate(documentId=doc_id, body={"requests": [
            {"insertText": {"location": {"index": 1}, "text": text}}
        ]}).execute()
