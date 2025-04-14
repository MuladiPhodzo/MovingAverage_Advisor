import os
import sys
import pandas as pd
import MetaTrader5 as mt5

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../main/python")))

import advisor.Advisor as Client
import unittest


class Test_Advisor(unittest.TestCase):  
    def testInitializor(self):
        
        client = Client.MetaTrader5Client()
        
        init = client.initialize()
        
        self.assertEqual(init[0], True)
        
        
    def testSymbolAvailability(self):
        
        client = Client.MetaTrader5Client()
        
        client.initialize()
        availability = client.check_symbols_availability()
        
        self.assertEqual(availability, True)
        
    def test_GetLiveData(self):
        
        timeframes = mt5.TIMEFRAME_H1
        
        client = Client.MetaTrader5Client()
        
        client.initialize()
        data = client.get_live_data("USDJPY", timeframes)
        
        self.assertTrue(data is not None)
        self.assertIsInstance(data, pd.DataFrame)
        
    def test_GetMultiTFData(self):
        
        timeframes = {
            "HTF": mt5.TIMEFRAME_H4,
            "LTF": mt5.TIMEFRAME_H1
        }
        
        client = Client.MetaTrader5Client()
        
        client.initialize()
        data = client.get_multi_tf_data("USDJPY")
        print(data)
        self.assertTrue(data is not None)
        self.assertIsInstance(data, dict)
        
        
if __name__ == '__main__':
    unittest.main()