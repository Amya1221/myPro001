import pandas as pd
import numpy as np


# Define the tech module functions
ema_periods = [5, 10, 20,30, 50, 100]
vol_periods = [5, 10, 20, 50]


def EMA(DF, n):
    df = DF.copy()
    df['EMA'] = df['Close'].ewm(span=n, adjust=False).mean()
    return df['EMA']


def volume_avg(DF, n):
    df = DF.copy()
    df['average'] = df['Volume'].rolling(window=n).mean()
    return df['average']


def RSI(DF, window=14):
    df = DF.copy()
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def vol_RSI(DF, window=14):
    df = DF.copy()
    diff = df['Close'] - df['Close'].shift(1)
    gain = df['Volume'].where(diff > 0, 0)
    loss = -df['Volume'].where(diff < 0, 0)
    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def ATR(DF, window=14):
    data = DF.copy()
    data['H-L'] = data['High'] - data['Low']
    data['H-PC'] = abs(data['High'] - data['Close'].shift(1))
    data['L-PC'] = abs(data['Low'] - data['Close'].shift(1))
    data['TR'] = data[['H-L', 'H-PC', 'L-PC']].max(axis=1)
    atr = data['TR'].rolling(window=window, min_periods=1).mean()
    return atr


def rolling_volume(data, window=10):
    diff = data['Close'] - data['Close'].shift(1)
    data['Volume_signed'] = data['Volume'].where(diff > 0, 0) - data['Volume'].where(diff < 0, 0)
    rol_volume = data['Volume_signed'].rolling(window=window, min_periods=1).sum()
    return rol_volume


def vol_index(DF, mcap, window=10):
    data = DF.copy()
    diff = data['Close'] - data['Close'].shift(1)
    data['Volume_signed'] = data['Volume'].where(diff > 0, 0) - data['Volume'].where(diff < 0, 0)
    try:
        data['vol_ind'] = data['Volume_signed'] * data['Close'].iloc[-1] * 100 / mcap
        data['vol_ind_rol'] = data['vol_ind'].rolling(window=window, min_periods=1).sum()
        return data['vol_ind'], data['vol_ind_rol']
    except Exception as e:
        data['vol_ind'] = data['Volume_signed'] * data['Close']
        data['vol_ind_rol'] = data['vol_ind'].rolling(window=window, min_periods=1).sum() / (
            data['vol_ind'].rolling(window=window * 10, min_periods=1).sum())
        return data['vol_ind'], data['vol_ind_rol']





def rolling_high_52(DF,period):
    window_size = {'daily': 200, 'weekly': 52, 'monthly': 12}
    if period=='daily':
        window=200
    elif period=='weekly':
        window=52
    else:
        window=12
    # print(window)
    df = DF.copy()
    df['52WH'] = df['High'].rolling(window=window, min_periods=1).max()
    return df['52WH']


def calculate_technicals(DF, symbol, nifty500_tickers, periods='daily'):
    try:
        for period in ema_periods:
            if len(DF) > period:
                DF[f'{period}ema'] = EMA(DF, period)

        for period in vol_periods:
            if len(DF) > period:
                DF[f'volume_{period}dma'] = volume_avg(DF, period)

        mcap = nifty500_tickers[nifty500_tickers["symbol"] == symbol.split('.')[0]]["mcap"].values[0]
        # print(f"Market Cap for {symbol}: {mcap}")
    except KeyError:
        mcap = 0
        print(f"Symbol '{symbol}' not found in nifty500_tickers. Setting mcap to 0.")
    except Exception as e:
        mcap = 0
        print(f'Error: {e}. Setting mcap to 0.')

    DF['vol_ind'], DF['vol_ind_rol'] = vol_index(DF, mcap)
    DF['rsi'] = RSI(DF)
    DF['atr'] = ATR(DF)
    DF['net_volume'] = rolling_volume(DF)
    DF['vol_rsi'] = vol_RSI(DF)
    # print(periods)
    DF['52WH']=rolling_high_52(DF,periods)
    DF['prev_close']=DF['Close'].shift(1)

    return DF
