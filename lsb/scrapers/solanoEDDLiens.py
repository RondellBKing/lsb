import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import re
import drivers
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
# import pygsheets
from datetime import date
from datetime import timedelta
import helper
from send_email import send_mail
import os


def getSolanoEDDLiens():
    day_delta = timedelta(days=5)
    today = date.today()
    prev_day = today - day_delta

    today_str = today.strftime("%m/%d/%Y")
    prev_day_str = prev_day.strftime("%m/%d/%Y")

    file_date = today_str.replace('/', '')
    filename = f"solano_{file_date}.csv"

    # START SCRAPING #
    browser = drivers.create_driver('http://recorderonline.solanocounty.com')

    time.sleep(1)

    # Hit Agree
    browser.find_element_by_id('ctl00_m_g_c6431b47_3ecb_4f66_9e13_f949e2ea5ca6_ctl00_btnAgree').click()
    time.sleep(1)

    # Show advanced search options
    browser.find_element_by_id('ctl00_m_g_53ad86ef_2077_49cd_915b_11a033357719_ctl00_btnShowAdvanced').click()
    time.sleep(1)

    # Enter Start Date
    WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.ID, "ctl00_m_g_53ad86ef_2077_49cd_915b_11a033357719_ctl00_txtDocumentDateFrom"))).clear()
    WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.ID, "ctl00_m_g_53ad86ef_2077_49cd_915b_11a033357719_ctl00_txtDocumentDateFrom"))).send_keys(prev_day_str)

    browser.find_element_by_css_selector('#dk_container_ctl00_m_g_53ad86ef_2077_49cd_915b_11a033357719_ctl00_'
                                         'drpFilingCode > a > span.dk_label').click()
    time.sleep(1)

    # lien - Federal tax lien
    browser.find_element_by_xpath('//*[@id="dk_container_ctl00_m_g_53ad86ef_2077_'
                                  '49cd_915b_11a033357719_ctl00_drpFilingCode"]'
                                  '/div[1]/ul/li[723]/a').click()
    time.sleep(1)

    browser.find_element_by_css_selector('#ctl00_m_g_53ad86ef_2077_49cd_915b_11a033357719_ctl00_btnAdvancedSearch').click()
    time.sleep(1)

    # per page drop down
    try:
        browser.find_element_by_xpath('//*[@id="dk_container_ctl00_PlaceHolderMain_ucSearchResults_drpResultsPerPage"]/div[1]/ul/li[5]/a').click()
        time.sleep(1)
    except Exception:
        pass

    html = browser.execute_script('return document.documentElement.outerHTML')
    sel_soup = BeautifulSoup(html, 'html.parser')
    liens = sel_soup.select('tbody > tr')  # select only the search results

    # Extract Table and write out the results
    # Todo move to central file
    header = ['Taxpayer', 'Recorded', 'State', 'County']  # File header name
    lead_list = []

    if liens:  # Scrape Page for lead results
        list_iterator = iter(liens)

        count = 0
        for row in list_iterator:
            try:
                lead = row.findChildren(['td'])[3].text.split('(E)')[0]
                lead = lead.replace('\n', "")
                lead = lead.strip()
                lead_list.append({header[0]: lead, header[1]: 'LSB', header[2]: 'CA', header[3]: 'Solano'})
            except IndexError:  # Skip empty rows
                pass

    if lead_list:
        print(f"Done scraping page, creating {filename} now")
        # Write csv and upload to google drive
        helper.write_csv(filename, header, lead_list)
        drivers.g_drive(filename, '1TrIpVdx9JCD_hungVPweQGfcDkJDB5dh')

        lead_count = len(lead_list)
        subject = f'Solano County - {lead_count} leads found for {today_str}'
        email_message = f"See https://drive.google.com/drive/folders/1TrIpVdx9JCD_hungVPweQGfcDkJDB5dh?usp=sharing"

        send_mail("ddrummond@blueprint-tax.com", subject, email_message)
    else:
        print(f'No Results found for {today_str}')
    browser.close()
    return lead_list


if __name__ == '__main__':
    os.chdir('/Users/rondellking/PycharmProjects/Rbot/rbot')
    getSolanoEDDLiens()

