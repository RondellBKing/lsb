# Base Class for the web scrapers. Web scrapers inherit this class and implement scrape + parse_table.

from abc import ABC, abstractmethod
import logging
import os
import glob
import sys
from datetime import date, timedelta
from dateutil.parser import parse
import json
import time

from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


import pandas as pd
import tempfile

from send_email import send_mail
import drivers

from scraper import Scraper

# logging.basicConfig(filename='scraper.log', level=logging.INFO)
logging.basicConfig(level=logging.INFO)


class Cofile(Scraper):


    # @abstractmethod
    def scrape(self):
        """
        Parses config file and automates the site steps to prep table html.
        :return:
        """
        f = open(f'../scraper_configs/{self.county_name}.json')
        # f = open(f'lsb/scraper_configs/{self.county_name}.json')
        # Load Json from script and execute steps from config
        site_json = json.load(f)

        bot_config = site_json.get('BOT_STEPS')
        site_link = site_json.get('SITE_LINK')
        bodyframe = site_json.get('BODYFRAME', True)

        browser = drivers.create_driver(site_link)

        try:

            for config_step in bot_config:
                self.process_action(browser, config_step)
            
            if bodyframe:
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

        browser.close()

        return tbl_html # List of tables for Maryland 
    
    # @abstractmethod
    # def parse_table(self, tbl_html):
    #     """
    #     Parse html table and extract pertinent lead data
    #     :return:
    #     """
    #     return []
