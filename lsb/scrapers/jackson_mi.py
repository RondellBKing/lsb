import logging

from core.scraper import Scraper


class JacksonMI(Scraper):
    def __init__(self, start_date=None, delta=5):
        super().__init__(start_date, delta)
        self.county_name = "JACKSON_MI"

    def parse_table(self, tbl_html):
        lead_list = []
        rows = tbl_html.findAll("tr")

        for row in rows:
            try:
                lead = row.findChildren(['td'])[6].getText().strip()
                if lead == 'FEDERAL TAX LIEN':
                    continue
                if lead != 'E':
                    lien_date = row.findChildren(['td'])[8].getText().strip()
                    lead_list.append([lien_date, lead, 'LSB', 'MI', self.county_name])
            except IndexError as e:  # Skip empty rows
                logging.error(f'Table parsing failed {e}')
                pass

        return lead_list
