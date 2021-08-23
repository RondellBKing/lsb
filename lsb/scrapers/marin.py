import requests
from bs4 import BeautifulSoup
from rbot.scraper import Scraper
from datetime import datetime
import logging

logger = logging.getLogger('Marin-Scraper')
logger.setLevel(logging.INFO)


class Marin(Scraper):
    # make tests
    # include error for (wrong input, no results, )
    def __init__(self, start_date, end_date):
        super().__init__(start_date, end_date)
        self.result_url = ""
        self.table = ""
        self.url_list = []

    def make_url(self):
        smonth = self.start_date.month
        sday = self.start_date.day
        syear = self.start_date.year
        emonth = self.end_date.month
        eday = self.end_date.day
        eyear = self.end_date.year
        self.result_url = 'https://apps.marincounty.org/RecordersIndexSearch/?Action=N&GCO=1&GCPR=100&NDT=&NED={}' \
                          '%2F{}%2F{}&NFN=&NLN=EMPLOYMENT%20DEVELOPMENT%20DEPARTMENT&NMI=&NSD={}%2F{}%2F{}&X' \
                          'HideDisclaimer=True'.format(emonth, eday, eyear, smonth, sday, syear)
        print('\n' + 'Url being parsed: ' + self.result_url + '\n')

    def get_table(self):
        res = requests.get(self.result_url)
        res.raise_for_status()
        soup = BeautifulSoup(res.content, "html.parser")
        self.table = soup.find(lambda tag: tag.name == 'table' and tag.has_attr('id') and tag['id'] == "i0")

    def build_url_list(self):
        for tr in list(self.table):
            if '>TAX LIEN<' in str(tr):
                url = tr.a.get('href')
                disclaimer = '&XHideDisclaimer=True'
                page = url + disclaimer
                self.url_list.append(page)

    def result_list(self):
        for link in self.url_list:
            link_result = []
            res = requests.get(link)
            res.raise_for_status()
            soup = BeautifulSoup(res.content, 'html.parser')
            table = soup.find('table')
            for row in table.findAll('tr'):
                text = row.text.replace('class=\"i19\"', '')
                link_result.append(text)
            self.results.append(link_result)

    def scrape(self):
        self.make_url()
        self.get_table()
        self.build_url_list()
        self.result_list()


if __name__ == '__main__':
    start_dt = datetime.strptime(input('Start Date(dd/mm/yyyy): '), "%d/%m/%Y")
    end_dt = datetime.strptime(input('End Date(dd/mm/yyyy): '), "%d/%m/%Y")
    marin = Marin(start_dt, end_dt)
    marin.scrape()
