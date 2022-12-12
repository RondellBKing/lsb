from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import core.drivers as drivers
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from core.scraper import Scraper


class CostaCa(Scraper):
    def __init__(self, start_date=None, delta=5):
        super().__init__(start_date, delta)
        self.county_name = "costa"

    def scrape(self):
        browser = drivers.create_driver('https://crsecurepayment.com/RW/?ln=en') # By Pass document type search
        
        # Click Fed Tax Lien
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="tabs-nohdr"]/ul/li[2]/a'))).click()
        # Click Notice of Fed Lien
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="tblDocTypesChk"]/tbody/tr[278]/td[2]'))).click()
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="MainContent_MainMenu1_SearchByDocType1_FromDate"]'))).send_keys(self.end_date)
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="MainContent_MainMenu1_SearchByDocType1_ToDate"]'))).send_keys(self.start_date)
        
        
        # Click Search Button
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="MainContent_MainMenu1_SearchByDocType1_btnSearch"]'))).click()
        
        time.sleep(5)

        html = browser.page_source
        tbl_html = BeautifulSoup(html, 'html.parser').find_all('td', id="docTypeGrtGrtee")

        browser.close()

        return tbl_html

    def parse_table(self, tbl_html):

        lead_list = []
        
        try:
            for row in tbl_html:
                lead_names = []

                for i in row.find_all('p'):
                    lead = i.text.strip()

                    # Ignore Fed Lien Lien and IRS
                    if lead not in ['NOTICE FED LIEN', 'INTERNAL REVENUE SERVICE']:
                        lead_names.append(lead)

                combined_lead_names = '|'.join(lead_names)
                lead_list.append(['-', combined_lead_names, 'LSB', 'CA', 'Orange'])
        except Exception as e:
            pass

        return lead_list
