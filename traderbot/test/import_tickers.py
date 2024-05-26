from datetime import datetime
from decimal import Decimal
import functools
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
                eod, status = process_eod_row(line, ticker)
                if status == "invalid":
                    break
                if not eod:
                    continue
                ticker = eod.ticker
                data.append(eod)
                # print(eod)
    if not ticker or not ticker.exists():
        return None

    last_eod = Eod.objects.filter(ticker=symbol).order_by("-day").first()

    if last_eod and data[-1].day == last_eod.day:
        print("SKIPPING: " + filepath)
        return None

    return data


def process_eod_row(line, ticker=None):
    cols = line.strip().split(",")
    # print(cols)
    eod = Eod()
    tick = to_ticker(cols[0])
    symbol = tick
    eod.id = tick + "-" + cols[2]
    if not ticker:
        ticker = get_ticker(tick)
        # ticker = Ticker.objects.filter(id=tick)
        # if not ticker.exists():
        if not ticker:
            print("NO_TICKER: " + tick)
            return None, "invalid"
        else:
            print("FOUND_TICKER: " + tick)

    op = Decimal(cols[4])
    hi = Decimal(cols[5])
    if op > 10000000 or hi > 10000000:
        print("BAD_DATA: " + line)
        return None, None
    eod.ticker = Ticker(id=tick)
    eod.day = datetime.strptime(cols[2], "%Y%m%d").date()
    eod.open = Decimal(cols[4])
    eod.close = Decimal(cols[7])
    eod.high = Decimal(cols[5])
    eod.low = Decimal(cols[6])
    eod.volume = Decimal(cols[8])
    eod.volume = math.floor(eod.volume)
    return eod, None


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


def cmp_eod(a, b):
    if a.ticker.id < b.ticker.id:
        return -1
    elif a.ticker.id > b.ticker.id:
        return 1
    elif a.day < b.day:
        return -1
    elif a.day > b.day:
        return 1
    else:
        return 0


def import_delta(filepath):
    # read file
    mismatches = []
    missing_stocks = []

    rows = []
    idx = 0
    errors = []
    with open(filepath, "r") as f:
        for line in f:
            idx += 1
            if idx == 1:
                continue
            eod, status = process_eod_row(line, ticker=None)
            if not eod:
                continue
            rows.append(eod)

    print(rows)

    # order by symbol, date
    rows.sort(key=functools.cmp_to_key(cmp_eod))

    # load latest N for symbol
    ticker = None
    existing = None
    skipTicker = False

    new_rows = []

    for idx in range(len(rows)):
        eod = rows[idx]
        if ticker != eod.ticker.id:
            existing = Eod.objects.filter(
                ticker__id=eod.ticker.id, day__gte=eod.day
            ).all()
            ticker = eod.ticker.id
            skipTicker = False
            print("Getting ", eod.ticker.id, eod.day, existing)
        elif skipTicker:
            print("SKIPPING_EOD", ticker)
            continue

        existingRecord = False
        for item in existing:
            if item.day == eod.day and abs(item.close - eod.close) > max(
                Decimal(0.02) * eod.close, Decimal(0.5)
            ):
                mismatches.append(
                    {"item": item, "existing.close": item.close, "eod.close": eod.close}
                )
                skipTicker = True
                break
            elif item.day == eod.day:
                existingRecord = True

        if skipTicker:
            continue

        if existingRecord:
            continue

        new_rows.append(eod)

    with transaction.atomic():
        Eod.objects.bulk_create(new_rows, ignore_conflicts=True)

    print("ADDED_ROWS", len(new_rows))
    print(new_rows)

    print("MISMATCHES", len(mismatches))
    print(mismatches)

    # compare with current prices
    # if not match, throw error
    # else, add new data


# all_tickers = None
all_tickers = None


def get_ticker(ticker):
    global all_tickers
    if not all_tickers:
        tickers = Ticker.objects.all()
        all_tickers = {}
        for tick in tickers:
            all_tickers[tick.id] = tick
    return all_tickers.get(ticker)


# daily update
# curl 'https://stooq.com/db/d/?d=20240515+20240516+20240517+20240518+20240519+20240520+20240521+20240522+20240523+20240524+20240525&t=d' \
#   -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' \
#   -H 'Accept-Language: en-US,en;q=0.9' \
#   -H 'Connection: keep-alive' \
#   -H 'Cookie: uid=usbdi78ap7v6dtsuws1y19ems1; PHPSESSID=u4kv2es0r0e2qdeko2vu9s9jd2; cookie_user=%7E00006enrka010fb; cookie_uu=240525000; __gads=ID=4d4e4c4c11458634:T=1714198471:RT=1716614978:S=ALNI_MZ2FZH0kZdvdrhl5wvNhJZKHU0tkA; __eoi=ID=77f0b3a021ceafd7:T=1714198471:RT=1716614978:S=AA-AfjZxCTRamPuGShZJvyBrn_BR' \
#   -H 'If-Modified-Since: Sat, 25 May 2024 07:32:43 GMT' \
#   -H 'Referer: https://stooq.com/db/' \
#   -H 'Sec-Fetch-Dest: document' \
#   -H 'Sec-Fetch-Mode: navigate' \
#   -H 'Sec-Fetch-Site: same-origin' \
#   -H 'Sec-Fetch-User: ?1' \
#   -H 'Upgrade-Insecure-Requests: 1' \
#   -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36' \
#   -H 'sec-ch-ua: "Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"' \
#   -H 'sec-ch-ua-mobile: ?0' \
#   -H 'sec-ch-ua-platform: "Windows"'


# curl 'https://stooq.com/db/d/?d=20240515+20240516+20240517+20240518+20240519+20240520+20240521+20240522+20240523+20240524+20240525&t=d' \
#   -H 'Cookie: uid=usbdi78ap7v6dtsuws1y19ems1; PHPSESSID=u4kv2es0r0e2qdeko2vu9s9jd2; cookie_user=%7E00006enrka010fb; cookie_uu=240525000; __gads=ID=4d4e4c4c11458634:T=1714198471:RT=1716614978:S=ALNI_MZ2FZH0kZdvdrhl5wvNhJZKHU0tkA; __eoi=ID=77f0b3a021ceafd7:T=1714198471:RT=1716614978:S=AA-AfjZxCTRamPuGShZJvyBrn_BR'

# curl 'https://stooq.com/db/d/?d=20240515+20240516+20240517+20240518+20240519+20240520+20240521+20240522+20240523+20240524+20240525&t=d' \
#   -H 'Cookie: uid=usbdi78ap7v6dtsuws1y19ems1; PHPSESSID=u4kv2es0r0e2qdeko2vu9s9jd2; cookie_user=%7E00006enrka010fb; cookie_uu=240525000; __gads=ID=4d4e4c4c11458634:T=1714198471:RT=1716614978:S=ALNI_MZ2FZH0kZdvdrhl5wvNhJZKHU0tkA; __eoi=ID=77f0b3a021ceafd7:T=1714198471:RT=1716614978:S=AA-AfjZxCTRamPuGShZJvyBrn_BR'

if __name__ == "__main__":
    # import_all_tickers()
    # glob_files("U:\\data\\stooq\\zip\\data\\**\\*.txt")
    # read_eod_file("U:\\data\\stooq\\zip\\data\\daily\\us\\nysemkt stocks\\gsat.us.txt")

    # import_eod_data()
    import_delta(filepath="U:\\data\\stooq\\delta\\data_d20240525.txt")
    # import_delta(filepath="U:\\data\\stooq\\delta\\test.txt")
