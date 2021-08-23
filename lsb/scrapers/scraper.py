# Base Class for the web scrapers. Web scrapers inherit this class.
# import pygsheets


class Scraper (object):

    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.results = []
        self.table = []
        self.error = ""
        self.html = ""

    def run(self):
        self.scrape()
        self.parse_table()
        self.upload_data_and_alert()

    def scrape(self):
        print(self.start_date)
        print(self.end_date)
        self.html = 'results'

    def parse_table(self):
        pass

    def upload_data_and_alert(self):
        pass
        # Check google drive and compare feeds
        # Write to google drive if any updates
        # Send Email
