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
    forwardTest = True
    movingAverageLength = 20

    try:
        opts, args = getopt.getopt(argv,"hp:c:n:s:e",["period=","currency=","exchange=","live"])
    except getopt.GetoptError:
        print('trading-bot.py -p <period length> -c <currency pair>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('trading-bot.py -p <period length> -c <currency pair>')
            sys.exit()
        elif opt in ("-s"):
            startTime = float(arg)
        elif opt in ("-e"):
            endTime = float(arg)
        elif opt in ("-p", "--period"):
            period = int(arg)
        elif opt in ("-c", "--currency"):
            pair = str(arg)
            shared.exchange['pair'] = pair
            shared.exchange['market'] = pair.split("_")[0]
            shared.exchange['coin'] = pair.split("_")[1]
        elif opt in ("--exchange"):
            if str(arg) not in ['', 'poloniex', 'kraken']:
                print("Only poloniex and kraken are supported for now")
                sys.exit()
            exchange = str(arg)
            shared.exchange['name'] = exchange
        elif opt == "--live":
            forwardTest = False
        elif opt == '-n':
            shared.strategy['movingAverageLength'] = int(arg)

    if shared.exchange['name'] == "kraken":
        shared.exchange['pair'] = str(shared.exchange['coin'])+str(shared.exchange['market'])


    # startTime specified: we are in backtest mode
    if (startTime):

        chart = BotChart(period, startTime, endTime)

        strategy = BotStrategy()
        strategy.showPortfolio()

        for candlestick in chart.getPoints():
            strategy.tick(candlestick)

        chart.drawChart(strategy.candlesticks, strategy.movingAverages, strategy.trades)

        strategy.showPortfolio()

    else:

        chart = BotChart(period, False, False, False)

        strategy = BotStrategy(False, forwardTest)
        strategy.showPortfolio()

        candlesticks = []
        developingCandlestick = BotCandlestick(float(period))

        x = 0
        while True:
            try:
                currentPrice = chart.getCurrentPrice()
            except Exception as e:
                print(e)
                print("Error fetching current price")
                return

            try:
                developingCandlestick.tick(currentPrice)
            except Exception as e:
                print(e)
                print("Error fetching tick")
                return

            if currentPrice and developingCandlestick and developingCandlestick.isClosed():
                candlesticks.append(developingCandlestick)
                strategy.tick(developingCandlestick)
                developingCandlestick = BotCandlestick(float(period))
                chart.drawChart(candlesticks, strategy.movingAverages, strategy.trades)
            elif currentPrice and developingCandlestick:
                # If current candlestick is not close, this little hack will allow to update chart anyway
                tempCandle = copy.copy(developingCandlestick)
                tempCandle.close = currentPrice
                tempCandles = copy.copy(candlesticks)
                tempCandles.append(tempCandle)
                chart.drawChart(tempCandles, strategy.movingAverages, strategy.trades)

            x+=1
            time.sleep(int(10))




if __name__ == "__main__":
    main(sys.argv[1:])
