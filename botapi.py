from botlog import BotLog
from botcandlestick import BotCandlestick
import sys
import shared
import poloniex
# import krakenex

class BotApi(object):

    def __init__(self):
        self.exchange = shared.exchange['name']
        self.key = shared.api['key']
        self.secret = shared.api['secret']
        self.output = BotLog()

        if shared.exchange['name'] == 'poloniex':
            self.api = poloniex.Poloniex(self.key, self.secret)
        elif shared.exchange['name'] == 'kraken':
            self.api = krakenex.API(self.key, self.secret)

    def returnChartData(self,pair,period,start,end):
        data = []
        if self.exchange == 'poloniex':
            if (period not in [300,900,1800,7200,14400,86400]):
                self.output.fail('Poloniex requires periods in seconds: 300,900,1800,7200,14400, or 86400')
                sys.exit(2)
            poloData = self.api.returnChartData(pair,period=int(period),start=int(start),end=int(end))
            #TODO: check for error
            for datum in poloData:
                if (datum['open'] and datum['close'] and datum['high'] and datum['low'] and datum['date'] and datum['volume'] and datum['weightedAverage']):
                    data.append(BotCandlestick(period,float(datum['open']),float(datum['close']),float(datum['high']),float(datum['low']),float(datum['weightedAverage']), float(datum['volume']), float(datum['date'])))

        elif self.exchange == 'kraken':
            if (period not in [1, 5, 15, 30, 60, 240, 1440, 10080, 21600]):
                self.output.fail('Kraken requires periods in minutes: 1, 5, 15, 30, 60, 240, 1440, 10080, 21600')
                sys.exit(2)
            krakenData = self.api.query_public('OHLC', data = {'pair': pair, 'since': start, 'interval': period})
            # check for error
            if len(krakenData['error']) > 0:
                for e in krakenData['error']:
                    self.output.fail(e)
                sys.exit()
            for datum in krakenData['result'][pair]:
                data.append(BotCandlestick(period,float(datum[1]),float(datum[4]),float(datum[2]),float(datum[3]),float(datum[5]),float(datum[0])))

        else:
            self.output.fail("Not a valid exchange")
            sys.exit(2)
        return data

    def returnTicker(self, pair):
        ticker = {}
        if self.exchange == 'poloniex':
            ticker = self.api.returnTicker()[pair]
            #TODO: check for error
        elif self.exchange == 'kraken':
            data = self.api.query_public('Ticker', data={'pair':pair})
            #TODO: check for error
            data = data['result'][pair]
            ticker = {
                'last': float(data['c'][0]),
                'lowestAsk': float(data['a'][0]),
                'highestBid': float(data['b'][0]),
                'high24hr': float(data['h'][1]),
                'low24hr': float(data['l'][1])
            }
        else:
            self.output.fail("Not a valid exchange")
            sys.exit(2)
        print(ticker)
        return ticker

    def returnOpenOrders(self, pair):
        orders = []
        if self.exchange == 'poloniex':
            data = self.api.returnOpenOrders(pair)
            #TODO: check for error
            orders = data
        elif self.exchange == 'kraken':
            data = self.api.query_private('OpenOrders')
            #TODO: check for error
            orders = data['result']
            #TODO: This is a bit tricky for now, need to figure out how to deal with pair names (XXDGXXBT is "the same" as XDGXBT for example)
        else:
            self.output.fail("Not a valid exchange")
            sys.exit(2)
        return orders

    def returnBalances(self):
        balances = {}
        if self.exchange == 'poloniex':
            try:
                data = self.api.returnBalances()
                balances = data
            except Exception as e:
                print(e)
                return False
        elif self.exchange == 'kraken':
            data = self.api.query_private('Balance')
            #TODO: check for error
            balances = data['result']
        else:
            self.output.fail("Not a valid exchange")
            sys.exit(2)
        return balances

    def marketBuy(self, pair, rate, amout):
        order = {}
        if self.exchange == 'poloniex':
            try:
                #no market buy on poloniex, buying at 110% of the price "hacks" this
                data = self.api.buy(shared.exchange['pair'], rate='{0:.10f}'.format(rate*1.1), amount=amount, orderType="fillOrKill")
                order = data
            except Exception as e:
                self.output.fail(e)
                return False
        elif self.exchange == 'kraken':
            data = self.api.query_private('AddOrder', data={'ordertype': 'market', 'pair':pair, 'type': 'buy', 'volume': str(amount)})
            if len(data['error']) > 0:
                for e in data['error']:
                    self.output.fail(e)
                return False
            order = {
                'orderNumber': data['result']['txid'][0]
            }
        else:
            self.output.fail("Not a valid exchange")
            sys.exit(2)
        return order

    def limitBuy(self, pair, rate, amount):
        order = {}
        if self.exchange == 'poloniex':
            try:
                data = self.api.buy(shared.exchange['pair'], rate='{0:.10f}'.format(rate), amount=amount)
                order = data
            except Exception as e:
                print(e)
                return False
        elif self.exchange == 'kraken':
            data = self.api.query_private('AddOrder', data={'ordertype': 'limit', 'pair':pair, 'type': 'buy', 'price': '{0:.10f}'.format(rate), 'volume': str(amount)})
            print(data)
            if len(data['error']) > 0:
                for e in data['error']:
                    self.output.fail(e)
                return False
            order = {
                'orderNumber': data['result']['txid'][0]
            }
        else:
            self.output.fail("Not a valid exchange")
            sys.exit(2)
        return order

    def marketSell(self, pair, rate, amount):
        order = {}
        if self.exchange == 'poloniex':
            try:
                #no market sell on poloniex, selling at 90% of the price "hacks" this
                data = self.api.sell(shared.exchange['pair'], rate='{0:.10f}'.format(rate*0.9), amount=amount, orderType="fillOrKill")
                order = data
            except Exception as e:
                print(e)
                return False
        elif self.exchange == 'kraken':
            data = self.api.query_private('AddOrder', data={'ordertype': 'market', 'pair':pair, 'type': 'sell', 'volume': str(amount)})
            if len(data['error']) > 0:
                for e in data['error']:
                    self.output.fail(e)
                return False
            order = {
                'orderNumber': data['result']['txid'][0]
            }
        else:
            self.output.fail("Not a valid exchange")
            sys.exit(2)
        return order

    def limitSell(self, pair, rate, amount):
        order = {}
        if self.exchange == 'poloniex':
            try:
                data = self.api.sell(shared.exchange['pair'], rate='{0:.10f}'.format(rate), amount=amount)
                order = data
            except Exception as e:
                print(e)
                return False
        elif self.exchange == 'kraken':
            data = self.api.query_private('AddOrder', data={'ordertype': 'limit', 'pair':pair, 'type': 'sell', 'price': '{0:.10f}'.format(rate), 'volume': str(amount)})
            if len(data['error']) > 0:
                for e in data['error']:
                    self.output.fail(e)
                return False
            order = {
                'orderNumber': data['result']['txid'][0]
            }
        else:
            self.output.fail("Not a valid exchange")
            sys.exit(2)
        return order

    def cancelOrder(self, orderID):
        orderCanceled = True
        if self.exchange == 'poloniex':
            try:
                data = self.api.cancelOrder(orderID)
                if data['success'] == 0:
                    return False
            except Exception as e:
                print(e)
                return False
        elif self.exchange == 'kraken':
            data = self.api.query_private('CancelOrder', data={'txid': orderID})
            if len(data['error']) > 0:
                for e in data['error']:
                    self.output.fail(e)
                return False
        else:
            self.output.fail("Not a valid exchange")
            sys.exit(2)
        return orderCanceled
