from typing import TextIO


import csv
import logging
import time
import re
import os
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException


def king_county():
    os.chdir('/Users/rondellking/PycharmProjects/lsb/lsb/scrapers')
    import drivers
    import helper
    from send_email import send_mail
    import sys

    # Selenium packages used to simulate web experience
    from selenium.webdriver.common.by import By

    from selenium.webdriver.support.ui import WebDriverWait
    from selenium import webdriver
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.keys import Keys
    from datetime import date
    from selenium.webdriver.common.action_chains import ActionChains

    today = date.today()
    today_str = today.strftime("%m/%d/%Y")

    file_date = today_str.replace('/', '')
    lead_date = today_str.replace('/', '.')
    filename = f"king_county_{file_date}.csv"

    # Options used to attempt to scrape site with element not interactable exception:w
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_argument("--disable-extensions")

    # Testing Move to own file
    page_url = 'https://recordsearch.kingcounty.gov/LandmarkWeb/search/index?theme=.blue&section=searchCriteriaLegal&quickSearchSelection='
    driver = drivers.create_driver(page_url, options)

    # Fill out dates
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "searchCriteriaDocuments-tab"))).click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "documentType-DocumentType"))).send_keys('FTL')
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "beginYesterday-DocumentType"))).click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "submit-DocumentType"))).click()

    time.sleep(10)
    html = driver.page_source
    ''' Make Above Separate Function'''

    soup = BeautifulSoup(html, 'html.parser')
    main_table = soup.find('table', id="resultsTable")

    lead_list = []

    # Todo move to central file
    header = ['Taxpayer', 'Recorded', 'State', 'County']  # File header name

    if main_table:  # Scrape Page for lead results
        rows = main_table.findChildren(['tr'])

        list_iterator = iter(rows)
        next(list_iterator)  # First row is empty so skip it

        count = 0
        for row in list_iterator:
            if count == 0:
                count += 1
                continue

            try:
                lead = row.findChildren(['td'])[5].text
                lead_list.append({header[0]: lead, header[1]: 'LSB', header[2]: 'WA', header[3]: 'King'})
            except IndexError:  # Skip empty rows
                pass

    if lead_list:
        logging.info("Done scraping page, creating {filename} now")
        print("Done scraping page, creating {filename} now")
        # Write csv and upload to google drive
        helper.write_csv(filename, header, lead_list)
        drivers.g_drive(filename, '1TrIpVdx9JCD_hungVPweQGfcDkJDB5dh')

        lead_count = len(lead_list)
        subject = f'King County - {lead_count} leads found for {today_str}'
        email_message = f"See https://drive.google.com/drive/folders/1TrIpVdx9JCD_hungVPweQGfcDkJDB5dh?usp=sharing"

        send_mail("ddrummond@blueprint-tax.com", subject, email_message)
    else:
        logging.info(f'No Results found for {today_str}')
        print(f'No Results found for {today_str}')
    driver.close()


if __name__ == "__main__":
    os.chdir('/Users/rondellking/PycharmProjects/lsb/lsb/scrapers')
    king_county()
