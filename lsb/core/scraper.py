# Base Class for the web scrapers. Web scrapers inherit this class and implement scrape + parse_table.

from abc import ABC, abstractmethod
import logging
import os
import sys
from datetime import date, timedelta
from dateutil.parser import parse
from pathlib import Path
import json
import time

from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from pretty_html_table import build_table

import pandas as pd

from core.helper import is_new_feed
from core.send_email import send_mail
import core.drivers as drivers
from core.biz_logic import is_business

# logging.basicConfig(filename='scraper.log', level=logging.INFO)
logging.basicConfig(level=logging.INFO)


class Scraper(ABC):

    def __init__(self, start_date, delta):
        self.start_date = start_date
        self.end_date = ''
        self.lead_list = []
        self.tbl_html = ""
        self.script_dir = os.path.abspath(os.path.dirname(sys.argv[0]) or '.')
        self.temp_dir = os.path.join(self.script_dir, 'temp') # Point of execution will be parent to current dir
        self.filename = ""
        self.county_name = ""
        self.email_recipients = "ddrummond@blueprint-tax.com, jjereb@blueprint-tax.com, AutoSquirrels@gmail.com"    
        # self.email_recipients = "kingstack08@gmail.com",
        self.sender = "kingstack08@gmail.com"
        self.header = ['LienDate', 'Taxpayer', 'Recorded', 'State', 'County']  # File header name
        self.delta = delta
        self.browser = ''

    def run(self, send_alert=True):
        """
        This is the main point of execution when scraping sites. Controls the flow of exeuction to data loading.
        """
        self.feed_setup()
        self.tbl_html = self.scrape() # Automate website execution and fetch html with results

        if self.tbl_html:
            self.lead_list = self.parse_table(self.tbl_html)

            if self.lead_list:
                new_feed, leads_df = is_new_feed(self.lead_list, self.temp_dir, self.county_name, self.header)

                if new_feed:
                    logging.info(f"Creating new feed {self.filename}")
                    leads_df.to_csv(self.filename, index=False)
                    new_lead_count = len(leads_df)

                    if send_alert:
                        leads_df_w_biz = is_business(leads_df)
                        email_message = """
                            <html>
                            <head>
                            </head>

                            <body>
                                    {0}
                                    <br>
                                    https://drive.google.com/drive/folders/1TrIpVdx9JCD_hungVPweQGfcDkJDB5dh?usp=sharing 
                            </body>

                            </html>
                            """.format(build_table(leads_df_w_biz, 'blue_light'))
                        subject = f' {self.county_name} - {new_lead_count} leads found for {self.end_date} - {self.start_date} '

                        logging.info('Sending email and uploading feed')
                        # drivers.g_drive(self.filename, '1TrIpVdx9JCD_hungVPweQGfcDkJDB5dh')

                        send_mail(self.email_recipients, subject, email_message, self.sender,  self.filename)
                        # Load to mongo, only for select counties during beta
                        # if self.county_name in ['king_county','harris_county','maryland']:
                        #     self.store_feed(leads_df)

                else:
                    logging.info('Feed is the same as previous, ending without sending to drive')
                    logging.info(f"New Results not found for {self.start_date}")

            else:
                logging.info(f'No Results found for {self.start_date}')

        else:
            logging.error(f'Table html not found after scraping {self.start_date}')

    def store_feed(self, lead_df):
        client = drivers.create_mongo_connection()
        db = client['scraped_leads']
        collection = db[self.county_name]
        lead_dict = lead_df.to_dict("records")
        try:
            logging.info("Loading data to mongo db")
            collection.insert_many(lead_dict)
            # collection.update_many({ "Taxpayer": { "$exists": True } },lead_dict, upsert=True)
        except Exception as e:
            logging.error(f'Failed to load to mongo {e}')

    def feed_setup(self):
        day_delta = timedelta(days=self.delta)

        if not self.start_date:
            self.start_date = date.today()
        else:
            self.start_date = parse(self.start_date)

        prev_day = self.start_date - day_delta

        self.start_date = self.start_date.strftime("%m/%d/%Y")
        self.end_date = prev_day.strftime("%m/%d/%Y")

        file_date = self.start_date.replace('/', '')

        self.filename = os.path.join(self.temp_dir, f'{self.county_name}_{file_date}.csv')
        logging.info(f'New reuslts are stored here -> {self.filename}')
        logging.info(f'Running for date range {self.start_date} - {self.end_date}')

        return {"file": self.filename, "delta": day_delta, "st_dt": self.start_date, "end_dt": self.end_date}

    def scrape(self):
        """
        Parses config file and automates the site steps to prep table html.
        :return:
        """

        try:
            self.process_automation_via_config()

            tbl_html = self.fetch_table_html()

        except Exception as e:
            logging.info(f'Site automation failed - {e}')
            tbl_html = []

        self.browser.close()

        return tbl_html

    def process_automation_via_config(self):
        '''
        This Method recieves steps from the config file and executes each action.
        '''

        parent_dir = os.fspath(Path(__file__).resolve().parents[1].resolve()) # Relative to point of execution
        f = open(os.path.join(parent_dir, 'scraper_configs', f'{self.county_name}.json'))
        
        site_json = json.load(f)
        bot_config = site_json.get('BOT_STEPS')
        site_link = site_json.get('SITE_LINK')

        self.browser = drivers.create_driver(site_link)

        for config_step in bot_config:
            action = config_step.get('ACTION')
            if config_step.get('XPATH'):
                action_string = config_step.get('XPATH')
                action_type = By.XPATH
            elif config_step.get('CLASS_NAME'):
                action_string = config_step.get('CLASS_NAME')
                action_type = By.CLASS_NAME

            logging.info(f'Executing {action} on {action_string}')

            if action == 'Click':
                WebDriverWait(self.browser, 30).until(EC.element_to_be_clickable((action_type, action_string))).click()
            elif action == 'Iframe':
                time.sleep(5)
                self.browser.switch_to.frame(self.browser.find_element_by_xpath(action_string))
            elif action == 'ParentIframe':
                self.browser.switch_to.parent_frame()
            elif action == 'Input':
                text = config_step.get('TEXT')
                if text == 'END_DATE':
                    WebDriverWait(self.browser, 20).until(EC.element_to_be_clickable((action_type, action_string))).send_keys(self.end_date)
                elif text == 'ST_DATE':
                    WebDriverWait(self.browser, 20).until(EC.element_to_be_clickable((action_type, action_string))).send_keys(self.start_date)
                else:
                    WebDriverWait(self.browser, 20).until(EC.element_to_be_clickable((action_type, action_string))).send_keys(text)

    def fetch_table_html(self):
        '''
        This method is used to extract the table from the results since this is what we are after.
        '''
        try:
            self.browser.switch_to.default_content()
            self.browser.switch_to.frame(self.browser.find_element_by_name('bodyframe'))
            self.browser.switch_to.frame(self.browser.find_element_by_name('resultFrame'))
            self.browser.switch_to.frame(self.browser.find_element_by_name('resultListFrame'))
        except Exception as e:
            logging.warning(f'No Result Frame found - {e}')

        html = BeautifulSoup(self.browser.page_source, 'html.parser')

        tbl_html = html.find('table', {'class': 'datagrid-btable'})

        return tbl_html

    @abstractmethod
    def parse_table(self, tbl_html):
        """
        Parse html table and extract pertinent lead data
        :return:
        """
        return []
