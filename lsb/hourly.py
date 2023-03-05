# from core import scraper  # Base class implementation
# /opt/anaconda3/envs/lsb/bin/python /Users/rondellbking/Desktop/Things/lsb/lsb/main.py
from scrapers import harris_county, king_county, maryland


if __name__ == "__main__":
    harris_county.HarrisCounty(delta=10).run(send_alert=True)
    king_county.KingCounty(delta=1).run(send_alert=True)
    maryland.Maryland(delta=5).run(send_alert=True)