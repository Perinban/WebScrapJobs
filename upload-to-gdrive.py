import json
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


def upload_to_drive():
    # Load service account credentials
    service_account_info = json.loads(os.getenv('GDRIVE_SERVICE_ACCOUNT_KEY'))
    credentials = service_account.Credentials.from_service_account_info(service_account_info)
    drive_service = build('drive', 'v3', credentials=credentials)

    # Get Folder ID from environment variable
    folder_id = os.getenv('GDRIVE_FOLDER_ID')

    # Upload the file
    file_metadata = {
        'name': 'job_summary.json',
        'parents': [folder_id]
    }
    media = MediaFileUpload('job_summary.json', mimetype='application/json')
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    print(f'File uploaded to Google Drive with ID: {file.get("id")}')


if __name__ == "__main__":
    upload_to_drive()