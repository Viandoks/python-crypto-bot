from datetime import datetime, timedelta
from botapi import BotApi
from botindicators import BotIndicators
import time
import sys
import pandas as pd
import shared

from botlog import BotLog


class BotChart(object):
    'Draws a classic trading chart, humanely readable'

    def __init__(self,period,startTime,endTime,backTest=True):

        self.exchange = shared.exchange['name']
        self.pair = shared.exchange['pair']
        self.period = int(period)
        self.startTime = int(startTime)
        self.endTime = int(endTime)
        self.backTest = bool(backTest)
        self.output = BotLog()
        self.tempCandle = None
        self.indicators = BotIndicators()

        self.data = []

        self.api = BotApi()

        if backTest:
            self.data = self.api.returnChartData(self.pair,period=int(self.period),start=self.startTime,end=self.endTime)

    def getPoints(self):
        return self.data


    def getCurrentPrice(self):
        if not self.backTest:
            currentValues = self.api.returnTicker(self.pair)
            lastPairPrice = {}
            lastPairPrice = currentValues["last"]
            return float(lastPairPrice)

    def drawChart(self, candlesticks, movingAverages, orders):

        # googlecharts
        output = open("./output/data.js",'w')
        output.truncate()

        # candlesticks
        candlesticks = pd.DataFrame.from_records([c.toDict() for c in candlesticks])
        ma = pd.DataFrame(movingAverages)
        candlesticks['ma'] = ma
        candlesticks.set_index('date', inplace=True)

        # orders
        orders = pd.DataFrame.from_records([o.toDict() for o in orders])
        if len(orders)>1:
            orders.set_index('date', inplace=True)
        else :
            orders['rate'] = 0
            orders['direction'] = 'None'
            orders['stopLoss'] = 0
            orders['takeProfit'] = 0
            orders['exitRate'] = 0

        # concat all to one dataframe
        data = pd.concat([candlesticks, orders], axis=1)
        data['direction'].fillna('None', inplace=True)
        data.fillna(0, inplace=True)

        # add to data.js
        output.write("var dataRows = "+data.to_json(orient='index')+";")
        output.write("var lastcall = '"+str(time.ctime())+"'")
