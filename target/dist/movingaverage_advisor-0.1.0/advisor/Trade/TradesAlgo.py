import MetaTrader5 as mt5
import pandas as pd
import datetime as dt

class MT5TradingAlgorithm:
    def __init__(self, symbol, lot_size=0.1, magic_number=1000):
        """
        Initialize the MT5 trading algorithm.
        :param symbol: The trading symbol (e.g., 'USDJPY').
        :param lot_size: The size of each trade.
        :param magic_number: Unique identifier for this strategy's trades.
        """
        self.TradesData = None
        self.symbol = symbol
        self.lot_size = lot_size
        self.magic_number = magic_number
        self.current_position = None  # Track 'buy', 'sell', or None

    def place_order(self, action, stop_loss=100, take_profit=300):
        """
        Place a buy or sell order.
        :param action: 'buy' or 'sell'.
        """
        # Define order type
        order_type = mt5.ORDER_TYPE_BUY if action == 'buy' else mt5.ORDER_TYPE_SELL
        print(f"🟢 Placing {order_type.upper()} order...")
        # Get symbol info
        symbol_info = mt5.symbol_info(self.symbol)
        point = symbol_info.point
        if not symbol_info:
            print(f"Symbol {self.symbol} not found, cannot place order.")
            return False

        # Prepare order request
        price = mt5.symbol_info_tick(self.symbol).ask if action == 'buy' else mt5.symbol_info_tick(self.symbol).bid
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": self.lot_size,
            "type": order_type,
            "price": price,
            "sl": price - stop_loss * point if order_type == mt5.ORDER_TYPE_BUY else price + stop_loss * point,
            "tp": price + take_profit * point if order_type == mt5.ORDER_TYPE_BUY else price - take_profit * point,
            "deviation": 10,
            "magic": self.magic_number,
            "comment": f"{action.capitalize()} trade by Moving Average strategy",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        # Send order
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Order failed: {result.retcode}")
            return False

        
        print(f"{action.capitalize()} order placed at {price}.")
        self.TradesData.add(request)
        self.TradesData = self.TradesData.drop(columns=['type_time', 'comment', 'type_filling', 'deviation'])
        self.current_position = action
        return True, request

    def run_Trades(self, market_bias, ltf_Bias,ltf_latest, current_price, THRESHOLD, symbol ):
        result : bool
        if abs(current_price - ltf_latest['Fast_MA']) <= THRESHOLD:
            if market_bias == "Bullish" and ltf_Bias == 'Buy' and current_price > ltf_latest['Fast_MA']:
                print(f"{symbol} - Confirmed Bullish Signal - Placing BUY order")
                result = self.place_order("buy")
                self.TradesData = ltf_latest
            elif market_bias == "Bearish" and ltf_Bias == 'Sell' and current_price < ltf_latest['Fast_MA']:
                print(f"{symbol} - Confirmed Bearish Signal - Placing SELL order")
                result = self.place_order("sell")
                self.TradesData = ltf_latest
            print(result)
        else:
            print(f'{self.symbol}-current price: {current_price} Fast_MA: {ltf_latest["Fast_MA"]}'),
            print(f"{dt.datetime.now()} {symbol} - No valid entry signal ")
            
    def close(self):
        """Shutdown MT5 connection."""
        mt5.shutdown()
        print("Disconnected from MetaTrader 5.")
