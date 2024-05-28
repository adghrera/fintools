import logging
import sys

# import ....basic_setup
# sys.path.append("../..")

from statsmodels.regression.rolling import RollingOLS
import pandas_datareader.data as web
import matplotlib.pyplot as plt
import statsmodels.api as sm
import pandas as pd
import numpy as np
import datetime as dt
import yfinance as yf
import pandas_ta
import warnings
from stockutils.tickers.stocktickers import StockTickerProvider
from stockutils.appconsts import DAY_SECS
from stockutils.cacheutils import AppCache

warnings.filterwarnings("ignore")
logger = logging.getLogger(__name__)


class SPY500Tickers(StockTickerProvider):

    def __init__(self):
        self.cache = None

    def get_ticker(self, ticker: str) -> dict:
        return self.get_tickers().get(ticker)

    def get_tickers(self):
        return self.fetch_tickers()

    def fetch_tickers(self):
        if self.cache and self.cache.get("SPY"):
            return self.cache

        # pickle data
        cached = AppCache("SPY500Tickers")
        cached.loadFromDisk(DAY_SECS)
        if cached.loadedFromDisk():
            logging.info("Loaded SPY500 tickers from file")
            print("loading...")
            self.cache = cached.get("tickers")
            return self.cache

        logging.info("Fetching SPY500 tickers")
        print("fetching...")
        sp500 = pd.read_html(
            "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        )[0]
        sp500["Symbol"] = sp500["Symbol"].str.replace(".", "-")
        symbols_list = sp500["Symbol"].unique().tolist()
        self.cache = {}
        for sym in symbols_list:
            self.cache[sym] = {"ticker": sym, "title": sym}

        cached.set("tickers", self.cache)
        cached.saveToDisk()

        return self.cache
