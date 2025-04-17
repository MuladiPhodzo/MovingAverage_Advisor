import time
import concurrent.futures as ft
# Now import MovingAverages
import Advisor
import MovingAverage.MovingAverage as MA
import Trade.TradesAlgo as algorithim
import GUI.userInput as GUI



class RunAdvisorBot:
	def __init__(self):
		self.symbols = None
		self.advisor = Advisor.MetaTrader5Client()
		self.init = None

	def backtest(self, symbols: list):
	 
		client = Advisor.MetaTrader5Client()
		client.initialize()
		for symbol in symbols:
			data = client.get_rates_range(symbol)
			htf_strategy = MA.MovingAverageCrossover(symbol, data=data["HTF"])
			ltf_strategy = MA.MovingAverageCrossover(symbol, data=data["LTF"])

			HTF_data = htf_strategy.calculate_moving_averages(data["HTF"])
			LTF_data = ltf_strategy.calculate_moving_averages(data["LTF"])
			data = {'HTF':HTF_data, 'LTF': LTF_data}
			ltf_strategy.run_moving_average_strategy(symbol, data, ltf_strategy)

	def main(self, symbol, client: Advisor.MetaTrader5Client):
	 
		print(f'✅ Thread started for {symbol}...')
		try:
			res = client.initialize()
			self.init = res[0]
			while self.init:
				
				data = client.get_multi_tf_data(symbol)

				if data is None:
					print(f'❌ No data returned for {symbol}. Retrying in 10 seconds...')
					time.sleep(10)
					continue

				print(f'📊 Data retrieved for {symbol}............')

				if "HTF" not in data or "LTF" not in data:
					print(f'⚠️ Missing timeframes for {symbol}. Skipping...')
					return

				print(f'✅ Processing {symbol} with Multi Timeframe Data')

				htf_strategy = MA.MovingAverageCrossover(symbol, data=data["HTF"])
				ltf_strategy = MA.MovingAverageCrossover(symbol, data=data["LTF"])

				HTF_data = htf_strategy.calculate_moving_averages(data["HTF"])
				LTF_data = ltf_strategy.calculate_moving_averages(data["LTF"])

				if "Fast_MA" not in LTF_data.columns or "Slow_MA" not in LTF_data.columns:
					print(f'❌ Missing MA columns in LTF data for {symbol}')
					continue

				if HTF_data is None or LTF_data is None:
					print(f'⚠️ Moving averages not calculated for {symbol}. Skipping...')
					time.sleep(10)
					continue

				htf_latest = HTF_data.iloc[-1]
				ltf_latest = LTF_data.iloc[-1]
	
				current_price = ltf_latest['close']
				market_Bias = "Bullish" if htf_latest['Fast_MA'] > htf_latest['Slow_MA'] else "Bearish"
				ltf_Bias = "Buy" if ltf_latest["Fast_MA"] > ltf_latest['Slow_MA'] else "Sell"

				print(f'{symbol}-current price: {current_price} Fast_MA: {ltf_latest["Fast_MA"]}')

				trade = algorithim.MT5TradingAlgorithm(symbol)
				trade.run_Trades(market_Bias, ltf_Bias, ltf_latest, current_price, client.THRESHOLD, symbol)

				print(f'🛌{symbol} Thread sleeping for 15 minutes....')
				time.sleep(900)  # 15 minutes

		except Exception as e:
			print(f'❌ Exception in thread {symbol}: {e}')

if __name__ == "__main__":
	import Advisor as Client
	gui = GUI.UserGUI()
	tempClient = Advisor.MetaTrader5Client()
	res = tempClient.initialize()
  
	# user_data = gui.get_user_input()
	bot = RunAdvisorBot()
	bot.symbols = res[1]
	bot.backtest(bot.symbols )

	tempClient.shutdown()


	print('marketwatch symbols: ', bot.symbols)

	print('running threads------------------------------------------------------')

	with ft.ThreadPoolExecutor(max_workers=len(bot.symbols)) as executor:
		futures = {
			executor.submit(
				bot.main,
				symbol,
				client = Client.MetaTrader5Client(),  # Create a new instance for each thread
			): symbol for symbol in bot.symbols
		}

		for future in ft.as_completed(futures):
			symbol = futures[future]

			try:
				future.result()
			except Exception as e:
				print(f'❌ Thread for {symbol} failed with error: {e}')
				continue

#  bot.advisor.shutdown()
