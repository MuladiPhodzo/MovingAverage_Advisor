import os
import sys
import pandas as pd
import MetaTrader5 as mt5

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../main/python")))

import advisor.Advisor as Client
import unittest


class Test_Advisor(unittest.TestCase):  
    def testInitializor(self):
        symbols = ["USDJPY", "USDCHF", "USDCAD", "USDZAR", "EURUSD"]
        client = Client.MetaTrader5Client(symbols)
        
        init = client.initialize()
        
        self.assertEqual(init, True)
        
        
    def testSymbolAvailability(self):
        symbols = ["USDJPY", "USDCHF", "USDCAD", "USDZAR", "EURUSD"]
        client = Client.MetaTrader5Client(symbols)
        
        client.initialize()
        availability = client.check_symbols_availability()
        
        self.assertEqual(availability, True)
        
    def test_GetLiveData(self):
        symbols = ["USDJPY", "USDCHF", "USDCAD", "USDZAR", "EURUSD"]
        timeframes = mt5.TIMEFRAME_H1
        
        client = Client.MetaTrader5Client(symbols)
        
        client.initialize()
        data = client.get_live_data("USDJPY", timeframes)
        
        self.assertTrue(data is not None)
        self.assertIsInstance(data, pd.DataFrame)
        
    def test_GetMultiTFData(self):
        symbols = ["USDJPY", "USDCHF", "USDCAD", "USDZAR", "EURUSD"]
        timeframes = {
            "HTF": mt5.TIMEFRAME_H4,
            "LTF": mt5.TIMEFRAME_H1
        }
        
        client = Client.MetaTrader5Client(symbols)
        
        client.initialize()
        data = client.get_multi_tf_data("USDJPY", timeframes)
        print(data)
        self.assertTrue(data is not None)
        self.assertIsInstance(data, dict)
        
        
if __name__ == '__main__':
    unittest.main()