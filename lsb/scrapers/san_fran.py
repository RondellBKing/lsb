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

        time.sleep(5)
        # Enter Start Date
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="datepicker-my"]'))).clear()
        time.sleep(5)
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="datepicker-my"]'))).send_keys(self.end_date)

        # Drop down for Type selection
        button = browser.find_element_by_xpath('//*[@id="spanDisplayFC"]')
        browser.execute_script("arguments[0].click();", button)
        WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ddlFilingCode"]/ul/li[11]'))).click()
        browser.find_element_by_class_name('blue_button').click()
        # browser.find_elements_by_id("btnSearch")[0].click()
        # time.sleep(5)

        # browser.find_elements_by_id("btnSearch")[1].click()
        time.sleep(5)

        
        try:
            # Click check box to reinforce filter (bug fix)
            WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ul_Less_FC"]/li/div[1]/input'))).click()
            
            # Fix to make the drop down clickable
            button = browser.find_element_by_xpath('//*[@id="spanPageNum"]')
            browser.execute_script("arguments[0].click();", button)
            time.sleep(5)
            
            # 100 page dropdown
            WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ddlDocsPerPage"]/ul/li[5]'))).click()
        except Exception:
            print("No Results found 100 page dropdown skipped")

        time.sleep(5)

        # html = browser.execute_script('return document.documentElement.outerHTML')
        html = browser.page_source
        # tbl_html = BeautifulSoup(html, 'html.parser').select('tbody > tr')  # select only the search results
        tbl_html = BeautifulSoup(html, 'html.parser').find('table', id="SearchResultsGrid")
        # browser.close()

        return tbl_html

    @staticmethod
    def parse_table(tbl_html):
        rows = tbl_html.findChildren(['tr'])
        list_iterator = iter(rows)
        # list_iterator = iter(tbl_html)
        lead_list = []

        for row in list_iterator:
            try:
                lien_date = row.findChildren(['td'])[1].getText().strip()
                lead = row.findChildren(['td'])[3].text
                
                # Strip out IRS reference
                lead = lead.replace('(E) USA IRS', '')
                lead = lead.replace('(R) USA IRS', '')

                # Stack multi leads into one line and sanitize
                lead = lead.replace('(E)', '|')
                lead =lead.replace('(R)', '')
                # lead = row.findChildren(['td'])[3].text.split('(E)')#[0]
                # row.findChildren(['td'])[3].text.split('(E)')[0].split('(R)')[-1].strip()
                lead = lead.strip()
                lead_list.append([lien_date, lead, 'LSB', 'CA', 'San Francisco'])
            except IndexError:  # Skip empty rows
                pass

        return lead_list


if __name__ == '__main__':
    os.chdir('/Users/rondellking/PycharmProjects/lsb/lsb/scrapers')
    SanFran(delta=10).run(send_mail=True)
