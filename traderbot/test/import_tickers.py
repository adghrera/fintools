import sys
import os
import django

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "traderbot.settings")
django.setup()


def import_tickers():

    # os.environ.setdefault("DJANGO_SETTINGS_MODULE", "traderbot.traderbot.settings")
    # os.environ.setdefault("DJANGO_SETTINGS_MODULE", "traderbot.settings")
    # django.setup()

    # from traderbot.traderbot.settings import INSTALLED_APPS
    # from traderbot.stockdata.models import Ticker
    from stockdata.models import Ticker

    ticker = Ticker()
    ticker.id = "AAPL"
    ticker.name = "Apple"
    ticker.sector = "Technology"
    ticker.exchange = "NASDAQ"
    result = ticker.save()
    print(result)


if __name__ == "__main__":
    # import shell from manage

    # SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    # sys.path.append(os.path.dirname(SCRIPT_DIR))
    # print(sys.path)

    import_tickers()
