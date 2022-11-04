import logging
import time
import os

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import drivers
from scraper import Scraper


class FranklinOh(Scraper):
    def __init__(self, start_date=None, delta=5):
        super().__init__(start_date, delta)
        self.county_name = "franklin_oh"

    def scrape(self):
        browser = drivers.create_driver('https://countyfusion5.kofiletech.us/countyweb/loginDisplay.action?countyname=Franklin') 
        try:
            # Click Input Button
            WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="maindiv"]/table[2]/tbody/tr[1]/td[2]/table/tbody/tr/td/input'))).click()
            WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="dialogheader"]/table/tbody/tr/td[2]/a/img'))).click() #Close pop-up
            
            browser.switch_to.frame(browser.find_element_by_xpath('//*[@id="corediv"]/iframe')) # Parent Frame
            time.sleep(2)
            browser.switch_to.frame(browser.find_element_by_xpath('//*[@id="dynSearchFrame"]')) # Frame that holds side selections

            WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_easyui_tree_17"]/span[4]'))).click() # All document Types
            WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_easyui_tree_21"]'))).click() # Federal Tax Lien

            # Enter Dates
            browser.switch_to.frame(browser.find_element_by_xpath('//*[@id="criteriaframe"]'))
            WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="elemDateRange"]/table/tbody/tr/td[2]/table/tbody/tr/td[1]/span/input[1]'))).send_keys(self.end_date)
            WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="elemDateRange"]/table/tbody/tr/td[2]/table/tbody/tr/td[3]/span/input[1]'))).send_keys(self.start_date)
            
            browser.switch_to.parent_frame()

            # Click Search Button
            WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="imgSearch"]'))).click()

            browser.switch_to.default_content()
            browser.switch_to.frame(browser.find_element_by_name('bodyframe'))
            browser.switch_to.frame(browser.find_element_by_name('resultFrame'))
            browser.switch_to.frame(browser.find_element_by_name('resultListFrame'))
            html = BeautifulSoup(browser.page_source, 'html.parser')
            
            tbl_html = html.find('table', {'class': 'datagrid-btable'})
        except Exception as e:
            logging.error('Failed to automate website, no results returned')
            tbl_html = []

        browser.close()

        return tbl_html

    def parse_table(self, tbl_html):
        lead_list = []
        rows = tbl_html.findAll("tr")

        for row in rows:
            try:
                lead = row.findChildren(['td'])[6].getText().strip()
                if lead != 'E':
                    lien_date = row.findChildren(['td'])[10].getText().strip()
                    lead_list.append([lien_date, lead, 'LSB', 'OH', self.county_name])
            except IndexError:  # Skip empty rows
                pass

        return lead_list


if __name__ == '__main__':
    FranklinOh(delta=5).run(send_mail=True)
