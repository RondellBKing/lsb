from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import drivers
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from scraper import Scraper


class OrangeFL(Scraper):
    def __init__(self, start_date=None, delta=5):
        super().__init__(start_date, delta)
        self.county_name = "orange_fl"

    def scrape(self):
        browser = drivers.create_driver('https://or.occompt.com/recorder/eagleweb/docSearch.jsp')

        # Click Disclaimer
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="middle_left"]/form/input[1]'))).click()

        # Click uncheck button
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="allTypesCB"]'))).click()
        
        time.sleep(5)

        # Click Lien
        select = Select(browser.find_element_by_name('__search_select'))
        select.select_by_visible_text('Lien')
        
        # Enter Start/End Date and filter on USA INTERNAL REVENUE
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="RecordingDateIDStart"]'))).send_keys(self.end_date)
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="RecordingDateIDEnd"]'))).send_keys(self.start_date)
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="GrantorIDSearchString"]'))).send_keys("USA INTERNAL REVENUE")
        
        # Click Search
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="searchTable"]/p[4]/input[1]'))).click()

        time.sleep(5)

        html = browser.page_source

        try:
            tbl_html_pd = pd.read_html(html, attrs = {'id': 'searchResultsTable'})
        except Exception :
            print('No Results found')
            tbl_html_pd = None

        browser.close()

        return tbl_html_pd

    def parse_table(self, tbl_html):
        tbl = tbl_html[0][['Description','Summary']]
        leads_df = tbl[tbl['Summary'].str.startswith('Grantee')]
        leads_df = leads_df['Summary'].str.split("Grantee:", n = 1, expand = True)[[1]]
        leads_df['Date'] = '-' #self.start_date
        leads_df['Type'] = 'LSB'
        leads_df['State'] = 'FL'
        leads_df['City'] = 'Orange'
        
        lead_list = leads_df[['Date',1,'Type','City','State' ]].to_numpy().tolist()

        return lead_list


if __name__ == '__main__':
    os.chdir('/Users/rondellking/PycharmProjects/lsb/lsb/scrapers')
    OrangeFL(delta=5).run(send_mail=True)
