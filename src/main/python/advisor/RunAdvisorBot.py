import time
import concurrent.futures as ft
import sys
import threading, queue

import Advisor
import MovingAverage.MovingAverage as MA
import Trade.TradesAlgo as algorithim
from GUI.userInput import UserGUI


class RunAdvisorBot:
    def __init__(self):
        self.symbols = None
        self.client = Advisor.MetaTrader5Client()
        self.init = None
        self.gui = UserGUI()
        self.symbol_queue = queue.Queue()

    def backtest(self, symbols: list):
        client = Advisor.MetaTrader5Client()
        client.initialize()
        for symbol in symbols:
            data = client.get_rates_range(symbol)
            
            htf_strategy = MA.MovingAverageCrossover(symbol, data=data["HTF"])
            ltf_strategy = MA.MovingAverageCrossover(symbol, data=data["LTF"])
            
            HTF_data = htf_strategy.calculate_moving_averages(data["HTF"])
            LTF_data = ltf_strategy.calculate_moving_averages(data["LTF"])
            
            data = {'HTF': HTF_data, 'LTF': LTF_data}
            ltf_strategy.run_moving_average_strategy(symbol, data, ltf_strategy)

    def worker(self):
        while not self.symbol_queue.empty():
            symbol = self.symbol_queue.get()
            try:
                print(f'✅ Thread started for {symbol}...')
                while self.init:
                    data = self.client.get_multi_tf_data(symbol)
                    if data is None:
                        print(f'❌ No data returned for {symbol}. Retrying in 10 seconds...')
                        time.sleep(10)
                        continue

                    print(f'📊 Data retrieved for {symbol}............')
                    if "HTF" not in data or "LTF" not in data:
                        print(f'⚠️ Missing timeframes for {symbol}. Skipping...')
                        break

                    print(f'✅ Processing {symbol} with Multi Timeframe Data')
                    htf_strategy = MA.MovingAverageCrossover(symbol, data=data["HTF"])
                    ltf_strategy = MA.MovingAverageCrossover(symbol, data=data["LTF"])

                    HTF_data = htf_strategy.calculate_moving_averages(data["HTF"])
                    LTF_data = ltf_strategy.calculate_moving_averages(data["LTF"])

                    if "Fast_MA" not in LTF_data.columns or "Slow_MA" not in LTF_data.columns:
                        print(f'❌ Missing MA columns in LTF data for {symbol}')
                        break

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
                    trade.run_Trades(market_Bias, ltf_Bias, ltf_latest, current_price, self.client.THRESHOLD, symbol)

                    print(f'🛌 {symbol} Thread sleeping for 15 minutes....')
                    time.sleep(900)  # 15 minutes

            except Exception as e:
                print(f'❌ Exception in thread {symbol}: {e}')

            finally:
                self.symbol_queue.task_done()
                print(f'❌ Thread for {symbol} has ended.')

    def start_bot_logic(self):
        tempClient = Advisor.MetaTrader5Client()
        res = tempClient.initialize(self.gui.user_data)
        if not res[0]:
            print('❌ Failed to initialize MetaTrader5. Exiting...')
            sys.exit(1)

        self.symbols = res[1]
        tempClient.shutdown()
        print('Marketwatch symbols:', self.symbols)

        for sym in self.symbols:
            self.symbol_queue.put(sym)

        if not self.client.logIn(self.gui.user_data):
            print('❌ Login failed.')
            return
        self.init = True

        print('🏃‍♂️ Running worker threads...')
        threads = []
        for _ in range(min(5, len(self.symbols))):  # Max 5 workers
            t = threading.Thread(target=self.worker)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        print("✅ All threads completed.")
        self.client.shutdown()


if __name__ == "__main__":
    bot = RunAdvisorBot()

    def check_gui_closed():
        if bot.gui.should_run:
            print('🟢 GUI closed, running bot...')
            bot.start_bot_logic()
        else:
            bot.gui.root.after(1000, check_gui_closed)

    check_gui_closed()
    bot.gui.root.mainloop()
