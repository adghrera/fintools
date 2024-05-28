import test_setup
from stockutils.tickers.spy500tickers import SPY500Tickers

if __name__ == "__main__":
    print(SPY500Tickers().get_tickers())
