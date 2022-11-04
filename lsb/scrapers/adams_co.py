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


class AdamsCounty(Scraper):
    def __init__(self, start_date=None, delta=5):
        super().__init__(start_date, delta)
        self.county_name = "adams"

    def scrape(self):
        # Options used to attempt to scrape site with element not interactable exception
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_argument("--disable-extensions")

        page_url = 'http://recording.adcogov.org/LandmarkWeb/Home/Index'
        driver = drivers.create_driver(page_url, options)

        # Automate selections
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="topNavLinksSearch"]/a'))).click()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="idAcceptYes"]'))).click()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="searchCriteriaDocuments-tab"]'))).click()

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="documentType-DocumentType"]'))).send_keys('TXLN')
        # Select option for last 7 days
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="lastNumOfDays-DocumentType"]/option[2]'))).click()
        
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="submit-DocumentType"]'))).click() # Submit

        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
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
                lead_cell = row.findChildren(['td'])[5]
                name = lead_cell.contents[0]
                address = lead_cell.contents[2]
                lead = f"{name}|{address}"

                lien_date = row.findChildren(['td'])[7].text
                lead_list.append([lien_date, lead, 'LSB', 'CO', self.county_name])
            except IndexError:  # Skip empty rows
                pass

        return lead_list


if __name__ == "__main__":
    AdamsCounty(delta=0).run(send_mail=True) # Uses last 7 day button
