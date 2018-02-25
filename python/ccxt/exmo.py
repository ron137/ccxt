# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.base.exchange import Exchange
import hashlib
from ccxt.base.errors import ExchangeError


class exmo (Exchange):

    def describe(self):
        return self.deep_extend(super(exmo, self).describe(), {
            'id': 'exmo',
            'name': 'EXMO',
            'countries': ['ES', 'RU'],  # Spain, Russia
            'rateLimit': 350,  # once every 350 ms ≈ 180 requests per minute ≈ 3 requests per second
            'version': 'v1',
            'has': {
                'CORS': False,
                'fetchOrder': True,
                'fetchOpenOrders': True,
                'fetchOrderTrades': True,
                'fetchOrderBooks': True,
                'fetchMyTrades': True,
                'fetchTickers': True,
                'withdraw': True,
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766491-1b0ea956-5eda-11e7-9225-40d67b481b8d.jpg',
                'api': 'https://api.exmo.com',
                'www': 'https://exmo.me',
                'doc': [
                    'https://exmo.me/en/api_doc',
                    'https://github.com/exmo-dev/exmo_api_lib/tree/master/nodejs',
                ],
                'fees': 'https://exmo.com/en/docs/fees',
            },
            'api': {
                'public': {
                    'get': [
                        'currency',
                        'order_book',
                        'pair_settings',
                        'ticker',
                        'trades',
                    ],
                },
                'private': {
                    'post': [
                        'user_info',
                        'order_create',
                        'order_cancel',
                        'user_open_orders',
                        'user_trades',
                        'user_cancelled_orders',
                        'order_trades',
                        'required_amount',
                        'deposit_address',
                        'withdraw_crypt',
                        'withdraw_get_txid',
                        'excode_create',
                        'excode_load',
                        'wallet_history',
                    ],
                },
            },
            'fees': {
                'trading': {
                    'maker': 0.2 / 100,
                    'taker': 0.2 / 100,
                },
                'funding': {
                    'withdraw': {
                        'BTC': 0.001,
                        'LTC': 0.01,
                        'DOGE': 1,
                        'DASH': 0.01,
                        'ETH': 0.01,
                        'WAVES': 0.001,
                        'ZEC': 0.001,
                        'USDT': 25,
                        'XMR': 0.05,
                        'XRP': 0.02,
                        'KICK': 350,
                        'ETC': 0.01,
                        'BCH': 0.001,
                    },
                    'deposit': {
                        'USDT': 15,
                        'KICK': 50,
                    },
                },
            },
        })

    def fetch_markets(self):
        markets = self.publicGetPairSettings()
        keys = list(markets.keys())
        result = []
        for p in range(0, len(keys)):
            id = keys[p]
            market = markets[id]
            symbol = id.replace('_', '/')
            base, quote = symbol.split('/')
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'limits': {
                    'amount': {
                        'min': float(market['min_quantity']),
                        'max': float(market['max_quantity']),
                    },
                    'price': {
                        'min': float(market['min_price']),
                        'max': float(market['max_price']),
                    },
                    'cost': {
                        'min': float(market['min_amount']),
                        'max': float(market['max_amount']),
                    },
                },
                'precision': {
                    'amount': 8,
                    'price': 8,
                },
                'info': market,
            })
        return result

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.privatePostUserInfo()
        result = {'info': response}
        currencies = list(self.currencies.keys())
        for i in range(0, len(currencies)):
            currency = currencies[i]
            account = self.account()
            if currency in response['balances']:
                account['free'] = float(response['balances'][currency])
            if currency in response['reserved']:
                account['used'] = float(response['reserved'][currency])
            account['total'] = self.sum(account['free'], account['used'])
            result[currency] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        request = self.extend({
            'pair': market['id'],
        }, params)
        if limit is not None:
            request['limit'] = limit
        response = self.publicGetOrderBook(request)
        result = response[market['id']]
        orderbook = self.parse_order_book(result, None, 'bid', 'ask')
        return self.extend(orderbook, {
            'bids': self.sort_by(orderbook['bids'], 0, True),
            'asks': self.sort_by(orderbook['asks'], 0),
        })

    def fetch_order_books(self, symbols=None, params={}):
        self.load_markets()
        ids = None
        if not symbols:
            ids = ','.join(self.ids)
            # max URL length is 2083 symbols, including http schema, hostname, tld, etc...
            if len(ids) > 2048:
                numIds = len(self.ids)
                raise ExchangeError(self.id + ' has ' + str(numIds) + ' symbols exceeding max URL length, you are required to specify a list of symbols in the first argument to fetchOrderBooks')
        else:
            ids = self.market_ids(symbols)
            ids = ','.join(ids)
        response = self.publicGetOrderBook(self.extend({
            'pair': ids,
        }, params))
        result = {}
        ids = list(response.keys())
        for i in range(0, len(ids)):
            id = ids[i]
            symbol = id
            if id in self.markets_by_id:
                market = self.markets_by_id[id]
                symbol = market['symbol']
            result[symbol] = self.parse_order_book(response[id], None, 'bid', 'ask')
        return result

    def parse_ticker(self, ticker, market=None):
        timestamp = ticker['updated'] * 1000
        symbol = None
        if market:
            symbol = market['symbol']
        last = float(ticker['last_trade'])
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'bid': float(ticker['buy_price']),
            'ask': float(ticker['sell_price']),
            'vwap': None,
            'open': None,
            'close': last,
            'last': last,
            'previousClose': None,
            'change': None,
            'percentage': None,
            'average': float(ticker['avg']),
            'baseVolume': float(ticker['vol']),
            'quoteVolume': float(ticker['vol_curr']),
            'info': ticker,
        }

    def fetch_tickers(self, symbols=None, params={}):
        self.load_markets()
        response = self.publicGetTicker(params)
        result = {}
        ids = list(response.keys())
        for i in range(0, len(ids)):
            id = ids[i]
            market = self.markets_by_id[id]
            symbol = market['symbol']
            ticker = response[id]
            result[symbol] = self.parse_ticker(ticker, market)
        return result

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        response = self.publicGetTicker(params)
        market = self.market(symbol)
        return self.parse_ticker(response[market['id']], market)

    def parse_trade(self, trade, market):
        timestamp = trade['date'] * 1000
        return {
            'id': str(trade['trade_id']),
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'order': self.safe_string(trade, 'order_id'),
            'type': None,
            'side': trade['type'],
            'price': float(trade['price']),
            'amount': float(trade['quantity']),
            'cost': self.safe_float(trade, 'amount'),
        }

    def parse_order(self, order, market):
        timestamp = int(order['created']) * 1000
        amount = float(order['quantity'])
        remaining = amount
        filled = 0
        price = float(order['price'])
        average = price
        cost = 0
        result = {
            'info': order,
            'id': str(order['order_id']),
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': 'limit',
            'side': order['type'],
            'price': price,
            'average': average,
            'cost': 0,
            'amount': amount,
            'filled': 0,
            'remaining': remaining,
            'status': 'open',
            'fee': None,
        }
        return result

    def fetch_open_orders(self, symbol=None, since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.privatePostUserOpenOrders(params)
        if symbol and self.market_id(symbol) in response:
            orders = response[self.market_id(symbol)]
        else:
            orders = []
            for market_id in response:
                for order in response[market_id]:
                    orders.append(order)

        return self.parse_orders(orders, market, since, limit)

    def fetch_my_trades(self, symbol=None, since=None, limit=10000, params={}):
        self.load_markets()
        market = self.market(symbol)
        if symbol:
            params['pair'] = self.market_id(symbol)
        response = self.privatePostUserTrades(self.extend({
            'limit': limit
            },params))
        if symbol:
            trades = response[self.market_id(symbol)]
        else:
            trades = []
            for market_id in response:
                for trade in response[market_id]:
                    trades.append(trade)

        return self.parse_trades(trades, market, since, limit)



    def fetch_trades(self, symbol, since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetTrades(self.extend({
            'pair': market['id'],
        }, params))
        return self.parse_trades(response[market['id']], market, since, limit)

    def fetch_my_trades(self, symbol=None, since=None, limit=None, params={}):
        self.load_markets()
        request = {}
        market = None
        if symbol is not None:
            market = self.market(symbol)
            request['pair'] = market['id']
        response = self.privatePostUserTrades(self.extend(request, params))
        if market is not None:
            response = response[market['id']]
        return self.parse_trades(response, market, since, limit)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        prefix = 'market_' if (type == 'market') else ''
        order = {
            'pair': self.market_id(symbol),
            'quantity': amount,
            'price': price,
            'type': prefix + side,
        }
        response = self.privatePostOrderCreate(self.extend(order, params))
        timestamp = self.milliseconds()
        return {
            'id': response['order_id'],
            'info': response,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'type': type,
            'side': side,
            'price': price,
            'average': price,
            'cost': 0,
            'amount': amount,
            'filled': 0,
            'remaining': amount,
            'status': 'open',
            'fee': None,
        }

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        return self.privatePostOrderCancel({'order_id': id})

    def fetch_order(self, id, symbol=None, params={}):
        self.load_markets()
        market = None
        if symbol is not None:
            market = self.market(symbol)
        response = self.privatePostOrderTrades(self.extend({'order_id': id}, params))
        return self.parse_order(response, market)

    def fetch_order_trades(self, id, symbol=None, since=None, limit=None, params={}):
        market = None
        if symbol is not None:
            self.load_markets()
            market = self.market(symbol)
        response = self.privatePostOrderTrades(self.extend({
            'order_id': id,
        }, params))
        return self.parse_trades(response['trades'], market, since, limit)

    def fetch_open_orders(self, symbol=None, since=None, limit=None, params={}):
        market = None
        if symbol is not None:
            self.load_markets()
            market = self.market(symbol)
        orders = self.privatePostUserOpenOrders()
        if market is not None:
            if orders[market['id']] is not None:
                orders = orders[market['id']]
            else:
                orders = []
        return self.parse_orders(orders, market, since, limit)

    def parse_order(self, order, market=None):
        id = self.safe_string(order, 'order_id')
        timestamp = self.safe_integer(order, 'created')
        iso8601 = None
        symbol = None
        side = self.safe_string(order, 'type')
        if market is None:
            marketId = None
            if 'pair' in order:
                marketId = order['pair']
            elif ('in_currency' in list(order.keys())) and('out_currency' in list(order.keys())):
                if side == 'buy':
                    marketId = order['in_currency'] + '_' + order['out_currency']
                else:
                    marketId = order['out_currency'] + '_' + order['in_currency']
            if marketId in self.markets_by_id:
                market = self.markets_by_id[marketId]
        amount = self.safe_float(order, 'quantity')
        if amount is None:
            amountField = 'in_amount' if (side == 'buy') else 'out_amount'
            amount = self.safe_float(order, amountField)
        price = self.safe_float(order, 'price')
        cost = self.safe_float(order, 'amount')
        filled = 0.0
        trades = []
        transactions = self.safe_value(order, 'trades')
        feeCost = None
        if transactions is not None:
            if isinstance(transactions, list):
                for i in range(0, len(transactions)):
                    trade = self.parse_trade(transactions[i], market)
                    if id is None:
                        id = trade['order']
                    if timestamp is None:
                        timestamp = trade['timestamp']
                    if timestamp > trade['timestamp']:
                        timestamp = trade['timestamp']
                    filled += trade['amount']
                    if feeCost is None:
                        feeCost = 0.0
                    # feeCost += trade['fee']['cost']
                    if cost is None:
                        cost = 0.0
                    cost += trade['cost']
                    trades.append(trade)
        if timestamp is not None:
            iso8601 = self.iso8601(timestamp)
        remaining = None
        if amount is not None:
            remaining = amount - filled
        status = self.safe_string(order, 'status')  # in case we need to redefine it for canceled orders
        if filled >= amount:
            status = 'closed'
        else:
            status = 'open'
        if market is None:
            market = self.get_market_from_trades(trades)
        feeCurrency = None
        if market is not None:
            symbol = market['symbol']
            feeCurrency = market['quote']
        if cost is None:
            if price is not None:
                cost = price * filled
        elif price is None:
            if filled > 0:
                price = cost / filled
        fee = {
            'cost': feeCost,
            'currency': feeCurrency,
        }
        return {
            'id': id,
            'datetime': iso8601,
            'timestamp': timestamp,
            'status': status,
            'symbol': symbol,
            'type': None,
            'side': side,
            'price': price,
            'cost': cost,
            'amount': amount,
            'filled': filled,
            'remaining': remaining,
            'trades': trades,
            'fee': fee,
            'info': order,
        }

    def get_market_from_trades(self, trades):
        tradesBySymbol = self.index_by(trades, 'pair')
        symbols = list(tradesBySymbol.keys())
        numSymbols = len(symbols)
        if numSymbols == 1:
            return self.markets[symbols[0]]
        return None

    def calculate_fee(self, symbol, type, side, amount, price, takerOrMaker='taker', params={}):
        market = self.markets[symbol]
        rate = market[takerOrMaker]
        cost = float(self.cost_to_precision(symbol, amount * rate))
        key = 'quote'
        if side == 'sell':
            cost *= price
        else:
            key = 'base'
        return {
            'type': takerOrMaker,
            'currency': market[key],
            'rate': rate,
            'cost': float(self.fee_to_precision(symbol, cost)),
        }

    def withdraw(self, currency, amount, address, tag=None, params={}):
        self.load_markets()
        request = {
            'amount': amount,
            'currency': currency,
            'address': address,
        }
        if tag is not None:
            request['invoice'] = tag
        result = self.privatePostWithdrawCrypt(self.extend(request, params))
        return {
            'info': result,
            'id': result['task_id'],
        }

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.version + '/' + path
        if api == 'public':
            if params:
                url += '?' + self.urlencode(params)
        else:
            self.check_required_credentials()
            nonce = self.nonce()
            body = self.urlencode(self.extend({'nonce': nonce}, params))
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Key': self.apiKey,
                'Sign': self.hmac(self.encode(body), self.encode(self.secret), hashlib.sha512),
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'result' in response:
            if response['result']:
                return response
            raise ExchangeError(self.id + ' ' + self.json(response))
        return response
