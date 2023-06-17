import ccxt
import ast


client = Client()

def get_historical_ohlc_data(symbol,past_days=None,interval=None):
    
    """Returns historcal klines from past for given symbol and interval
    past_days: how many days back one wants to download the data"""
    
    if not interval:
        interval='1h' # default interval 1 hour
    if not past_days:
        past_days=30  # default past days 30.

    start_str=str((pd.to_datetime('today')-pd.Timedelta(str(past_days)+' days')).date())
    
    D=pd.DataFrame(client.get_historical_klines(symbol=symbol,start_str=start_str,interval=interval))
    D.columns=['open_time','open', 'high', 'low', 'close', 'volume', 'close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol','is_best_match']
    D['open_date_time']=[dt.datetime.fromtimestamp(x/1000) for x in D.open_time]
    D['symbol']=symbol
    D=D[['symbol','open_date_time','open', 'high', 'low', 'close', 'volume', 'num_trades', 'taker_base_vol', 'taker_quote_vol']]

    return D

def send_order(data):

	
    exchange = ccxt.binance({
        'apiKey': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        'secret': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        'enableRateLimit': True,})
    
    
    balance = exchange.fetch_balance()
    balance = ( balance['total']['USDT'] ) 
    amount = (balance/float(data['price']))
    ticker = data['symbol'].replace('USDT','/USDT')
	
    print('Sending:', ticker, data['type'], data['side'], amount, data['price'])
    order = exchange.create_order(ticker, data['type'], data['side'], amount, float(data['price']))
	
	
    print('Exchange Response:', order)

