import os
import requests
import datetime
import time

import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request


CLIENT_SECRET_FILE = "secrets\client_secret_410744381950-lqd7vj2nn2itp5shc9646d6h9hfrbtoo.apps.googleusercontent.com.json"
API_NAME = "photoslibrary"
API_VERSION = "v1"
SCOPES = ["https://www.googleapis.com/auth/photoslibrary"]

END_TIME = datetime.datetime(2020,9,19,18,30)

def create_service(client_secret_file, api_name, api_version, *scopes):
    print(client_secret_file, api_name, api_version, scopes, sep='-')
    CLIENT_SECRET_FILE = client_secret_file
    API_SERVICE_NAME = api_name
    API_VERSION = api_version
    SCOPES = [scope for scope in scopes[0]]
    print(SCOPES)

    cred = None

    pickle_file = f'token_{API_SERVICE_NAME}_{API_VERSION}.pickle'
    # print(pickle_file)

    if os.path.exists(pickle_file):
        with open(pickle_file, 'rb') as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            cred = flow.run_local_server()

        with open(pickle_file, 'wb') as token:
            pickle.dump(cred, token)

    try:
        service = build(API_SERVICE_NAME, API_VERSION, credentials=cred)
        print(API_SERVICE_NAME, 'service created successfully')
        return service
    except Exception as e:
        print('Unable to connect.')
        print(e)
        return None


def get_files_metadata(service):

    pictures = service.mediaItems().list().execute()
    picture_list = pictures.get("mediaItems")

    return picture_list


def download_file(url, destination_folder, file_name):

    response = requests.get(url)
    if response.status_code == 200:
        print('Downloading file {0}'.format(file_name))
        with open(os.path.join(destination_folder, file_name), 'wb') as f:
            f.write(response.content)
            f.close()

if __name__ == "__main__":

    service = create_service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    downloaded_files = set(os.listdir("pictures"))

    while datetime.datetime.now() < END_TIME:

        pictures = get_files_metadata(service)
        for picture in pictures:

            if picture["filename"] not in downloaded_files:
                download_file(picture["baseUrl"], "pictures", picture["filename"])
                downloaded_files.add(picture["filename"])

        time.sleep(30)
