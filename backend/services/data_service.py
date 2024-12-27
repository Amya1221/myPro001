from datetime import datetime
import pandas as pd
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor
from utils import tech


class DataService:
    def __init__(self, data_path='D:/codings/amya2/', batch_size=20):
        self.data_path = data_path
        self.batch_size = batch_size  # Number of symbols to process in parallel batches
        self.ohlcv_data_full = {'daily': {}, 'weekly': {}, 'monthly': {}}

    def load_ohlcv_data(self, intervals, scriplist):
        """Load OHLCV data from local CSV files or download if missing."""
        ohlcv_data = {}
        for interval in intervals:
            ohlcv_data[interval] = {}
            failed_symbols = []
            for symbol in scriplist:
                try:
                    file_name = f'{self.data_path}{symbol}_{interval}.csv'
                    ohlcv_data[interval][symbol] = pd.read_csv(file_name, index_col='Date')
                except Exception:
                    print(f'Data unavailable for {symbol} for timeframe {interval}. Downloading...')
                    failed_symbols.append(symbol)

            # Download data for failed symbols
            if failed_symbols:
                downloaded_data = self.download_ohlcv_batch(failed_symbols)
                for symbol, data in downloaded_data['daily'].items():
                    ohlcv_data['daily'][symbol] = data

        return ohlcv_data

    def download_ohlcv_with_retry(self, symbol, max_retry_attempts=3):
        """Download data for a symbol with retries."""
        retry_count = 0
        while retry_count < max_retry_attempts:
            try:
                ticker = yf.Ticker(symbol)
                stock_daily = ticker.history(period='max', interval='1d')
                print(f"Downloading data for {symbol}")
                return symbol, stock_daily
            except Exception as e:
                retry_count += 1
                print(f"Failed to download {symbol}. Retrying ({retry_count}/{max_retry_attempts})...")
        print(f"Failed to download {symbol} after {max_retry_attempts} attempts.")
        return symbol, None

    def download_ohlcv_batch(self, scriplist):
        """Download data for a batch of symbols using threading."""
        ohlcv_data = {'daily': {}}
        symbol_batches = [scriplist[i:i + self.batch_size] for i in range(0, len(scriplist), self.batch_size)]

        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self.download_ohlcv_with_retry, symbol) for batch in symbol_batches for symbol in batch
            ]
            for future in futures:
                symbol, daily = future.result()
                if daily is not None:
                    ohlcv_data['daily'][symbol] = tech.calculate_technicals(daily, symbol, 'daily')

        return ohlcv_data

    def update_data(self, df, scriplist, scriptdetails):
        """Update OHLCV data for all symbols using yfinance batch downloading."""
        print(scriptdetails)
        ohlcv_data = df['daily']
        end_date = datetime.today()
        start_date = end_date - pd.Timedelta(days=7)
        end_date = end_date + pd.Timedelta(days=1)

        start_date = start_date.strftime('%Y-%m-%d')
        end_date = end_date.strftime('%Y-%m-%d')

        ohlcv_data_updated = {'daily': {}}
        delete_symbols = []

        try:
            # Download the data for all symbols in one call
            data = yf.download(
                tickers=" ".join(scriplist),
                start=start_date,
                end=end_date,
                group_by='ticker'
            )
            failed_symbols = [symbol for symbol in scriplist if data[symbol].isnull().all().all()]
            if failed_symbols:
                print("Retrying for failed symbols:", failed_symbols)
                retry_data = yf.download(tickers=" ".join(failed_symbols), start=start_date, end=end_date,
                                         group_by='ticker')

                # Merge the retry data into the original dataframe
                for symbol in failed_symbols:
                    if not retry_data.empty:
                        data[symbol] = retry_data[symbol]
                    else:
                        delete_symbols.append(symbol)
            print("Data download completed.")
        except Exception as e:
            print(f"Error during batch download: {e}")
            return ohlcv_data_updated, []

        # Process data for each symbol
        for symbol in scriplist:
            try:
                if symbol in data:
                    # Handle the symbol's data
                    new_data = data[symbol]
                    new_data.index = new_data.index.strftime('%Y-%m-%d')
                    if symbol in ohlcv_data:
                        # Combine with existing data
                        combined_data = pd.concat([ohlcv_data[symbol], new_data]).sort_index()
                        updated_index = []
                        for date in combined_data.index:
                            updated_index.append(date.split(' ')[0])
                        combined_data.index=updated_index
                        # ohlcv_data[symbol]=combined_data
                        # ohlcv_data[symbol] = ohlcv_data[symbol].drop_duplicates(keep='last')
                        # combined_data = combined_data.drop_duplicates(keep='last')
                        # print(ohlcv_data[symbol])
                        combined_data = combined_data[~combined_data.index.duplicated(keep='last')]
                    else:
                        combined_data = new_data
                    # print('final data')
                    # print(combined_data)
                    # Calculate technical indicators and update
                    # technical_data = tech.calculate_technicals(combined_data, symbol, scriptdetails, periods='daily')
                    # ohlcv_data_updated['daily'][symbol] = technical_data
                    # ohlcv_data_updated['daily'][symbol]=combined_data
                    technical_data = tech.calculate_technicals(combined_data, symbol, scriptdetails, periods='daily')
                    ohlcv_data_updated['daily'][symbol] = technical_data
                else:
                    print(f"No data found for {symbol}. Marking for deletion.")
                    delete_symbols.append(symbol)
            except Exception as e:
                print(f"Error processing data for {symbol}: {e}")
                delete_symbols.append(symbol)
        # print('update complete')
        # Determine successfully updated symbols
        updated_symbols = [symbol for symbol in scriplist if symbol not in delete_symbols]
        return ohlcv_data_updated, updated_symbols
