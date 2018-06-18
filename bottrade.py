from botlog import BotLog
import poloniex
import time
import sys
import shared
import logging
logging.basicConfig(level=logging.INFO)

orderNb = 0
class BotTrade(object):
    def __init__(self,direction,amount,rate,total,date,stopLoss=0, takeProfit=0, backtest=True, forwardtest=True):
        global orderNb
        self.output = BotLog()
        self.status = "OPEN"
        self.entryPrice = rate
        self.direction = direction
        self.stopLoss = stopLoss
        self.takeProfit = takeProfit
        self.date = date
        self.exitPrice = 0.0
        self.exitDate = 0.0
        self.amount = amount
        self.total = total
        self.info = ''
        self.orderNumber = 0
        self.backTest = backtest
        self.forwardTest = forwardtest
        self.api = poloniex.Poloniex(shared.api['key'], shared.api['secret'])

        orderSuccess = True
        if self.direction == "BUY":
            if not self.backTest and not self.forwardTest:
                try:
                    order = self.api.buy(shared.exchange['pair'], rate=rate, amount=amount)
                    self.orderNumber = int(order['orderNumber'])
                except:
                    orderSuccess = False
                    self.output.warning("Buy order failed")
            else:
                self.orderNumber = orderNb
                orderNb+=1
            if orderSuccess:
                shared.exchange['nbMarket'] -= self.total
                shared.exchange['nbCoin'] += self.amount
                self.output.info(str(time.ctime(date)) + " - Order "+str(self.orderNumber)+": Buy "+str(amount)+' '+shared.exchange['coin']+' at '+str(rate)+' for '+str(total)+' '+shared.exchange['market']+' - stopLoss: '+str(self.stopLoss)+' - takeProfit: '+str(takeProfit))

        elif self.direction == "SELL":
            if not self.backTest and not self.forwardTest:
                try:
                    order = self.api.sell(shared.exchange['pair'], rate=rate, amount=amount)
                    self.orderNumber = int(order['orderNumber'])
                except:
                    orderSuccess = False
                    self.output.warning("Sell order failed")
            else:
                self.orderNumber = orderNb
                orderNb+=1
            if orderSuccess:
                shared.exchange['nbMarket'] += self.total
                shared.exchange['nbCoin'] -= self.amount
                if shared.exchange['nbMarket'] < 0:
                    print(amount, total, rate, amount*rate)
                    raw_input()
                self.output.info(str(time.ctime(date)) + " - Order "+str(self.orderNumber)+": Sell "+str(amount)+' '+shared.exchange['coin']+' at '+str(rate)+' for '+str(total)+' '+shared.exchange['market']+' - stopLoss: '+str(self.stopLoss)+' - takeProfit: '+str(takeProfit))

    def tick(self, currentPrice, date):
        if self.stopLoss:
            if (self.direction == 'BUY' and currentPrice < self.stopLoss) or (self.direction == 'SELL' and currentPrice > self.stopLoss):
                self.output.fail(str(time.ctime(date)) + " - Order "+str(self.orderNumber)+": Stop Loss")
                self.close(currentPrice, date)
                self.showTrade()
        if self.takeProfit:
            if (self.direction == 'BUY' and currentPrice > self.takeProfit) or (self.direction == 'SELL' and currentPrice < self.takeProfit):
                self.output.success(str(time.ctime(date)) + " - Order "+str(self.orderNumber)+": Take Profit")
                self.close(currentPrice, date)
                self.showTrade()

    def close(self, currentPrice, date=0.0):
        if not self.backTest and not self.forwardTest:
            date = float(time.time())
            # TODO: implement not backtest
            pass
        self.status = "CLOSED"
        self.exitPrice = currentPrice
        self.exitDate =  date
        if self.direction == 'BUY':
            shared.exchange['nbMarket'] += self.amount*self.exitPrice
            shared.exchange['nbCoin'] -= self.amount
        elif self.direction == 'SELL':
            shared.exchange['nbMarket'] -= self.total
            shared.exchange['nbCoin'] += self.total/self.exitPrice

    def showTrade(self):
        tradeStatus = "Entry Price: "+str(self.entryPrice)+" Status: "+str(self.status)+" Exit Price: "+str(self.exitPrice)

        if (self.status == "CLOSED"):
            if (self.direction == 'BUY' and self.exitPrice > self.entryPrice) or (self.direction == 'SELL' and self.exitPrice < self.entryPrice):
                tradeStatus = tradeStatus + " Profit: \033[92m"
            else:
                tradeStatus = tradeStatus + " Loss: \033[91m"

            tradeStatus = tradeStatus+str(self.exitPrice - self.entryPrice)+"\033[0m"

        self.output.log(tradeStatus)
