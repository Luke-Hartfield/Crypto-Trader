##################################################
## Title: Binance Crypto Trading Bot
## Author: Luke Hartfield & Jack Preston
## Version: v0.1
## Status: Development
##################################################


# Import packages
import websocket, json, talib, numpy, math
import config
from binance.client import Client
from binance.enums import *

# Global variables
closes = []
RSI_PERIOD = 9
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'BTCBUSD'
COIN = 'BTC'
DESIRED_SPEND = 30



# Initialise client
client = Client(config.API_KEY, config.API_SECRET, )

# Set stream
SOCKET = "wss://stream.binance.com:9443/ws/btcbusd@kline_1m"

# Place order
def order(symbol, side, quantity):
    try:
        print("Sending Order: ")
        order = client.create_order(
            symbol = symbol,
            side = side,
            type = ORDER_TYPE_MARKET,
            quantity = quantity)
        print(order)
        print(get_order())
        print(get_balance())

    except Exception as e:
        print(e)
        
    return True

# Check for open
def on_open(ws):
    print('Connection opened')

# Check for close
def on_close(ws):
    print('Connection closed')

def get_price():
    return client.get_symbol_ticker(symbol = TRADE_SYMBOL)['price']

def get_balance():
    #return math.floor(float(client.get_asset_balance(asset = COIN)['free']))
    return round(float(client.get_asset_balance(asset = COIN)['free']), 6) #For BTC

def get_buy_quantity(price):
    return round(DESIRED_SPEND / float(price), 6)

def get_order():
    return client.get_open_orders(symbol = TRADE_SYMBOL)

# Get close prices
def on_message(ws, message):    
    global closes

    # Check if owned
    balance = get_balance()    
    sell_amount = round((balance * 0.999), 6)
    owned_or_not = balance != 0
    #print(balance)

    # Get current price and calc $x worth
    price = get_price()
    #print(price)
    buy_quantity = get_buy_quantity(price)  
    #print("Q: ", buy_quantity)

    json_message = json.loads(message)
    #pprint.pprint(json_message)

    candle = json_message['k']
    is_closed = candle['x']
    close_price = candle['c']

    if is_closed:
        closes.append(float(close_price))
        #print("Close Price: ", close_price)
        print("Close Prices:")
        print(closes)
    
        if len(closes) > RSI_PERIOD:
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            last_rsi = rsi[-1]
            #print("All RSIs: ", rsi)
            print("Last RSI: ", last_rsi)

            if last_rsi > RSI_OVERBOUGHT:
                if owned_or_not:
                    print("SELL!")
                    order_success = order(TRADE_SYMBOL, SIDE_SELL, sell_amount)
                    if order_success:
                        print("Sold Coins at: ", float(price['price']))
                else:
                    print("Overbought but nothing owned, nothing to do")

            if last_rsi < RSI_OVERSOLD:
                if owned_or_not:
                    print("Oversold but already own it, nothing to do") 
                else:
                    print("BUY!")
                    order_success = order(TRADE_SYMBOL, SIDE_BUY, buy_quantity)
                    if order_success:
                        print("Bought Coins at: ", float(price['price']))

# Initialise connection
ws = websocket.WebSocketApp(SOCKET, on_open = on_open, on_close = on_close, on_message = on_message)

# Start connection
ws.run_forever()


