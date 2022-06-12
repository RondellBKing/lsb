#See https://developers.google.com/identity
# 720-835-2283 - 
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

def create_g_auth():
    # # Try to load saved client credentials
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("credentials.json")

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
    drive = create_g_auth()
    gfile = drive.CreateFile({'parents': [{'id': '1TrIpVdx9JCD_hungVPweQGfcDkJDB5dh'}]})
    gfile['title'] = 'test.csv'
    gfile.SetContentFile('/Users/rondellking/PycharmProjects/lsb/lsb/scrapers/test.csv')

    gfile.Upload()