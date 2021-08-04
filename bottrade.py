from botapi import BotApi
from botlog import BotLog

import logging
import shared
import sys
import time

logging.basicConfig(level=logging.INFO)

orderNb = 1
class BotTrade(object):
    def __init__(self,direction,amount,rate,total,date,stopLoss=0, takeProfit=0, backtest=True, live=False):
        global orderNb
        self.amount = amount
        self.backTest = backtest
        self.date = date
        self.direction = direction
        self.exitDate = 0.0
        self.exitRate = 0.0
        self.fee = float(shared.exchange['fee'])
        self.filledOn = ""
        self.live = live
        self.orderNumber = orderNb
        self.output = BotLog()
        self.rate = rate
        self.status = "OPEN"
        self.stopLoss = stopLoss
        self.takeProfit = takeProfit
        self.total = total

        # API
        self.api = BotApi()

        orderSuccess = True
        if self.direction == "BUY":
            if not self.backTest and self.live:
                try:
                    order = self.api.exchange.createLimitBuyOrder(shared.exchange['pair'], amount, rate)
                    self.orderNumber = order['id']
                except Exception as e:
                    self.output.fail(str(e))
                    orderSuccess = False
                    self.output.fail("Buy order failed")
            elif self.total < 0.00001:
                orderSuccess = False
                self.output.fail("Not enough funds to place Buy Order")
            if orderSuccess:
                shared.exchange['nbMarket'] -= self.total
                self.amount -= self.amount*self.fee
                self.output.info(str(time.ctime(date)) + " - Order "+str(self.orderNumber)+": Buy "+str(self.amount)+' '+shared.exchange['asset']+' ('+str(self.fee*100)+'% fees) at '+str(self.rate)+' for '+str(self.total)+' '+shared.exchange['market']+' - stopLoss: '+str(self.stopLoss)+' - takeProfit: '+str(self.takeProfit))

        elif self.direction == "SELL":
            if not self.backTest and self.live:
                try:
                    order = self.api.exchange.createLimitSellOrder(shared.exchange['pair'], amount, rate)
                    self.orderNumber = order['id']
                except Exception as e:
                    print(e)
                    orderSuccess = False
                    self.output.warning("Sell order failed")
            elif self.total < 0.00001:
                orderSuccess = False
                self.output.fail("Not enough funds to place Sell Order")
            if orderSuccess:
                shared.exchange['nbAsset'] -= self.amount
                self.total -= self.total*self.fee
                self.output.info(str(time.ctime(date)) + " - Order "+str(self.orderNumber)+": Sell "+str(self.amount)+' '+shared.exchange['asset']+' at '+str(self.rate)+' for '+str(self.total)+' ('+str(self.fee*100)+'% fees) '+shared.exchange['market']+' - stopLoss: '+str(self.stopLoss)+' - takeProfit: '+str(self.takeProfit))


        orderNb+=1
        if not orderSuccess:
            self.status = 'FAILED'

    def __setitem__(self, key, value):
          setattr(self, key, value)

    def __getitem__(self, key):
          return getattr(self, key)

    def toDict(self):
        return {
            'date': self.date,
            'direction': self.direction,
            'amount': self.amount,
            'rate': self.rate,
            'total': self.total,
            'stopLoss': self.stopLoss,
            'takeProfit': self.takeProfit,
            'exitRate': self.exitRate,
            'filledOn': self.filledOn,
            'exitDate': self.exitDate,
            'orderNumber': self.orderNumber
        }

    def tick(self, candlestick, date):
        if not self.backTest and self.live:
            date = float(time.time())
            # TODO: implement not backtest
            pass
        if not self.filledOn:
            if (self.direction == 'BUY' and candlestick.high > self.rate) or (self.direction == 'SELL' and candlestick.low < self.rate):
                self.filledOn = date
                if self.direction == 'BUY':
                    shared.exchange['nbAsset'] += self.amount
                elif self.direction == 'SELL':
                    shared.exchange['nbMarket'] += self.total
                if not self.stopLoss and not self.takeProfit:
                    self.status = 'CLOSED'
                else:
                    if self.direction =='BUY':
                        shared.exchange['coinsInOrder'] += self.amount
                    elif self.direction =='SELL':
                        shared.exchange['marketInOrder'] += self.total
                self.output.info(str(time.ctime(date)) + " - Order "+str(self.orderNumber)+" filled")

        if self.stopLoss and self.filledOn:
            # TODO: implement live
            if self.direction == 'BUY' and candlestick.low < self.stopLoss:
                self.total -= self.total*self.fee
                shared.exchange['nbAsset'] -= self.amount
                shared.exchange['coinsInOrder'] -= self.amount
                self.output.warning(str(time.ctime(date)) + " - Order "+str(self.orderNumber)+": Stop Loss - Sell "+str(self.amount)+' '+shared.exchange['asset']+' at '+str(self.stopLoss)+' for '+str(self.total)+' '+shared.exchange['market']+' ('+str(self.fee*100)+'% fees)')
                self.close(self.stopLoss, date)
                return
            elif self.direction == 'SELL' and candlestick.high > self.stopLoss:
                self.amount -= self.amount*self.fee
                shared.exchange['nbMarket'] -= self.total
                shared.exchange['marketInOrder'] -= self.total
                self.output.warning(str(time.ctime(date)) + " - Order "+str(self.orderNumber)+": Stop Loss - Buy "+str(self.amount)+' '+shared.exchange['asset']+' ('+str(self.fee*100)+'% fees) at '+str(self.stopLoss)+' for '+str(self.total)+' '+shared.exchange['market'])
                self.close(self.stopLoss, date)
                return
        if self.takeProfit and self.filledOn:
            if self.direction == 'BUY' and candlestick.high > self.takeProfit:
                self.total -= self.total*self.fee
                shared.exchange['nbAsset'] -= self.amount
                shared.exchange['coinsInOrder'] -= self.amount
                self.output.success(str(time.ctime(date)) + " - Order "+str(self.orderNumber)+": Take Profit - Sell "+str(self.amount)+' '+shared.exchange['asset']+' at '+str(self.stopLoss)+' for '+str(self.total)+' '+shared.exchange['market']+' ('+str(self.fee*100)+'% fees)')
                self.close(self.takeProfit, date)
                return
            elif self.direction == 'SELL' and candlestick.low < self.takeProfit:
                self.amount -= self.amount*self.fee
                shared.exchange['nbMarket'] -= self.total
                shared.exchange['marketInOrder'] -= self.total
                self.output.success(str(time.ctime(date)) + " - Order "+str(self.orderNumber)+": Take Profit - Buy "+str(self.amount)+' '+shared.exchange['asset']+' ('+str(self.fee*100)+'% fees) at '+str(self.stopLoss)+' for '+str(self.total)+' '+shared.exchange['market'])
                self.close(self.takeProfit, date)
                return

    def close(self, currentPrice, date=0.0):
        if not self.backTest and self.live:
            date = float(time.time())
            # TODO: implement not backtest
            pass
        self.status = "CLOSED"
        self.exitRate = currentPrice
        self.exitDate =  date
        if self.direction == 'BUY':
            shared.exchange['nbMarket'] += self.total
        elif self.direction == 'SELL':
            shared.exchange['nbAsset'] += self.amount
        self.output.info(str(time.ctime(date)) + " - Order "+str(self.orderNumber)+" Closed")
        self.showTrade()

    def showTrade(self):
        tradeStatus = "Order #"+str(self.orderNumber)+" - Entry Price: "+str(self.rate)+" Status: "+str(self.status)+" Exit Price: "+str(self.exitRate)

        if (self.status == "CLOSED"):
            if (self.direction == 'BUY' and self.exitRate > self.rate) or (self.direction == 'SELL' and self.exitRate < self.rate):
                tradeStatus = tradeStatus + " Profit: \033[92m"
            else:
                tradeStatus = tradeStatus + " Loss: \033[91m"
            if self.direction == 'BUY':
                tradeStatus = tradeStatus+str((self.exitRate - self.rate)/self.total)+str(shared.exchange['market'])+"\033[0m"
            else:
                tradeStatus = tradeStatus+str((self.rate - self.exitRate)/self.exitRate*self.amount)+str(shared.exchange['asset'])+"\033[0m"

        self.output.log(tradeStatus)

    def updateStop(self, newStop):
        oldStop = self.stopLoss
        self.stopLoss = float(newStop);
        self.output.log("Trade stop moved from "+str(oldStop)+" to "+str(newStop))
