from botlog import BotLog
from botindicators import BotIndicators
from bottrade import BotTrade
import shared
import poloniex


class BotStrategy(object):
    def __init__(self, backtest=True, forwardtest=True):
        self.output = BotLog()
        self.pair = shared.exchange['pair']
        self.backTest = backtest
        self.currentState = ""
        self.forwardTest = forwardtest
        self.prices = []
        self.closes = []
        self.trades = []
        self.currentPrice = ""
        self.currentClose = ""
        self.simultaneousTrades = 4
        self.tradeMultiplier = 0.1
        self.ticker = {}
        self.indicators = BotIndicators()

        self.candlesticks = []
        self.movingAverages = []
        self.movingAveragePeriod = shared.strategy['movingAverageLength']
        self.trueRanges = []
        self.averageTrueRanges = []

        # portfolio
        self.openOrders = []

        #api
        self.api = poloniex.Poloniex(shared.api['key'], shared.api['secret'])

    def tick(self,candlestick):

        if candlestick and candlestick.close:
            self.candlesticks.append(candlestick)
            self.closes.append(candlestick.close)

        self.currentPrice = candlestick.currentPrice
        self.prices.append(candlestick.currentPrice)

        ma = self.indicators.movingAverage(self.closes[-(shared.strategy['movingAverageLength']):], shared.strategy['movingAverageLength'])
        self.movingAverages.append(ma)

        previousCandle = False
        if len(self.candlesticks[-2:-1]) > 0:
            previousCandle = self.candlesticks[-2:-1][0]
        tr = self.indicators.trueRange(candlestick, previousCandle)
        self.trueRanges.append(tr)

        atr = self.indicators.averageTrueRange(tr, self.averageTrueRanges, 5)
        self.averageTrueRanges.append(atr)

        self.ticker = self.getTicker()

        portfolioUpdated = self.updatePortfolio()
        # If live and portfolio not updated, we may run into some unpleasant issues.
        # Better stop here for now
        if not portfolioUpdated:
            return

        # Strategy needs at least 2 prices to work
        if len(self.prices) > 1:
            self.evaluatePositions()
            self.updateOpenTrades()

    def evaluatePositions(self):

        openOrders = self.getOpenOrders()

        '''
            Go Long (buy) if all of these are met:
                Previous  price is lower movingAverage
                Current price is higher than moving average
            Go short (sell) if:
                Previous price is higher than moving average
                Current Price is lower than moving average
        '''

        golong1 = self.prices[-2] < self.movingAverages[-1]
        golong2 = self.currentPrice > self.movingAverages[-1]
        goshort1 = self.prices[-2] > self.movingAverages[-1]
        goshort2 = self.currentPrice < self.movingAverages[-1]

        if golong1 and golong2 and len(openOrders) < self.simultaneousTrades:
            rate = float(self.ticker['lowestAsk'])
            total = shared.exchange['nbMarket']*self.tradeMultiplier
            stoploss = self.currentPrice-self.averageTrueRanges[-1]
            takeProfit = self.currentPrice+(2*self.averageTrueRanges[-1])
            self.buy(rate, total, self.candlesticks[-1].date, stoploss, takeProfit)

        if goshort1 and goshort2 and len(openOrders) < self.simultaneousTrades:
            rate = float(self.ticker['highestBid'])
            amount = shared.exchange['nbCoin']*self.tradeMultiplier
            stoploss = self.currentPrice+self.averageTrueRanges[-1]
            takeProfit = self.currentPrice-(2*self.averageTrueRanges[-1])
            self.sell(rate, amount, self.candlesticks[-1].date, stoploss, takeProfit)

    def updateOpenTrades(self):
        openOrders = self.getOpenOrders()
        for trade in openOrders:
            trade.tick(self.currentPrice, self.candlesticks[-1].date)

    def getOpenOrders(self):
        if not self.backTest and not self.forwardTest:
            orders = self.api.returnOpenOrders(shared.exchange['pair'])
            return orders
        else:
            openOrders = []
            for order in self.trades:
                if order.status == 'OPEN':
                    openOrders.append(order)
            return openOrders

    def getCurrentPrice(self):
        if not self.backTest:
            return self.api.returnTicker()[self.pair]['last']
        else:
            return self.candlesticks[-1].close

    def getTicker(self):
        if not self.backTest:
            return self.api.returnTicker()[self.pair]
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
                shared.exchange['nbMarket'] = float(portfolio[shared.exchange['market']])
                shared.exchange['nbCoin'] = float(portfolio[shared.exchange['coin']])
                return True
            except:
                self.output.warning("Error updating portfolio")
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
