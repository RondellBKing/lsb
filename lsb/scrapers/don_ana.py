from bs4 import BeautifulSoup
import time
import core.drivers as drivers
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from core.scraper import Scraper


class DonAna(Scraper):
    def __init__(self, start_date=None, delta=5):
        super().__init__(start_date, delta)
        self.county_name = "don_ana"

    def scrape(self):
        browser = drivers.create_driver('http://records.donaanacounty.org/countyweb/loginDisplay.action?countyname=DonaAna') # By Pass document type search
        
        # Click Search Public Records
        WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="maindiv"]/table[2]/tbody/tr[1]/td[2]/table/tbody/tr/td/input'))).click()
        time.sleep(5)
        WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="menudiv"]/table/tbody/tr/td[1]/table/tbody/tr/td[5]/a'))).click()

        browser.switch_to.frame(browser.find_element_by_xpath('//*[@id="corediv"]/iframe')) # Parent Frame
        browser.switch_to.frame(browser.find_element_by_xpath('//*[@id="dynSearchFrame"]')) # Frame that holds side selections
        
        # Click Federal Tax Lien
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_easyui_tree_13"]/span[4]/b'))).click()
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_easyui_tree_19"]/span[2]'))).click()
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_easyui_tree_26"]/span[6]'))).click()

        # Enter Dates
        browser.switch_to.frame(browser.find_element_by_xpath('//*[@id="criteriaframe"]'))
        WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="elemDateRange"]/table/tbody/tr/td[2]/table/tbody/tr/td[1]/span/input[1]'))).send_keys(self.end_date)
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="elemDateRange"]/table/tbody/tr/td[2]/table/tbody/tr/td[3]/span/input[1]'))).send_keys(self.start_date)
        
        browser.switch_to.parent_frame()

        # Click Search Button
        WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="imgSearch"]'))).click()
        browser.switch_to.default_content()
        browser.switch_to.frame(browser.find_element_by_name('bodyframe'))
        browser.switch_to.frame(browser.find_element_by_name('resultFrame'))
        browser.switch_to.frame(browser.find_element_by_name('resultListFrame'))
        html = BeautifulSoup(browser.page_source, 'html.parser')
        

        tbl_html = html.find('table', {'class': 'datagrid-btable'})
        # table = bs.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="Table1") 
        # rows = table.findAll(lambda tag: tag.name=='tr')
        browser.close()

        return tbl_html

    def parse_table(self, tbl_html):
        lead_list = []
        rows = tbl_html.findAll("tr")

        for row in rows:
            try:
                lead = row.findChildren(['td'])[5].getText()
                if lead != '2':
                    lien_date = row.findChildren(['td'])[7].getText()
                    lead_list.append([lien_date, lead, 'LSB', 'NM', self.county_name])

            except IndexError:  # Skip empty rows
                pass

        return lead_list


if __name__ == '__main__':
    DonAna(delta=20).run(send_mail=True)
