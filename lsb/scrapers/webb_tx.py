from bs4 import BeautifulSoup
import time
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import drivers
from helper import is_date
from scraper import Scraper


class WebbTx(Scraper):
    def __init__(self, start_date=None, delta=5):
        super().__init__(start_date, delta)
        self.county_name = "webb_tx"

    def scrape(self):
        browser = drivers.create_driver('https://countyfusion13.kofiletech.us/countyweb/loginDisplay.action?countyname=WebbTX') 
        
        # Click Input Button
        WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="maindiv"]/table[2]/tbody/tr[1]/td[2]/table/tbody/tr/td/input'))).click()
        browser.switch_to.frame(browser.find_element_by_xpath('//*[@id="corediv"]/iframe')) # Parent frame on popup screen
        WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="accept"]'))).click() #Close pop-up
        WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="dialogheader"]/table/tbody/tr/td[2]/a/img'))).click()
        
        time.sleep(5)
        browser.switch_to.frame(browser.find_element_by_xpath('//*[@id="corediv"]/iframe')) # Parent Frame

        WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="datagrid-row-r1-2-0"]/td/div'))).click() # Click Search Records
        
        # Fill in side parameters
        browser.switch_to.frame(browser.find_element_by_xpath('//*[@id="dynSearchFrame"]')) # Parent Frame
        WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_easyui_tree_17"]/span[3]'))).click() # Uncheck All
        WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_easyui_tree_24"]/span[2]'))).click() # Expand Fed Lien
        WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_easyui_tree_33"]/span[5]'))).click() # Click Federal Tax Lien
        WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_easyui_tree_34"]/span[5]'))).click() # Click Federal Tax Lien

        # Enter Dates
        browser.switch_to.frame(browser.find_element_by_xpath('//*[@id="criteriaframe"]'))
        WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="elemDateRange"]/table/tbody/tr/td[2]/table/tbody/tr/td[1]/span/input[1]'))).send_keys(self.end_date)
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="elemDateRange"]/table/tbody/tr/td[2]/table/tbody/tr/td[3]/span/input[1]'))).send_keys(self.start_date)
        
        browser.switch_to.parent_frame()

        # Click Search Button
        WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="imgSearch"]'))).click()

        # Additional iframe code
        browser.switch_to.default_content()
        browser.switch_to.frame(browser.find_element_by_name('bodyframe'))
        browser.switch_to.frame(browser.find_element_by_name('resultFrame'))
        browser.switch_to.frame(browser.find_element_by_name('resultListFrame'))

        html = BeautifulSoup(browser.page_source, 'html.parser')

        browser.close()

        return html 

    def parse_table(self, tbl_html):
        lead_list = []
        rows = tbl_html.findAll("tr")

        list_iterator = iter(rows)
        next(list_iterator)  # First row is empty so skip it

        for row in list_iterator:
            try:
                lead = row.findChildren(['td'])[10].getText().strip()
                
                if is_date(lead): # Temp fix for duplicate rows storing date in different order
                    continue
                lien_date = row.findChildren(['td'])[11].getText().strip()
                
                lead_list.append([lien_date, lead, 'LSB', 'TX', self.county_name])
                # print(f"{lead} - {lien_date}")
            except IndexError:  # Skip empty rows
                pass

        return lead_list


if __name__ == '__main__':
    os.chdir('/Users/rondellking/PycharmProjects/lsb/lsb/scrapers')
    WebbTx(delta=10).run(send_mail=True)
