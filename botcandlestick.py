from botlog import BotLog

import shared
import sys, getopt
import time
import utils


class BotCandlestick(object):
    def __init__(self,date=None,open=None,high=None,low=None,close=None,volume=None):
        self.close = close
        self.currentPrice = close
        self.date = date
        self.high = high
        self.low = low
        self.open = open
        self.output = BotLog()
        self.priceAverage = False
        self.startTime = time.time()
        self.volume = volume

        if self.close:
            self.currentPrice = self.close

    def __setitem__(self, key, value):
          setattr(self, key, value)

    def __getitem__(self, key):
          return getattr(self, key)

    def toDict(self):
        return {
            'close': self.close,
            'currentPrice': self.currentPrice,
            'date': self.date,
            'high': self.high,
            'low': self.low,
            'open' : self.open,
            'priceAverage': self.priceAverage,
            'startTime': self.startTime,
            'volume': self.volume
        }

    def tick(self, price):
        self.currentPrice = float(price)

        if self.date is None:
            self.date = time.time()
        if (self.open is None):
            self.open = self.currentPrice

        if (self.high is None) or (self.currentPrice > self.high):
            self.high = self.currentPrice

        if (self.low is None) or (self.currentPrice < self.low):
            self.low = self.currentPrice


        timedelta = utils.parseTimedelta(shared.strategy['timeframe'])
        if time.time() >= ( self.startTime + timedelta):
            self.close = self.currentPrice
            self.priceAverage = ( self.high + self.low + self.close ) / float(3)

        self.output.log("Start time: "+str(self.startTime)+",  Open: "+str(self.open)+" Close: "+str(self.close)+" High: "+str(self.high)+" Low: "+str(self.low)+" currentPrice: "+str(self.currentPrice))

    def isClosed(self):
        if (self.close is not None):
            return True
        else:
            return False
