import numpy

from botcandlestick import BotCandlestick
from operator import attrgetter

class BotIndicators(object):
    def __init__(self):
         pass

    def averageTrueRange(self, trueRanges=[], period = 14):
        trueRanges=trueRanges[-period:]
        if len(trueRanges) < period:
            period = len(trueRanges)
        atr = self.sma(trueRanges, period, False)
        return atr

    def donchianChannels(self, candlesticks, period=20):
        candlesticks = candlesticks[-period:]
        return {
            'donchian_up': float(max([c['high'] for c in candlesticks])),
            'donchian_low': float(min([c['low'] for c in candlesticks]))
        }


    def ema(self, data, period, key=False):
        if len(data) <= period:
            period = len(data)

        weights = numpy.exp(numpy.linspace(-1., 0., period))
        weights /= weights.sum()

        if key:
           dataPoints = numpy.asarray([c[key] for c in data])
        else:
            dataPoints = numpy.asarray(data)

        # not so sure about this, need to double check
        avg = numpy.convolve(dataPoints, weights, mode='full')[:len(dataPoints)]
        return avg[-1]

    def gmma(self, candlesticks, key='close', p1=3, p2=5, p3=8, p4=10, p5=12, p6=15):
        return [
            self.sma(candlesticks, p1, key),
            self.sma(candlesticks, p2, key),
            self.sma(candlesticks, p3, key),
            self.sma(candlesticks, p4, key),
            self.sma(candlesticks, p5, key),
            self.sma(candlesticks, p6, key)
            ]


    def heikinashi(self, currentCandle, previousHeikinashiCandle=False):
        if not previousHeikinashiCandle:
            o = (currentCandle.open+currentCandle.close)/2
        else:
            o = (previousHeikinashiCandle.open+previousHeikinashiCandle.close)/2

        c = (currentCandle.open+currentCandle.high+currentCandle.low+currentCandle.close)/4

        h = max((o, c, currentCandle.high))
        l = min((o, c, currentCandle.low))

        return BotCandlestick(14400,o,c,h,l,0, currentCandle.date)

    #ichimoku default periods are 9, 26, 26, here default values are adapted to crypto market
    def ichimoku(self, candlesticks, tenkanPeriod=10, kijunPeriod=30, senkouBPeriod=60, displacement=30):
        tenkan = kijun = senkouA = senkouB = chikou = False
        if len(candlesticks)>=tenkanPeriod:
            high = float(max(candlesticks[-tenkanPeriod:-1], key=attrgetter('high')).high)
            low = float(min(candlesticks[-tenkanPeriod:-1], key=attrgetter('low')).low)
            tenkan = (high+low)/2
        if len(candlesticks)>=kijunPeriod:
            high = float(max(candlesticks[-kijunPeriod:-1], key=attrgetter('high')).high)
            low = float(min(candlesticks[-kijunPeriod:-1], key=attrgetter('low')).low)
            kijun = (high+low)/2
        if tenkan and kijun:
            senkouA = (tenkan+kijun)/2
        if len(candlesticks)>=senkouBPeriod:
            high = float(max(candlesticks[-senkouBPeriod:-1], key=attrgetter('high')).high)
            low = float(min(candlesticks[-senkouBPeriod:-1], key=attrgetter('low')).low)
            senkouB = (high+low)/2
        if len(candlesticks)>=displacement:
            chikou = candlesticks[-1].close

        return {
            'tenkan': tenkan,
            'kijun':kijun,
            'senkouA': senkouA,
            'senkouB': senkouB,
            'chikou': chikou,
            'displacement': displacement
        }

    def MACD(self, prices, nslow=26, nfast=12):
        emaslow = self.ema(prices, nslow)
        emafast = self.ema(prices, nfast)
        return {
            'ema_slow': emaslow,
            'ema_fast': emafast,
            'macd': emafast - emaslow
            }

    def momentum (self, data, period=14, key=False):
        if (len(data) <= period-1):
            raise ValueError("Not enough Data")
        if not key:
            return data[-1] * 100 / dataPoints[-period]
        else:
            return data[-1][key] * 100 / dataPoints[-period][key]

    #Simple Moving Average
    def sma(self, data, period, key=False):
        if len(data) < period:
            period = len(data)
        if key:
            dataPoints = [c[key] for c in data[-period:]]
        else:
            dataPoints = data
        return sum(dataPoints) / float(len(dataPoints))

    def RSI (self, prices, period=14):
        deltas = np.diff(prices)
        seed = deltas[:period+1]
        up = seed[seed >= 0].sum()/period
        down = -seed[seed < 0].sum()/period
        rs = up/down
        rsi = np.zeros_like(prices)
        rsi[:period] = 100. - 100./(1. + rs)

        for i in range(period, len(prices)):
            delta = deltas[i - 1]  # cause the diff is 1 shorter
            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta

            up = (up*(period - 1) + upval)/period
            down = (down*(period - 1) + downval)/period
            rs = up/down
            rsi[i] = 100. - 100./(1. + rs)
            if len(prices) > period:
                return rsi[-1]
            else:
                return 50 # output a neutral amount until enough prices in list to calculate RSI

    def trueRange(self, candles):
       atr1 = atr2 = atr3 = 0
       candles = candles[-2:]
       atr1 = abs(candles[-1]['high'] - candles[-1]['low'])
       if len(candles) > 1:
           atr2 = abs(candles[-1]['high'] - candles[-2]['close'])
           atr3 = abs(candles[-1]['low'] - candles[-2]['close'])
       return max([atr1, atr2, atr3])

    def williamsFractal(self, data, period=2):
        bull = bear = False
        nbCandles = period*2+1
        candlesticks = candlesticks[-nbCandles:]
        if len(candlesticks)>nbCandles:
            candlesticks = candlesticks[-nbCandles:]
            #bullish fractal
            lows = [c['low'] for c in candlesticks]
            if(lows.index(min(lows)) == period):
                bull = True
            #bearish fractal
            highs = [c['high'] for c in candlesticks]
            if(highs.index(max(highs)) == period):
                bear = True
        return {
            'williamsFractalPeriod': period,
            'bullFractal': bull,
            'bearFractal': bear
        }
