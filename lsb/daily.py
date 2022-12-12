# from core import scraper  # Base class implementation
from scrapers import solanoEDDLiens


if __name__ == "__main__":
    solanoEDDLiens.Solano(delta=10).run(send_alert=False)
