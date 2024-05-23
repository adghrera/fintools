import test_setup
from django.db import IntegrityError, transaction

from stockutils.tickers.stocktickers import DefaultStockTickerProvider
from stockdata.models import Ticker


def import_all_tickers():
    tickers = DefaultStockTickerProvider().get_tickers()
    rows = []
    for name, data in tickers.items():
        ticker = Ticker()
        ticker.id = data["ticker"]
        ticker.name = data["title"]
        rows.append(ticker)
    # print(rows)

    with transaction.atomic():
        Ticker.objects.bulk_create(rows, ignore_conflicts=True)

        # Ticker.objects.bulk_create(rows)
        # for row in rows:
        #     row.save()
    # print(tickers)


def demo_tickers():
    from stockdata.models import Ticker

    ticker = Ticker()
    ticker.id = "AAPL"
    ticker.name = "Apple"
    ticker.sector = "Technology"
    ticker.exchange = "NASDAQ"
    ticker.save()

    ticker = Ticker()
    ticker.id = "PYPL"
    ticker.name = "Paypal"
    ticker.save()


if __name__ == "__main__":
    import_all_tickers()
