# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.base.exchange import Exchange
from ccxt.base.errors import ExchangeError
from ccxt.base.errors import NotSupported
from ccxt.base.errors import AuthenticationError
from ccxt.base.errors import PermissionDenied
from ccxt.base.errors import InsufficientFunds
from ccxt.base.errors import InvalidOrder
from ccxt.base.errors import OrderNotFound
from ccxt.base.errors import InvalidNonce


class bitbank (Exchange):

    def describe(self):
        return self.deep_extend(super(bitbank, self).describe(), {
            'id': 'bitbank',
            'name': 'bitbank',
            'countries': 'JP',
            'version': 'v1',
            'has': {
                'fetchOHLCV': True,
                'fetchOpenOrders': True,
                'fetchMyTrades': True,
                # 'fetchDepositAddress': True,
                # 'withdraw': True,
            },
            'timeframes': {
                '1m': '1min',
                '5m': '5min',
                '15m': '15min',
                '30m': '30min',
                '1h': '1hour',
                '4h': '4hour',
                '8h': '8hour',
                '12h': '12hour',
                '1d': '1day',
                '1w': '1week',
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/37808081-b87f2d9c-2e59-11e8-894d-c1900b7584fe.jpg',
                'api': {
                    'public': 'https://public.bitbank.cc',
                    'private': 'https://api.bitbank.cc',
                },
                'www': 'https://bitbank.cc/',
                'doc': 'https://docs.bitbank.cc/',
                'fees': 'https://bitbank.cc/docs/fees/',
            },
            'api': {
                'public': {
                    'get': [
                        '{pair}/ticker',
                        '{pair}/depth',
                        '{pair}/transactions',
                        '{pair}/transactions/{YYYYMMDD}',
                        '{pair}/candlestick/{candle-type}/{YYYYMMDD}',
                    ],
                },
                'private': {
                    'get': [
                        'user/assets',
                        'user/spot/order',
                        'user/spot/active_orders',
                        'user/spot/trade_history',
                        'user/withdrawal_account',
                    ],
                    'post': [
                        'user/spot/order',
                        'user/spot/cancel_order',
                        'user/spot/cancel_orders',
                        'user/spot/orders_info',
                        'user/request_withdrawal',
                    ],
                },
            },
            'markets': {
                'BCH/BTC': {'id': 'bcc_btc', 'symbol': 'BCH/BTC', 'base': 'BCH', 'quote': 'BTC', 'baseId': 'BCC'},
                'BCH/JPY': {'id': 'bcc_jpy', 'symbol': 'BCH/JPY', 'base': 'BCH', 'quote': 'JPY', 'baseId': 'BCC'},
                'MONA/BTC': {'id': 'mona_btc', 'symbol': 'MONA/BTC', 'base': 'MONA', 'quote': 'BTC'},
                'MONA/JPY': {'id': 'mona_jpy', 'symbol': 'MONA/JPY', 'base': 'MONA', 'quote': 'JPY'},
                'ETH/BTC': {'id': 'eth_btc', 'symbol': 'ETH/BTC', 'base': 'ETH', 'quote': 'BTC'},
                'LTC/BTC': {'id': 'ltc_btc', 'symbol': 'LTC/BTC', 'base': 'LTC', 'quote': 'BTC'},
                'XRP/JPY': {'id': 'xrp_jpy', 'symbol': 'XRP/JPY', 'base': 'XRP', 'quote': 'JPY'},
                'BTC/JPY': {'id': 'btc_jpy', 'symbol': 'BTC/JPY', 'base': 'BTC', 'quote': 'JPY'},
            },
            'fees': {
                'trading': {
                    # only temporarily
                    'maker': 0.0,
                    'taker': 0.0,
                },
                'funding': {
                    'withdraw': {
                        # 'JPY': amount => amount > 756 if 30000 else 540,
                        'BTC': 0.001,
                        'LTC': 0.001,
                        'XRP': 0.15,
                        'ETH': 0.0005,
                        'MONA': 0.001,
                        'BCC': 0.001,
                    },
                },
            },
            'precision': {
                'price': 8,
                'amount': 8,
            },
        })

    def parse_ticker(self, ticker, market=None):
        symbol = market['symbol']
        timestamp = ticker['timestamp']
        last = float(ticker['last'])
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'bid': float(ticker['buy']),
            'bidVolume': None,
            'ask': float(ticker['sell']),
            'askVolume': None,
            'vwap': None,
            'open': None,
            'close': last,
            'last': last,
            'previousClose': None,
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': float(ticker['vol']),
            'quoteVolume': None,
            'info': ticker,
        }

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetPairTicker(self.extend({
            'pair': market['id'],
        }, params))
        return self.parse_ticker(response['data'], market)

    def fetch_order_book(self, symbol, limit=None, params={}):
        self.load_markets()
        response = self.publicGetPairDepth(self.extend({
            'pair': self.market_id(symbol),
        }, params))
        orderbook = response['data']
        return self.parse_order_book(orderbook, orderbook['timestamp'])

    def parse_trade(self, trade, market=None):
        timestamp = trade['executed_at']
        price = float(trade['price'])
        amount = float(trade['amount'])
        symbol = market['symbol']
        cost = self.cost_to_precision(symbol, price * amount)
        id = self.safe_string(trade, 'transaction_id')
        if not id:
            id = self.safe_string(trade, 'trade_id')
        fee = None
        if 'fee_amount_quote' in trade:
            fee = {
                'currency': market['quote'],
                'cost': self.safe_float(trade, 'fee_amount_quote'),
            }
        return {
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'id': id,
            'order': self.safe_string(trade, 'order_id'),
            'type': self.safe_string(trade, 'type'),
            'side': trade['side'],
            'price': price,
            'amount': amount,
            'cost': cost,
            'fee': fee,
            'info': trade,
        }

    def fetch_trades(self, symbol, since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        trades = self.publicGetPairTransactions(self.extend({
            'pair': market['id'],
        }, params))
        return self.parse_trades(trades['data']['transactions'], market, since, limit)

    def parse_ohlcv(self, ohlcv, market=None, timeframe='5m', since=None, limit=None):
        return [
            ohlcv[5],
            float(ohlcv[0]),
            float(ohlcv[1]),
            float(ohlcv[2]),
            float(ohlcv[3]),
            float(ohlcv[4]),
        ]

    def fetch_ohlcv(self, symbol, timeframe='5m', since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        date = self.milliseconds()
        date = self.ymd(date)
        date = date.split('-')
        response = self.publicGetPairCandlestickCandleTypeYYYYMMDD(self.extend({
            'pair': market['id'],
            'candle-type': self.timeframes[timeframe],
            'YYYYMMDD': ''.join(date),
        }, params))
        ohlcv = response['data']['candlestick'][0]['ohlcv']
        return self.parse_ohlcvs(ohlcv, market, timeframe, since, limit)

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.privateGetUserAssets(params)
        result = {'info': response}
        balances = response['data']['assets']
        for i in range(0, len(balances)):
            balance = balances[i]
            id = balance['asset']
            currency = self.common_currency_code(id)
            account = {
                'free': float(balance['free_amount']),
                'used': float(balance['locked_amount']),
                'total': float(balance['onhand_amount']),
            }
            result[currency] = account
        return self.parse_balance(result)

    def parse_order(self, order, market=None):
        marketId = self.safe_string(order, 'pair')
        symbol = None
        if marketId and not market and(marketId in list(self.marketsById.keys())):
            market = self.marketsById[marketId]
        if market:
            symbol = market['symbol']
        timestamp = self.safe_integer(order, 'ordered_at') * 1000
        price = float(order['price'])
        amount = self.safe_float(order, 'start_amount')
        filled = self.safe_float(order, 'executed_amount')
        remaining = self.safe_float(order, 'remaining_amount')
        cost = filled * self.safe_float(order, 'average_price')
        status = self.safe_string(order, 'status')
        # UNFILLED
        # PARTIALLY_FILLED
        # FULLY_FILLED
        # CANCELED_UNFILLED
        # CANCELED_PARTIALLY_FILLED
        if status == 'FULLY_FILLED':
            status = 'closed'
        elif status == 'CANCELED_UNFILLED' or status == 'CANCELED_PARTIALLY_FILLED':
            status = 'canceled'
        else:
            status = 'open'
        return {
            'id': self.safe_string(order, 'order_id'),
            'datetime': self.iso8601(timestamp),
            'timestamp': timestamp,
            'status': status,
            'symbol': symbol,
            'type': order['type'],
            'side': order['side'],
            'price': price,
            'cost': cost,
            'amount': amount,
            'filled': filled,
            'remaining': remaining,
            'trades': None,
            'fee': None,
            'info': order,
        }

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        if price is None:
            raise InvalidOrder(self.id + ' createOrder requires a price argument for both market and limit orders')
        request = {
            'pair': market['id'],
            'amount': self.amount_to_string(symbol, amount),
            'price': self.price_to_precision(symbol, price),
            'side': side,
            'type': type,
        }
        response = self.privatePostUserSpotOrder(self.extend(request, params))
        id = response['data']['order_id']
        order = self.parse_order(response['data'], market)
        self.orders[id] = order
        return order

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.privatePostUserSpotCancelOrder(self.extend({
            'order_id': id,
            'pair': market['id'],
        }, params))
        return response['data']

    def fetch_order(self, id, symbol=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.privateGetUserSpotOrder(self.extend({
            'order_id': id,
            'pair': market['id'],
        }, params))
        return self.parse_order(response['data'])

    def fetch_open_orders(self, symbol=None, since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        request = {
            'pair': market['id'],
        }
        if limit:
            request['count'] = limit
        if since:
            request['since'] = int(since / 1000)
        orders = self.privateGetUserSpotActiveOrders(self.extend(request, params))
        return self.parse_orders(orders['data']['orders'], market, since, limit)

    def fetch_my_trades(self, symbol=None, since=None, limit=None, params={}):
        market = None
        if symbol is not None:
            self.load_markets()
            market = self.market(symbol)
        request = {}
        if market is not None:
            request['pair'] = market['id']
        if limit is not None:
            request['count'] = limit
        if since is not None:
            request['since'] = int(since / 1000)
        trades = self.privateGetUserSpotTradeHistory(self.extend(request, params))
        return self.parse_trades(trades['data']['trades'], market, since, limit)

    def fetch_deposit_address(self, code, params={}):
        #
        # TODO: test
        #
        #     self.load_markets()
        #     currency = self.currency(code)
        #     response = self.privatePostReturnDepositAddresses(self.extend({
        #         'asset': currency['id'],
        #     }, params))
        #     # Not sure about self if there could be more accounts...
        #     accounts = response['data']['accounts']
        #     address = self.safe_string(accounts[0], 'address')
        #     status = 'ok' if address else 'none'
        #     return {
        #         'currency': currency,
        #         'address': address,
        #         'tag': None,
        #         'status': status,
        #         'info': response,
        #     }
        #
        raise NotSupported(self.id + ' fetchDepositAddress is not implementednot ')

    def withdraw(self, code, amount, address, tag=None, params={}):
        #
        # TODO: test
        #
        #     if not('uuid' in list(params.keys())):
        #         raise ExchangeError(self.id + ' uuid is required for withdrawal')
        #     }
        #     self.load_markets()
        #     currency = self.currency(code)
        #     response = self.privatePostRequestWithdrawal(self.extend({
        #         'asset': currency['id'],
        #         'amount': amount,
        #     }, params))
        #     return {
        #         'info': response,
        #         'id': response['data']['txid'],
        #     }
        #
        raise NotSupported(self.id + ' withdraw is not implementednot ')

    def nonce(self):
        return self.milliseconds()

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        query = self.omit(params, self.extract_params(path))
        url = self.urls['api'][api] + '/'
        if api == 'public':
            url += self.implode_params(path, params)
            if query:
                url += '?' + self.urlencode(query)
        else:
            self.check_required_credentials()
            nonce = str(self.nonce())
            auth = nonce
            url += self.version + '/' + self.implode_params(path, params)
            if method == 'POST':
                body = self.json(query)
                auth += body
            else:
                auth += '/' + self.version + '/' + path
                if query:
                    query = self.urlencode(query)
                    url += '?' + query
                    auth += '?' + query
            headers = {
                'Content-Type': 'application/json',
                'ACCESS-KEY': self.apiKey,
                'ACCESS-NONCE': nonce,
                'ACCESS-SIGNATURE': self.hmac(self.encode(auth), self.encode(self.secret)),
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        success = self.safe_integer(response, 'success')
        data = self.safe_value(response, 'data')
        if not success or not data:
            errorMessages = {
                '10000': 'URL does not exist',
                '10001': 'A system error occurred. Please contact support',
                '10002': 'Invalid JSON format. Please check the contents of transmission',
                '10003': 'A system error occurred. Please contact support',
                '10005': 'A timeout error occurred. Please wait for a while and try again',
                '20001': 'API authentication failed',
                '20002': 'Illegal API key',
                '20003': 'API key does not exist',
                '20004': 'API Nonce does not exist',
                '20005': 'API signature does not exist',
                '20011': 'Two-step verification failed',
                '20014': 'SMS authentication failed',
                '30001': 'Please specify the order quantity',
                '30006': 'Please specify the order ID',
                '30007': 'Please specify the order ID array',
                '30009': 'Please specify the stock',
                '30012': 'Please specify the order price',
                '30013': 'Trade Please specify either',
                '30015': 'Please specify the order type',
                '30016': 'Please specify asset name',
                '30019': 'Please specify uuid',
                '30039': 'Please specify the amount to be withdrawn',
                '40001': 'The order quantity is invalid',
                '40006': 'Count value is invalid',
                '40007': 'End time is invalid',
                '40008': 'end_id Value is invalid',
                '40009': 'The from_id value is invalid',
                '40013': 'The order ID is invalid',
                '40014': 'The order ID array is invalid',
                '40015': 'Too many specified orders',
                '40017': 'Incorrect issue name',
                '40020': 'The order price is invalid',
                '40021': 'The trading classification is invalid',
                '40022': 'Start date is invalid',
                '40024': 'The order type is invalid',
                '40025': 'Incorrect asset name',
                '40028': 'uuid is invalid',
                '40048': 'The amount of withdrawal is illegal',
                '50003': 'Currently, self account is in a state where you can not perform the operation you specified. Please contact support',
                '50004': 'Currently, self account is temporarily registered. Please try again after registering your account',
                '50005': 'Currently, self account is locked. Please contact support',
                '50006': 'Currently, self account is locked. Please contact support',
                '50008': 'User identification has not been completed',
                '50009': 'Your order does not exist',
                '50010': 'Can not cancel specified order',
                '50011': 'API not found',
                '60001': 'The number of possessions is insufficient',
                '60002': 'It exceeds the quantity upper limit of the tender buying order',
                '60003': 'The specified quantity exceeds the limit',
                '60004': 'The specified quantity is below the threshold',
                '60005': 'The specified price is above the limit',
                '60006': 'The specified price is below the lower limit',
                '70001': 'A system error occurred. Please contact support',
                '70002': 'A system error occurred. Please contact support',
                '70003': 'A system error occurred. Please contact support',
                '70004': 'We are unable to accept orders as the transaction is currently suspended',
                '70005': 'Order can not be accepted because purchase order is currently suspended',
                '70006': 'We can not accept orders because we are currently unsubscribed ',
            }
            errorClasses = {
                '20001': AuthenticationError,
                '20002': AuthenticationError,
                '20003': AuthenticationError,
                '20005': AuthenticationError,
                '20004': InvalidNonce,
                '40020': InvalidOrder,
                '40021': InvalidOrder,
                '40013': OrderNotFound,
                '40014': OrderNotFound,
                '50008': PermissionDenied,
                '50009': OrderNotFound,
                '50010': OrderNotFound,
                '60001': InsufficientFunds,
            }
            code = self.safe_string(data, 'code')
            message = self.safe_string(errorMessages, code, 'Error')
            ErrorClass = self.safe_value(errorClasses, code)
            if ErrorClass is not None:
                raise ErrorClass(message)
            else:
                raise ExchangeError(self.id + ' ' + self.json(response))
        return response
