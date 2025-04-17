import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import numpy as np

class MovingAverageCrossover:

    def __init__(self,  symbol, data, fast_period=50, slow_period=150):
        """
        Initialize the strategy with data and parameters.
        
        :param data: DataFrame containing historical data (must include 'close').
        :param fast_period: Period for the fast-moving average.
        :param slow_period: Period for the slow-moving average.
        """
        ltf_data = data
        self.entries = None
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signals = None
        self.results = None
        self.symbol = symbol

    def calculate_moving_averages(self, data):
        """Calculate the fast and slow moving averages."""
        if 'close' not in data.columns:
            raise ValueError("'close' column is missing in the data.")
  
        data['Fast_MA'] = data['close'].rolling(window=self.fast_period).mean().shift()
        data['Slow_MA'] = data['close'].rolling(window=self.slow_period).mean().shift()
        data['Signal'] = np.where(data['Fast_MA'] > data['Slow_MA'], 1, 
                          np.where(data['Fast_MA'] < data['Slow_MA'], -1, 0))
  
        data['Crossover'] = data['Signal'].diff()
        data['Bias'] = np.where(data['Fast_MA'] > data['Slow_MA'], "Bullish", "Bearish")


        self.data = data.dropna()
        print(f'📈 MA Data Available for {self.symbol}')
        print("Moving averages calculated.")
        return self.data	

    def identify_entry_levels(self, HTS_data: pd.DataFrame, LTS_data: pd.DataFrame):
        """
        _summary_
        Identify entry levels (buy and sell) based on crossovers.
        requires HTS_data and LTS_data to have 'Bias' column.

        Returns:
            - LTS_data: DataFrame with entry levels and stop loss/take profit levels.
            _type_: _DataFrame_
        """        
        if 'Bias' not in HTS_data.columns or 'Bias' not in LTS_data.columns:
            raise ValueError("'Bias' column is missing in the data.")   
        
        # Define constants outside the loop
        sl_distance = 0.003
        tp_distance = 0.01
        threshold = 50 * 0.01 if self.symbol == 'USDJPY' else 0.0050  # 50 pips × pip size

        for i in range(len(LTS_data)):
            row = LTS_data.iloc[i]
            ltf_time = pd.to_datetime(row['time'])

            # Match HTF row
            htf_match = HTS_data[HTS_data['time'] <= ltf_time]
            if htf_match.empty:
                continue

            htf_row = htf_match.iloc[-1]
            market_bias = htf_row['Bias']
            ltf_bias = row['Bias']
            
            # Derive LTF label
            ltf_Bias_label = "Buy" if ltf_bias == 'Bullish' else "Sell"

            # Calculate Range
            range_value = abs(row['close'] - row['Fast_MA'])

            # Set columns cleanly
            LTS_data.loc[i, 'Market_bias'] = market_bias
            LTS_data.loc[i, 'ltf_bias'] = ltf_bias
            LTS_data.loc[i, 'Range'] = range_value

            if range_value <= threshold:
                if market_bias == 'Bullish' and ltf_Bias_label == 'Buy' and row['close'] > row['Fast_MA']:
                    LTS_data.loc[i, 'Entry'] = 'Buy'
                    LTS_data.loc[i, 'Level'] = row['close']
                    LTS_data.loc[i, 'SL'] = row['close'] - sl_distance
                    LTS_data.loc[i, 'TP'] = row['close'] + tp_distance

                elif market_bias == 'Bearish' and ltf_Bias_label == 'Sell' and row['close'] < row['Fast_MA']:
                    LTS_data.loc[i, 'Entry'] = 'Sell'
                    LTS_data.loc[i, 'Level'] = row['close']
                    LTS_data.loc[i, 'SL'] = row['close'] + sl_distance
                    LTS_data.loc[i, 'TP'] = row['close'] - tp_distance

            else:
                LTS_data.loc[i, 'Entry'] = None
                LTS_data.loc[i, 'Level'] = None
                LTS_data.loc[i, 'SL'] = None
                LTS_data.loc[i, 'TP'] = None


        # Clean up bad columns created by tuple headers (from Excel maybe?)
        cleaned_data = LTS_data.drop(columns=['tick_volume', 'real_volume', 'spread', 'Signal'])
        # trades = cleaned_data.copy().dropna()
        
        print(f'{self.symbol}-entries:\n {cleaned_data.head(50)}')
            
        return cleaned_data
                
            
        print("Entry levels identified.")

    def save_signals_to_csv(self, data, file_name="src/main/python/advisor/Logs"):
        """
        Save identified entry levels to a CSV file.
        - Creates the file if it doesn't exist.
        - Appends to the file if it already exists.
        """
  
        if data is not None:
            file_exists = os.path.isfile(file_name)
            if not file_exists:
                data.to_csv(file_name, index=False, mode='w')
                print(f"New file created and entry levels saved to {file_name}.")
            else:
                data.to_csv(file_name, index=False, mode='a', header=False)
                print(f"Entry levels appended to existing file {file_name}.")
        else:
                print("No signals to save. Please run 'identify_entry_levels()' first.")

    def backtest_strategy(self):
        """Backtest the strategy by calculating strategy returns."""

        self.data['Position'] = self.data['Entry'].shift(1)  # Avoid lookahead bias
        self.data['Market_Returns'] = self.data['close'].pct_change()
        self.data['Strategy_Returns'] = self.data['Market_Returns'] * self.data['Position']
        self.data['Cumulative_Market_Returns'] = (1 + self.data['Market_Returns']).cumprod()
        self.data['Cumulative_Strategy_Returns'] = (1 + self.data['Strategy_Returns']).cumprod()
        self.results = self.data.dropna().copy() 
        print("Backtest completed.")
        return self.results

    def plot_performance(self):
        """Visualize the strategy performance against market performance."""
        if self.results is None:
                raise ValueError("No results available. Run backtest_strategy() first.")
        
        plt.figure(figsize=(12, 6))
        plt.plot(self.results.index, self.results['Cumulative_Market_Returns'], label='Market Returns', color='blue')
        plt.plot(self.results.index, self.results['Cumulative_Strategy_Returns'], label='Strategy Returns', color='green')
        plt.title('Moving Average Crossover Strategy Performance')
        plt.legend()
        plt.show()
            
    def plot_charts(self, ltf_data):
        if 'Entry' not in ltf_data.columns:
            raise ValueError("Error: 'Entry' column is missing in `ltf_data`. Check data processing.")
        if 'close' not in ltf_data.columns or ltf_data['close'].empty:
            raise ValueError("No Close data available")

        # Ensure both datasets use datetime index for consistency
        if not isinstance(self.data.index, pd.DatetimeIndex):
            self.data.index = pd.to_datetime(self.data.index)

        # Check for abnormally large timestamp (only if needed)
        # max_time = ltf_data['time'].max()
        # if isinstance(max_time, pd.Timestamp) and max_time.timestamp() > 1e11:
        #     raise ValueError("Abnormally large timestamp detected in 'time' column.")

        # else:
        #     ltf_data['time'] = pd.to_datetime(ltf_data['time'], unit='s')
        #     ltf_data.set_index('time', inplace=True)
        # Only keep rows where the index (or time column) is not null
        fig, ax = plt.subplots(figsize=(18, 6))

        # Plot market data (uses self.data.index)
        # Ensure time column is in datetime format and sorted
        ltf_data['time'] = pd.to_datetime(ltf_data['time'])
        ltf_data = ltf_data.sort_values(by='time')

        # Set time as x-axis ticks properly
        ax.plot(ltf_data['time'], ltf_data['close'], label="Close", color='black')
        ax.plot(ltf_data['time'], ltf_data['Fast_MA'], label=f"Fast MA ({self.fast_period})", color='blue')
        ax.plot(ltf_data['time'], ltf_data['Slow_MA'], label=f"Slow MA ({self.slow_period})", color='red')
        
        ax.fill_between(ltf_data['time'], ltf_data['Fast_MA'], ltf_data['Slow_MA'], where=(ltf_data['Fast_MA'] > ltf_data['Slow_MA']), color='green', alpha=0.3, label='Bullish Zone')
        ax.fill_between(ltf_data['time'], ltf_data['Fast_MA'], ltf_data['Slow_MA'], where=(ltf_data['Fast_MA'] < ltf_data['Slow_MA']), color='red', alpha=0.3, label='Bearish Zone')
        ax.fill_between(ltf_data['time'], ltf_data['Fast_MA'], ltf_data['close'], where=(ltf_data['Fast_MA'] - ltf_data['close'] <= 0.005), color='orange', alpha=0.3, label='Range')

        # Plot Buy signals
        buy_signals = ltf_data[ltf_data['Entry'] == 'Buy']
        if not buy_signals.empty:
            for i in buy_signals.index:
                time = buy_signals.loc[i, 'time']
                tp = buy_signals.loc[i, 'TP']
                sl = buy_signals.loc[i, 'SL']
                ax.scatter(time, buy_signals.loc[i, 'Level'], marker='^', color='green', label='Buy Signal' if i == buy_signals.index[0] else "")
                # Draw short horizontal lines (1-minute window or so)
                ax.hlines(y=tp, xmin=time - pd.Timedelta(minutes=1), xmax=time + pd.Timedelta(minutes=1),
                        color='green', linestyles='--', label='TP' if i == buy_signals.index[0] else "")
                
                ax.hlines(y=sl, xmin=time - pd.Timedelta(minutes=1), xmax=time + pd.Timedelta(minutes=1),
                        color='red', linestyles='--', label='SL' if i == buy_signals.index[0] else "")
        # Plot Sell signals
        sell_signals = ltf_data[ltf_data['Entry'] == 'Sell']
        if not sell_signals.empty:
            for i in sell_signals.index:
                time = sell_signals.loc[i, 'time']
                tp = sell_signals.loc[i, 'TP']
                sl = sell_signals.loc[i, 'SL']
                
                ax.scatter(time, sell_signals.loc[i, 'Level'], marker='v', color='red', label='Sell Signal' if i == sell_signals.index[0] else "")
                
                # Draw short horizontal lines (1-minute window or so)
                ax.hlines(y=tp, xmin=time - pd.Timedelta(minutes=1), xmax=time + pd.Timedelta(minutes=1),
                        color='green', linestyles='--', label='TP' if i == sell_signals.index[0] else "")
                
                ax.hlines(y=sl, xmin=time - pd.Timedelta(minutes=1), xmax=time + pd.Timedelta(minutes=1),
                        color='red', linestyles='--', label='SL' if i == sell_signals.index[0] else "")

        ax.set_xticks(ltf_data['time'][::max(1, len(ltf_data) // 10)])  # show ~10 evenly spaced labels
        ax.tick_params(axis='x', rotation=45)

        plt.title(f"{self.symbol}-Moving Average Entry Signals")
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.xticks(rotation=45)
        plt.xlabel("Time")
        plt.ylabel("Price")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()    
    
    def run_moving_average_strategy(self, symbol, data, MA: 'MovingAverageCrossover'):
        """
        Fetch rates data and apply the Moving Average Crossover strategy.

        :param symbol: The symbol to fetch data for (e.g., 'EURUSD').
        :param timeframe: Timeframe for the rates (e.g., mt5.TIMEFRAME_M15).
        :param start_time: Starting datetime for fetching rates.
        :param count: Number of bars to fetch.
        """
    
        ltf_data  = data['LTF']
        htf_data = data['HTF']
        
        if data is None:
            print(f"Failed to retrieve data for {symbol}.")
            return None
        
        ltf_data = self.identify_entry_levels(ltf_data, htf_data)
        self.save_signals_to_csv(file_name=f"src/main/python/Advisor/Logs/{self.symbol}_entry_levels.csv", data=ltf_data)
        
        # results = self.backtest_strategy()

        # Plot the results
        self.plot_charts(ltf_data)
        # self.plot_performance()s
        
