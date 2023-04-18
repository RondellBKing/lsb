import logging
from bs4 import BeautifulSoup
from core.scraper import Scraper

class CALI_SOS(Scraper):
    def __init__(self, start_date=None, delta=5):
        super().__init__(start_date, delta)
        self.county_name = "CALI_SOS"
    
    def fetch_table_html(self):
        '''
        This method is used to extract the table from the results since this is what we are after.
        '''

        html = BeautifulSoup(self.browser.page_source, 'html.parser')
        tbl_html = html.find('table', {'class': 'div-table center-container'})

        return tbl_html        

    def parse_table(self, tbl_html):
        lead_list = []
        rows = tbl_html.findAll("tr")

        for row in rows:
            try:
                lead = row.findChildren(['td'])[4].getText().strip()
                if lead != 'E':
                    lien_date = row.findChildren(['td'])[8].getText().strip()
                    lead_list.append([lien_date, lead, 'LSB', 'MI', self.county_name])
            except IndexError as e:  # Skip empty rows
                logging.error(f'Table parsing failed {e}')
                pass

        return lead_list
