import logging
import time
import os
import sys
 
# current = os.path.dirname(os.path.realpath(__file__))
 
# # Getting the parent directory name
# # where the current directory is present.
# parent = os.path.dirname(current)
 
# # adding the parent directory to
# # the sys.path.
# print(os.path.join(parent, 'core'))
# sys.path.append(os.path.join(parent, 'core'))
 

from bs4 import BeautifulSoup


# Selenium packages used to simulate web experience
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from core.scraper import Scraper  # Base class implementation
from core import drivers


logging.basicConfig(level=logging.INFO)


class HarrisCounty(Scraper):
    def __init__(self, start_date=None, delta=5):
        super().__init__(start_date, delta)
        self.county_name = "harris_county"
        logging.basicConfig(filename=f'{self.county_name}.log', level=logging.INFO)

    def scrape(self):
        # Testing Move to own file
        driver = drivers.create_driver('https://www.cclerk.hctx.net/applications/websearch/RP.aspx')

        # Fill out dates instrument and click:w

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "ctl00$ContentPlaceHolder1$txtInstrument"))).send_keys('T/L')
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "ctl00$ContentPlaceHolder1$txtFrom"))).send_keys(self.end_date)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "ctl00$ContentPlaceHolder1$txtTo"))).send_keys(self.start_date)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "ctl00$ContentPlaceHolder1$btnSearch"))).click()
        time.sleep(5)

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        main_table = soup.find('table', id="itemPlaceholderContainer")
        driver.close()

        return main_table

    @staticmethod
    def parse_table(tbl_html):
        rows = tbl_html.findChildren(['tr'])

        list_iterator = iter(rows)
        next(list_iterator)  # First row is empty so skip it

        lead_list = []

        for row in list_iterator:
            lead_names = []

            try:
                lien_name_rows = row.findChildren(['td'])[4].findChildren(['tr'])
                date_span = row.findChildren(['td'])[2]
                lien_date = date_span.get_text(strip=True)

                for lien_name_row in lien_name_rows:
                    row_list = lien_name_row.findChildren(['td'])

                    if row_list:
                        lead = row_list[1].findChildren('span')[0].text

                        if lead:
                            if lead == 'INTERNAL REVENUE SERVICE':
                                continue

                            lead_names.append(lead)

                combined_lead_names = '|'.join(lead_names)

                if combined_lead_names:
                    logging.debug(f'Found {combined_lead_names}')
                    lead_list.append([lien_date, combined_lead_names, 'LSB', 'TX', 'Harris'])

            except IndexError:  # Skip empty rows
                logging.debug('Skipping empty row')

        logging.debug(f'Found leads below {lead_list}')
        return lead_list


if __name__ == "__main__":
    HarrisCounty(delta=10).run(send_mail=False)
