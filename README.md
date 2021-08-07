# python-crypto-bot

Automated crypto trading in Python.

This is my attempt to write a robust python3 framework to implement different automated trading strategies.

This project works with [CCXT](https://github.com/ccxt/ccxt) and is therefor compatible with many exchanges.

## !!! Disclaimer !!!

This software is for educational purposes only. Do not risk money which you are not ready to lose. USE THE SOFTWARE AT YOUR OWN RISK. I WILL NOT ASSUME RESPONSIBILITY FOR YOUR LOSSES.

NEVER RUN THE SOFTWARE IN LIVE MODE IF YOU'RE NOT 100% SURE OF WHAT YOU ARE DOING. Once again, I will NOT take ANY responsibilities regarding the results of your trades.

As is, the software is obviously not viable, but with some research and a bit of coding, it could become your best ally in automating strategies.

## Shoutouts

This project is strongly inspired by [bwentzloff](https://github.com/bwentzloff)'s trading bot which you can find here: https://github.com/bwentzloff/trading-bot.
If you're new to python trading I strongly recommend checking his [Youtube Chanel](https://youtube.com/cryptocurrencytrading)

Shoutout to [CCXT](https://github.com/ccxt) for their wonderful work on their super awesome [library](https://github.com/ccxt/ccxt)

And finally a big thx to [sentdex](https://github.com/Sentdex) who's youtube tutorials inspired me to get into python automated trading years ago

## GETTING STARTED

This project is compatible with python3 and there's no reason why I should spend more time to make it compatible with python2.

### Prerequisites

```
pip install ccxt
pip install numpy
pip install pandas
```

### Install

```
git clone https://github.com/Viandoks/python-crypto-bot.git
cd python-crypto-bot
```

### How to

#### Configuration
Rename `.env.sample` to `.env` and edit it to your preferences.
```.env
API_KEY=                        YourApiKey
API_SECRET=                     YourApiSecret

ASSET=BTC                       or any asset available on the exchance 
MARKET=USDT                     or any base asset available on the exchange
TIMEFRAME=1m                    or any timeframce available
COINS_ASSET=1                   used for backtest, how much assets to start with
COINS_MARKET=100                used for backtest, how much base assets to start with

EXCHANGE=poloniex               your choice of exchange available in CCXT
FEES=0.125                      used for backtest, emulate fees in %
SPREAD=0.00                     used for backtest, emulate spread in %

ALLOCATION=1                    how much of your assets do you want to play at each order (1==100%)
INTERVAL=10                      used for forward test and live, interval between each call to the API in seconds 
START_DATE=2021-01-01 00:00:00  date at which backtest should start, if not specified, bot will run in forward test mode         
``` 

#### Run backtest

```
python bot.py 
```

This will launch the trading strategy on the pair `ASSET`/`MARKET`, with a candlestick period of `TIMEFRAME`, starting on `START_DATE`.

You can see the result in the command line AND the output/index.html file in the project

#### Run forward test

Leave `START_DATE` empty to run forward test 

A new call is made every `INTERVAL` seconds. You can follow the trades almost live be reloading output/index.html

#### Run live
!!!!! DO NOT DO THIS IF YOU'RE NOT 100% SURE OF WHAT YOU'RE DOING! I WILL NOT BE HELD RESPONSIBLE IF YOU LOSE MONEY!!!!!
To run the bot live you need to enter your api key and secret in the shared.py file. If you don't know what an api key is, you shouldn't even try to launch that bot live. However feel free to have fun in backtest and forward test mode.
```
python bot.py --live
```

### Important files
`shared.py` contains a bunch of variable shared across the different modules

`bot.py` is where everything start

`botapi.py` is where the connections are made between the bot and the registered APIs.

`botstrategy.py` is where the magic happens. The default strategy is a simple Moving Average Crossover strategy. IT WILL NOT WORK LIVE! Feel free to experiment and write your own strategy

`botindicators.py` contains all the indicator available in bostrategy.py

`botchart.py` generates the candlesticks data in backtest mode, as well as the data for the final graph viewable in `output/output.html`. It is based on [googlecharts](https://developers.google.com/chart/) and can be overwelming work with at first. If you change the strategy, there is a 99% that you need to modify output.html and botchart.py as well.
If you want rendering of your trades, you gonna have to dig into this. Sorry.

Other files are pretty much self explanatory. Feel free to checkout [bwentzloff](https://github.com/bwentzloff/trading-bot) if something is not clear.

### Last notes

This project is not perfect, it probably still have a few bugs/unwanted behaviors. It could probably be improved a lot. I already have a few improvement/changes in mind. Feel free to open  ticket if you find/think about something. I'll try to work on them when I have time/faith. Even better, work on it yourself and do a pull request :D
Unfortunately coding is not my main goal in life anymore so please be patient.

What is this spreadPercentage thingy in shared.py?
I implemented this to emulate the difference between ask and bid price. How many time did I think I was gonna get rich in a matter of days just because I forgot about the spread. Going live is full of bad surprises.

Kraken's api has been quite a turbulent child recently, often returning a time out. There is a [pull request](https://github.com/veox/python3-krakenex/pull/100) on krakenex to attempt to fix that but is not merge to master yet... so be patient or try and fix it by yourself ;)
Once again I do not recommend the use of Kraken API.

Also pairs on kraken are a bit weird, if you intend to trade on the ETHXBT market you should use XXBT_XETH as the currency_pair argument. I'll probably do some more work on that in the future, but for now... that's the way.

I know this is not the best readme ever but hey... at least there is one.

As I said earlier, the strategy in there DOES NOT WORK. It is merely a tool for you to write your own and pwn the market. It took me years to write a winning strategy, hang in there!

### Tip Me

You like what you see? Feel free to tip me, you'll earn my eternal gratitude:

BTC - 1MT45xgCJe68c3eL2iTJMSQLwsDobmzz7r

ETH - 0x4Aa63028CA72D8Ce79E904DE1c53AbC91d2F2347

### Final Words

HAVE FUN!
