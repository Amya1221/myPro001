import pandas as pd
def initialize():
    # nifty500_tickers = pd.read_csv('D:/codings/nse_mcap.csv')
    # nifty500_tickers.dropna(inplace=True)
    # nifty500_tickers['symbol']=[tick+'.NS' for tick in nifty500_tickers['symbol']]
    # nifty500_symbol=nifty500_tickers['symbol'].tolist()
    # nifty500_tickers.set_index('symbol', inplace=True)
    fundamentals = pd.read_csv('D:/codings/fundamental_sec.csv', index_col='symbol')
    fundamentals_fund = pd.read_csv('D:/codings/fundamental.csv')

    nifty500_tickers = pd.read_csv('D:/codings/fundamental_sec.csv')
    nifty500_tickers.dropna(inplace=True)
    # sector = nifty500_tickers.loc[nifty500_tickers["symbol"] == "RELIANCE", "sector"].values[0]
    # print('sector:',sector)
    # mcap = nifty500_tickers.loc[nifty500_tickers["symbol"] == symbol, "mcap"].values[0] if s in nifty500_tickers[
    #     "symbol"].values else "Unknown"
    # print(nifty500_tickers['symbol'])
    data = nifty500_tickers['symbol'].tolist()
    scriplist = [tick + '.NS' for tick in data]
    scriplist=scriplist[0:10]
    return scriplist,nifty500_tickers,fundamentals,fundamentals_fund
# initialize()