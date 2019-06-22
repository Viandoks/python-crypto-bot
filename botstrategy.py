from botlog import BotLog
from botindicators import BotIndicators
from bottrade import BotTrade
from botapi import BotApi
import shared
import poloniex
import sys


# THIS STRATEGY IS OBVIOUSLY NOT WORKING! DON'T GO LIVE USING IT!!!
# THIS STRATEGY IS OBVIOUSLY NOT WORKING! DON'T GO LIVE USING IT!!!
# THIS STRATEGY IS OBVIOUSLY NOT WORKING! DON'T GO LIVE USING IT!!!
# THIS STRATEGY IS OBVIOUSLY NOT WORKING! DON'T GO LIVE USING IT!!!
# THIS STRATEGY IS OBVIOUSLY NOT WORKING! DON'T GO LIVE USING IT!!!
# THIS STRATEGY IS OBVIOUSLY NOT WORKING! DON'T GO LIVE USING IT!!!
# THIS STRATEGY IS OBVIOUSLY NOT WORKING! DON'T GO LIVE USING IT!!!
class BotStrategy(object):
    def __init__(self, backtest=True, forwardtest=True):
        self.output = BotLog()
        self.pair = shared.exchange['pair']
        self.coinsInOrder = shared.exchange['coinsInOrder']
        self.marketInOrder = shared.exchange['marketInOrder']
        self.trades = []
        self.currentPrice = ""
        self.currentClose = ""
        self.lowestAsk = 0.00
        self.highestBid = 0.00
        self.simultaneousTrades = 4
        self.tradeMultiplier = 0.1
        self.ticker = {}
        self.backTest = backtest
        self.forwardTest = forwardtest
        self.indicators = BotIndicators()

        self.candlesticks = []
        self.movingAverages = []
        self.movingAveragePeriod = shared.strategy['movingAverageLength']
        self.trueRanges = []
        self.averageTrueRanges = []

        # portfolio
        self.openOrders = []

        #api
        self.api = BotApi()

    def tick(self,candlestick):

        #strategy works on closed candles only
        if not candlestick.isClosed():
            return
        else:
            self.candlesticks.append(candlestick)

        self.currentPrice = candlestick.currentPrice
        ma = self.indicators.movingAverage(self.candlesticks, shared.strategy['movingAverageLength'])
        self.movingAverages.append(ma)

        previousCandle = False
        if len(self.candlesticks[-2:-1]) > 0:
            previousCandle = self.candlesticks[-2:-1][0]
        tr = self.indicators.trueRange(candlestick, previousCandle)
        self.trueRanges.append(tr)

        atr = self.indicators.averageTrueRange(tr, self.averageTrueRanges, 5)
        self.averageTrueRanges.append(atr)

        self.ticker = self.getTicker(self.pair)

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
            stoploss = self.currentPrice-self.averageTrueRanges[-1]
            takeprofit = self.currentPrice+(2*self.averageTrueRanges[-1])
            self.buy(rate, total, self.candlesticks[-1].date, stoploss, takeprofit)

        if goshort1 and goshort2 and len(openOrders) < self.simultaneousTrades:
            rate = float(self.ticker['highestBid'])
            amount = (shared.exchange['nbCoin']-shared.exchange['coinsInOrder'])*self.tradeMultiplier
            stoploss = self.currentPrice+self.averageTrueRanges[-1]
            takeprofit = self.currentPrice-(2*self.averageTrueRanges[-1])
            self.sell(rate, amount, self.candlesticks[-1].date, stoploss, takeprofit)

    def updateOpenTrades(self, pair):
        openOrders = self.getOpenOrders(pair)
        # TODO: implement not backtest
        for trade in openOrders:
            trade.tick(self.candlesticks[-1], self.candlesticks[-1].date)

    def getOpenOrders(self, pair):
        if not self.backTest and not self.forwardTest:
            orders = self.api.returnOpenOrders(pair)
            return orders
        else:
            openOrders = []
            for order in self.trades:
                if order.status == 'OPEN':
                    openOrders.append(order)
            return openOrders

    def getCurrentPrice(self, pair):
        if not self.backTest:
            return self.api.returnTicker(pair)['last']
        else:
            return self.candlesticks[-1].close

    def getTicker(self, pair):
        if not self.backTest:
            return self.api.returnTicker(pair)
        else:
            return {
                'last': self.currentPrice,
                'highestBid': self.currentPrice-self.currentPrice*shared.exchange['spreadPercentage'],
                'lowestAsk': self.currentPrice+self.currentPrice*shared.exchange['spreadPercentage']
            }

    def updatePortfolio(self):
        if not self.backTest and not self.forwardTest:
            try:
                portfolio = self.api.returnBalances()
                if shared.exchange['market'] in portfolio:
                    shared.exchange['nbMarket'] = float(portfolio[shared.exchange['market']])
                else:
                    shared.exchange['nbMarket'] = 0.00
                if shared.exchange['coin'] in portfolio:
                    shared.exchange['nbCoin'] = float(portfolio[shared.exchange['coin']])
                else:
                    shared.exchange['nbCoin'] = 0.00
                return True
            except Exception as e:
                self.output.warning("Error updating portfolio")
                print(e)
                return False
        else:
            return True

    def showPortfolio(self):
        if not self.backTest and not self.forwardTest:
            self.updatePortfolio()
        self.output.log(str(shared.exchange['nbMarket'])+" "+str(shared.exchange['market'])+' - '+str(shared.exchange['nbCoin'])+" "+str(shared.exchange['coin']))

    def buy(self, rate, total, date, stopLoss=0, takeProfit=0):
        amount = total/rate
        order = BotTrade('BUY', rate=rate, amount=amount, total=total, date=date, stopLoss=stopLoss, takeProfit=takeProfit, backtest=self.backTest, forwardtest=self.forwardTest)
        self.trades.append(order)


    def sell(self, rate, amount, date, stopLoss=0, takeProfit=0):
        total = rate*amount
        order = BotTrade('SELL',rate=rate,amount=amount, total=total, date=date, stopLoss=stopLoss, takeProfit=takeProfit, backtest=self.backTest, forwardtest=self.forwardTest)
        self.trades.append(order)
