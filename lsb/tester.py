# from core import scraper  # Base class implementation
from scrapers import test_runner


if __name__ == "__main__":
    test_runner.Tester(delta=10).run(send_alert=False)
