import logging
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from scraper import Scraper


class Jackson(Scraper):
    def __init__(self, start_date=None, delta=5):
        super().__init__(start_date, delta)
        self.county_name = "JACKSON" 
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
    Jackson(delta=5).run(send_mail=True)
