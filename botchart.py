from datetime import datetime, timedelta
import time
import sys
import poloniex
import pandas as pd
import shared

from botcandlestick import BotCandlestick
from botindicators import BotIndicators
from botlog import BotLog


class BotChart(object):
    def __init__(self,exchange,period,startTime,endTime,backTest=True):

        self.exchange = str(exchange)
        self.pair = shared.exchange['pair']
        self.period = int(period)
        self.startTime = int(startTime)
        self.endTime = int(endTime)
        self.backTest = bool(backTest)
        self.indicators = BotIndicators()
        self.output = BotLog()
        self.tempCandle = None

        self.data = []

        if (self.exchange == "poloniex"):
            self.api = poloniex.Poloniex()

            if backTest:
                if (self.period not in [300,900,1800,7200,14400,86400]):
                    self.output.fail('Poloniex requires periods in 300,900,1800,7200,14400, or 86400 second increments')
                    sys.exit(2)
                poloData = self.api.returnChartData(self.pair,period=int(self.period),start=self.startTime,end=self.endTime)
                for datum in poloData:
                    if (datum['open'] and datum['close'] and datum['high'] and datum['low'] and datum['date']):
                        self.data.append(BotCandlestick(self.period,float(datum['open']),float(datum['close']),float(datum['high']),float(datum['low']),float(datum['weightedAverage']), float(datum['date'])))



    def getPoints(self):
        return self.data


    def getCurrentPrice(self):
        if not self.backTest:
            currentValues = self.api.returnTicker()[self.pair]
            lastPairPrice = {}
            lastPairPrice = currentValues["last"]
            return float(lastPairPrice)

    def drawChart(self, candlesticks, movingAverages, trades):

        # googlecharts
        output = open("./output/data.js",'w')
        output.truncate()
        temp = []
        x = 0
        for candle in candlesticks:
            temp.append(candle.toDict())
            if x < len(movingAverages):
                temp[x]['ma'] = movingAverages[x]
                x+=1
            else:
                closes = []
                for c in candlesticks[-(shared.strategy['movingAverageLength']):]:
                    closes.append(c.close)
                ma = self.indicators.movingAverage(closes, shared.strategy['movingAverageLength'])
                temp[x]['ma'] = ma

        candlesticks = pd.DataFrame(temp)
        candlesticks.set_index('date', inplace=True)

        orders = []
        for o in trades:
            orders.append({'date': o.date, 'orderRate': o.entryPrice, 'orderDirection': o.direction, 'stopLoss':o.stopLoss, 'takeProfit': o.takeProfit, 'exitPrice':o.exitPrice})
        orders = pd.DataFrame(orders)
        if len(orders)>1:
            orders.set_index('date', inplace=True)
        else :
            orders = pd.DataFrame()
            orders['orderRate'] = 0
            orders['orderDirection'] = 'None'
            orders['stopLoss'] = 0
            orders['takeProfit'] = 0
            orders['exitPrice'] = 0

        points = pd.concat([candlesticks, orders], axis=1)
        points['orderRate'].fillna(0, inplace=True)
        points['stopLoss'].fillna(0, inplace=True)
        points['takeProfit'].fillna(0, inplace=True)
        points['orderDirection'].fillna('None', inplace=True)
        points['exitPrice'].fillna(0, inplace=True)

        output.write("var dataRows = [];")

        # New elements should be added to dataRows in accordance with the datatable in output.hmtl
        for date, point in points.iterrows():
            output.write("dataRows.push([new Date("+str(int(date)*1000)+"), "+str(point.low)+", "+str(point.open)+","+str(point.close)+","+str(point.high)+","+str(point.ma)+","+str(point.orderRate)+",'"+str(point.orderDirection)+"',"+str(point.stopLoss)+","+str(point.takeProfit)+","+str(point.exitPrice)+"]);\n")


        output.write("var lastcall = '"+str(time.ctime())+"'")
