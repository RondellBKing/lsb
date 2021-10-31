# Base Class for the web scrapers. Web scrapers inherit this class and implement scrape + parse_table.

from abc import ABC, abstractmethod
import logging
import os
import glob
import sys
from datetime import date
from datetime import timedelta
from dateutil.parser import parse
import pandas as pd
import tempfile

from send_email import send_mail
import drivers

# logging.basicConfig(filename='scraper.log', level=logging.INFO)
logging.basicConfig(level=logging.INFO)


class Scraper(ABC):

    def __init__(self, start_date, delta):
        self.start_date = start_date
        self.end_date = ''
        self.lead_list = []
        self.table = []
        self.error = ""
        self.tbl_html = ""
        self.temp_dir = tempfile.gettempdir()
        self.script_dir = os.path.abspath(os.path.dirname(sys.argv[0]) or '.')
        self.temp_dir = os.path.join(self.script_dir, f'../temp')
        self.filename = ""
        self.county_name = ""
        self.send_mail = ""
        self.email_recipients = "ddrummond@blueprint-tax.com"
        # self.email_recipients = "kingstack08@gmail.com"
        self.header = ['LienDate', 'Taxpayer', 'Recorded', 'State', 'County']  # File header name
        self.delta = delta

        os.chdir('/Users/rondellking/PycharmProjects/lsb/lsb/scrapers')

    # Main Scraper Flow
    def run(self, send_mail=True):
        self.send_mail = send_mail

        self.feed_setup()
        self.tbl_html = self.scrape()

        if self.tbl_html:
            self.lead_list = self.parse_table(self.tbl_html)
            self.upload_data_and_alert()
        else:
            logging.info(f'No Results found for {self.start_date}')
            print(f'No Results found for {self.start_date}')

    def upload_data_and_alert(self):
        """
        Check google drive and compare feeds
        Write to google drive if any updates

        Send Email
        :return:
        """

        # Compare latest existing feed, only create a new one if there are differences.
        list_of_files = glob.glob(f'{self.temp_dir}/{self.county_name}*')
        if list_of_files:
            latest_file = max(list_of_files, key=os.path.getmtime)
            logging.info(f'Latest feed found {latest_file}')

            # Create Dataframe from the previous lead source and the new
            latest_data_feed_df = pd.read_csv(latest_file, index_col=False)
        else:
            latest_data_feed_df = pd.DataFrame()

        leads_df = pd.DataFrame(self.lead_list, columns=self.header)

        new_lead_count = len(leads_df)
        prev_lead_count = len(latest_data_feed_df)

        logging.info(f'Found {new_lead_count} in latest pull compared to {prev_lead_count} in previous feed')

        if not leads_df.equals(latest_data_feed_df):

            logging.info(f"Creating new feed {self.filename}")
            leads_df.to_csv(self.filename, index=False)

            subject = f' {self.county_name} - {new_lead_count} leads found for {self.start_date} - {self.end_date}'
            email_message = f"See https://drive.google.com/drive/folders/1TrIpVdx9JCD_hungVPweQGfcDkJDB5dh?usp=sharing"

            if self.send_mail:
                logging.info('Sending email and uploading feed')
                drivers.g_drive(self.filename, '1TrIpVdx9JCD_hungVPweQGfcDkJDB5dh')
                send_mail(self.email_recipients, subject, email_message)
        else:
            logging.info('Feed is the same as previous, ending without sending to drive')

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
        self.filename = os.path.join(self.script_dir, f'../temp/{self.county_name}_{file_date}.csv')
        logging.info(self.filename)
        logging.info(f'Running for date range {self.start_date} - {self.end_date}')

        return {"file": self.filename, "delta": day_delta, "st_dt": self.start_date, "end_dt": self.end_date}

    @abstractmethod
    def scrape(self):
        """
        Connects to site simulates search and fetch html
        :return:
        """
        print(self.start_date)
        print(self.end_date)
        self.tbl_html = 'results'

    @staticmethod
    @abstractmethod
    def parse_table(tbl_html):
        """
        Parse html table and extract pertinent lead data
        :return:
        """
        return []
