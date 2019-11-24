import sys, getopt
import time
import pprint
import copy
import shared

from botchart import BotChart
from botstrategy import BotStrategy
from botcandlestick import BotCandlestick

def main(argv):

    startTime = False
    endTime = False
    live = False
    movingAverageLength = 20

    try:
        opts, args = getopt.getopt(argv,"ht:c:n:s:e",["timeframe=","currency=","exchange=","live"])
    except getopt.GetoptError:
        print('trading-bot.py -t <timeframe> -c <currency pair>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('trading-bot.py -t <timeframe> -c <currency pair>')
            sys.exit()
        elif opt in ("-s"):
            startTime = str(arg)
        elif opt in ("-e"):
            endTime = str(arg)
        elif opt in ("-t", "--timeframe"):
            timeframe = str(arg)
            shared.strategy['timeframe'] = timeframe
        elif opt in ("-c", "--currency"):
            pair = str(arg)
            shared.exchange['pair'] = pair
            shared.exchange['market'] = pair.split("/")[1]
            shared.exchange['coin'] = pair.split("/")[0]
        elif opt in ("--exchange"):
            exchange = str(arg)
            shared.exchange['name'] = exchange
        elif opt == "--live":
            print("You're going live... All loss are your reponsability only!")
            live = True

    # startTime specified: we are in backtest mode
    if (startTime):

        chart = BotChart(timeframe, startTime, endTime)

        strategy = BotStrategy()
        strategy.showPortfolio()

        for candlestick in chart.getPoints():
            strategy.tick(candlestick)

        chart.drawChart(strategy.candlesticks, strategy.trades, strategy.movingAverages)

        strategy.showPortfolio()

    else:

        chart = BotChart(timeframe, False, False, False)

        strategy = BotStrategy(False, live)
        strategy.showPortfolio()

        candlestick = BotCandlestick()

        x = 0
        while True:
            currentPrice = chart.getCurrentPrice()
            candlestick.tick(currentPrice)
            strategy.tick(candlestick)

            drawingCandles = copy.copy(strategy.candlesticks)
            if not candlestick.isClosed():
                drawingCandles.append(copy.copy(candlestick))
                drawingCandles[-1].close = candlestick.currentPrice
            chart.drawChart(drawingCandles, strategy.trades, strategy.movingAverages)

            if candlestick.isClosed():
                candlestick = BotCandlestick()

            x+=1
            time.sleep(int(10))

if __name__ == "__main__":
    main(sys.argv[1:])
