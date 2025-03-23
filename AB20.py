import futures as ft

# import yfinance as yf
import pandas as pd

# import matplotlib.pyplot as plt
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

global prev_hls
prev_hls = {"HH": 0, "LL": float("inf")}
prev_hl = {"High": 0, "Low": 0}
global sma
sma = []
excel_df = pd.DataFrame(
    columns=[
        "Action",
        "Trade_LS",
        "Entry_Date",
        "SMA",
        "Entry_Value",
        "Exit_Value",
        "Exit_Date",
        "Profit_Loss",
        "Stop_Loss",
    ]
)
trades = []


def sma_calc(i, ind_vals, days):
    i = i + days - 1
    adder = 0
    for j in range(i, i - days, -1):
        adder = adder + ind_vals[j]

    sma.append(adder / days)


def flag(sma, val_close, val_high, val_low, candle):
    if (
        sma[-1] > val_close
    ):  # and candle == "Red") or (sma[-1] >= val_low and sma[-1] >= val_high)): #
        prev_hl["Low"] = val_low
        return "Sell"
    if (
        sma[-1] < val_close
    ):  # and candle == "Green") or (sma[-1] <= val_low and sma[-1] <= val_high)):
        prev_hl["High"] = val_high
        return "Buy"


def trade(
    fig,
    entry_buff,
    exit_buff,
    i,
    action,
    open_val,
    high_val,
    low_val,
    close_val,
    date_val,
    candle,
    ind_history,
    line,
    days,
    msl,
    bep,
):
    global prev_hls
    global prev_hl
    buff_high = prev_hl["High"] * entry_buff * 0.01  # buffer to exeute buy
    buff_low = prev_hl["Low"] * entry_buff * 0.01  # buffer to execute sell
    buffer_high = prev_hl["High"] + buff_high  # top + buffer
    buffer_low = prev_hl["Low"] - buff_low  # bottom - buffer

    try:
        if trades[-1]["Action"] == "Sell" and trades[-1]["Trade_LS"] == "Short":
            trade_exit(
                buffer_high,
                buffer_low,
                fig,
                entry_buff,
                exit_buff,
                trades,
                open_val,
                close_val,
                high_val,
                low_val,
                date_val,
                candle,
                i,
                ind_history,
                line,
                days,
            )
    except:
        pass

    try:
        if prev_hl["High"] and prev_hl["Low"]:
            if (
                trades
                and trades[-1]["Trade_LS"] == "Long"
                and high_val > prev_hls["HH"]
            ):
                prev_hls["HH"] = high_val

            elif (
                trades
                and trades[-1]["Trade_LS"] == "Short"
                and low_val < prev_hls["LL"]
            ):
                prev_hls["LL"] = low_val
        # print(action)
        if action == "Buy":
            # print("Entered buy")
            if (
                (trades)
                and trades[-1]["Action"] == "Buy"
                and trades[-1]["Trade_LS"] == "Long"
            ):
                # print("Hold")
                pass
            else:
                if high_val > buffer_high:
                    Buy(
                        fig,
                        buffer_high,
                        open_val,
                        high_val,
                        low_val,
                        date_val,
                        i,
                        ind_history,
                        line,
                        days,
                        msl,
                    )

        if (
            (trades)
            and trades[-1]["Action"] == "Buy"
            and trades[-1]["Trade_LS"] == "Long"
        ):
            buy = trades[-1]["Entry_Value"]
            sl = trades[-1]["Stop_Loss"]
            if sl == buy and bep == "yes":
                pass
            # print("SMA = ", sma[-1], "SL = ", sl)
            if buy <= sma[-1]:
                sl = sma[-1]
                trades[-1]["Stop_Loss"] = round(sl, 2)
                # print("passed sma for buy")
            if sl != buy and sl != sma[-1] and bep == "yes":
                threshold = buy + (buy * msl * 0.01)
                if high_val >= threshold:
                    sl = buy
                trades[-1]["Stop_Loss"] = round(sl, 2)

        if (
            (trades)
            and trades[-1]["Action"] == "Buy"
            and trades[-1]["Trade_LS"] == "Long"
        ):
            trade_exit(
                buffer_high,
                buffer_low,
                fig,
                entry_buff,
                exit_buff,
                trades,
                open_val,
                close_val,
                high_val,
                low_val,
                date_val,
                candle,
                i,
                ind_history,
                line,
                days,
            )

        if action == "Sell":
            if (
                (trades)
                and trades[-1]["Action"] == "Sell"
                and trades[-1]["Trade_LS"] == "Short"
            ):
                # print("Hold")
                pass
            else:
                if low_val < buffer_low:
                    Sell(
                        fig,
                        buffer_low,
                        open_val,
                        low_val,
                        high_val,
                        date_val,
                        i,
                        ind_history,
                        line,
                        days,
                        msl,
                    )

        if (
            (trades)
            and trades[-1]["Action"] == "Sell"
            and trades[-1]["Trade_LS"] == "Short"
        ):
            sell = trades[-1]["Entry_Value"]
            sl = trades[-1]["Stop_Loss"]
            if sl == sell and bep == "yes":
                pass
            # print("SMA = ", sma[-1], "SL = ", sl)
            if sell >= sma[-1]:
                sl = sma[-1]
                # print("passed sma for buy")
                trades[-1]["Stop_Loss"] = round(sl, 2)

            if sl != sell and sl != sma[-1] and bep == "yes":
                threshold = sell - (sell * msl * 0.01)
                if low_val <= threshold:
                    sl = sell
                trades[-1]["Stop_Loss"] = round(sl, 2)

        if (
            (trades)
            and trades[-1]["Action"] == "Sell"
            and trades[-1]["Trade_LS"] == "Short"
        ):
            trade_exit(
                buffer_high,
                buffer_low,
                fig,
                entry_buff,
                exit_buff,
                trades,
                open_val,
                close_val,
                high_val,
                low_val,
                date_val,
                candle,
                i,
                ind_history,
                line,
                days,
            )

    except Exception as e:
        # print(e)
        pass


def Buy(
    fig, buy_val, val_open, val_high, val_low, date_val, i, ind_history, line, days, msl
):
    if trades and trades[-1]["Trade_LS"] == "Short":
        trades[-1]["HH/LL"] = val_low
    prev_hls["HH"] = val_high
    # print("Entered buy")
    buy = buy_val
    if buy < val_low:
        buy = val_open
    sl = buy - (buy * msl * 0.01)
    trades.append(
        {
            "Action": "Buy",
            "Trade_LS": "Long",
            "Entry_Date": date_val.strftime("%Y-%m-%d"),
            "SMA": round(sma[-1], 2),
            "Entry_Value": round(buy, 2),
            "Exit_Value": 0,
            "Exit_Date": 0,
            "Profit_Loss": 0,
            "Stop_Loss": round(sl, 2),
        }
    )
    fig.add_annotation(
        x=ind_history[line].index[i + days],
        y=buy,
        ax=20,
        ay=50,
        text="Buy<br>" + str(buy),
        showarrow=True,
        arrowhead=5,
    )


def Sell(
    fig,
    sell_val,
    val_open,
    val_low,
    val_high,
    date_val,
    i,
    ind_history,
    line,
    days,
    msl,
):
    global prev_hls
    if trades and trades[-1]["Trade_LS"] == "Long":
        trades[-1]["HH/LL"] = val_high
    # print("Entered Sell")
    prev_hls["LL"] = val_low
    sell = sell_val
    if sell > val_high:
        sell = val_open
    sl = sell + (sell * msl * 0.01)
    trades.append(
        {
            "Action": "Sell",
            "Trade_LS": "Short",
            "Entry_Date": date_val.strftime("%Y-%m-%d"),
            "SMA": round(sma[-1], 2),
            "Entry_Value": round(sell, 2),
            "Exit_Value": 0,
            "Exit_Date": 0,
            "Profit_Loss": 0,
            "Stop_Loss": round(sl, 2),
        }
    )
    fig.add_annotation(
        x=ind_history[line].index[i + days],
        y=sell,
        ax=20,
        ay=50,
        text="Sell<br>" + str(sell),
        showarrow=True,
        arrowhead=5,
    )


def trade_exit(
    buffer_high,
    buffer_low,
    fig,
    entry_buff,
    exit_buff,
    trades,
    val_open,
    val_close,
    val_high,
    val_low,
    date_val,
    candle,
    i,
    ind_history,
    line,
    days,
):
    global prev_hls
    try:
        # print(f"sl = {sl}, date = {date_val.strftime('%Y-%m-%d')}")
        # print(trades[-1]["Action"], trades[-1]["Trade_LS"])
        if (
            trades[-1]["Action"] == "Buy" and trades[-1]["Trade_LS"] == "Long"
        ):  # and (val_open > val_close)#
            if (
                date_val.strftime("%Y-%m-%d") == trades[-1]["Entry_Date"]
            ) and candle == "Green":
                pass
            else:
                # print("Entered buy exit")
                buff_exit = prev_hl["Low"] - (prev_hl["Low"] * exit_buff * 0.01)
                tsl = trades[-1]["Stop_Loss"]
                sl = max(tsl, buff_exit)
                if sl > val_open or sl > val_low or sl > val_high or sl > val_close:
                    if sl > val_high:
                        sl = val_open
                    # trades[-1]["Trade_LS"] = "Stop Loss triggered"
                    trades[-1]["Exit_Date"] = date_val.strftime("%Y-%m-%d")
                    trades[-1]["Exit_Value"] = round(sl, 2)
                    if sl == tsl:
                        trades[-1]["Trade_LS"] = "MSL"
                    else:
                        trades[-1]["Trade_LS"] = "MSL"

                    trades[-1]["HH/LL"] = prev_hls["HH"]
                    prev_hls = {"HH": 0, "LL": float("inf")}
                    fig.add_annotation(
                        x=ind_history[line].index[i + days],
                        y=sl,
                        ax=20,
                        ay=50,
                        text="Exit<br>" + str(sl),
                        showarrow=True,
                        arrowhead=5,
                        bordercolor="#c7c7c7",
                        borderwidth=2,
                        borderpad=4,
                        bgcolor="#ff7f0e",
                        opacity=0.8,
                    )

        if (
            trades[-1]["Action"] == "Sell" and trades[-1]["Trade_LS"] == "Short"
        ):  # and (val_open < val_close)
            if (
                date_val.strftime("%Y-%m-%d") == trades[-1]["Entry_Date"]
            ) and candle == "Red":
                pass
            else:
                # print("Entered sell Exit")
                buff_exit = prev_hl["High"] + (prev_hl["High"] * exit_buff * 0.01)
                tsl = trades[-1]["Stop_Loss"]
                sl = min(tsl, buff_exit)
                if sl < val_close or sl < val_high or sl < val_open or sl < val_low:
                    if sl < val_low:
                        sl = val_open
                    # trades[-1]["Trade_LS"] = "Exit"
                    if sl == tsl:
                        trades[-1]["Trade_LS"] = "MSL"
                    else:
                        trades[-1]["Trade_LS"] = "MSL"
                    trades[-1]["HH/LL"] = prev_hls["LL"]
                    prev_hls = {"HH": 0, "LL": float("inf")}
                    trades[-1]["Exit_Date"] = date_val.strftime("%Y-%m-%d")
                    trades[-1]["Exit_Value"] = round(sl, 2)
                    fig.add_annotation(
                        x=ind_history[line].index[i + days],
                        y=sl,
                        ax=20,
                        ay=50,
                        text="Exit<br>" + str(sl),
                        showarrow=True,
                        arrowhead=5,
                        bordercolor="#c7c7c7",
                        borderwidth=2,
                        borderpad=4,
                        bgcolor="#ff7f0e",
                        opacity=0.8,
                    )

    except Exception as e:
        # print("Caught in trade exit", e)
        pass


def report(index, days, lot_size, bep):
    for i in range(1, len(trades)):
        try:
            if trades[i - 1]["Exit_Value"] == 0:
                trades[i - 1]["Exit_Value"] = trades[i]["Entry_Value"]
                trades[i - 1]["Exit_Date"] = trades[i]["Entry_Date"]
            if trades[i - 1]["Action"] == "Buy":
                trades[i - 1]["Profit_Loss"] = round(
                    trades[i - 1]["Exit_Value"] - trades[i - 1]["Entry_Value"], 2
                )
                trades[i - 1]["Action"] = "Long"
                trades[i - 1]["% ITM"] = round(
                    (
                        (trades[i - 1]["HH/LL"] - trades[i - 1]["Entry_Value"])
                        / trades[i - 1]["Entry_Value"]
                    )
                    * 100,
                    2,
                )
            else:
                trades[i - 1]["Profit_Loss"] = round(
                    trades[i - 1]["Entry_Value"] - trades[i - 1]["Exit_Value"], 2
                )
                trades[i - 1]["Action"] = "Short"
                trades[i - 1]["% ITM"] = round(
                    (
                        (trades[i - 1]["Entry_Value"] - trades[i - 1]["HH/LL"])
                        / trades[i - 1]["Entry_Value"]
                    )
                    * 100,
                    2,
                )

            if trades[i - 1]["Profit_Loss"] == 0 and bep == "yes":
                trades[i - 1]["Trade_LS"] = "BEP"

            if index[1] == "FUT":
                trades[i - 1]["Lot_Size"] = lot_size
            if (i - 1) == 0:
                trades[i - 1]["Cumm PL"] = trades[i - 1]["Profit_Loss"]
            else:
                trades[i - 1]["Cumm PL"] = (
                    trades[i - 1]["Profit_Loss"] + trades[i - 2]["Cumm PL"]
                )

            trades[i - 1]["System"] = str(days) + "AB"

        except Exception as e:
            # print("report error", e)
            pass
    excel_df = pd.DataFrame()
    # excel_df = pd.DataFrame(
    #     columns=[
    #         "Action",
    #         "Trade_LS",
    #         "Entry_Date",
    #         "SMA",
    #         "Entry_Value",
    #         "Exit_Value",
    #         "Exit_Date",
    #         "Profit_Loss",
    #         "Stop_Loss",
    #     ]
    # )
    try:
        if index[1] == "FUT":
            trades[-1]["Lot_Size"] = lot_size

        trades[-1]["System"] = str(days) + "AB"
        for i in trades:
            row = pd.DataFrame([i])
            excel_df = pd.concat([excel_df, row], ignore_index=True)

        excel_df = excel_df.drop(["SMA", "Stop_Loss"], axis=1)
        print(excel_df)
        if index[1] == "FUT":
            excel_df = excel_df.iloc[:, [11, 2, 5, 0, 9, 3, 4, 6, 10, 1, 7, 8]]
        else:
            excel_df = excel_df.iloc[:, [10, 2, 5, 0, 3, 4, 6, 9, 1, 7, 8]]
        excel_df.index += 1

    except:
        pass

    excel_df.rename(
        columns={
            "Entry_Date": "Entry Date",
            "Exit_Date": "Exit Date",
            "Action": "Trade",
            "Entry_Value": "Entry",
            "Exit_Value": "Exit",
            "Profit_Loss": "P&L",
            "Lot_Size": "Lot Size",
            "Trade_LS": "Comments",
        },
        inplace=True,
    )

    # print("\nexcel after appending:")
    # print(excel_df)
    # print("\n\n")
    # excel_df.to_csv("reportAB.csv")
    return excel_df


def set_up():
    global sma
    global trades
    global prev_hl
    global prev_hls
    prev_hl = {"High": 0, "Low": 0}
    prev_hls = {"HH": 0, "LL": float("inf")}
    sma = []
    excel_df = pd.DataFrame(
        columns=[
            "Action",
            "Trade_LS",
            "Entry_Date",
            "SMA",
            "Entry_Value",
            "Exit_Value",
            "Exit_Date",
            "Profit_Loss",
            "Stop_Loss",
        ]
    )
    trades = []


def run(info):
    set_up()
    index = info[0].split()
    line = info[1]
    entry_buff = info[2]
    exit_buff = info[3]
    days = info[4]
    msl = info[5]
    bep = info[6]
    start_date = info[7]
    end_date = info[8]

    # ind = yf.Ticker(index)
    if (
        index[0] == "NIFTY" or index[0] == "BANKNIFTY" or index[0] == "FINNIFTY"
    ) and index[1] == "EQ":
        ind_history = ft.get_index_prices(index[0], start_date, end_date)
    elif index[1] == "FUT":
        ind_history = ft.get_futures_prices(index[0], start_date, end_date)
    elif index[1] == "EQ":
        ind_history = ft.get_equity_prices(index[0], start_date, end_date)
    # ind_history = ind.history(start= "2022-09-27", end = "2022-11-26")
    ind_date = pd.Index.tolist(ind_history[line].index)
    ind_vals = [float(ele) for ele in pd.Series.tolist(ind_history[line])]

    # print(ind_history)

    ind_open_or = [
        float(ele) for ele in pd.Series.tolist(ind_history["Open"])
    ]  # open values
    ind_high_or = [
        float(ele) for ele in pd.Series.tolist(ind_history["High"])
    ]  # high values
    ind_low_or = [
        float(ele) for ele in pd.Series.tolist(ind_history["Low"])
    ]  # low values
    ind_close_or = [
        float(ele) for ele in pd.Series.tolist(ind_history["Close"])
    ]  # close values
    if index[1] == "FUT":
        lot_size = [float(ele) for ele in pd.Series.tolist(ind_history["Lot Size"])]
        lot_size = lot_size[-1]
    ind_date = ind_date[days:]
    ind_open = ind_open_or[days:]
    ind_high = ind_high_or[days:]
    ind_low = ind_low_or[days:]
    ind_close = ind_close_or[days:]

    # ind_history = ind_history.drop(['Volume', 'Dividends', 'Stock Splits'],axis = 1)
    # print(type(ind_history))
    # fig = px.line(ind_history, x = ind_history[line].index, y = [ind_history["Open"],ind_history["High"],ind_history["Low"],ind_history["Close"]])#.plot(label='Open')
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=ind_date, open=ind_open, high=ind_high, low=ind_low, close=ind_close
            )
        ]
    )
    # print(fig.layout.xaxis.range)

    for i in range(0, len(ind_open)):
        try:
            candle = "None"
            if ind_open[i] > ind_close[i]:
                candle = "Red"
            else:
                candle = "Green"
            sma_calc(i, ind_vals, days)
            action = flag(sma, ind_close[i], ind_high[i], ind_low[i], candle)
            trade(
                fig,
                entry_buff,
                exit_buff,
                i + 1,
                action,
                ind_open[i + 1],
                ind_high[i + 1],
                ind_low[i + 1],
                ind_close[i + 1],
                ind_date[i + 1],
                candle,
                ind_history,
                line,
                days,
                msl,
                bep,
            )

        except Exception as e:
            # print("Caught in for loop ", e)
            pass

    fig.add_trace(go.Scatter(x=ind_date, y=sma, line=dict(color="#0000ff")))
    # print(trades )
    # fig.show()
    # fig.write_html("20AB.html")
    if index[1] == "FUT":
        excel_df = report(index, days, lot_size, bep)
    else:
        excel_df = report(index, days, 1, bep)

    return excel_df


# run(("NIFTY FUT", "Close", 0.15, 0.15, 20, 3, "no", "2021-01-01", "2021-01-01"))
