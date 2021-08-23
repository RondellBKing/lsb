from selenium import webdriver
import os


def g_drive(file_location, drive_folder_id):

    os.chdir('/Users/rondellking/PycharmProjects/Rbot/rbot')
    # Connect to google drive and upload csv.
    from pydrive.auth import GoogleAuth
    from pydrive.drive import GoogleDrive

    gauth = GoogleAuth()
    drive = GoogleDrive(gauth)

    # LSB Folder
    gfile = drive.CreateFile({'parents': [{'id': drive_folder_id}]})
    gfile.SetContentFile(file_location)

    gfile.Upload()  # Upload the file.


#def create_driver(url, options, driver_loc=''):
def create_driver(url, driver_loc=''):
    op = webdriver.ChromeOptions()
    op.add_argument('headless')

    # login_driver = webdriver.Chrome(options=options, executable_path='/Users/rondellking/PycharmProjects/chromedriver')
    login_driver = webdriver.Chrome(executable_path='/Users/rondellking/PycharmProjects/chromedriver')#, options=op)
    login_driver.get(url)
    login_driver.maximize_window()

    return login_driver
