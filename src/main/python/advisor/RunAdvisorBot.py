import Advisor
import sys
import os

# Add src/main/python to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

sys.path.append("src\main\python\MovingAverages")
# Now import MovingAverages
import MovingAverages.MovingAverage as MA
import MetaTrader5 as mt5
import Trade.TradesAlgo as algorithim
import time
import concurrent.futures as ft


class RunAdvisorBot:
	def __init__(self, advisor: Advisor.MetaTrader5Client = None):
		self.symbols = None
		self.advisor = advisor


	def mt5Client_StartUp(self, symbols: list):

		self.symbols = symbols
		self.advisor = Advisor.MetaTrader5Client(symbols).initialize()

	def main(self, symbol, client: Advisor.MetaTrader5Client, timeframes: dict):

		while(True):

			client.data = client.get_multi_tf_data(symbol, timeframes)
			
			trade = algorithim.MT5TradingAlgorithm(client.data, symbol)

			if "HTF" not in client.data or "LTF" not in client.data:
				return None

			htf_strategy = MA.MovingAverageCrossover(symbol, data=client.data["HTF"])
			ltf_strategy = MA.MovingAverageCrossover(symbol, data=client.data["LTF"])

			HTF_data = htf_strategy.calculate_moving_averages()
			LTF_data = ltf_strategy.calculate_moving_averages()

			htf_latest = HTF_data.iloc[-1]
			ltf_latest = LTF_data.iloc[-1]
			current_price = ltf_latest['close']

			market_Bias = "Bullish" if htf_latest['Fast_MA'] > htf_latest['Slow_MA'] else "Bearish"
			ltf_Bias = "Buy" if ltf_latest["Fast_MA"] > ltf_latest['Slow_MA'] else "Sell"

			trade.run_Trades(market_Bias, ltf_Bias, ltf_latest, current_price, client.THRESHOLD, symbol)
			time.sleep(60)

if __name__ == "__main__":
	
	symbols = []
	bot = RunAdvisorBot()
	bot.advisor = bot.mt5Client_StartUp
	bot.advisor.TF = {
		"HTF": mt5.TIMEFRAME_H4,
		"LTF" :mt5.TIMEFRAME_H1}
 
	if not bot.advisor.initialize():
		exit()
	"""
	print("ACCOUNT.info: ", client.account_info)
	print("terminal.info: ", client.terminal_info)
	 """

	if not bot.advisor.check_symbols_availability():
		bot.advisor.shutdown()
		exit()
	
	with ft.ThreadPoolExecutor(max_workers=len(symbols)) as executor:
		executor.map(lambda symbol: bot.main(symbol, bot.advisor, bot.advisor.TF))
	bot.advisor.shutdown()
	