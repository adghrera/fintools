from datetime import datetime
from decimal import Decimal
import glob
import math
import test_setup
from django.db import IntegrityError, transaction

from stockutils.tickers.stocktickers import DefaultStockTickerProvider
from stockdata.models import Eod, Ticker


def import_all_tickers():
    tickers = DefaultStockTickerProvider().get_tickers()
    rows = []
    for name, data in tickers.items():
        ticker = Ticker()
        ticker.id = data["ticker"]
        ticker.name = data["title"]
        rows.append(ticker)

    with transaction.atomic():
        Ticker.objects.bulk_create(rows, ignore_conflicts=True)


def to_ticker(symbol):
    return symbol.split(".")[0].upper()


def read_eod_file(filepath):
    print("Processing: " + filepath)
    # 0 <TICKER>, 1 <PER>, 2 <DATE>, 3 <TIME>, 4 <OPEN>,
    # 5 <HIGH>, 6 <LOW>, 7 <CLOSE>, 8 <VOL>, 9 <OPENINT>
    data = []
    ticker = None
    symbol = None
    with open(filepath, "r") as f:
        firstline = True
        for line in f:
            if firstline:
                firstline = False
                print("importing ", filepath)
            else:
                cols = line.strip().split(",")
                # print(cols)
                eod = Eod()
                tick = to_ticker(cols[0])
                symbol = tick
                eod.id = tick + "-" + cols[2]
                if not ticker:
                    ticker = Ticker.objects.filter(id=tick)
                    if not ticker.exists():
                        print("NO_TICKER: " + tick)
                        break
                op = Decimal(cols[4])
                hi = Decimal(cols[5])
                if op > 10000000 or hi > 10000000:
                    print("BAD_DATA: " + line)
                    return None
                eod.ticker = Ticker(id=tick)
                eod.day = datetime.strptime(cols[2], "%Y%m%d").date()
                eod.open = Decimal(cols[4])
                eod.close = Decimal(cols[7])
                eod.high = Decimal(cols[5])
                eod.low = Decimal(cols[6])
                eod.volume = Decimal(cols[8])
                eod.volume = math.floor(eod.volume)
                data.append(eod)
                # print(eod)
    if not ticker or not ticker.exists():
        return None

    last_eod = Eod.objects.filter(ticker=symbol).order_by("-day").first()

    if last_eod and data[-1].day == last_eod.day:
        print("SKIPPING: " + filepath)
        return None

    return data


def import_eod_file(filepath):
    try:
        data = read_eod_file(filepath)
        if not data:
            print("NO_DATA: " + filepath)
            return
        with transaction.atomic():
            Eod.objects.bulk_create(data, ignore_conflicts=True)
        print("Imported file: " + filepath)
        return True
    except Exception as e:
        print("ERROR: " + str(e))
        return False


def glob_files(root):
    filepaths = []
    for name in glob.glob(root, recursive=True):
        filepaths.append(name)
        print(name)
    return filepaths


def import_eod_data(globpath="U:\\data\\stooq\\zip\\data\\daily\\**\\*.txt"):
    # loop thru stooq files
    # import into db
    filepaths = glob_files(globpath)
    counter = 0
    success = 0
    for filepath in filepaths:
        result = import_eod_file(filepath)
        if result:
            success += 1
        counter += 1
        print(
            "Imported file: "
            + filepath
            + "... "
            + str(success)
            + " / "
            + str(counter)
            + " of "
            + str(len(filepaths))
        )
    print("done")


if __name__ == "__main__":
    # import_all_tickers()
    # glob_files("U:\\data\\stooq\\zip\\data\\**\\*.txt")
    # read_eod_file("U:\\data\\stooq\\zip\\data\\daily\\us\\nysemkt stocks\\gsat.us.txt")
    import_eod_data()
