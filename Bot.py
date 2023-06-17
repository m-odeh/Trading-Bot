"""
python bot that works with tradingview webhool alerts


"""

from actions import send_order,get_historical_ohlc_data
from flask import Flask, request, abort
import threading
import time
import ccxt
import json
from binance.client import Client
from finta import TA
import pandas as pd
from binance.client import Client
import datetime as dt

bot_status='buy' # Initial Bot status = Buy ; looking to buy an asset 
api_key1=''
api_secret1=''
client = Client(api_key1, api_secret1) 

def get_price(coinpair):
    all_coins = client.get_all_tickers()
    for i in all_coins:
        if i['symbol'] == coinpair:
            return i['price']
            
    
exchange = ccxt.binance({
	'apiKey': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', # Your API KEY
	'secret': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', # Your Secret
	'enableRateLimit': True,})

app = Flask(__name__)


@app.route('/')
def root():
    return 'online'


@app.route('/webhook', methods=['POST'])
def webhook():
    global bot_status

    if request.method == 'POST':
        
		# Parse the string data from tradingview into a python dict
        print('POST Received:')
        print('bot_status started = ',bot_status)
        if bot_status=='buy':
		
            data =json.loads(request.get_data())
            print('POST Received:', data)
            print('data type is:',type(data))
            send_order(data)
            time.sleep(5)
            bot_status='sell'
            print('bot_status Now = ',bot_status)
            balance = exchange.fetch_balance()

            if bot_status == 'sell': # Looking to sell an asset

                asset_bought=(data['symbol']).replace('USDT','')
                ticker = data['symbol'].replace('USDT','/USDT')
                bag=balance['free'][asset_bought] 
                purchase_price = float(data['price'])

                ohlc=get_historical_ohlc_data(symbol=data['symbol'],interval='30m')
                ohlc['open']=pd.to_numeric(ohlc['open'], errors='coerce')
                ohlc['high']=pd.to_numeric(ohlc['high'], errors='coerce')
                ohlc['low']=pd.to_numeric(ohlc['low'], errors='coerce')
                ohlc['close']=pd.to_numeric(ohlc['close'], errors='coerce')
                ohlc['ATR']=TA.ATR(ohlc)
                last_candle=ohlc.iloc[-1]
                ATR=last_candle['ATR']

                target_price =  purchase_price + ATR
                stop_loss =   purchase_price - (2*ATR)

                while(bot_status == 'sell'):
                
                    coinpair = data['symbol']
                    current_price = get_price(coinpair)

                    print('bot_status Now at',bot_status)
                    print('===============================')			
                    print('The coin bought is: ',asset_bought )
                    print('Balance = ',bag )
                    print('ticker =',ticker )
                    print('Purchase price = ',purchase_price )
                    print('ATR = ',ATR )
                    print('Selling target price = ',target_price )
                    print('Stop Loss = ',stop_loss )
                    print('current price = ',current_price )
                    print('===============================')

                    if float(current_price) >= target_price:
                        balance = exchange.fetch_balance()
                        bag=balance['free'][asset_bought]
                        print('Sending:', ticker, data['type'], 'sell', bag, current_price)
                        order = exchange.create_order(ticker, data['type'],'sell', bag, current_price)
                        bot_status='buy'
                        time.sleep(5)
                       
                        
                    elif float(current_price) <= stop_loss:
                        balance = exchange.fetch_balance()
                        bag=balance['free'][asset_bought]
                        print('Stop loss triggered, Sending:', ticker, data['type'], 'sell', bag, current_price )
                        order = exchange.create_order(ticker, data['type'],'sell', bag, current_price)
                        bot_status='buy'
                        time.sleep(5)
                    
                    time.sleep(5)

    else:
        abort(400)
    return 'Done '
    
if __name__ == '__main__':
    app.run(debug=False)