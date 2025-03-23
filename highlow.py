import futures as ft
import mcx as mc
# import yfinance as yf
import pandas as pd

# import matplotlib.pyplot as plt
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go


global prev_hl
global prev_hls
global anomaly
prev_hl = {"High": 0, "Low": 0}
trades = []
prev_hls = {"HH": 0, "LL": float("inf")}
anomaly = False


def highest_lowest(i, ind_high, ind_low):
    high = max(ind_high[i], ind_high[i - 1])
    low = min(ind_low[i], ind_low[i - 1])

    prev_hl["High"] = high
    prev_hl["Low"] = low


def trade(
    bep,
    line,
    entry_buff,
    exit_buff,
    ind_history,
    val,
    val_open,
    val_high,
    val_low,
    val_close,
    i,
    fig,
    ind_date,
    msl,
):
    global day_count
    global prev_hls
    global anomaly
    candle = None
    trade_date, trade_action, trade_ls = ind_date[i], "null", "null"
    buff_top = prev_hl["High"] * entry_buff * 0.01  # buffer to exeute buy
    buff_bottom = prev_hl["Low"] * entry_buff * 0.01  # buffer to execute sell
    buffer_high = prev_hl["High"] + buff_top  # High + buffer
    buffer_low = prev_hl["Low"] - buff_bottom  # Low - buffer

    # print("called")
    # calculate if the candle is a red candle or green candle
    if val_close > val_open:
        candle = "Green"
    else:
        candle = "Red"

    if prev_hl["High"] and prev_hl["Low"]:
        try:
            if (
                trades
                and trades[-1]["Trade_LS"] == "Long"
                and val_high > prev_hls["HH"]
            ):
                prev_hls["HH"] = val_high

            elif (
                trades
                and trades[-1]["Trade_LS"] == "Short"
                and val_low < prev_hls["LL"]
            ):
                prev_hls["LL"] = val_low

            if (val_open > buffer_high or val_high > buffer_high) and (
                val_open < buffer_low or val_low < buffer_low
            ):
                # print("anomaly")
                anomaly = True
                check_backtesting_anomaly(
                    val_open,
                    entry_buff,
                    exit_buff,
                    bep,
                    line,
                    ind_history,
                    ind_date,
                    buffer_high,
                    buffer_low,
                    val_high,
                    val_low,
                    val_close,
                    candle,
                    i,
                    msl,
                    fig,
                )
                anomaly = False
            else:
                # check OHLC for buying
                if val_open >= (buffer_high) or val_high >= (buffer_high):
                    if (trades) and (
                        trades[-1]["Action"] == "Buy"
                        and trades[-1]["Trade_LS"] == "Long"
                    ):  # print("Hold")
                        pass
                    else:
                        if (
                            trades
                            and trades[-1]["Action"] == "Sell"
                            and trades[-1]["Trade_LS"] == "Short"
                            and bep == "yes"
                        ):
                            sell = trades[-1]["Entry_Value"]
                            tsl = trades[-1]["Stop_Loss"]
                            if tsl == sell:
                                pass
                            else:
                                threshold = sell - (sell * msl * 0.01)
                                if val_low <= threshold:
                                    tsl = sell
                                trades[-1]["Stop_Loss"] = round(tsl, 2)
                            trade_exit(
                                entry_buff,
                                exit_buff,
                                ind_history,
                                line,
                                trades,
                                val_open,
                                val_close,
                                val_high,
                                val_low,
                                ind_date[i],
                                candle,
                                i,
                                fig,
                            )

                        Buy(
                            val_open,
                            line,
                            ind_history,
                            ind_date,
                            val_high,
                            val_low,
                            buffer_high,
                            i,
                            msl,
                            fig,
                            bep,
                        )
                        day_count = 1

                if (
                    trades
                    and trades[-1]["Action"] == "Buy"
                    and trades[-1]["Trade_LS"] == "Long"
                    and bep == "yes"
                ):
                    # print("Entered BEP")
                    buy = trades[-1]["Entry_Value"]
                    tsl = trades[-1]["Stop_Loss"]
                    if tsl == buy:
                        pass
                    else:
                        threshold = buy + (buy * msl * 0.01)
                        if val_high >= threshold:
                            tsl = buy
                        trades[-1]["Stop_Loss"] = round(tsl, 2)

                if (
                    trades
                    and trades[-1]["Action"] == "Buy"
                    and trades[-1]["Trade_LS"] == "Long"
                ):
                    trade_exit(
                        entry_buff,
                        exit_buff,
                        ind_history,
                        line,
                        trades,
                        val_open,
                        val_close,
                        val_high,
                        val_low,
                        ind_date[i],
                        candle,
                        i,
                        fig,
                    )

                # check OHLC for selling
                if val_open <= (buffer_low) or val_low <= (buffer_low):
                    if (trades) and (
                        trades[-1]["Action"] == "Sell"
                        and trades[-1]["Trade_LS"] == "Short"
                    ):
                        # print("Hold")
                        pass

                    else:
                        # print("Entered Sell")
                        Sell(
                            val_open,
                            line,
                            ind_history,
                            ind_date,
                            val_low,
                            val_high,
                            buffer_low,
                            i,
                            msl,
                            fig,
                            bep,
                        )
                        day_count = 1

                if (
                    trades
                    and trades[-1]["Action"] == "Sell"
                    and trades[-1]["Trade_LS"] == "Short"
                    and bep == "yes"
                ):
                    sell = trades[-1]["Entry_Value"]
                    tsl = trades[-1]["Stop_Loss"]
                    if tsl == sell:
                        pass
                    else:
                        threshold = sell - (sell * msl * 0.01)
                        if val_low <= threshold:
                            tsl = sell
                        trades[-1]["Stop_Loss"] = round(tsl, 2)

                if (
                    trades
                    and trades[-1]["Action"] == "Sell"
                    and trades[-1]["Trade_LS"] == "Short"
                ):
                    trade_exit(
                        entry_buff,
                        exit_buff,
                        ind_history,
                        line,
                        trades,
                        val_open,
                        val_close,
                        val_high,
                        val_low,
                        ind_date[i],
                        candle,
                        i,
                        fig,
                    )

        except Exception as e:
            # print("trade error", e)
            pass


def Buy(
    val_open,
    line,
    ind_history,
    ind_date,
    val_high,
    val_low,
    buffer_high,
    i,
    msl,
    fig,
    bep,
):
    global prev_hls
    if trades and trades[-1]["Trade_LS"] == "Short":
        trades[-1]["HH/LL"] = val_low
    prev_hls["HH"] = val_high
    # print("Buy", ind_date[i])
    # print(trades)
    # msl =  buffer_high - (buffer_high * risk_percent * 0.01)
    buy = buffer_high
    # to make sure buy sell does not happen outside the graph
    if buffer_high < val_low:
        buy = val_open

    tsl = buy - (buy * msl * 0.01)
    threshold = buy + (buy * msl * 0.01)
    if val_high >= threshold and bep == "yes":
        tsl = buy
    # fig.add_trace(go.Scatter(x=[ind_history[line].index[i]], y=[buy], mode='markers', marker=dict(color='blue', size=12),showlegend=False, text=f"Action: Buy<br>Entry: {buy}<br>Date: {ind_date[i].strftime('%Y-%m-%d')}"))
    fig.add_annotation(
        x=ind_history[line].index[i],
        y=buy,
        ax=50,
        ay=-40,
        text="Buy<br>" + str(buy),
        showarrow=True,
        arrowhead=5,
    )
    trades.append(
        {
            "Action": "Buy",
            "Trade_LS": "Long",
            "Entry_Date": ind_date[i].strftime("%Y-%m-%d"),
            "Previous High": prev_hl["High"],
            "Previous Low": prev_hl["Low"],
            "Entry_Value": round(buy, 2),
            "Exit_Value": 0,
            "Exit_Date": 0,
            "Profit_Loss": 0,
            "Stop_Loss": round(tsl, 2),
        }
    )
    if trades[-2]["Trade_LS"] == "Short":
        trades[-2]["Trade_LS"] = "SAR"


def Sell(
    val_open,
    line,
    ind_history,
    ind_date,
    val_low,
    val_high,
    buffer_low,
    i,
    msl,
    fig,
    bep,
):
    global prev_hls
    if trades and trades[-1]["Trade_LS"] == "Long":
        trades[-1]["HH/LL"] = val_high
    # print("Sell", ind_date[i])
    prev_hls["LL"] = val_low
    # print(trades)
    # msl =  buffer_low + (buffer_low * risk_percent * 0.01)
    sell = buffer_low
    if buffer_low > val_high:
        sell = val_open
    tsl = sell + (sell * msl * 0.01)
    threshold = sell - (sell * msl * 0.01)
    if val_low <= threshold and bep == "yes":
        tsl = sell
    # fig.add_trace(go.Scatter(x=[ind_history[line].index[i]], y=[sell], mode='markers', marker=dict(color='yellow', size=12),showlegend=False, text=f"Action: Sell<br>Entry: {sell}<br>Date: {ind_date[i].strftime('%Y-%m-%d')}"))
    fig.add_annotation(
        x=ind_history[line].index[i],
        y=sell,
        ax=20,
        ay=50,
        text="Sell<br>" + str(sell),
        showarrow=True,
        arrowhead=5,
    )
    trades.append(
        {
            "Action": "Sell",
            "Trade_LS": "Short",
            "Entry_Date": ind_date[i].strftime("%Y-%m-%d"),
            "Previous High": prev_hl["High"],
            "Previous Low": prev_hl["Low"],
            "Entry_Value": round(sell, 2),
            "Exit_Value": 0,
            "Exit_Date": 0,
            "Profit_Loss": 0,
            "Stop_Loss": round(tsl, 2),
        }
    )
    if trades[-2]["Trade_LS"] == "Long":
        trades[-2]["Trade_LS"] = "SAR"


def trade_exit(
    entry_buff,
    exit_buff,
    ind_history,
    line,
    trades,
    val_open,
    val_close,
    val_high,
    val_low,
    date_val,
    candle,
    i,
    fig,
):
    global prev_hl
    global prev_hls
    try:
        tsl = trades[-1]["Stop_Loss"]
        # print(f"tsl = {tsl}, date = {date_val.strftime('%Y-%m-%d')} & ", trades[-1]["Entry_Date"], candle)
        # print(trades[-1]["Action"], trades[-1]["Trade_LS"])
        if (
            trades[-1]["Action"] == "Buy" and trades[-1]["Trade_LS"] == "Long"
        ):  # and (val_open > val_close)#
            if (
                date_val.strftime("%Y-%m-%d") == trades[-1]["Entry_Date"]
            ) and candle == "Green":
                # print("passed green candle")
                pass
            else:
                buff_exit = prev_hl["Low"] - (prev_hl["Low"] * exit_buff * 0.01)
                sl = max(tsl, buff_exit)
                if sl > val_open or sl > val_low or sl > val_high or sl > val_close:
                    # trades[-1]["Trade_LS"] = "Exit"
                    trades[-1]["Exit_Date"] = date_val.strftime("%Y-%m-%d")
                    if sl == tsl:
                        trades[-1]["Trade_LS"] = "MSL"
                        # print("TSL = ", sl)
                    else:
                        trades[-1]["Trade_LS"] = "SAR"

                    if sl < val_low or sl > val_high or sl > val_open:
                        trades[-1]["Exit_Value"] = val_open
                        sl = val_open
                    else:
                        trades[-1]["Exit_Value"] = round(sl, 2)

                    trades[-1]["HH/LL"] = prev_hls["HH"]
                    prev_hls = {"HH": 0, "LL": float("inf")}

                    fig.add_annotation(
                        x=date_val,
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
                buff_exit = prev_hl["High"] + (prev_hl["High"] * exit_buff * 0.01)
                sl = min(tsl, buff_exit)
                # print("Entered Sell exit")
                if sl < val_close or sl < val_high or sl < val_open or sl < val_low:
                    # trades[-1]["Trade_LS"] = "Exit"
                    trades[-1]["Exit_Date"] = date_val.strftime("%Y-%m-%d")
                    trades[-1]["HH/LL"] = prev_hls["LL"]
                    prev_hls = {"HH": 0, "LL": float("inf")}
                    fig.add_annotation(
                        x=date_val,
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
                    if sl == tsl:
                        trades[-1]["Trade_LS"] = "MSL"
                        # print("TSL = ", sl)
                    else:
                        trades[-1]["Trade_LS"] = "SAR"

                    if sl < val_low or sl > val_high or sl < val_open:
                        trades[-1]["Exit_Value"] = val_open
                        sl = val_open
                    else:
                        trades[-1]["Exit_Value"] = round(sl, 2)

                    fig.add_annotation(
                        x=date_val,
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
        # print("Exit error", e)
        pass


def check_backtesting_anomaly(
    val_open,
    entry_buff,
    exit_buff,
    bep,
    line,
    ind_history,
    ind_date,
    buffer_high,
    buffer_low,
    val_high,
    val_low,
    val_close,
    candle,
    i,
    msl,
    fig,
):
    if abs(val_high - val_close) < abs(val_low - val_close):
        if (trades) and (
            trades[-1]["Action"] == "Sell" and trades[-1]["Trade_LS"] == "Short"
        ):
            pass
        else:
            trade_exit(
                entry_buff,
                exit_buff,
                ind_history,
                line,
                trades,
                val_open,
                val_close,
                val_high,
                val_low,
                ind_date[i],
                candle,
                i,
                fig,
            )
            Sell(
                line,
                ind_history,
                ind_date,
                val_low,
                val_high,
                buffer_low,
                i,
                msl,
                fig,
                bep,
            )

        trade_exit(
            entry_buff,
            exit_buff,
            ind_history,
            line,
            trades,
            val_open,
            val_close,
            val_high,
            val_low,
            ind_date[i],
            candle,
            i,
            fig,
        )
        Buy(
            val_open,
            line,
            ind_history,
            ind_date,
            val_high,
            val_low,
            buffer_high,
            i,
            msl,
            fig,
            bep,
        )

    else:
        if (trades) and (
            trades[-1]["Action"] == "Buy" and trades[-1]["Trade_LS"] == "Long"
        ):  # print("Hold")
            pass
        else:
            trade_exit(
                entry_buff,
                exit_buff,
                ind_history,
                line,
                trades,
                val_open,
                val_close,
                val_high,
                val_low,
                ind_date[i],
                candle,
                i,
                fig,
            )
            Buy(
                val_open,
                line,
                ind_history,
                ind_date,
                val_high,
                val_low,
                buffer_high,
                i,
                msl,
                fig,
                bep,
            )

        trade_exit(
            entry_buff,
            exit_buff,
            ind_history,
            line,
            trades,
            val_open,
            val_close,
            val_high,
            val_low,
            ind_date[i],
            candle,
            i,
            fig,
        )
        Sell(
            line, ind_history, ind_date, val_low, val_high, buffer_low, i, msl, fig, bep
        )


def report(bep, index, lot_size):
    for i in range(1, len(trades)):
        try:
            if trades[i - 1]["Exit_Value"] == 0:
                trades[i - 1]["Exit_Value"] = trades[i]["Entry_Value"]
                trades[i - 1]["Exit_Date"] = trades[i]["Entry_Date"]
            if trades[i - 1]["Action"] == "Buy":
                trades[i - 1]["% ITM"] = round(
                    (
                        (trades[i - 1]["HH/LL"] - trades[i - 1]["Entry_Value"])
                        / trades[i - 1]["Entry_Value"]
                    )
                    * 100,
                    2,
                )
                if trades[i - 1]["% ITM"] < 0:
                    trades[i - 1]["% ITM"] = -trades[i - 1]["% ITM"]
                trades[i - 1]["Profit_Loss"] = round(
                    trades[i - 1]["Exit_Value"] - trades[i - 1]["Entry_Value"], 2
                )
            else:
                trades[i - 1]["% ITM"] = round(
                    (
                        (trades[i - 1]["Entry_Value"] - trades[i - 1]["HH/LL"])
                        / trades[i - 1]["Entry_Value"]
                    )
                    * 100,
                    2,
                )
                if trades[i - 1]["% ITM"] < 0:
                    trades[i - 1]["% ITM"] = -trades[i - 1]["% ITM"]
                trades[i - 1]["Profit_Loss"] = round(
                    trades[i - 1]["Entry_Value"] - trades[i - 1]["Exit_Value"], 2
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

            trades[i - 1]["System"] = "High-Low"

        except:
            pass
    excel_df = pd.DataFrame()
    try:
        if index[1] == "FUT":
            trades[-1]["Lot_Size"] = lot_size

        trades[-1]["System"] = "High-Low"

        for i in trades:
            row = pd.DataFrame([i])
            excel_df = pd.concat([excel_df, row], ignore_index=True)

        # print("\nexcel after appending:")
        # print(excel_df)
        # print("\n\n")
        excel_df = excel_df.drop(["Previous High", "Previous Low", "Stop_Loss"], axis=1)
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

    # excel_df.to_csv("report_high-low.csv")

    return excel_df


def set_up():
    global trades
    global excel_df
    global prev_hl
    global prev_hls
    prev_hl = {"High": 0, "Low": 0}
    prev_hls = {"HH": 0, "LL": float("inf")}
    excel_df = pd.DataFrame(
        columns=[
            "Action",
            "Trade_LS",
            "Entry_Date",
            "Previous High",
            "Previous Low",
            "Entry_Value",
            "Exit_Value",
            "Exit_Date",
            "Profit_Loss",
            "Stop_Loss",
        ]
    )
    trades = []


def run(info):
    index = info[0].split(" ")
    line = info[1]
    entry_buff = info[2]
    exit_buff = info[3]
    days = info[4]
    msl = info[5]
    bep = info[6]
    start_date = info[7]
    end_date = info[8]

    # ind = yf.Ticker(index)
    # ind_history = ind.history(start= "2021-11-01", end = "2023-01-01")
    # ind_history = ind.history(start= "2022-09-27", end = "2022-11-26")

    if (
        index[0] == "NIFTY" or index[0] == "BANKNIFTY" or index[0] == "FINNIFTY"
    ) and index[1] == "EQ":
        ind_history = ft.get_index_prices(index[0], start_date, end_date)
    elif index[1] == "FUT":
        ind_history = ft.get_futures_prices(index[0], start_date, end_date)
    elif index[1] == "EQ":
        ind_history = ft.get_equity_prices(index[0], start_date, end_date)
    elif index[1] == "FUTCOM":
        ind_history = mc.get_comm_prices(index[0], start_date, end_date)

    ind_date = pd.Index.tolist(ind_history[line].index)
    ind_vals = [float(ele) for ele in pd.Series.tolist(ind_history[line])]

    # print(ind_history)

    ind_open = [
        float(ele) for ele in pd.Series.tolist(ind_history["Open"])
    ]  # open values
    ind_high = [
        float(ele) for ele in pd.Series.tolist(ind_history["High"])
    ]  # high values
    ind_low = [float(ele) for ele in pd.Series.tolist(ind_history["Low"])]  # low values
    ind_close = [
        float(ele) for ele in pd.Series.tolist(ind_history["Close"])
    ]  # close values
    if index[1] == "FUT":
        lot_size = [float(ele) for ele in pd.Series.tolist(ind_history["Lot Size"])]
        lot_size = lot_size[-1]

    # ind_history = ind_history.drop(['Volume', 'Dividends', 'Stock Splits'],axis = 1)
    # print(type(ind_history))
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=ind_date, open=ind_open, high=ind_high, low=ind_low, close=ind_close
            )
        ]
    )
    fig.update_yaxes(fixedrange=False)

    excel_df = pd.DataFrame(
        columns=[
            "Action",
            "Trade_LS",
            "Entry_Date",
            "Previous High",
            "Previous Low",
            "Entry_Value",
            "Exit_Value",
            "Exit_Date",
            "Profit_Loss",
            "Stop_Loss",
        ]
    )

    for j in range(1, len(ind_vals)):
        try:
            highest_lowest(j, ind_high, ind_low)
            # fig.add_trace(go.Scatter(x = ind_date[j], y = prev_hl["High"], line = dict(color = "#0000ff")))
            # fig.add_trace(go.Scatter(x = ind_date[j], y = prev_hl["Low"], line = dict(color = "#0000ff")))

            trade(
                bep,
                line,
                entry_buff,
                exit_buff,
                ind_history,
                ind_vals[j + 1],
                ind_open[j + 1],
                ind_high[j + 1],
                ind_low[j + 1],
                ind_close[j + 1],
                j + 1,
                fig,
                ind_date,
                msl,
            )
        except Exception as e:
            # print("for loop error", e)
            pass
    # fig.show()
    if index[1] == "FUT":
        excel_df = report(bep, index, lot_size)
    else:
        excel_df = report(bep, index, 1)

    return excel_df


# print(trades)
# info = ("NIFTY FUT", "Close", 0.225, 0.225, 2, 2.25, "yes", "2021-01-01", "2022-12-01")
# run(info)
