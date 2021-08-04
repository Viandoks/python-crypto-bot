import ccxt
import shared

def BotApi():
    ccxt.exchange = getattr(ccxt, shared.exchange['name'])({
        'apiKey': shared.api['key'],
        'secret': shared.api['secret']
    })
    return ccxt
