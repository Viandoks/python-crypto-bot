from botapi import BotApi
from botindicators import BotIndicators
from botlog import BotLog
from bottrade import BotTrade

import shared
import sys


# THIS STRATEGY IS OBVIOUSLY NOT WORKING! DON'T GO LIVE USING IT!!!
# THIS STRATEGY IS OBVIOUSLY NOT WORKING! DON'T GO LIVE USING IT!!!
# THIS STRATEGY IS OBVIOUSLY NOT WORKING! DON'T GO LIVE USING IT!!!
# THIS STRATEGY IS OBVIOUSLY NOT WORKING! DON'T GO LIVE USING IT!!!
# THIS STRATEGY IS OBVIOUSLY NOT WORKING! DON'T GO LIVE USING IT!!!
# THIS STRATEGY IS OBVIOUSLY NOT WORKING! DON'T GO LIVE USING IT!!!
# THIS STRATEGY IS OBVIOUSLY NOT WORKING! DON'T GO LIVE USING IT!!!
class BotStrategy(object):
    def __init__(self, backtest=True, live=False):
        self.output = BotLog()
        self.pair = shared.exchange['pair']
        self.coinsInOrder = shared.exchange['coinsInOrder']
        self.marketInOrder = shared.exchange['marketInOrder']
        self.trades = []
        self.currentPrice = ""
        self.currentClose = ""
        self.live = live
        self.lowestAsk = 0.00
        self.highestBid = 0.00
        self.simultaneousTrades = 1
        self.tradeMultiplier = 1
        self.ticker = {}
        self.backTest = backtest
        self.indicators = BotIndicators()

        self.candlesticks = []
        self.movingAverages = []
        self.movingAveragePeriod = 3
        self.trueRanges = []
        self.averageTrueRanges = []
        self.openOrders = []

        # API
        self.api = BotApi()

    def tick(self, candlestick):

        # strategy works on closed candles only
        if not candlestick.isClosed():
            return
        else:
            self.candlesticks.append(candlestick)

        self.currentPrice = candlestick.currentPrice
        ma = self.indicators.sma(self.candlesticks, shared.strategy['movingAverageLength'], 'close')
        self.movingAverages.append(ma)

        tr = self.indicators.trueRange(self.candlesticks)
        self.trueRanges.append(tr)

        atr = self.indicators.averageTrueRange(self.candlesticks, 5)
        self.averageTrueRanges.append(atr)

        self.ticker = self.getTicker()

        portfolioUpdated = self.updatePortfolio()
        # If live and portfolio not updated, we may run into some unpleasant issues.
        # Better stop here for now
        if not portfolioUpdated:
            return

        # Strategy needs at least 2 candles to work
        if len(self.candlesticks) > 1 and candlestick.isClosed():
            self.updateOpenTrades(self.pair)
            self.evaluatePositions()

    def evaluatePositions(self):

        openOrders = self.getOpenOrders(self.pair)

        '''
            Go Long (buy) if all of these are met:
                Previous  price is lower movingAverage
                Current price is higher than moving average
            Go short (sell) if:
                Previous price is higher than moving average
                Current Price is lower than moving average
        '''

        golong1 = self.candlesticks[-2].close < self.movingAverages[-1]
        golong2 = self.currentPrice > self.movingAverages[-1]
        goshort1 = self.candlesticks[-2].close > self.movingAverages[-1]
        goshort2 = self.currentPrice < self.movingAverages[-1]

        if golong1 and golong2 and len(openOrders) < self.simultaneousTrades:
            rate = float(self.ticker['lowestAsk'])
            total = (shared.exchange['nbMarket']-shared.exchange['marketInOrder'])*self.tradeMultiplier
            self.buy(rate, total, self.candlesticks[-1].date)

        if goshort1 and goshort2 and len(openOrders) < self.simultaneousTrades:
            rate = float(self.ticker['highestBid'])
            amount = (shared.exchange['nbAsset']-shared.exchange['coinsInOrder'])*self.tradeMultiplier
            self.sell(rate, amount, self.candlesticks[-1].date)

    def updateOpenTrades(self, pair):
        openOrders = self.getOpenOrders(pair)
        # TODO: implement not backtest
        for trade in openOrders:
            trade.tick(self.candlesticks[-1], self.candlesticks[-1].date)

    def getOpenOrders(self, pair):
        openOrders = []
        #TODO: implement live
        for order in self.trades:
            if order.status == 'OPEN':
                openOrders.append(order)
        return openOrders

    def getTicker(self):
        if not self.backTest:
            ticker = self.api.exchange.fetchTicker(self.pair)
            return {
                'last': ticker['last'],
                'highestBid': ticker['bid'],
                'lowestAsk': ticker['ask']
            }
        else:
            return {
                'last': self.currentPrice,
                'highestBid': self.currentPrice-self.currentPrice*shared.exchange['spreadPercentage'],
                'lowestAsk': self.currentPrice+self.currentPrice*shared.exchange['spreadPercentage']
            }

    def updatePortfolio(self):
        if not self.backTest and self.live:
            try:
                portfolio = self.api.exchange.fetchBalance()
                if shared.exchange['market'] in portfolio:
                    shared.exchange['nbMarket'] = float(portfolio[shared.exchange['market']]['free'])
                    shared.exchange['marketInOrder'] = float(portfolio[shared.exchange['market']]['used'])
                else:
                    shared.exchange['nbMarket'] = 0.00
                    shared.exchange['marketInOrder'] = 0.00
                if shared.exchange['coin'] in portfolio:
                    shared.exchange['nbCoin'] = float(portfolio[shared.exchange['coin']]['free'])
                    shared.exchange['coinsInOrder'] = float(portfolio[shared.exchange['coin']]['used'])
                else:
                    shared.exchange['nbCoin'] = 0.00
                    shared.exchange['coinsInOrder'] = 0.00
                return True
            except Exception as e:
                self.output.warning("Error updating portfolio")
                print(e)
                return False
        else:
            return True

    def showPortfolio(self):
        if not self.backTest and self.live:
            self.updatePortfolio()
        self.output.log(str(shared.exchange['nbMarket'])+" "+str(shared.exchange['market'])+' - '+str(shared.exchange['nbAsset'])+" "+str(shared.exchange['asset']))

    def buy(self, rate, total, date, stopLoss=0, takeProfit=0):
        amount = total/rate
        order = BotTrade('BUY', rate=rate, amount=amount, total=total, date=date, stopLoss=stopLoss, takeProfit=takeProfit, backtest=self.backTest, live=self.live)
        self.trades.append(order)


    def sell(self, rate, amount, date, stopLoss=0, takeProfit=0):
        total = rate*amount
        order = BotTrade('SELL',rate=rate,amount=amount, total=total, date=date, stopLoss=stopLoss, takeProfit=takeProfit, backtest=self.backTest, live=self.live)
        self.trades.append(order)
