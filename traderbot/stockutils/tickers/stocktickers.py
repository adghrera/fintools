import abc
import json
import time

import requests

from traderbot.stockutils.appexceptions import AppError
from traderbot.stockutils.config import ConfigManager, TICKERS, RAW_TICKERS

REFRESH_INTERVAL = 24*60*60
TICKERS_URL = 'https://www.sec.gov/files/company_tickers.json'

class StockTickerProvider:

    @abc.abstractmethod
    def get_ticker(self, ticker: str) -> dict:
        """Load in the data set"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_tickers(self) -> dict:
        """Load in the data set"""
        raise NotImplementedError


class DefaultStockTickerProvider(StockTickerProvider):

    def __init__(self):
        self.tickers = None
        self.last_updated = 0

    def get_ticker(self, ticker: str) -> dict:
        return self.get_tickers().get(ticker)


    def get_tickers(self):
        now = int(time.time())
        if not self.tickers or self.last_updated < now - REFRESH_INTERVAL:
            self.tickers = self.fetch_external_tickers()
        return self.tickers

    def fetch_external_tickers(self):
        with open(RAW_TICKERS, "r") as f:
            t = json.load(f)

            result = {}
            for id, tick in t.items():
                result[tick['ticker']] = tick

            return result
    def fetch_external_tickers_dynamic(self):
        now = int(time.time())
        cm = ConfigManager()
        updated = cm.get_config('tickers.updated', 0)

        result = None
        if updated < now - REFRESH_INTERVAL:
            r = requests.get(TICKERS_URL)

            if r.status_code != 200:
                print(r)
                raise AppError('Error getting tickers')

            data = r.json()
            result = {}

            for id, tick in data.items():
                result[tick['ticker']] = tick

            with open(TICKERS, "w") as f:
                json.dump(result, f)

            updated = now
            cm.set_config('tickers.updated', updated)
        else:
            with open(TICKERS, "r") as f:
                result = json.load(f)

        return result

if __name__ == '__main__':
    tp = DefaultStockTickerProvider()
    t = tp.get_ticker('AAPL')
    print(t)
