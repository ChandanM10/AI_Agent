from __future__ import annotations
from loguru import logger
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os, pickle

YOUTUBE_SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

class YouTubeUploader:
    def __init__(self, client_secrets: str, token_path: str):
        self.client_secrets = client_secrets
        self.token_path = token_path
        self.creds = None

    def _auth(self):
        if os.path.exists(self.token_path):
            with open(self.token_path,'rb') as token:
                self.creds = pickle.load(token)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.client_secrets, YOUTUBE_SCOPES)
                self.creds = flow.run_local_server(port=0)
            with open(self.token_path,'wb') as token:
                pickle.dump(self.creds, token)
        return build('youtube','v3', credentials=self.creds)

    def upload(self, video_path: str, title: str, description: str, tags: list[str], schedule_iso: str | None = None) -> dict:
        youtube = self._auth()
        body = {
            'snippet': {
                'title': title[:100],
                'description': description,
                'tags': [t.replace('#','') for t in tags],
                'categoryId': '22'
            },
            'status': {
                'privacyStatus': 'private' if schedule_iso else 'public'
            }
        }
        if schedule_iso:
            body['status']['publishAt'] = schedule_iso
            body['status']['privacyStatus'] = 'private'
            body['status']['selfDeclaredMadeForKids'] = False
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        request = youtube.videos().insert(part=','.join(body.keys()), body=body, media_body=media)
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                logger.info(f"Upload progress: {int(status.progress()*100)}%")
        logger.info(f"Uploaded video id: {response.get('id')}")
        return response
