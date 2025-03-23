import urllib
from datetime import datetime, timedelta
import datetime
import pandas as pd
# from nsedt import utils
# from nsedt.resources import constants as cns
# from nsedt.utils import data_format
from nselib import capital_market as cm
from nselib import derivatives as dv
# from nsedt import indices as ind
# from nsedt import equity as eq
from datetime import date

INDICES = ["NIFTY", "FINNIFTY", "BANKNIFTY", "MIDCPNIFTY"]
format = '%d-%m-%Y'
def futures(symbol, inst, start_date, end_date):
    new_data = dv.future_price_volume_data(symbol=symbol, instrument=inst, from_date=start_date, to_date=end_date)
    return new_data

def get_futures_prices(symbol, instrument, start, end):
    start = datetime.datetime.strptime(start, "%Y-%m-%d")
    end = datetime.datetime.strptime(end, "%Y-%m-%d")
    start = datetime.datetime.strftime(start, format)
    end = datetime.datetime.strftime(end, format)
    res_date = start
    dates = []
    dataset = pd.DataFrame()
    # while res_date <= end:
    #     dates.append(str(res_date.strftime("%d-%m-%Y")))
    #     res_date += datetime.timedelta(days=30)
    #     if end - start >= datetime.timedelta(days=29):
    #         dates.append(
    #             str((res_date - datetime.timedelta(days=1)).strftime("%d-%m-%Y"))
    #         )
    # dates.append(str(end.strftime("%d-%m-%Y")))
    # for i in range(len(dates) - 1):
    #     data = futures(symbol, dates[i], dates[i + 1])
    #     dataset = pd.concat([dataset, data], ignore_index=True, sort=True)
    dataset = futures(symbol, instrument, start, end)
    dataset = dataset.drop(
        [
            # "_id",
            "INSTRUMENT",
            "SYMBOL",
            "STRIKE_PRICE",
            "OPTION_TYPE",
            "MARKET_TYPE",
            "SETTLE_PRICE",
            "TOT_TRADED_QTY",
            "TOT_TRADED_VAL",
            "OPEN_INT",
            "CHANGE_IN_OI",
            "UNDERLYING_VALUE",
            # "TIMESTAMP",
        ],
        axis=1,
    )
    dataset = dataset.drop_duplicates(ignore_index=True)

    # find nearest expiry dates
    new_df = pd.DataFrame()
    data = dataset
    data["TIMESTAMP"] = pd.to_datetime(data["TIMESTAMP"], format="%d-%b-%Y")
    data["EXPIRY_DT"] = pd.to_datetime(data["EXPIRY_DT"], format="%d-%b-%Y")

    sorted_unique_dates = sorted(set(data["TIMESTAMP"]))

    for i in sorted_unique_dates:
        temp_df = data[data["TIMESTAMP"] == i]
        min_exp_deets = temp_df[
            (
                temp_df["EXPIRY_DT"]
                == (i + min(abs(temp_df["EXPIRY_DT"] - temp_df["TIMESTAMP"])))
            )
            & (temp_df["TIMESTAMP"] == i)
        ]
        new_df = pd.concat([new_df, min_exp_deets], ignore_index=True)
    new_df.rename(
        columns={
            "OPENING_PRICE": "Open",
            "TRADE_HIGH_PRICE": "High",
            "CLOSING_PRICE": "Close",
            "TRADE_LOW_PRICE": "Low",
            "EXPIRY_DT": "Expiry Date",
            "MARKET_LOT": "Lot Size",
        },
        inplace=True,
    )

    new_df = new_df.drop_duplicates(subset=["TIMESTAMP"], ignore_index=True)
    return new_df.set_index("TIMESTAMP")
    # return data


def get_equity_prices(symbol, start, end):
    start = datetime.datetime.strptime(start, "%Y-%m-%d")
    end = datetime.datetime.strptime(end, "%Y-%m-%d")
    start = datetime.datetime.strftime(start, format)
    end = datetime.datetime.strftime(end, format)
    data = cm.price_volume_and_deliverable_position_data(symbol=symbol, from_date=start, to_date=end)
    # data = data.set_index('Date')
    data.rename(
        columns={
            "OpenPrice": "Open",
            "HighPrice": "High",
            "ClosePrice": "Close",
            "LowPrice": "Low",
        },
        inplace=True,
    )
    return (
        data.sort_values(by=["Date"], ignore_index=True)
        .drop_duplicates(ignore_index=True)
        .set_index("Date")
    )


def get_index_prices(symbol, start, end):
    start = datetime.datetime.strptime(start, "%Y-%m-%d")
    end = datetime.datetime.strptime(end, "%Y-%m-%d")
    # print(ind.get_price(start_date=start_date, end_date=end_date, symbol="NIFTY 50"))
    start = datetime.datetime.strftime(start, format)
    end = datetime.datetime.strftime(end, format)
    data = cm.index_data(index=symbol, from_date=start, to_date=end)
    # To change date format from '%d-%b-%Y' to '%Y-%m-%d'
    data["Date"] = pd.to_datetime(data["Date"], format="%d-%b-%Y")
    data.rename(
        columns={
            "OpenPrice": "Open",
            "HighPrice": "High",
            "ClosePrice": "Close",
            "LowPrice": "Low",
        },
        inplace=True,
    )
    return (
        data.sort_values(by=["Date"], ignore_index=True)
        .drop_duplicates(ignore_index=True)
        .set_index("Date")
    )


def get_all_symbols_list():
    f_dict = cm.fno_equity_list()
    eq_list = []
    for i in f_dict['symbol']:
        eq_list.append(f'{i} FUT')
        eq_list.append(f'{i} EQ')
    for item in INDICES:
        eq_list.append(f"{item} FUT")
        eq_list.append(f"{item} EQ")
    return eq_list

# data = get_futures_prices("NIFTY", "2024-05-25", "2024-12-25")
# print("Hi!")
# data = get_all_symbols_list()
# print(data)
# data.to_csv("scraped_data.csv")