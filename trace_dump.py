import urllib
from datetime import datetime, timedelta
import datetime
import pandas as pd
from nsedt import utils
from nsedt.resources import constants as cns
from nsedt.utils import data_format
import requests as req
from nsedt import indices as ind
from nsedt import equity as eq
from datetime import date
import httpx
import chardet
import json
import codecs
import base64
import pickle
import zlib

def futures(symbol, start_date, end_date):
    base_url = "https://www.nseindia.com/"
    event_api = "api/historical/foCPV?"
    header = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.6",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }

    params = {
        "symbol": symbol,
        "from": start_date,
        "to": end_date,
    }
    if symbol in cns.INDICES:
        params["instrumentType"] = "FUTIDX"
    else:
        params["instrumentType"] = "FUTSTK"

    cookies = utils.get_cookies()
    url = base_url + event_api + urllib.parse.urlencode(params)
    print(url)
    # data = utils.fetch_url(url, cookies)#, response_type="json")
    data = req.get(url=url, cookies=cookies, headers=header)
    # print(data.text)
    print(data.content)
    print("\n================================================================\n")
    print(chardet.detect(data.content)['encoding'])
    data = data.text.decode('utf-8', errors='ignore')
    print(data)
    print("\n================================================================\n")
    data = json.loads(data)
    print(data)
    print("\n================================================================\n")
    if data["data"]:
        new_data = pd.json_normalize(data["data"])
        # print(new_data)

        # new_data.columns = [
        #     "_id",
        #     "FH_INSTRUMENT",
        #     "FH_SYMBOL",
        #     "FH_EXPIRY_DT",
        #     "FH_STRIKE_PRICE",
        #     "FH_OPTION_TYPE",
        #     "FH_MARKET_TYPE",
        #     "FH_OPENING_PRICE",
        #     "FH_TRADE_HIGH_PRICE",
        #     "FH_TRADE_LOW_PRICE",
        #     "FH_CLOSING_PRICE",
        #     "FH_LAST_TRADED_PRICE",
        #     "FH_PREV_CLS",
        #     "FH_SETTLE_PRICE",
        #     "FH_TOT_TRADED_QTY",
        #     "FH_TOT_TRADED_VAL",
        #     "FH_OPEN_INT",
        #     "FH_CHANGE_IN_OI",
        #     "FH_MARKET_LOT",
        #     "FH_TIMESTAMP",
        #     "FH_UNDERLYING_VALUE",
        #     "TIMESTAMP",
        # ]

        return new_data

def get_futures_prices(symbol, start, end):
    start = datetime.datetime.strptime(start, "%Y-%m-%d")
    end = datetime.datetime.strptime(end, "%Y-%m-%d")
    res_date = start
    dates = []
    dataset = pd.DataFrame()
    while res_date <= end:
        dates.append(str(res_date.strftime("%d-%m-%Y")))
        res_date += datetime.timedelta(days=30)
        if end - start >= datetime.timedelta(days=29):
            dates.append(
                str((res_date - datetime.timedelta(days=1)).strftime("%d-%m-%Y"))
            )
    dates.append(str(end.strftime("%d-%m-%Y")))
    for i in range(len(dates) - 1):
        data = futures(symbol, dates[i], dates[i + 1])
        dataset = pd.concat([dataset, data], ignore_index=True, sort=True)
    dataset = dataset.drop(
        [
            "_id",
            "FH_INSTRUMENT",
            "FH_SYMBOL",
            "FH_STRIKE_PRICE",
            "FH_OPTION_TYPE",
            "FH_MARKET_TYPE",
            "FH_SETTLE_PRICE",
            "FH_TOT_TRADED_QTY",
            "FH_TOT_TRADED_VAL",
            "FH_OPEN_INT",
            "FH_CHANGE_IN_OI",
            "FH_UNDERLYING_VALUE",
            "TIMESTAMP",
        ],
        axis=1,
    )
    dataset = dataset.drop_duplicates(ignore_index=True)

    # find nearest expiry dates
    new_df = pd.DataFrame()
    data = dataset
    data["FH_TIMESTAMP"] = pd.to_datetime(data["FH_TIMESTAMP"], format="%d-%b-%Y")
    data["FH_EXPIRY_DT"] = pd.to_datetime(data["FH_EXPIRY_DT"], format="%d-%b-%Y")

    sorted_unique_dates = sorted(set(data["FH_TIMESTAMP"]))

    for i in sorted_unique_dates:
        temp_df = data[data["FH_TIMESTAMP"] == i]
        min_exp_deets = temp_df[
            (
                temp_df["FH_EXPIRY_DT"]
                == (i + min(abs(temp_df["FH_EXPIRY_DT"] - temp_df["FH_TIMESTAMP"])))
            )
            & (temp_df["FH_TIMESTAMP"] == i)
        ]
        new_df = pd.concat([new_df, min_exp_deets], ignore_index=True)
    new_df.rename(
        columns={
            "FH_OPENING_PRICE": "Open",
            "FH_TRADE_HIGH_PRICE": "High",
            "FH_CLOSING_PRICE": "Close",
            "FH_TRADE_LOW_PRICE": "Low",
            "FH_EXPIRY_DT": "Expiry Date",
            "FH_MARKET_LOT": "Lot Size",
        },
        inplace=True,
    )

    new_df = new_df.drop_duplicates(subset=["FH_TIMESTAMP"], ignore_index=True)
    return new_df.set_index("FH_TIMESTAMP")
    # return data


def get_all_symbols_list():
    client = httpx.Client()
    cookies = utils.get_cookies()
    base_url = cns.BASE_URL
    session = req.Session()
    # base_url = "https://www.nseindia.com/"
    event_api = "api/market-data-pre-open?key=FO"
    header = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.6",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }

    url = base_url + event_api
    print(url)
    data = req.get(url=url, cookies=cookies, headers=header)
    print("\n================================================================\n")
    print(data.content)
    print("\n================================================================\n")
    print(data.content.decode('utf-8'))
    f_dict = data.to_dict()
    eq_list = []
    for i in range(len(f_dict["data"])):
        eq_list.append(f'{f_dict["data"][i]["metadata"]["symbol"]} FUT')
        eq_list.append(f'{f_dict["data"][i]["metadata"]["symbol"]} EQ')
    for item in cns.INDICES:
        eq_list.append(f"{item} FUT")
        eq_list.append(f"{item} EQ")
    return eq_list

print("Hi!")
try:
    data = get_futures_prices("TCS", "2024-05-25", "2024-06-25")
    print(data)
except Exception as e:
    print(e)
print("\nXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\n")
try:
    data = futures("TCS", "2024-05-25", "2024-06-25")
    print(data)
except Exception as e:
    print(e)
print("\nXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\n")
try:
    data = get_all_symbols_list()
    # print(data)
except Exception as e:
    print(e)