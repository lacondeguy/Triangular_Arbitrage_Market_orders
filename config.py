import ccxt

base_ticker = 'USDT'
INVESTMENT_AMOUNT_DOLLARS = 100
MIN_PROFIT_DOLLARS = 0.5


proxy_list = ['socks5://login:pass@ip:port',
              'socks5://login:pass@ip:port',
              'socks5://login:pass@ip:port']


# The last value is the trading commission on the exchange
all_exchanges = {'binance' :     ["https://binance.com/ru/trade/", "/_", ccxt.binance(), 0.1],
                 'coinbasepro' : ["https://pro.coinbase.com/trade/", "/-", ccxt.coinbasepro(), 0.6],
                 'gateio' :      ["https://www.gate.io/ru/trade/", "/_", ccxt.gateio(), 0.3],
                 'kraken' :      ["https://trade.kraken.com/ru-ru/charts/KRAKEN:", "/-", ccxt.kraken(), 0.25],
                 'kucoin' :      ["https://www.kucoin.com/trade/", "/-", ccxt.kucoin(), 0.3],
                 'okx' :         ["https://www.okx.com/ru/trade-spot/", "/-", ccxt.okx(), 0.1],
                 }

