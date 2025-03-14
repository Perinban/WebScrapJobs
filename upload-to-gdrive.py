import json
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

def upload_to_drive():
    try:
        # Load service account credentials
        service_account_info = json.loads(os.getenv('GDRIVE_SERVICE_ACCOUNT_KEY'))
        credentials = service_account.Credentials.from_service_account_info(service_account_info)
        drive_service = build('drive', 'v3', credentials=credentials)

        # Get Folder ID from env variable
        folder_id = os.getenv('GDRIVE_FOLDER_ID')
        if not folder_id:
            raise ValueError("GDRIVE_FOLDER_ID environment variable is not set")

        file_name = 'job_summary.json'

        # Search for existing file in the folder
        query = f"name='{file_name}' and '{folder_id}' in parents and trashed=false"
        results = drive_service.files().list(q=query, fields="files(id)").execute()
        files = results.get('files', [])

        # Delete existing file if found
        if files:
            file_id = files[0]['id']
            drive_service.files().delete(fileId=file_id).execute()
            print(f"Deleted existing file with ID: {file_id}")

        # Upload the new file
        file_metadata = {'name': file_name, 'parents': [folder_id]}
        media = MediaFileUpload(file_name, mimetype='application/json')
        new_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

        print(f'File uploaded to Google Drive with ID: {new_file.get("id")}')

    except json.JSONDecodeError:
        print("Error: Invalid JSON in GDRIVE_SERVICE_ACCOUNT_KEY environment variable.")
    except HttpError as error:
        print(f"Google Drive API error: {error}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    upload_to_drive()