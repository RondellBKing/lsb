from bs4 import BeautifulSoup
import time
import os
import drivers
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from scraper import Scraper


class SanFran(Scraper):
    def __init__(self, start_date=None, delta=5):
        super().__init__(start_date, delta)
        self.county_name = "san_francisco"

    def scrape(self):
        browser = drivers.create_driver('https://recorder.sfgov.org/#!/simple')

        # Click Advanced Search
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="x_box_outer"]/div[2]/div/div[2]/input'))).click()

        # Drop down for Type selection
        button = browser.find_element_by_xpath('//*[@id="spanDisplayFC"]')
        browser.execute_script("arguments[0].click();", button)
        WebDriverWait(browser, 30).until(EC.element_to_be_clickable((
                                        By.XPATH, '//*[@id="ddlFilingCode"]/ul/li[11]'))).click()

        # Enter Start Date
        WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="datepicker-my"]'))).clear()

        WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="datepicker-my"]'))).send_keys(self.end_date)

        browser.find_elements_by_id("btnSearch")[1].click()
        # WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.ID, 'btnSearch'))).click()

        # per page drop down
        try:  # Todo fix drop down click
            browser.find_element_by_xpath('//*[@id="dk_container_ctl00_PlaceHolderMain_ucSearchResults_drpResultsPerPage"]/div[1]/ul/li[5]/a').click()
            time.sleep(30)
        except Exception:
            pass

        html = browser.execute_script('return document.documentElement.outerHTML')
        tbl_html = BeautifulSoup(html, 'html.parser').select('tbody > tr')  # select only the search results

        browser.close()

        return tbl_html

    @staticmethod
    def parse_table(tbl_html):
        list_iterator = iter(tbl_html)
        lead_list = []

        for row in list_iterator:
            try:
                lien_date = row.findChildren(['td'])[1].getText().strip()
                lead = row.findChildren(['td'])[3].text.split('(E)')[0]
                lead = lead.strip()
                lead_list.append([lien_date, lead, 'LSB', 'CA', 'Solano'])
            except IndexError:  # Skip empty rows
                pass

        return lead_list


if __name__ == '__main__':
    os.chdir('/Users/rondellking/PycharmProjects/lsb/lsb/scrapers')
    SanFran(delta=30).run(send_mail=False)
