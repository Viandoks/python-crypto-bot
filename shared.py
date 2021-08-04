import os
from dotenv import load_dotenv

load_dotenv()

EXCHANGE_MAX_BARS = os.getenv('EXCHANGE_MAX_BARS')

api = {
    'key': os.getenv('API_KEY'),
    'secret': os.getenv('API_SECRET')
}

strategy = {
    'movingAverageLength': 14,
    'timeframe': os.getenv('TIMEFRAME'),
    'start_date': os.getenv('START_DATE'),
    'allocation': os.getenv('ALLOCATION')
}

exchange = {
    'name': os.getenv('EXCHANGE'),
    'pair': os.getenv('ASSET')+'/'+os.getenv('MARKET'),
    'market': os.getenv('MARKET'),
    'nbMarket': float(os.getenv('COINS_MARKET')),
    'asset': os.getenv('ASSET'),
    'nbAsset': float(os.getenv('COINS_ASSET')),
    'marketInOrder': 0.0,
    'coinsInOrder': 0.0,
    'spreadPercentage': float(os.getenv('SPREAD')),
    'fee': float(os.getenv('FEES')),
    'interval': float(os.getenv('INTERVAL'))
}
