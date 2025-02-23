import advisor.Advisor as Client
import unittest


class TestYourModule(unittest.TestCase):  
    def testInitializor(self):
        symbols = ["USDJPY", "USDCHF", "USDCAD", "USDZAR", "EURUSD"]
        client = Client.MetaTrader5Client(symbols)
        
        init = client.initialize()
        
        self.assertEqual(init, True)