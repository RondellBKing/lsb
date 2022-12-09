import logging
import os

from scraper import Scraper

class SNOHOMISH_WA(Scraper):
    def __init__(self, start_date=None, delta=5):
        super().__init__(start_date, delta)
        self.county_name = "SNOHOMISH_WA"

    def parse_table(self, tbl_html):
        lead_list = []
        rows = tbl_html.findAll("tr")

        for row in rows:
            try:
                lead = row.findChildren(['td'])[5].getText().strip()
                if lead != 'E':
                    lien_date = row.findChildren(['td'])[8].getText().strip()
                    lead_list.append([lien_date, lead, 'LSB', 'MI', self.county_name])
            except IndexError as e:  # Skip empty rOWs
                logging.error(f'Table parsing failed {e}')
                pass

        return lead_list


if __name__ == '__main__':
    SNOHOMISH_WA(delta=5).run(send_mail=True)