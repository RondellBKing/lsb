from selenium import webdriver
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


def g_drive(file_location, drive_folder_id):
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

    drive = GoogleDrive(gauth)

    # Upload File to LSB folder
    gfile = drive.CreateFile({'parents': [{'id': drive_folder_id}]})
    gfile['title'] = file_location.split('/')[-1]
    gfile.SetContentFile(file_location)

    gfile.Upload()


def create_driver(url, driver_loc=''):
    op = webdriver.ChromeOptions()
    op.add_argument('headless')

    login_driver = webdriver.Chrome(executable_path='/Users/rondellking/PycharmProjects/chromedriver')
    login_driver.get(url)
    login_driver.maximize_window()

    return login_driver
