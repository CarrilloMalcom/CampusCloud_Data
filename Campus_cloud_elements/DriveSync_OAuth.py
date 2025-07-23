
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

SCOPES = ['https://www.googleapis.com/auth/drive.file']

EXCEL_FILENAME = "subjects_data.xlsx"
EXCEL_LOCAL_PATH = os.path.join("subjects_data", EXCEL_FILENAME)
DRIVE_FOLDER_ID = "13GCsXnsEmxUHmC5sM0_O1Qs3HHmQo2Xo"  

def get_authenticated_service():
    creds = None
    token_path = "token.pickle"
    credentials_path = "credentials_oauth.json"  

    if os.path.exists(token_path):
        with open(token_path, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "wb") as token:
            pickle.dump(creds, token)

    return build("drive", "v3", credentials=creds)

def upload_excel_to_drive():
    service = get_authenticated_service()
    if not os.path.exists(EXCEL_LOCAL_PATH):
        print("No existe el archivo local para subir.")
        return

    query = f"name='{EXCEL_FILENAME}' and trashed=false"
    if DRIVE_FOLDER_ID:
        query += f" and '{DRIVE_FOLDER_ID}' in parents"

    results = service.files().list(q=query, fields="files(id)").execute()
    files = results.get("files", [])

    for file in files:
        service.files().delete(fileId=file["id"]).execute()

    file_metadata = {"name": EXCEL_FILENAME}
    if DRIVE_FOLDER_ID:
        file_metadata["parents"] = [DRIVE_FOLDER_ID]

    media = MediaFileUpload(EXCEL_LOCAL_PATH, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    print("Archivo subido a Drive con ID:", file.get("id"))

def download_excel_from_drive():
    service = get_authenticated_service()

    query = f"name='{EXCEL_FILENAME}' and trashed=false"
    if DRIVE_FOLDER_ID:
        query += f" and '{DRIVE_FOLDER_ID}' in parents"

    results = service.files().list(q=query, fields="files(id)").execute()
    files = results.get("files", [])

    if not files:
        print("No se encontró el archivo en Drive.")
        return

    file_id = files[0]["id"]
    request = service.files().get_media(fileId=file_id)
    os.makedirs("subjects_data", exist_ok=True)

    with open(EXCEL_LOCAL_PATH, "wb") as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Descargando: {int(status.progress() * 100)}%")

    print("Archivo descargado exitosamente.")
