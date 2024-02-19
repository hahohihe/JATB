import ccxt
import pandas as pd
import math
import numpy as np
import time
import datetime

def init() :
    global binance, symbol, fees, longK, shortK, long_target, short_target, isLoop, isTarget, position, start_time, end_time, alarm_period
    binance = get_binance()
    symbol = 'ETH/USDT'
    fees = 0.0
    longK, shortK = 0.5, 0.5
    long_target, short_target = 0, 0

    isLoop = True
    isTarget = False
    position = {
        "Type" : 'None',
        "EntryPrice" : 0,
        "Amount" : 0,
        "Size" : 0,
    }

    start_time = '0910'
    end_time = '0850'
    alarm_period = 3

def get_binance() :
    # api Key, secret을 통해 가져오기
    with open("api.txt") as f :
        lines = f.readlines()
        api_key = lines[0].strip()
        secret = lines[1].strip()

    # Binance 객체 생성
    binance = ccxt.binance(config={
        'apiKey': api_key,
        'secret': secret,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'future'
        }
    })
    return binance

def get_symbol():
    return symbol

def get_current_price(symbol):
    if symbol != '' :
        ticker = binance.fetch_ticker(symbol)
        return ticker['last']
    return 0

def get_open_price(symbol):
    return binance.fetch_ohlcv(symbol=symbol, timeframe='1d', since=None, limit=1)[-1][1]

def get_symbol_info(symbol, timeframe = '1d', since = None, limit = 1) :
    symbol_info = binance.fetch_ohlcv(symbol, timeframe, since, limit)
    df = pd.DataFrame(
        data=symbol_info,
        columns=['datetime', 'open', 'high', 'low', 'close', 'volume']
    )
    df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')

    return df

def get_balance() :
    balance = binance.fetch_balance(params={"type":"future"})
    return round(balance['total']['USDT'], 2)

def get_crr(df, fees, k) :
    df['range'] = df['high'].shift(1) - df['low'].shift(1)
    df['long_target'] = df['open'] + df['range'] * k
    df['short_target'] = df['open'] - df['range'] * k
    df['long_drr'] = np.where(df['high'] > df['long_target'], (df['close'] / (1 + fees)) / (df['long_target'] * (1 + fees)) - 1, 0)
    df['long_crr'] = (df['long_drr'] + 1).cumprod() - 1
    df['short_drr'] = np.where(df['low'] < df['short_target'], 1 - (df['close'] / (1 + fees)) / (df['short_target'] * (1 + fees)), 0)
    df['short_crr'] = (df['short_drr'] + 1).cumprod() - 1

    #return df
    return df['long_crr'].iloc[-2], df['short_crr'].iloc[-2]

def get_position() :
    return position

def get_best_k(symbol, fees = 0.0) :
    global longK, shortK

    df = get_symbol_info(symbol, '1d', None, 21)
    time.sleep(0.1)
    
    max_long_crr, max_short_crr = -999, -999
    best_long_k, best_short_k = 0.5, 0.5

    for k in np.arange(0.3, 0.8, 0.01) :
        long_crr, short_crr = get_crr(df, fees, k)
        if (long_crr > max_long_crr).any() :
            max_long_crr = long_crr
            best_long_k = k
        if (short_crr > max_short_crr).any() :
            max_short_crr = short_crr
            best_short_k = k

    longK = round(best_long_k, 2)
    shortK = round(best_short_k, 2)

def get_amount(symbol, price, portion = 1) :
    market_info = binance.fetch_markets()
    info = next(info for info in market_info if info['symbol'] == symbol)
    min_order_qty = info['limits']['amount']['min']

    usdt = get_balance()
    usdt_trade = usdt * portion
    amount = math.floor(usdt_trade * (1/min_order_qty) / price) / (1/min_order_qty)
    return amount

def cal_target_price(symbol) :
    global long_target, short_target, isTarget

    df = get_symbol_info(symbol, '1d', None, 2)

    yesterday = df.iloc[-2]
    today = df.iloc[-1]
    range = yesterday['high'] - yesterday['low']

    long_target = today['open'] + range * longK
    short_target = today['open'] - range * shortK

    long_target = round(long_target, 2)
    short_target = round(short_target, 2)

    isTarget = True

def enter_position(type, symbol, price, amount) :
    if type == 'Long' :
        binance.create_market_buy_order(symbol, amount)
        set_position(type, price, amount)
    elif type == 'Short' :
        binance.create_market_sell_order(symbol, amount)
        set_position(type, price, amount)        

def set_position(type, price, amount) :
    position['Type'] = type
    position['EntryPrice'] = price
    position['Amount'] = amount
    position['Size'] = round(price * amount, 2)

def exit_position(symbol) :
    if position['Type'] == 'Long' :
        binance.create_market_sell_order(symbol, position['Amount'])
        set_position('None', 0, 0)
    elif position['Type'] == 'Short' :
        binance.create_market_buy_order(symbol, position['Amount'])
        set_position('None', 0, 0)    

binance = get_binance()
symbol = 'ETH/USDT'
fees = 0.0
longK, shortK = 0.5, 0.5
long_target, short_target = 0, 0 

isLoop = True
isTarget = False
isAlarm = True
position = {
    "Type" : 'None',
    "EntryPrice" : 0,
    "Amount" : 0,
    "Size" : 0,
}

start_time = '0910'
end_time = '0850'
alarm_period = 3