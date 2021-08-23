# Base Class for the web scrapers. Web scrapers inherit this class.
# import pygsheets


class Scraper (object):

    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.results = []
        self.error = ""

    def scrape(self):
        print(self.start_date)
        print(self.end_date)
        self.results = 'results'

    def write_results(self):
        pass
        # Google Sheets for now - > https://developers.google.com/sheets/api/quickstart/python
        # gc = pygsheets.authorize(client_secret='/Users/mitchellhall/programming/pyprojects/taxlaw/taxlaw/credentials.json')
        # sh = gc.open('Lien Lead Generation')
        # wks = sh.worksheet_by_title('Sheet1')
        # wks.clear()
        # wks.update_values(crange='A1', values=self.results)
        # print(self.results)
