# See https://developers.google.com/identity
# Generete credentials.json based on client_secrets.json
# https://console.cloud.google.com/apis/credentials?project=lsb-rbot

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pathlib import Path

import os

def create_g_auth():
    # # Try to load saved client credentials
    gauth = GoogleAuth()

    parent_dir = os.fspath(Path(__file__).resolve().parents[1].resolve()) # Relative to point of execution
    # secret_loc = os.path.join(parent_dir, 'local', 'credentials.json')

    # # don't start path with '/', as this causes it to look relative to the root folder    
    client_json_path = os.path.join(parent_dir, 'local', 'client_secrets.json')
    credentials_json_path = os.path.join(parent_dir, 'credentials.json')
    GoogleAuth.DEFAULT_SETTINGS['client_config_file'] = client_json_path

    # print(secret_loc)
    gauth.LoadCredentialsFile(credentials_json_path)

    if gauth.credentials is None:
        # Authenticate if credentials are missing
        gauth.GetFlow()
        gauth.flow.params.update({'access_type': 'offline'})
        gauth.flow.params.update({'approval_prompt': 'force'})

        gauth.LocalWebserverAuth()

    elif gauth.access_token_expired:
        # Refresh them if expired
        gauth.Refresh()
    else:
        # Initialize the saved creds
        gauth.Authorize()

    # Save the current credentials to a file
    gauth.SaveCredentialsFile("credentials.json")

    return GoogleDrive(gauth)

if __name__ == '__main__':
    # For Testing 
    drive = create_g_auth()
    gfile = drive.CreateFile({'parents': [{'id': '1TrIpVdx9JCD_hungVPweQGfcDkJDB5dh'}]})
    gfile['title'] = 'test.csv'
    gfile.SetContentFile('test.csv')

    gfile.Upload()