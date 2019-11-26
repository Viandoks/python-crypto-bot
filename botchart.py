from botapi import BotApi
from botcandlestick import BotCandlestick


from datetime import datetime, timedelta
import pandas as pd
import time
import shared
import sys

from botlog import BotLog


class BotChart(object):
    'Draws a classic trading chart, humanely readable'

    def __init__(self,timeframe,startTime,endTime,backTest=True):

        self.pair = shared.exchange['pair']
        self.timeframe = str(timeframe)
        self.startTime = str(startTime)
        self.endTime = str(endTime)
        self.backTest = bool(backTest)
        self.output = BotLog()
        self.tempCandle = None

        self.data = []

        # API
        self.api = BotApi()

        if backTest:
            from_timestamp = self.api.parse8601(self.startTime)
            try:
                print(self.api.milliseconds(), 'Fetching candles starting from', self.api.iso8601(from_timestamp))
                ohlcvs = self.api.fetch_ohlcv(shared.exchange['pair'], timeframe=self.timeframe, since=from_timestamp)
                print(self.api.milliseconds(), 'Fetched', len(ohlcvs), 'candles')

                for ohlcv in ohlcvs:
                    self.data.append(BotCandlestick(float(ohlcv[0]), float(ohlcv[1]), float(ohlcv[2]), float(ohlcv[3]), float(ohlcv[4]), float(ohlcv[5])))


            except (ccxt.ExchangeError, ccxt.AuthenticationError, ccxt.ExchangeNotAvailable, ccxt.RequestTimeout) as error:
                print('Got an error', type(error).__name__, error.args)
                exit(2)

    def getPoints(self):
        return self.data

    def getCurrentPrice(self):
        if not self.backTest:
            ticker = self.api.fetchTicker(self.pair)
            price = ticker["last"]
            return float(price)

    def drawChart(self, candlesticks, orders, movingAverages):

        # googlecharts
        output = open("./output/data.js",'w')
        output.truncate()

        # candlesticks
        candlesticks = pd.DataFrame.from_records([c.toDict() for c in candlesticks])
        ma = pd.DataFrame(movingAverages)
        if len(ma) > 0:
            candlesticks['ma'] = ma
        else:
            candlesticks['ma'] = 0
        candlesticks['date'] = candlesticks['date']/1000
        candlesticks.set_index('date', inplace=True)

        # orders
        orders = pd.DataFrame.from_records([o.toDict() for o in orders])
        orders['date'] = orders['date']/1000
        if len(orders)>1:
            orders.set_index('date', inplace=True)
        else :
            orders['orderNumber'] = 0
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
