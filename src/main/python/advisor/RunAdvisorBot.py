import pandas as pd

# Now import MovingAverages
import Advisor
import MovingAverage.MovingAverage as MA
import MetaTrader5 as mt5
import Trade.TradesAlgo as algorithim
import time
import concurrent.futures as ft


class RunAdvisorBot:
	def __init__(self):
		self.symbols = None
		self.advisor = Advisor.MetaTrader5Client()
		self.init = self.advisor.initialize()


	def mt5Client_StartUp(self):

		self.advisor = Advisor.MetaTrader5Client()
		self.init = self.advisor.initialize()
		self.symbols = self.advisor.symbols
  
	def main(self, symbol, client: Advisor.MetaTrader5Client, timeframes: dict):
		print(f'✅ Thread started for {symbol}...')
		
		while True:
			print(f'🔍 Fetching data for {symbol}...')

			client.data = client.get_multi_tf_data(symbol, timeframes)

			if client.data is None:
				print(f'❌ No data returned for {symbol}. Retrying in 10 seconds...')
				time.sleep(10)
				continue  # Retry after delay

			print(f'📊 Data retrieved for {symbol}: {client.data.keys()}')

			if "HTF" not in client.data or "LTF" not in client.data:
				print(f'⚠️ Missing timeframes for {symbol}. Skipping...')
				return  # Instead of returning None, exit cleanly

			print(f'✅ Processing {symbol} with Multi Timeframe Data')

			htf_strategy = MA.MovingAverageCrossover(symbol, data=client.data["HTF"])
			ltf_strategy = MA.MovingAverageCrossover(symbol, data=client.data["LTF"])

			HTF_data = htf_strategy.calculate_moving_averages()
			LTF_data = ltf_strategy.calculate_moving_averages()

			if HTF_data is None or LTF_data is None:
				print(f'⚠️ Moving averages not calculated for {symbol}. Skipping...')
				time.sleep(10)
				continue  # Retry

			print(f'📈 MA Data Available for {symbol}')

			htf_latest = HTF_data.iloc[-1]
			ltf_latest = LTF_data.iloc[-1]
			current_price = ltf_latest['close']

			market_Bias = "Bullish" if htf_latest['Fast_MA'] > htf_latest['Slow_MA'] else "Bearish"
			ltf_Bias = "Buy" if ltf_latest["Fast_MA"] > ltf_latest['Slow_MA'] else "Sell"

			print(f'📌 Trading Decision - {symbol}: Market Bias={market_Bias}, LTF Bias={ltf_Bias}')

			trade = algorithim.MT5TradingAlgorithm(client.data, symbol)
			trade.run_Trades(market_Bias, ltf_Bias, ltf_latest, current_price, client.THRESHOLD, symbol)

			print(f'✅ Trade executed for {symbol}, sleeping for 1 hour...')
			time.sleep(3600)


if __name__ == "__main__":
	
	symbols = ["USDJPY", "USDCHF", "USDCAD", "USDZAR", "EURUSD"]
	bot = RunAdvisorBot()
	
 
	if not bot.init:
		print('bot not initialized!')
		exit()
	else:
		print('bot initialized: ', bot.init)
   
   
	bot.advisor.TF = {
		"HTF": mt5.TIMEFRAME_H4,
		"LTF" :mt5.TIMEFRAME_H1}
 
	
	
	print("ACCOUNT.info: ", bot.advisor.account_info)
	print("terminal.info: ", bot.advisor.terminal_info)
	

	# if not bot.advisor.check_symbols_availability():
	# 	bot.advisor.shutdown()
	# 	exit()
	print('marketwatch symbols: ', bot.advisor.symbols)
	
	print('running threads------------------------------------------------------')
	with ft.ThreadPoolExecutor(max_workers=len(bot.advisor.symbols)) as executor:
		futures = {executor.submit(bot.main, symbol, bot.advisor, bot.advisor.TF): symbol for symbol in bot.advisor.symbols}
		
		for future in ft.as_completed(futures):
			symbol = futures[future]

			try:
				future.result()
			except:
				print(f'❌ Thread for {symbol} failed.')
				continue
 
 # bot.advisor.shutdown()
	