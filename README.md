# python-crypto-bot
Automated crypto trading in Python.

This is my attempt to write a robust python3 base to implement different automated trading strategies

As for now, it is only compatible with Poloniex and Kraken. I may or may not add support for other exchanges in the future (looking at you [CCXT](https://github.com/ccxt/ccxt)).
However I do not recommend using Kraken for this bot as their API seems extremely unstable and I haven't been working on it for a while

## !!! Disclaimer !!!

This software is for educational purposes only. Do not risk money which you are afraid to lose. USE THE SOFTWARE AT YOUR OWN RISK. I WILL NOT ASSUME RESPONSIBILITY FOR YOUR LOSSES.

NEVER RUN THE SOFTWARE IN LIVE MODE IF YOU'RE NOT 100% SURE OF WHAT YOU ARE DOING. Once again, I will NOT take ANY responsibilities regarding the results of your trades.

As is, the software is obviously not viable, but with some research and a bit of coding, it could become your best friend in automating strategies.

## Shoutouts

This project is strongly inspired by [bwentzloff](https://github.com/bwentzloff)'s trading bot which you can find here: https://github.com/bwentzloff/trading-bot.
If you're new to python trading I strongly recommend checking his [Youtube Chanel](https://youtube.com/cryptocurrencytrading)

Shoutout to [s4w3d0ff](https://github.com/s4w3d0ff) for the wonderful work on his [poloniex wrapper](https://github.com/s4w3d0ff/python-poloniex) without which this project probably wouldn't be working that smoothly.

Big up to [veox](https://github.com/veox) for his work on [Krakenex](https://github.com/veox/python3-krakenex) and made kraken trading possible for this app.

And finally a big thx to [sentdex](https://github.com/Sentdex) who's youtube tutorials inspired me to get into python automated trading years ago

## GETTING STARTED

This project is compatible with python3 and there's no reason why I should spend more time to make it compatible with python2.

### Prerequisites

```
pip3 install https://github.com/s4w3d0ff/python-poloniex/archive/v0.4.7.zip (if you wanna use poloniex api)
pip3 install krakenex (if you wanna use kraken api. I do NOT recommend it as kraken seems to be very unstable when it comes to it's API)
```

### Install

```
git clone https://github.com/Viandoks/python-crypto-bot.git
cd python-crypto-bot
```

### How to

#### Run backtest

```
python3 bot.py -c 'USDT_BTC' -p 86400 -s 1494491969
```

This will launch the trading strategy on the pair USDT/BTC, with a candlestick period of 1 day,  starting at the timestamp 1494491969

You can see the result in the command line AND the output/output.html file in the project

#### Run forward test

Not specifying the -s argument will launch the bot in forward test mode
```
python3 bot.py -c 'USDT_BTC' -p 86400
```

A new call is made every 10 seconds. You can follow the trades almost live be reloading output/output.html

#### Run live
!!!!! DO NOT DO THIS IF YOU'RE NOT 100% SURE OF WHAT YOU'RE DOING! I WILL NOT BE HELD RESPONSIBLE IF YOU LOSE MONEY!!!!!
To run the bot live you need to enter your api key and secret in the shared.py file. If you don't know what an api key is, you shouldn't even try to launch that bot live. However feel free to have fun in backtest and forward test mode.
```
python3 bot.py -c 'USDT_BTC' -p 86400 --live
```

#### Arguments

**Mandatory**

`-c currency_pair` to let know the bot on what currency pair it should be woking. eg: `-c USDT_BTC`

`-p candlestick_period` period in seconds. In backtest mode this should be a period compatible with Poloniex API (300,900,1800,7200,14400 or 86400). In forward test and live mode, it can be any increment of seconds you want.

**Optional**

`-s timestamp` if specified bot will automatically launch in backtestmode. This is the timestamp of the starting date eg: `-s 1494491969`. If -s is not specified then bot will launch in forward test

`-e timestamp` This is the timestamp of the ending tests for the tests. It should be greater than `-s`

`-exchange str` For now only poloniex (default) and kraken are accepted

`--live` Whill launch bot in live mode.

### Important files
`shared.py` contains a bunch of variable shared accross the different modules

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

### Tips

You like what you see? Feel free to tip me, you'll earn my eternal gratitude:

BTC - 1MT45xgCJe68c3eL2iTJMSQLwsDobmzz7r

ETH - 0x4Aa63028CA72D8Ce79E904DE1c53AbC91d2F2347

### Final Words

HAVE FUN!
