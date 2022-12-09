from selenium import webdriver
from pathlib import Path
from pymongo import MongoClient
import os
from g_auth import create_g_auth

#See https://developers.google.com/identity
# 720-835-2283 - 
def g_drive(file_location, drive_folder_id):
    drive = create_g_auth()

    # Upload File to LSB folder
    gfile = drive.CreateFile({'parents': [{'id': drive_folder_id}]})
    gfile['title'] = file_location.split('/')[-1]
    gfile.SetContentFile(file_location)

    gfile.Upload()

def create_driver(url):
    op = webdriver.ChromeOptions()
    op.add_argument('headless')

    # Chrome driver should be stored one level above the scrapers driver
    path = os.fspath(Path(__file__).resolve().parents[3].resolve())
    chrome_driver_exe = os.path.join(path,'chromedriver')
    login_driver = webdriver.Chrome(executable_path=chrome_driver_exe) # '/Users/rondellbking/Desktop/Things/lsb'
    # login_driver = webdriver.Chrome(executable_path='/Users/rondellbking/Desktop/Things/chromedriver')

    login_driver.get(url)
    login_driver.maximize_window()

    return login_driver

# Todo Create seperate class for mongo connection and helper functions
def create_mongo_connection():
    uri = "mongodb+srv://lsb.lkcja.mongodb.net/myFirstDatabase?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
    client = MongoClient(uri,
                        tls=True,
                        tlsCertificateKeyFile='/Users/rondellking/PycharmProjects/lsb/lsb/X509-cert-7132846088829326577.pem') # Todo use relative directory
    return client
