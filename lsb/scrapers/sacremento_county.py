from bs4 import BeautifulSoup
import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Local imports
import drivers
from scraper import Scraper


class Solano(Scraper):
    def __init__(self, start_date=None, delta=5):
        super().__init__(start_date, delta)
        self.county_name = "sacremento"

    def scrape(self):
        browser = drivers.create_driver('https://recordersdocumentindex.saccounty.net/#!/disclaimer')
        time.sleep(5)

        # Hit Agree
        browser.find_elements_by_class_name("blue_button")[1].click()
        time.sleep(5)

        # Fill in Text and Hit Search
        WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.NAME, "last-name"))).send_keys('internal revenue service')
        time.sleep(1)
        browser.find_elements_by_id("btnSearch")[1].click()  # Now the Search button

        time.sleep(10)
        browser.find_element_by_xpath('//*[@id="ul_Less_FC"]/li[1]/div[1]/input').click()  # Click Federal Lien checkbox
        time.sleep(10)

        # Fix to make the drop down clickable
        button = browser.find_element_by_xpath('//*[@id="spanPageNum"]')
        browser.execute_script("arguments[0].click();", button)

        # 100 page dropdown
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable((
                                        By.XPATH, '//*[@id="ddlDocsPerPage"]/ul/li[5]'))).click()
        time.sleep(5)

        # Extract Table and close page
        # Todo move to scraper.py and add id parameter
        html = browser.page_source
        tbl_html = BeautifulSoup(html, 'html.parser').find('table', id="SearchResultsGrid")
        browser.close()

        return tbl_html

    @staticmethod
    def parse_table(tbl_html):
        rows = tbl_html.findChildren(['tr'])
        list_iterator = iter(rows)
        lead_list = []

        for row in list_iterator:
            try:
                lien_date = row.findChildren(['td'])[1].getText().strip()

                # Strip out the (E) completely and trim the string of (R) if it exist
                lead = row.findChildren(['td'])[3].text.split('(E)')[0].split('(R)')[-1].strip()
                lead_list.append([lien_date, lead, 'LSB', 'CA', 'Sacramento'])
            except Exception:  # Skip empty rows
                pass
        return lead_list


if __name__ == '__main__':
    os.chdir('/Users/rondellking/PycharmProjects/lsb/lsb/scrapers')
    Solano(delta=0).run(send_mail=True)
