from botlog import BotLog
from botapi import BotApi
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
        self.filledOn = ""
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
        self.fee = float(shared.exchange['fee'])
        self.api = BotApi()

        orderSuccess = True
        if self.direction == "BUY":
            if not self.backTest and not self.forwardTest:
                try:
                    order = self.api.limitBuy(shared.exchange['pair'], rate=rate, amount=amount)
                    self.orderNumber = order['orderNumber']
                except Exception as e:
                    self.output.error(e)
                    orderSuccess = False
                    self.output.error("Buy order failed")
            else:
                self.orderNumber = orderNb
                orderNb+=1
            if orderSuccess:
                shared.exchange['nbMarket'] -= self.total
                self.amount -= self.amount*self.fee
                self.output.info(str(time.ctime(date)) + " - Order "+str(self.orderNumber)+": Buy "+str(amount)+' '+shared.exchange['coin']+' ('+str(self.fee*100)+'% fees) at '+str(rate)+' for '+str(total)+' '+shared.exchange['market']+' - stopLoss: '+str(self.stopLoss)+' - takeProfit: '+str(takeProfit))

        elif self.direction == "SELL":
            if not self.backTest and not self.forwardTest:
                try:
                    order = self.api.sell(shared.exchange['pair'], rate=rate, amount=amount)
                    self.orderNumber = order['orderNumber']
                except Exception as e:
                    print(e)
                    orderSuccess = False
                    self.output.warning("Sell order failed")
            else:
                self.orderNumber = orderNb
                orderNb+=1
            if orderSuccess:
                shared.exchange['nbCoin'] -= self.amount
                self.total -= self.total*self.fee
                self.output.info(str(time.ctime(date)) + " - Order "+str(self.orderNumber)+": Sell "+str(self.amount)+' '+shared.exchange['coin']+' at '+str(rate)+' for '+str(self.total)+' ('+str(self.fee*100)+'% fees) '+shared.exchange['market']+' - stopLoss: '+str(self.stopLoss)+' - takeProfit: '+str(takeProfit))

    def tick(self, candlestick, date):
        if not self.backTest and not self.forwardTest:
            date = float(time.time())
            # TODO: implement not backtest
            pass
        if not self.filledOn:
            if (self.direction == 'BUY' and candlestick.high > self.entryPrice) or (self.direction == 'SELL' and candlestick.low < self.entryPrice):
                self.filledOn = date
                if self.direction =='BUY':
                    shared.exchange['nbCoin'] += self.amount
                elif self.direction =='SELL':
                    shared.exchange['nbMarket'] += self.total
                if not self.stopLoss and not self.takeProfit:
                    self.status = 'CLOSED'
                self.output.info(str(time.ctime(date)) + " - Order "+str(self.orderNumber)+" filled")

        if self.stopLoss:
            if (self.direction == 'BUY' and candlestick.low < self.stopLoss) or (self.direction == 'SELL' and candlestick.high > self.stopLoss):
                self.output.warning(str(time.ctime(date)) + " - Order "+str(self.orderNumber)+": Stop Loss")
                self.close(self.stopLoss, date)
                return
        if self.takeProfit:
            if (self.direction == 'BUY' and candlestick.high > self.takeProfit) or (self.direction == 'SELL' and candlestick.low < self.takeProfit):
                self.output.success(str(time.ctime(date)) + " - Order "+str(self.orderNumber)+": Take Profit")
                self.close(self.takeProfit, date)
                return

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
        elif self.direction == 'SELL':
            shared.exchange['nbCoin'] += self.total/self.exitPrice
        self.output.info(str(time.ctime(date)) + " - Order "+str(self.orderNumber)+" Closed")
        self.showTrade()

    def showTrade(self):
        tradeStatus = "Order #"+str(self.orderNumber)+" - Entry Price: "+str(self.entryPrice)+" Status: "+str(self.status)+" Exit Price: "+str(self.exitPrice)

        if (self.status == "CLOSED"):
            if (self.direction == 'BUY' and self.exitPrice > self.entryPrice) or (self.direction == 'SELL' and self.exitPrice < self.entryPrice):
                tradeStatus = tradeStatus + " Profit: \033[92m"
            else:
                tradeStatus = tradeStatus + " Loss: \033[91m"
            if self.direction == 'BUY':
                tradeStatus = tradeStatus+str((self.exitPrice - self.entryPrice)/self.total)+str(shared.exchange['market'])+"\033[0m"
            else:
                tradeStatus = tradeStatus+str((self.entryPrice - self.exitPrice)/self.exitPrice*self.amount)+str(shared.exchange['coin'])+"\033[0m"

        self.output.log(tradeStatus)

    def updateStop(self, newStop):
        oldStop = self.stopLoss
        self.stopLoss = float(newStop);
        self.output.log("Trade stop moved from "+str(oldStop)+" to "+str(newStop))
