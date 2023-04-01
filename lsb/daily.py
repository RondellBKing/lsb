# from core import scraper  # Base class implementation
from scrapers import solanoEDDLiens
from scrapers import shiawassee_mi
from scrapers import franklin_oh

if __name__ == "__main__":
    solanoEDDLiens.Solano(delta=10).run(send_alert=True)
    shiawassee_mi.Shiawassee(delta=5).run(send_alert=True)
    franklin_oh.FranklinOh(delta=5).run(send_mail=True)