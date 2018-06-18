import sys, getopt
import time

from botlog import BotLog

class BotCandlestick(object):
    def __init__(self,period,open=None,close=None,high=None,low=None,priceAverage=None,date=None):
        self.open = open
        self.close = close
        self.high = high
        self.low = low
        self.startTime = time.time()
        self.period = period
        self.output = BotLog()
        self.priceAverage = priceAverage
        self.date = date
        self.currentPrice = priceAverage
        if self.close:
            self.currentPrice = self.close



    def toDict(self):
        return {
            'currentPrice': self.currentPrice,
            'open' : self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'startTime': self.startTime,
            'period': self.period,
            'priceAverage': self.priceAverage,
            'date': self.date
        }

    def tick(self,price):
        self.currentPrice = float(price)
        if self.date is None:
            self.date = time.time()
        if (self.open is None):
            self.open = self.currentPrice

        if (self.high is None) or (self.currentPrice > self.high):
            self.high = self.currentPrice

        if (self.low is None) or (self.currentPrice < self.low):
            self.low = self.currentPrice

        if time.time() >= ( self.startTime + self.period):
            self.close = self.currentPrice
            self.priceAverage = ( self.high + self.low + self.close ) / float(3)

        self.output.log("Start time: "+str(self.startTime)+", period: "+str(self.period)+" Open: "+str(self.open)+" Close: "+str(self.close)+" High: "+str(self.high)+" Low: "+str(self.low)+" currentPrice: "+str(self.currentPrice))

    def isClosed(self):
        if (self.close is not None):
            return True
        else:
            return False
