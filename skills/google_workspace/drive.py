"""Google Drive integration."""
import os
from typing import Dict, Any, List

class GoogleDrive:
    def __init__(self, credentials_path: str = ""):
        self.creds_path = credentials_path or os.getenv("GOOGLE_CREDS_PATH", "credentials.json")

    def _get_service(self):
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        creds = Credentials.from_authorized_user_file(self.creds_path)
        return build("drive", "v3", credentials=creds)

    def list_files(self, query: str = "", limit: int = 20) -> List[Dict]:
        svc = self._get_service()
        q = f"name contains '{query}'" if query else ""
        result = svc.files().list(q=q, pageSize=limit, fields="files(id,name,mimeType,size)").execute()
        return result.get("files", [])

    def upload(self, local_path: str, folder_id: str = "") -> Dict[str, Any]:
        from googleapiclient.http import MediaFileUpload
        svc = self._get_service()
        meta = {"name": os.path.basename(local_path)}
        if folder_id:
            meta["parents"] = [folder_id]
        media = MediaFileUpload(local_path)
        file = svc.files().create(body=meta, media_body=media, fields="id,name").execute()
        return file
