import numpy as np

from botcandlestick import BotCandlestick
from operator import attrgetter

class BotIndicators(object):
    def __init__(self):
         pass

    def averageTrueRange(self, candles, window = 14):
        if len(candles)<window:
            window = len(candles)

        trueRanges = []
        for i in range(0, window):
            if i > 0:
                trueRanges.append(self.trueRange(candles[-i-1:-i]))
            else:
                trueRanges.append(self.trueRange(candles[-1:]))
        atr = self.sma(trueRanges, window, False)
        return atr

    def directionalMovement(self, candles, window=14):
        if len(candles) < window+2:
            window = len(candles)
        candles = candles[-(window+2):]
        highs = []
        lows = []
        closes = []
        pDMs = []
        nDMs = []
        for i in range(0, len(candles)):
            highs.append(candles[i]['high'])
            lows.append(candles[i]['low'])
            closes.append(candles[i]['close'])
            pDM = 0
            nDM = 0
            if i > 0:
                upMove = highs[i]-highs[i-1]
                dnMove = lows[i-1] - lows[i]
                if (upMove>dnMove) & (upMove > 0):
                    pDM = upMove
                if (dnMove>upMove) & (dnMove > 0):
                    nDM = dnMove
            pDMs.append(pDM)
            nDMs.append(nDM)

        ATR = self.averageTrueRange(candles, window)
        pDI = self.sma(pDMs, window)/ATR*100
        nDI = self.sma(nDMs, window)/ATR*100
        sum = pDI+nDI
        sum = 1 if sum==0 else sum
        DX = abs(pDI-nDI)/sum*100
        return {
            'pDI': pDI,
            'nDI': nDI,
            'DX': DX
        }


        DMI = pd.DataFrame(columns=['pDI', 'nDI', 'DX', 'ADX'])
        upMove = highs - highs.shift()
        dnMove = lows.shift() - lows
        pDM = closes*0
        nDM = closes*0
        pDM[(upMove>dnMove) & (upMove > 0)] = upMove
        nDM[(dnMove>upMove) & (dnMove > 0)] = dnMove
        TR = self.trueRange(highs, lows, closes)
        ATR = self.smoothedMovingAverage(TR, window, fillna)
        pDI = self.smoothedMovingAverage(pDM)/ATR*100
        nDI = self.smoothedMovingAverage(nDM)/ATR*100
        sum = pDI+nDI
        sum[pDI+nDI==0] = 1
        DX = abs(pDI-nDI)/sum*100
        ADX = self.smoothedMovingAverage(DX, adxWindow-1, fillna)
        DMI['pDI'] = pDI
        DMI['nDI'] = nDI
        DMI['DX'] = DX
        DMI['ADX'] = ADX
        return DMI
    def DMI(self, highs, lows, closes, window=14, adxWindow=14, fillna = False):
        return self.directionalMovementIndex(highs, lows, closes, window, adxWindow, fillna)

    def donchianChannels(self, candlesticks, period=20):
        candlesticks = candlesticks[-period:]
        return {
            'donchian_up': float(max([c['high'] for c in candlesticks])),
            'donchian_low': float(min([c['low'] for c in candlesticks]))
        }

    def ema(self, data, period, key=False):
        if len(data) <= period:
            period = len(data)

        weights = np.exp(np.linspace(-1., 0., period))
        weights /= weights.sum()

        if key:
           dataPoints = np.asarray([c[key] for c in data])
        else:
            dataPoints = np.asarray(data)

        # not so sure about this, need to double check
        avg = np.convolve(dataPoints, weights, mode='full')[:len(dataPoints)]
        return avg[-1]

    def gmma(self, candlesticks, key='close', p1=3, p2=5, p3=8, p4=10, p5=12, p6=15):
        return [
            self.ma(candlesticks, p1, key),
            self.ma(candlesticks, p2, key),
            self.ma(candlesticks, p3, key),
            self.ma(candlesticks, p4, key),
            self.ma(candlesticks, p5, key),
            self.ma(candlesticks, p6, key)
        ]


    def heikinashi(self, currentCandle, previousCandle=False):
        if not previousCandle:
            o = (currentCandle.open+currentCandle.close)/2
        else:
            o = (previousCandle.open+previousCandle.close)/2

        c = (currentCandle.open+currentCandle.high+currentCandle.low+currentCandle.close)/4

        h = max((o, c, currentCandle.high))
        l = min((o, c, currentCandle.low))

        return BotCandlestick(currentCandle.date,o,h,l,c,0)

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

    #simple moving average
    def ma(self, data, window, key=False):
        if len(data) < window:
            window = len(data)
        if key:
            dataPoints = [c[key] for c in data[-window:]]
        else:
            dataPoints = data[-window:]
        return sum(dataPoints) / float(len(dataPoints))

    #smoothed Moving Average
    def sma(self, data, window=14, key=False):
        if len(data) < window:
            window = len(data)
        if key:
            dataPoints = [c[key] for c in data[-window:]]
        else:
            dataPoints = data[-window:]
        weights = np.repeat(1.0, window) / window
        return np.convolve(dataPoints, weights, 'valid')[0]

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
