import time
import concurrent.futures as ft
import sys
import os	
# Now import MovingAverages
import Advisor
import MovingAverage.MovingAverage as MA
import Trade.TradesAlgo as algorithim
from GUI.userInput import UserGUI, LogWindow
import Telegram.Messanger as Tlg





class RunAdvisorBot:
	def __init__(self):
		self.symbols = None
		self.advisor = Advisor.MetaTrader5Client()
		self.init = None
  
		self.gui = UserGUI()
		self.logger = self.gui.log_window
  
		# sys.stdout = self.logger.redirector   # Redirect print to logger window
		# sys.stderr = self.logger.redirector   # Optional: Also set stderr if you want error logs too
		
		# Tlg.stop(self.stop_advisor)

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

	def main(self, user_data, symbol, client: Advisor.MetaTrader5Client):
	 
		print(f'✅ Thread started for {symbol}...')
		try:
			res = client.logIn(user_data)
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
		finally:
			client.shutdown()
			print(f'❌ Thread for {symbol} has ended.')
			# self.Logger.root.quit()
			# self.Logger.root.destroy()

if __name__ == "__main__":
    import sys

    bot = RunAdvisorBot()

    def start_bot_logic():
        tempClient = Advisor.MetaTrader5Client()
        res = tempClient.initialize(bot.gui.user_data)

        if not res[0]:
            print('❌ Failed to initialize MetaTrader5. Exiting...')
            sys.exit(1)

        bot.symbols = res[1]
        tempClient.shutdown()

        print('Marketwatch symbols:', bot.symbols)
        print('🏃‍♂️ Running threads...')

        with ft.ThreadPoolExecutor(max_workers=len(bot.symbols)) as executor:
            futures = {
                executor.submit(
                    bot.main,
                    bot.gui.user_data,
                    symbol,
                    client=Advisor.MetaTrader5Client()
                ): symbol for symbol in bot.symbols
            }

            for future in ft.as_completed(futures):
                symbol = futures[future]
                try:
                    future.result()
                except Exception as e:
                    print(f'❌ Thread for {symbol} failed with error: {e}')

    # Wait for GUI submission
    def check_gui_closed():
        if bot.gui.should_run:
            # Main GUI closed (after submit)
            print('running bot...')
            start_bot_logic()
        else:
            
            bot.gui.root.after(1000, check_gui_closed)

    check_gui_closed()
    bot.gui.root.mainloop()

