import time
import os
from bs4 import BeautifulSoup

# Selenium packages used to simulate web experience
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC

import drivers
from scraper import Scraper  # Base class implementation


class KingCounty(Scraper):
    def __init__(self, start_date=None, delta=5):
        super().__init__(start_date, delta)
        self.county_name = "king_county"

    def scrape(self):
        # Options used to attempt to scrape site with element not interactable exception
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_argument("--disable-extensions")

        page_url = 'https://recordsearch.kingcounty.gov/LandmarkWeb/search/index?theme=.blue&section=searchCriteriaLegal&quickSearchSelection='
        driver = drivers.create_driver(page_url, options)

        # Fill out dates

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "searchCriteriaDocuments-tab"))).click()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "searchCriteriaDocuments-tab"))).click()
        # WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "beginDate - DocumentType"))).send_keys('10/10/2021')
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "documentType-DocumentType"))).send_keys('FTL')
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "beginYesterday-DocumentType"))).click()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "submit-DocumentType"))).click()

        time.sleep(10)
        html = driver.page_source
        ''' Make Above Separate Function'''

        soup = BeautifulSoup(html, 'html.parser')
        main_table = soup.find('table', id="resultsTable")

        driver.close()
        
        return main_table

    def parse_table(self, tbl_html):
        lead_list = []
        rows = tbl_html.findChildren(['tr'])

        list_iterator = iter(rows)
        next(list_iterator)  # First row is empty so skip it

        count = 0

        for row in list_iterator:
            if count == 0:
                count += 1
                continue
            try:
                lead = row.findChildren(['td'])[5].text
                lien_date = row.findChildren(['td'])[7].text
                if lead:
                    lead_list.append([lien_date, lead, 'LSB', 'WA', 'King'])
            except IndexError:  # Skip empty rows
                pass

        return lead_list


if __name__ == "__main__":
    os.chdir('/Users/rondellking/PycharmProjects/lsb/lsb/scrapers')
    KingCounty(delta=0).run(send_mail=True)
