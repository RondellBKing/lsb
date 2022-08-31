import json
import logging
from bs4 import BeautifulSoup
import pandas as pd
import time
import json
import os
import drivers

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from scraper import Scraper


class Tuscola_MI(Scraper):
    def __init__(self, start_date=None, delta=5):
        super().__init__(start_date, delta)
        self.county_name = "TUSCOLA"

    def scrape(self):
        
        f = open(f'../scraper_configs/{self.county_name}.json')
        
        site_json = json.load(f)
        bot_config = site_json.get('BOT_STEPS')
        site_link = site_json.get('SITE_LINK')

        browser = drivers.create_driver(site_link)

        try:
            for config_step in bot_config:
                action = config_step.get('ACTION')
                xpath = config_step.get('XPATH')
                logging.info(f'Executing {action} on {xpath}')
                if action == 'Click':
                    WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, xpath))).click()
                elif action == 'Iframe':
                    time.sleep(5)
                    browser.switch_to.frame(browser.find_element_by_xpath(xpath))
                elif action == 'ParentIframe':
                    browser.switch_to.parent_frame()
                elif action == 'Input':
                    text = config_step.get('TEXT')
                    if text == 'END_DATE':
                        WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, xpath))).send_keys(self.end_date)
                    elif text == 'ST_DATE':
                        WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, xpath))).send_keys(self.start_date)
                    else:
                        WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, xpath))).send_keys(text)
                
            browser.switch_to.default_content()
            browser.switch_to.frame(browser.find_element_by_name('bodyframe'))
            browser.switch_to.frame(browser.find_element_by_name('resultFrame'))
            browser.switch_to.frame(browser.find_element_by_name('resultListFrame'))

            html = BeautifulSoup(browser.page_source, 'html.parser')
        
            tbl_html = html.find('table', {'class': 'datagrid-btable'})
        except Exception as e:
            logging.info(f'Site automation failed - {e}')
            tbl_html = []

        browser.close()

        return tbl_html # List of tables for Maryland 

    def parse_table(self, tbl_html):
        lead_list = []
        rows = tbl_html.findAll("tr")

        for row in rows:
            try:
                lead = row.findChildren(['td'])[5].getText().strip()
                if lead != 'E':
                    lien_date = row.findChildren(['td'])[8].getText().strip()
                    lead_list.append([lien_date, lead, 'LSB', 'MI', self.county_name])
            except IndexError as e:  # Skip empty rows
                logging.error(f'Table parsing failed {e}')
                pass

        return lead_list


if __name__ == '__main__':
    os.chdir('/Users/rondellking/PycharmProjects/lsb/lsb/scrapers')
    Tuscola_MI(delta=5).run(send_mail=True)
