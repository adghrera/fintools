from requests import Session
from requests_cache import CacheMixin, SQLiteCache
from requests_ratelimiter import LimiterMixin, MemoryQueueBucket
from pyrate_limiter import Duration, RequestRate, Limiter
import yfinance as yf


class CachedLimiterSession(CacheMixin, LimiterMixin, Session):
    pass


# session = CachedSession('demo_cache', expire_after=360)

session = CachedLimiterSession(
    limiter=Limiter(
        RequestRate(2, Duration.SECOND * 5)
    ),  # max 2 requests per 5 seconds
    bucket_class=MemoryQueueBucket,
    backend=SQLiteCache("yfinance.cache"),
    expire_after=3600,
)


def get_eod(ticker):
    return yf.download(ticker, session=session)


def find_buy_events(ticker):
    eod = get_eod(ticker)
    spy = get_eod("SPY")

    # calculate daily price change
    eod["price_change"] = eod["Close"] - eod["Close"].shift(1)
    spy["price_change"] = spy["Close"] - spy["Close"].shift(1)

    # calculate daily return
    eod["return"] = eod["price_change"] / eod["Close"].shift(1)
    spy["return"] = spy["price_change"] / spy["Close"].shift(1)

    spy_return = 0
    eod_return = 0
    buy_day = 0
    for i in range(1, 6):
        key = "return" + str(i)
        spy[key] = (spy["Close"] - spy["Close"].shift(i)) / spy["Close"].shift(i)
        eod[key] = (eod["Close"] - eod["Close"].shift(i)) / eod["Close"].shift(i)

        # eod["buy_signal"] = spy[key] < -0.02 & eod[key] < -0.03
    SPY_DIP = 0.01
    EOD_DIP = 0.03
    # # buy signal is when spy dips by more than 2% in 1 or 2 or 3 or 4 or 5 days and stock dips by  more than 3% in the same period
    eod["buy_signal"] = (
        ((spy["return1"] < -SPY_DIP) & (eod["return1"] < -EOD_DIP))
        | ((spy["return2"] < -SPY_DIP) & (eod["return2"] < -EOD_DIP))
        | ((spy["return3"] < -SPY_DIP) & (eod["return3"] < -EOD_DIP))
        | ((spy["return4"] < -SPY_DIP) & (eod["return4"] < -EOD_DIP))
        | ((spy["return5"] < -SPY_DIP) & (eod["return5"] < -EOD_DIP))
    )

    # eod["buy_signal"] = (spy["return"] < -0.02) & (eod["return"] < -0.03)

    return eod


if __name__ == "__main__":
    # print(get_eod("SPY"))
    # print(get_eod("GOOG"))
    # print(get_eod("QQQ"))
    # print(get_eod("V"))
    events = find_buy_events("V")
    # filter events by buy_signal
    events = events[events["buy_signal"]]

    print(events)
