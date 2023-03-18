from threading import Thread
from bot_logic import main, slice
from config import *


def start_bot():
    name_exchange = input(f'''Supported exchanges:
binance, coinbasepro, gateio, kraken, kucoin, okx\n
Enter exchange name:\n''')
    combinations_list = slice(name_exchange)
    count_slise = 0
    for proxy in proxy_list:
        combinations = combinations_list[count_slise]
        count_slise += 1
        th = Thread(target=main, args=(name_exchange, proxy, combinations, INVESTMENT_AMOUNT_DOLLARS, MIN_PROFIT_DOLLARS))
        th.start()

start_bot()
