import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import numpy as np
import MetaTrader5 as mt5
import time
from dateutil.relativedelta import relativedelta
import datetime
import os


register_matplotlib_converters()


class MetaTrader5Client:
    def __init__(self, 
                threshold = 0.0100, 
                timeframes= {
                "HTF": mt5.TIMEFRAME_H4,
                "LTF" :mt5.TIMEFRAME_H1}
            ):
        self.symbols = []
        self.THRESHOLD = threshold
        self.account_info = None
        self.terminal_info = None
        self.TF = timeframes

    def initialize(self):
        try:
            if not mt5.initialize():
                print("initialize() failed, error code =", mt5.last_error())
                mt5.shutdown()
                return False

        finally:
            self.account_info = mt5.account_info()
            self.terminal_info = mt5.terminal_info()
            print('searching for available symbols...')
            symbols = self.get_Symbols()

            return [True, symbols]

    def check_symbols_availability(self):
        """
        Checks the availability of the symbols in the MetaTrader 5 Market Watch.

        This method iterates through the list of symbols stored in the instance
        and checks if each symbol is available in the MetaTrader 5 Market Watch.
        If any symbol is not available, it prints a message indicating the symbol
        is not available and suggests checking if it is enabled in Market Watch.

        Returns:
            bool: True if all symbols are available, False otherwise.
        """
        available_symbols = [s.name for s in mt5.symbols_get()]
        for pair in self.symbols:
            if pair not in available_symbols:
                print(f"Pair {pair} is not available. Check if it's enabled in Market Watch.")
                return False
        return True

    def get_Symbols(self): 
        all_symbols = mt5.symbols_get()
        symbols = []
        for symbol in all_symbols:
            if symbol.visible:
                symbols.append(symbol.name)
        return symbols

    def get_live_data(self, symbol, timeframe, bars=1000):
        """
        Fetch live market data for a given symbol and timeframe.
        Parameters:
        symbol (str): The financial instrument symbol to retrieve data for.
        timeframe (int): The timeframe for the data (e.g., MT5 timeframes like mt5.TIMEFRAME_M1).
        bars (int, optional): The number of bars to retrieve. Default is 100.
        Returns:
        pd.DataFrame: A DataFrame containing the market data if successful, None otherwise.
        Prints:
        - The client's timeframe and its type.
        - A message if data retrieval fails.
        - The retrieved market data.
        """
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
        if rates is None:
            print(f"Failed to get data for {symbol}")
            return None

        return pd.DataFrame(rates)

    def get_rates_range(self, symbol):
        multi_tf_data = {}

        end_date = datetime.datetime.now()
        start_date = end_date - relativedelta(months=6)

        for tf_name, tf_value in self.TF.items():
            rates = mt5.copy_rates_range(symbol, tf_value, start_date, end_date)
            if rates is not None and len(rates) > 0:
                df = pd.DataFrame(rates)
                df['time'] = pd.to_datetime(df['time'], unit='s')  # convert timestamps to datetime
                multi_tf_data[tf_name] = df
            else:
                print(f"Failed to retrieve {symbol} rates for {tf_name}, error: {mt5.last_error()}")

        return multi_tf_data

    def get_multi_tf_data(self, symbol):
        """Fetch data for multiple timeframes and return as a dictionary with HTF and LTF keys."""

        multi_tf_data = {}

        print(f'🔍 Fetching data for {symbol}...')
        
        # Loop over the provided timeframes
        for tf_name, tf_value in self.TF.items():
           
            # Fetch live data for each timeframe
            data = self.get_live_data(symbol, tf_value, 1000)

            if data is not None:
                # Store the fetched data in the dictionary under its corresponding timeframe name
                multi_tf_data[tf_name] = pd.DataFrame(data)
            else:
                print(f"Failed to fetch data for {symbol} on {tf_name}.")

        # Store the data and return
        self.data = multi_tf_data
        return multi_tf_data

    def toCSVFile(self, file_path):
        """
        Save ratesData to a CSV file.
        - Creates the file if it doesn't exist.
        - Appends to the file if it already exists.
        """

        if self.Ratesdata is not None:
            file_exists = os.path.isfile(file_path)

            if not file_exists:
                self.Ratesdata.to_csv(file_path, index=False, mode='w', header=True)
                print(f"New file created and entry levels saved to {file_path}.")
            else:
                self.Ratesdata.to_csv(file_path, index=False, mode='a', header=False)
                print(f"Entry levels appended to existing file {file_path}.")
        else:
                print("No rates to save.")

    def shutdown(self):
        mt5.shutdown()
        return False

class DataPlotter:

    @staticmethod
    def plot_ticks(ticks, title):
        if ticks is None or len(ticks) == 0:
            print("No data to plot.")
            return
        ticks_frame = pd.DataFrame(ticks)
        ticks_frame['time'] = pd.to_datetime(ticks_frame['time'], unit='s')
        plt.plot(ticks_frame['time'], ticks_frame['ask'], 'r-', label='ask')
        plt.plot(ticks_frame['time'], ticks_frame['bid'], 'b-', label='bid')
        plt.legend(loc='upper left')
        plt.title(title)
        plt.show()

    @staticmethod
    def plot_rates(rates, title):
        if rates is None or len(rates) == 0:
            print("No data to plot.")
            return
        rates_frame = pd.DataFrame(rates)
        rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')
        plt.plot(rates_frame['time'], rates_frame['close'], label='close')
        plt.title(title)
        plt.legend()
        plt.show()

    @staticmethod
    def plot_charts(rates, entries, fast_period, slow_period):
        if rates is None:
                raise ValueError("Error: `self.results` is None. Run `backtest_strategy()` before plotting.")

        if 'Crossover' not in rates.columns:
                raise ValueError("Error: 'Crossover' column is missing in `self.results`. Check data processing.")

        if 'close' not in rates.columns or rates['close'].empty:
                raise ValueError("No Close data available")

        plt.figure(figsize=(12, 6))

        # Plot the close price
        plt.plot(rates.index, rates['close'], label="Close", color='black')

        # Plot the fast and slow moving averages
        plt.plot(rates.index, rates['Fast_MA'], label=f"Fast MA ({fast_period})", color='blue')
        plt.plot(rates.index, rates['Slow_MA'], label=f"Slow MA ({slow_period})", color='red')

        # Plot buy signals (crossover == 2)
        plt.plot(rates.loc[rates['Crossover'] == 2].index,
                        rates.loc[rates['Crossover'] == 2, 'Fast_MA'],
                        '^', color='green', markersize=12, label="Buy Signal")
        
        # Plot sell signals (crossover == -2)
        plt.plot(rates.loc[rates['Crossover'] == -2].index,
                        rates.loc[rates['Crossover'] == -2, 'Fast_MA'],
                        'v', color='red', markersize=12, label="Sell Signal")

        # Add title and legend
        plt.title('Moving Average Crossover Signals')
        plt.legend(loc='upper left')
        plt.show()

# if __name__ == "__main__":
# 	# Initialize client and symbols
# 	symbols = ["USDJPY", "USDCHF", "USDCAD", "USDZAR", "EURUSD"]
# 	Now = datetime.now()

# 	plotter = DataPlotter()
# 	client = MetaTrader5Client(symbols)
# 	client.TF = {
#    "HTF": mt5.TIMEFRAME_H4,
#    "LTF" :mt5.TIMEFRAME_H1}

# 	THRESHOLD = 0.0005

# 	if not client.initialize():
# 		exit()
# 	"""
# 	print("ACCOUNT.info: ", client.account_info)
# 	print("terminal.info: ", client.terminal_info)
# 	 """

# 	if not client.check_symbols_availability():
# 		client.shutdown()
# 		exit()

# 		# for symbol in symbols:

# 		# 	print(f"Fetching {symbol} rates...")
# 		# 	filepath = f'src/main/python/Logs/Rates/{symbol}_rates'
# 		# 	rangedRates = client.get_rates_range(symbol, client.TF, datetime(2024, 8, 1, 00), Now)
# 		# 	client.Ratesdata = pd.DataFrame(rangedRates)
# 		# 	strategy = MA.MovingAverageCrossover(symbol, data=client.Ratesdata, fast_period=50, slow_period=100)
# 		# 	data = strategy.run_moving_average_strategy(symbol, client.TF, datetime(2024, 11, 28, 13), 1000)


# 		# 	data = client.get_multi_tf_data(symbol, client.TF)
# 		# 	if data is None:
# 		# 		client.shutdown()

# 		# 	htf_data = data["HTF"]
# 		# 	ltf_data = data["LTF"]
# 		# 	trade = Algo.MT5TradingAlgorithm(rates_data, symbol,)



# 		# 	HTF_MovingAverage = MA.MovingAverageCrossover(symbol, htf_data)
# 		# 	LTF_MovingAverage = MA.MovingAverageCrossover(symbol, ltf_data)
# 		# 	HTF_data = HTF_MovingAverage.calculate_moving_averages()
# 		# 	LTF_data = LTF_MovingAverage.calculate_moving_averages()

# 		# 	latest = data.iloc[-1]
# 		# 	current_price = latest['close']

# 		# 	client.Ratesdata = data
# 		# 	print(client.Ratesdata)

# 		# 	plotter.plot_charts(
# 		# 			client.Ratesdata,
# 		# 			client.Ratesdata['close'].rolling(window=50).mean(),
# 		# 			client.Ratesdata['close'].rolling(window=100).mean())

# 		# 	# Check if the price is within the threshold of moving averages
# 		# 	trade.run_Trades(latest, current_price, THRESHOLD, symbol)
# 		# 	time.sleep(60)

# 	with ft.ThreadPoolExecutor(max_workers=len(symbols)) as executor:
# 		executor.map(lambda symbol:
# 			MA.MovingAverageCrossover(symbol,
#                              		data=client.data).multi_Timeframe_Synthesis(symbol,
# 																																		client,
# 																																		client.TF,
# 																																		THRESHOLD))
# 	client.shutdown()
