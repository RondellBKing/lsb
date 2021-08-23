from typing import TextIO


import csv
import logging
import time

from bs4 import BeautifulSoup
import os
from selenium.common.exceptions import NoSuchElementException


if __name__ == "__main__":
    os.chdir('/Users/rondellking/PycharmProjects/Rbot/rbot')
    from send_email import send_mail
    import drivers
    import helper
    import sys

    # Selenium packages used to simulate web experience
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from datetime import date
    from datetime import timedelta

    # Get Previous 5 days in pull
    # Todo Move to helper.py
    # Todo Create a class to organize the scrapers

    day_delta = timedelta(days=5)
    today = date.today()
    prev_day = today - day_delta

    today_str = today.strftime("%m/%d/%Y")
    prev_day_str = prev_day.strftime("%m/%d/%Y")

    file_date = today_str.replace('/', '')
    filename = f"harris_county_{file_date}.csv"

    # Testing Move to own file
    driver = drivers.create_driver('https://www.cclerk.hctx.net/applications/websearch/RP.aspx')

    # Fill out dates
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "ctl00$ContentPlaceHolder1$txtInstrument"))).send_keys('T/L')
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "ctl00$ContentPlaceHolder1$txtFrom"))).send_keys(prev_day_str)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "ctl00$ContentPlaceHolder1$txtTo"))).send_keys(today_str)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "ctl00$ContentPlaceHolder1$btnSearch"))).click()
    #
    time.sleep(10)
    html = driver.page_source
    ''' Make Above Separate Function'''

    #
    soup = BeautifulSoup(html, 'html.parser')
    main_table = soup.find('table', id="itemPlaceholderContainer")

    lead_list = []

    # Todo move to central file
    # Todo add data to feed
    header = ['Taxpayer', 'Recorded', 'State', 'County']  # File header name

    if main_table:  # Scrape Page for lead results
        rows = main_table.findChildren(['tr'])

        list_iterator = iter(rows)
        next(list_iterator)  # First row is empty so skip it

        for row in list_iterator:
            try:
                lien_name_rows = row.findChildren(['td'])[4].findChildren(['tr'])

                for lien_name_row in lien_name_rows:
                    row_list = lien_name_row.findChildren(['td'])
                    if row_list:
                        lead = row_list[1].findChildren('span')[0].text
                        if lead == 'INTERNAL REVENUE SERVICE':
                            continue
                        lead_list.append({header[0]: lead, header[1]: 'LSB', header[2]: 'TX', header[3]: 'Harris'})
            except IndexError:  # Skip empty rows
                pass
    driver.close()
    if lead_list:
        logging.info("Done scraping page, creating {filename} now")

        # Write csv and upload to google drive
        helper.write_csv(filename, header, lead_list)
        drivers.g_drive(filename, '1TrIpVdx9JCD_hungVPweQGfcDkJDB5dh')

        lead_count = len(lead_list)
        subject = f'Harris County - {lead_count} leads found for {today_str}'
        email_message = f"See https://drive.google.com/drive/folders/1TrIpVdx9JCD_hungVPweQGfcDkJDB5dh?usp=sharing"

        send_mail("ddrummond@blueprint-tax.com", subject, email_message)

    else:
        logging.info(f'No Results found for {today_str}')
        print(f'No Results found for {today_str}')
