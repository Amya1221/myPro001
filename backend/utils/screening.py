import pandas as pd


def screen_data(conditions, scriplist, ohlcv_data, nifty500_tickers, fundamentals, fundamentals_fund,interval='daily'):
    screened_symbols_data = pd.DataFrame()
    to_be_removed = set()
    # print('to be removed',to_be_removed)
    # Initial symbol list
    symbols = [symbol for symbol in scriplist]
    # print(conditions)
    for condition in conditions:
        print(f"Testing condition: {condition}")
        field1 = condition['field1']
        field2 = condition['field2']
        operator = condition['operator']
        multiple = condition.get('multiple', 1)

        try:
            multiple = float(multiple)
        except (ValueError, TypeError):
            multiple = 1

        for symbol in symbols:
            try:
                print(f"Screening for symbol: {symbol}")
                data = ohlcv_data[interval][symbol]

                # Apply condition
                if operator == ">" and (data[field1].iloc[-1] <= multiple * data[field2].iloc[-1]):
                    to_be_removed.add(symbol)
                elif operator == "<" and (data[field1].iloc[-1] >= multiple * data[field2].iloc[-1]):
                    to_be_removed.add(symbol)
            except Exception as e:
                print(f"Error while screening {symbol}: {e}")
                to_be_removed.add(symbol)
            # print('updated to be removed',to_be_removed)
        # Update valid symbols
        symbols = [symbol for symbol in symbols if symbol not in to_be_removed]

    # print(f"Screened Symbols: {symbols}")

    # Collect data for screened symbols
    for symbol in symbols:
        try:
            data = ohlcv_data[interval][symbol]
            date = data.index[-1]
            close_value = data['Close'].iloc[-1]

            # Handle missing 'Close' values
            if pd.isna(close_value):
                print(f"Warning: 'Close' value is NaN for symbol {symbol}. Skipping...")
                continue

            # Gather fundamental data
            s = symbol.split('.')[0]
            try:
                total_fund = fundamentals_fund[fundamentals_fund['Symbol'] == symbol]['total'].iloc[0]
            except Exception as err:
                total_fund=100
            print('total for ',symbol,':',total_fund)
            # print('reliance funda:', reliance_fund if not reliance_fund.empty else 100)
            sector = nifty500_tickers.loc[nifty500_tickers["symbol"] == s, "sector"].values[0] if s in nifty500_tickers[
                "symbol"].values else "Unknown"
            mcap = nifty500_tickers.loc[nifty500_tickers["symbol"] == s, "mcap"].values[0] if s in nifty500_tickers[
                "symbol"].values else "Unknown"

            # Build record
            record = {
                'Symbol': s,
                'Date': date,
                'Open': data['Open'].iloc[-1],
                'High': data['High'].iloc[-1],
                'Low': data['Low'].iloc[-1],
                'Close': data['Close'].iloc[-1],
                'Volume': data['Volume'].iloc[-1],
                'MarketCap': mcap,
                'Sector': sector,
                'Fundamentals': total_fund,
                'Link': f'https://in.tradingview.com/chart/GC72xsHV/?symbol=NSE%3A{s}'
            }
            screened_symbols_data = pd.concat([screened_symbols_data, pd.DataFrame([record])], ignore_index=True)
        except Exception as e:
            print(f"Error collecting data for {symbol}: {e}")
    screened_symbols_data_json = screened_symbols_data.dropna().to_dict(orient='records')
    # Convert DataFrame to JSON
    return screened_symbols_data_json
