from bs4 import BeautifulSoup
import time
import os
import drivers
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from scraper import Scraper


class Solano(Scraper):
    def __init__(self, start_date=None, delta=5):
        super().__init__(start_date, delta)
        self.county_name = "solano"

    def scrape(self):
        browser = drivers.create_driver('http://recorderonline.solanocounty.com')

        time.sleep(1)

        # Hit Agree
        browser.find_element_by_id('ctl00_m_g_c6431b47_3ecb_4f66_9e13_f949e2ea5ca6_ctl00_btnAgree').click()
        time.sleep(1)

        # Show advanced search options
        browser.find_element_by_id('ctl00_m_g_53ad86ef_2077_49cd_915b_11a033357719_ctl00_btnShowAdvanced').click()
        time.sleep(1)

        # Enter Start Date
        WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.ID, "ctl00_m_g_53ad86ef_2077_49cd_915b_11a033357719_ctl00_txtDocumentDateFrom"))).clear()
        WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.ID, "ctl00_m_g_53ad86ef_2077_49cd_915b_11a033357719_ctl00_txtDocumentDateFrom"))).send_keys(self.end_date)

        browser.find_element_by_css_selector('#dk_container_ctl00_m_g_53ad86ef_2077_49cd_915b_11a033357719_ctl00_'
                                             'drpFilingCode > a > span.dk_label').click()
        time.sleep(1)

        # lien - Federal tax lien
        browser.find_element_by_xpath('//*[@id="dk_container_ctl00_m_g_53ad86ef_2077_'
                                      '49cd_915b_11a033357719_ctl00_drpFilingCode"]'
                                      '/div[1]/ul/li[723]/a').click()
        time.sleep(1)

        browser.find_element_by_css_selector('#ctl00_m_g_53ad86ef_2077_49cd_915b_11a033357719_ctl00_btnAdvancedSearch').click()
        time.sleep(1)

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
    Solano(delta=5).run(send_mail=True)
