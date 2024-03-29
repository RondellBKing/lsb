from bs4 import BeautifulSoup
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import core.drivers as drivers
from core.scraper import Scraper


class Maryland(Scraper):
    def __init__(self, start_date=None, delta=5):
        super().__init__(start_date, delta)
        self.county_name = "maryland"

    def scrape(self):
        browser = drivers.create_driver('http://jportal.mdcourts.gov/judgment/judgementSearch.jsf') # By Pass document type search
        
        # Click Fed Tax Lien
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="searchForm:companyIndicatorRadio:1"]'))).click()
        # Click Notice of Fed Lien
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="searchForm:companyName"]'))).send_keys('internal revenue service')
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="searchForm:filingStartDate_input"]'))).send_keys(self.end_date)
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="searchForm:filingEndDate_input"]'))).send_keys(self.start_date)
        
        # Click Search Button
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="searchForm:caseSearchGet"]'))).click()
        
        time.sleep(5)

        soup = BeautifulSoup(browser.page_source, 'html.parser')

        # Click pages to fetch additional results
        tbl_paginator = soup.find('table', attrs = {'class': 'paginator'})
        pagination = tbl_paginator.find_all('td') if tbl_paginator else ['dummy'] # If single page of results
        x=1
        tables = []

        for i in pagination:
            if x > 1: # Only need to click NEXT after the first page is stored
                WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="j_idt8:scrollidx{x}"]'))).click()
                soup = BeautifulSoup(browser.page_source, 'html.parser')

            tbl_html = soup.find('table', id="j_idt8:data")
            tables.append(tbl_html)

            x+=1

        browser.close()

        return tables

    def parse_table(self, tbl_html):

        lead_list = []

        for html in tbl_html: # For Maryland we get three tables worth of html.

            rows = html.findChildren(['tr'])
            list_iterator = iter(rows)

            next(list_iterator) # First row is header with links

            try:
                for row in list_iterator:
                    lead_names = []

                    if row.get_text() != '\nInternal Revenue Service\n':
                        if len(row) == 8 : # Columns with rows properly formatted have len == 8
                            rows_td = row.find_all('td')
                            num_of_cells_in_row = len(rows_td)
                            
                            # The elements in the row are > 10 when there are multiple names for the same lead
                            lead_names.append(rows_td[4].get_text())
                            if num_of_cells_in_row > 10: # If there are 11 cells, means we have multiple aliases
                                lead_names.append(rows_td[5].get_text())

                            combined_lead_names = '|'.join(lead_names)
                            cty = rows_td[num_of_cells_in_row - 5].get_text()
                            amt = rows_td[num_of_cells_in_row - 3].get_text()
                            date = rows_td[num_of_cells_in_row - 1].get_text()
                                
                            lead_list.append([date, combined_lead_names, 'LSB', 'MD', cty])

            except Exception as e:
                print('Failed to retrieve data')
                print(e)

        return lead_list
