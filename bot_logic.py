import ccxt
import pandas as pd
import time
from datetime import datetime
import math
import requests
import random
from config import *
import numpy as np


# Send alert to Telegram channel
def send_telegram(text: str):
    token = ""
    url = "https://api.telegram.org/bot"
    channel_id = "@channel"
    url += token
    method = url + "/sendMessage"

    r = requests.post(method, data={
         "chat_id": channel_id,
         "text": text
          })

    if r.status_code != 200:
        raise Exception("post_text error")


def slice(name_exchange):
    slises = []
    combinations_list = get_crypto_combinations(base_ticker, name_exchange)
    count = len(proxy_list)
    slises = np.array_split(combinations_list, count)
    return slises


# Get all combinations
def get_crypto_combinations(base, name_exchange):
    combinations = []
    exchange_class = all_exchanges[name_exchange][2]
    markets = exchange_class.fetchMarkets()
    market_symbols = [market['symbol'] for market in markets]
    for sym1 in market_symbols:

        sym1_token1 = sym1.split('/')[0]
        sym1_token2 = sym1.split('/')[1]

        if (sym1_token2 == base):
            for sym2 in market_symbols:
                sym2_token1 = sym2.split('/')[0]
                sym2_token2 = sym2.split('/')[1]
                if (sym1_token1 == sym2_token2):
                    for sym3 in market_symbols:
                        sym3_token1 = sym3.split('/')[0]
                        sym3_token2 = sym3.split('/')[1]
                        if ((sym2_token1 == sym3_token1) and (sym3_token2 == sym1_token2)):
                            combination = {
                                'base': sym1_token2,
                                'intermediate': sym1_token1,
                                'ticker': sym2_token1,
                            }
                            combinations.append(combination)
    return combinations


# Ask price
def fetch_current_ticker_price_ask(ticker):
    current_ticker_details = exchange.fetch_ticker(ticker)
    ticker_volume = current_ticker_details['askVolume']
    ticker_price = current_ticker_details['ask'] if current_ticker_details is not None else None
    print(f"аск {current_ticker_details['ask']}, бид {current_ticker_details['bid']}")
    print(ticker)
    return ticker_price, ticker_volume


# Bid price
def fetch_current_ticker_price_bid(ticker):
    current_ticker_details = exchange.fetch_ticker(ticker)
    ticker_volume = current_ticker_details['bidVolume']
    ticker_price = current_ticker_details['bid'] if current_ticker_details is not None else None
    print(f"аск {current_ticker_details['ask']}, бид {current_ticker_details['bid']}")
    print(ticker)
    return ticker_price, ticker_volume


def check_if_float_zero(value):
    return math.isclose(value, 0.0, abs_tol=1e-3)

# Check triangular arbitrage for buy-buy-sell
def check_buy_buy_sell(scrip1, scrip2, scrip3, initial_investment):
    ## SCRIP1
    current_volume1 = 0
    current_volume2 = 0
    current_volume3 = 0
    investment_amount1 = initial_investment
    current_price1, current_volume1 = fetch_current_ticker_price_ask(scrip1)
    final_price = 0
    scrip_prices = {}

    if current_price1 is not None and current_volume1 and not check_if_float_zero(current_price1):
        buy_quantity1 = round(investment_amount1 / current_price1, 8)

        # Check Volume №1
        if current_volume1 > buy_quantity1:

            # Delay
            time.sleep(1)
            ## SCRIP2
            investment_amount2 = buy_quantity1
            current_price2, current_volume2 = fetch_current_ticker_price_ask(scrip2)
            if current_price2 is not None and current_volume2 is not None and not check_if_float_zero(current_price2):
                buy_quantity2 = round(investment_amount2 / current_price2, 8)


                # Check Volume №2
                if current_volume2 >  buy_quantity2:

                    # Dalay
                    time.sleep(1)
                    ## SCRIP3
                    investment_amount3 = buy_quantity2
                    current_price3, current_volume3 = fetch_current_ticker_price_bid(scrip3)
                    if current_price3 is not None and current_volume3 and not check_if_float_zero(current_price3):
                        sell_quantity3 = buy_quantity2


                        # Check Volume №3
                        if current_volume3 > sell_quantity3:
                            final_price = round(sell_quantity3 * current_price3, 3)
                            scrip_prices = {scrip1: current_price1, scrip2: current_price2, scrip3: current_price3}

    return final_price, scrip_prices, current_volume1, current_volume2, current_volume3

# Check triangular arbitrage for buy-sell-sell
def check_buy_sell_sell(scrip1, scrip2, scrip3, initial_investment):
    # SCRIP1
    current_volume1 = 0
    current_volume2 = 0
    current_volume3 = 0
    investment_amount1 = initial_investment
    current_price1, current_volume1 = fetch_current_ticker_price_ask(scrip1)
    final_price = 0
    scrip_prices = {}
    if current_price1 is not None and current_volume1 and not check_if_float_zero(current_price1):
        buy_quantity1 = round(investment_amount1 / current_price1, 8)

        # Check Volume №1
        if current_volume1 > buy_quantity1:

            # Delay
            time.sleep(1)
            # SCRIP2
            investment_amount2 = buy_quantity1
            current_price2, current_volume2 = fetch_current_ticker_price_bid(scrip2)
            if current_price2 is not None and current_volume2 and not check_if_float_zero(current_price2):
                sell_quantity2 = buy_quantity1
                sell_price2 = round(sell_quantity2 * current_price2, 8)

                # Check Volume №2
                if current_volume2 > sell_quantity2:


                    # Delay
                    time.sleep(1)
                    # SCRIP1
                    investment_amount3 = sell_price2
                    current_price3, current_volume3 = fetch_current_ticker_price_bid(scrip3)
                    if current_price3 is not None and current_volume3 and not check_if_float_zero(current_price3):
                        sell_quantity3 = sell_price2


                        # Check Volume №3
                        if current_volume3 > sell_quantity3:
                            final_price = round(sell_quantity3 * current_price3, 3)
                            scrip_prices = {scrip1: current_price1, scrip2: current_price2, scrip3: current_price3}

    return final_price, scrip_prices, current_volume1, current_volume2, current_volume3

# Check profit
def check_profit_loss(total_price_after_sell,initial_investment,transaction_brokerage, min_profit):
    apprx_brokerage = transaction_brokerage * initial_investment/100 * 3
    min_profitable_price = initial_investment + apprx_brokerage + min_profit
    profit_loss = round(total_price_after_sell - min_profitable_price,3)
    return profit_loss



def perform_triangular_arbitrage(scrip1, scrip2, scrip3, arbitrage_type, initial_investment,
                                 transaction_brokerage, min_profit, link1, link2):
    final_price = 0.0
    if (arbitrage_type == 'BUY_BUY_SELL'):
        # Check this combination for triangular arbitrage: scrip1 - BUY, scrip2 - BUY, scrip3 - SELL
        final_price, scrip_prices, current_volume1, current_volume2, current_volume3 = check_buy_buy_sell(scrip1, scrip2, scrip3, initial_investment)

    elif (arbitrage_type == 'BUY_SELL_SELL'):
        # Check this combination for triangular arbitrage: scrip1 - BUY, scrip2 - SELL, scrip3 - SELL
        final_price, scrip_prices, current_volume1, current_volume2, current_volume3 = check_buy_sell_sell(scrip1, scrip2, scrip3, initial_investment)

    profit_loss = check_profit_loss(final_price, initial_investment, transaction_brokerage, min_profit)

    if profit_loss > 0 and (arbitrage_type == 'BUY_BUY_SELL'):
        send_telegram(f'''BUY_BUY_SELL\n, {scrip_prices}\n
{current_volume1}, {current_volume2}, {current_volume3}''')

    if profit_loss > 0 and (arbitrage_type == 'BUY_SELL_SELL'):
        send_telegram(f'''BUY_SELL_SELL\n, {scrip_prices}\n
{current_volume1}, {current_volume2}, {current_volume3}''')



    if profit_loss > 0:
        print(f"Время: {datetime.now().strftime('%H:%M:%S')}:\n" \
              f"Тип: {arbitrage_type}\n" \
              f"{scrip1}, {scrip2}, {scrip3}\n" \
              f"Профит: {round(final_price - initial_investment - transaction_brokerage * 3, 3)}$\n")

        send_telegram(f"Время: {datetime.now().strftime('%H:%M:%S')}\n" \
              f"Тип: {arbitrage_type}\n" \
              f"{scrip1}, {scrip2}, {scrip3}\n" \
              f"Профит: {round(final_price - initial_investment - transaction_brokerage * 3, 3)}$\n\n" \
              f"{link1}{scrip1.replace(link2[0], link2[1])}\n" \
              f"{link1}{scrip2.replace(link2[0], link2[1])}\n" \
              f"{link1}{scrip3.replace(link2[0], link2[1])}")

        # place order func
        # place_trade_orders(arbitrage_type, scrip1, scrip2, scrip3, initial_investment, scrip_prices)

# Loop
def main(name_exchange, proxy, combinations, INVESTMENT_AMOUNT_DOLLARS, MIN_PROFIT_DOLLARS):
    global exchange

    exchange_class = all_exchanges[name_exchange][2]
    link1 = all_exchanges[name_exchange][0]
    link2 = all_exchanges[name_exchange][1]
    BROKERAGE_PER_TRANSACTION_PERCENT = all_exchanges[name_exchange][3]
    exchange = exchange_class
    exchange.proxies = {
        'socks5': proxy
    }

    print(f"Использую прокси: ', {proxy}\n")
    wx_combinations_usdt = combinations
    cominations_df = pd.DataFrame(wx_combinations_usdt)
    cominations_df.head()

    while(1):

        print('Использую прокси: ', proxy)
        combination = random.choice(wx_combinations_usdt)
        base = combination['base']
        intermediate = combination['intermediate']
        ticker = combination['ticker']

        s1 = f'{intermediate}/{base}'  # Eg: BTC/USDT
        s2 = f'{ticker}/{intermediate}'  # Eg: ETH/BTC
        s3 = f'{ticker}/{base}'  # Eg: ETH/USDT

        # Check triangular arbitrage for buy-buy-sell
        perform_triangular_arbitrage(s1, s2, s3, 'BUY_BUY_SELL', INVESTMENT_AMOUNT_DOLLARS,
                                     BROKERAGE_PER_TRANSACTION_PERCENT, MIN_PROFIT_DOLLARS, link1, link2)
        # Sleep to avoid rate limit on api calls (RateLimitExceeded exception)
        time.sleep(1)
        # Check triangular arbitrage for buy-sell-sell
        perform_triangular_arbitrage(s3, s2, s1, 'BUY_SELL_SELL', INVESTMENT_AMOUNT_DOLLARS,
                                     BROKERAGE_PER_TRANSACTION_PERCENT, MIN_PROFIT_DOLLARS, link1, link2)
        time.sleep(1)
        print('Checking...\n')

