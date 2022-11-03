import os
import io
from googleapiclient.http import MediaIoBaseDownload
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
import zipfile


def authenticate_with_google():
    """
    We need to authenticate with the service account
    before we do anything.

    """
    scope = ['https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('service_account.json', scope)
    service = build('drive', 'v3', credentials=credentials)

    return service


def get_id_of_file(service, querystring):
    """
    This gets the id of the file we want,
    identified by the querystring (file name).
    
    We need the id so we can download it.
    
    """
    files = []
    page_token = None
        # pylint: disable=maybe-no-member
    response = service.files().list(q=querystring,
                                    spaces='drive',
                                    fields='nextPageToken, '
                                            'files(id, name)',
                                    pageToken=page_token).execute()

    for file in response.get('files', []):
        print(f'Found file: {file.get("name")}, {file.get("id")}')
        file_id = file["id"]
    
    return file_id


def download_zip_file_from_google_drive(service, file_id, file_name):
    """
    This takes the fild_id so it knows which file to download
    and the file_name so it knows what to call the downloaded
    file.

    Then it downloads it.
    
    """
    request = service.files().get_media(fileId=file_id)

    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fd=fh, request=request)

    done = False

    while not done:
        status, done = downloader.next_chunk()
        print("Download Progress {0}".format(status.progress() * 100))

    fh.seek(0)

    with open(os.path.join('', file_name  ), 'wb') as f:
        f.write(fh.read())
        f.close()
    
    return("file_name")


def unzip_files(zip_file_name):
    """
    This takes a zip file name and then
    unzips all the files in it and dumps them
    in a folder called unzipped_invoices.

    If the folder doesn't exist, it'll create it.
    
    """
    with zipfile.ZipFile(zip_file_name, 'r') as zip_ref:
        zip_ref.extractall("unzipped_invoices")
