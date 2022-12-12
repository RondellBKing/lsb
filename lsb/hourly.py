# from core import scraper  # Base class implementation
from scrapers import harris_county, king_county, maryland


if __name__ == "__main__":
    harris_county.HarrisCounty(delta=10).run(send_alert=False)
    king_county.KingCounty(delta=1).run(send_alert=False)
    maryland.Maryland(delta=5).run(send_alert=False)
