# Base Class for the web scrapers. Web scrapers inherit this class and implement scrape + parse_table.

import logging
import os
from pathlib import Path 
import json

from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import drivers

from scraper import Scraper

# logging.basicConfig(filename='scraper.log', level=logging.INFO)
logging.basicConfig(level=logging.INFO)


class Cofile(Scraper):
    def __init__(self, start_date=None, delta=5):
        super().__init__(start_date, delta)
        self.bodyframe = True # Some sights in cofile have an extra body frame step at the end


    def scrape(self):
        """
        Parses config file and automates the site steps to prep table html.
        :return:
        """
        # Todo Move to load json function
        config_path = os.fspath(Path(__file__).resolve().parents[1].resolve()) # Relative to point of execution
        f = open(os.path.join(config_path, 'scraper_configs', f'{self.county_name}.json'))

        site_json = json.load(f)

        bot_config = site_json.get('BOT_STEPS')
        site_link = site_json.get('SITE_LINK')

        browser = drivers.create_driver(site_link)

        try:

            for config_step in bot_config:
                self.process_action(browser, config_step)
            
            if self.bodyframe:
                # Move this to seperate function
                browser.switch_to.default_content()
                browser.switch_to.frame(browser.find_element_by_name('bodyframe'))
                browser.switch_to.frame(browser.find_element_by_name('resultFrame'))
                browser.switch_to.frame(browser.find_element_by_name('resultListFrame'))

            html = BeautifulSoup(browser.page_source, 'html.parser')
            tbl_html = html.find('table', {'class': 'datagrid-btable'})

        except Exception as e:
            logging.info(f'Site automation failed - {e}')
            tbl_html = []

        logging.info(f'Site automation Successful - {e}')
        browser.close()

        return tbl_html
