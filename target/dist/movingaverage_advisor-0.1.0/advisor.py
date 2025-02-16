from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import MetaTrader5 as mt5
import MovingAverage as MA
import TradesAlgo as Algo
import os


register_matplotlib_converters()


class MetaTrader5Client:
	def __init__(self, symbols):
		self.symbols = symbols
		self.Ratesdata = None
		self.account_info = None
		self.terminal_info = None
		self.TF = None

	def initialize(self):
		if not mt5.initialize():
			print("initialize() failed, error code =", mt5.last_error())
			mt5.shutdown()
			return False
		'''self.account_info = mt5.account_info()
		self.terminal_info = mt5.terminal_info()'''
		return True

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

	def get_live_data(self, symbol, timeframe, bars=100):
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
		print(f"client.TF: {timeframe}, Type: {type(timeframe)}")

		rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
		if rates is None:
				print(f"Failed to get data for {symbol}")
				return None
		return pd.DataFrame(rates)

	def get_rates_range(self, symbol, timeframe, start_time, end_time):
		rates = mt5.copy_rates_range(symbol, timeframe, start_time, end_time)
		if rates is None:
			print(f"Failed to retrieve {symbol} rates range, error code:", mt5.last_error())
 
		return pd.DataFrame(rates)

	def toCSVFile(self, rates, file_path):
		# Convert rates to DataFrame
		self.Ratesdata = pd.DataFrame(rates)

		# Ensure the directory exists before writing
		os.makedirs(os.path.dirname(file_path), exist_ok=True)

		# Write DataFrame to CSV, creating the file if it doesn’t exist
		self.Ratesdata.to_csv(file_path, index=True, mode='w', header=True)

	def shutdown(self):
		mt5.shutdown()


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
	def plot_charts(rates, fast_period, slow_period):
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

if __name__ == "__main__":
	# Initialize client and symbols
	symbols = ["USDJPY", "USDCHF", "USDCAD", "USDZAR", "EURUSD"]
	plotter = DataPlotter()
	client = MetaTrader5Client(symbols)
	client.TF = mt5.TIMEFRAME_H1
	THRESHOLD = 0.0005

	if not client.initialize():
		exit()
	"""
	print("ACCOUNT.info: ", client.account_info)
	print("terminal.info: ", client.terminal_info)
	 """

	if not client.check_symbols_availability():
		client.shutdown()
		exit()

	print("Assembling dataframes......")
	for symbol in symbols:
		print(f"Fetching {symbol} rates...")
		rangedRates = client.get_rates_range(symbol, client.TF, datetime(2024, 8, 1, 00), datetime.now())
		client.Ratesdata = pd.DataFrame(rangedRates)
		strategy = MA.MovingAverageCrossover(symbol, data=client.Ratesdata, fast_period=50, slow_period=100)
		data = strategy.run_moving_average_strategy(symbol, mt5.TIMEFRAME_M15, datetime(2024, 11, 28, 13), 1000)
		print("data: ", data[1])
		bias = data[1]['Bias']
		for symbol in symbols:
			data = client.get_live_data(symbol, client.TF, 1000)
			rates_data = pd.DataFrame(data)
			trade = Algo.MT5TradingAlgorithm(rates_data, symbol,)
			if rates_data is None:
				client.shutdown()
			
			MovingAverage = MA.MovingAverageCrossover(symbol, data=rates_data, fast_period=50, slow_period=100)
			data = MovingAverage.calculate_moving_averages()
			latest = data.iloc[-1]
			current_price = latest['close']
			
			client.Ratesdata = data
			print(client.Ratesdata)
			plotter.plot_charts(
					client.Ratesdata, 
					client.Ratesdata['close'].rolling(window=50).mean(),
					client.Ratesdata['close'].rolling(window=100).mean())
			# Check if the price is within the threshold of moving averages
			if abs(current_price - latest['Fast_MA']) <= THRESHOLD or abs(current_price - latest['Slow_MA']) <= THRESHOLD:
					if latest['Bias'] == "Bullish":
							print("Bullish Signal - Placing BUY order")
							trade.place_order(symbol, 'buy')
					elif latest['Bias'] == "Bearish":
							print("Bearish Signal - Placing SELL order")
							trade.place_order(symbol, 'sell')
			else:
					print("No trade - Price too far from moving averages")
	client.shutdown()
