import unittest
import pandas as pd
from advisor.MovingAverage import MovingAverage as MA
import advisor.Advisor as Client
import MetaTrader5 as mt5


class test_MovingAverages(unittest.TestCase):
    
    def setUp_Client(self):
         client = Client.MetaTrader5Client('ÚSDJPY')
         
         data = client.get_live_data('USDJPY', mt5.TIMEFRAME_H1)
         
         return data
    
    def test_CalculateAverages(self):
        clientData = self.setUp_Client()
        
        Averages = MA.MovingAverageCrossover('USDJPY', clientData)
        
        AveragesData = Averages.calculate_moving_averages()
        
        self.assertTrue(AveragesData is not None)
        self.assertIsInstance(AveragesData, pd.DataFrame)
        self.assertTrue('Fast_MA' in AveragesData.columns)
        self.assertTrue('Slow_MA' in AveragesData.columns)
        self.assertTrue('Crossover' in AveragesData.columns)
        self.assertTrue('Bias' in AveragesData.columns)
        self.assertTrue('Signal' in AveragesData.columns)
    
    def test_BackTest(self):
        clientData = self.setUp_Client()
        
        Averages = MA.MovingAverageCrossover('USDJPY', clientData)
        
        AveragesData = Averages.calculate_moving_averages()
        
        BackTestedData = Averages.backtest_strategy()
        
        self.assertTrue(BackTestedData is not None)
        self.assertIsInstance(BackTestedData, pd.DataFrame)
        self.assertTrue('Position' in BackTestedData.columns)
        self.assertTrue('Market_Returns' in BackTestedData.columns)
        self.assertTrue('Strategy_Returns' in BackTestedData.columns)
        self.assertTrue('Cumulative_Market_Returns' in BackTestedData.columns)
        self.assertTrue('Cumulative_Strategy_Returns' in BackTestedData.columns)
    
    def test_runMovingAverageStrategy(self):
        pass