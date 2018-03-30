# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.base.exchange import Exchange
from ccxt.base.errors import ExchangeError

import time


class bitso (Exchange):

    def describe(self):
        return self.deep_extend(super(bitso, self).describe(), {
            'id': 'bitso',
            'name': 'Bitso',
            'countries': 'MX',  # Mexico
            'rateLimit': 2000,  # 30 requests per minute
            'version': 'v3',
            'has': {
                'CORS': True,
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766335-715ce7aa-5ed5-11e7-88a8-173a27bb30fe.jpg',
                'api': 'https://api.bitso.com',
                'www': 'https://bitso.com',
                'doc': 'https://bitso.com/api_info',
                'fees': 'https://bitso.com/fees?l=es',
            },
            'api': {
                'public': {
                    'get': [
                        'available_books',
                        'ticker',
                        'order_book',
                        'trades',
                    ],
                },
                'private': {
                    'get': [
                        'account_status',
                        'balance',
                        'fees',
                        'fundings',
                        'fundings/{fid}',
                        'funding_destination',
                        'kyc_documents',
                        'ledger',
                        'ledger/trades',
                        'ledger/fees',
                        'ledger/fundings',
                        'ledger/withdrawals',
                        'mx_bank_codes',
                        'open_orders',
                        'order_trades/{oid}',
                        'orders/{oid}',
                        'user_trades',
                        'user_trades/{tid}',
                        'withdrawals/',
                        'withdrawals/{wid}',
                    ],
                    'post': [
                        'bitcoin_withdrawal',
                        'debit_card_withdrawal',
                        'ether_withdrawal',
                        'orders',
                        'phone_number',
                        'phone_verification',
                        'phone_withdrawal',
                        'spei_withdrawal',
                    ],
                    'delete': [
                        'orders/{oid}',
                        'orders/all',
                    ],
                },
            },
        })

    def fetch_markets(self):
        markets = self.publicGetAvailableBooks()
        result = []
        for i in range(0, len(markets['payload'])):
            market = markets['payload'][i]
            id = market['book']
            symbol = id.upper().replace('_', '/')
            base, quote = symbol.split('/')
            limits = {
                'amount': {
                    'min': float(market['minimum_amount']),
                    'max': float(market['maximum_amount']),
                },
                'price': {
                    'min': float(market['minimum_price']),
                    'max': float(market['maximum_price']),
                },
                'cost': {
                    'min': float(market['minimum_value']),
                    'max': float(market['maximum_value']),
                },
            }
            precision = {
                'amount': self.precision_from_string(market['minimum_amount']),
                'price': self.precision_from_string(market['minimum_price']),
            }
            lot = limits['amount']['min']
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'info': market,
                'lot': lot,
                'limits': limits,
                'precision': precision,
            })
        return result

    def load_fees(self):
        self.load_markets()
        self.fees['trading']['taker'] = {}
        self.fees['trading']['maker'] = {}
        response = self.privateGetFees()
        fees = response['payload']['fees']
        for fee in fees:
            self.fees['trading']['taker'][fee['book']] = fee['fee_decimal']

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.privateGetBalance()
        balances = response['payload']['balances']
        result = {'info': response}
        for b in range(0, len(balances)):
            balance = balances[b]
            currency = balance['currency'].upper()
            account = {
                'free': float(balance['available']),
                'used': float(balance['locked']),
                'total': float(balance['total']),
            }
            result[currency] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, limit=None, params={}):
        self.load_markets()
        response = self.publicGetOrderBook(self.extend({
            'book': self.market_id(symbol),
        }, params))
        orderbook = response['payload']
        timestamp = self.parse8601(orderbook['updated_at'])
        return self.parse_order_book(orderbook, timestamp, 'bids', 'asks', 'price', 'amount')

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        response = self.publicGetTicker(self.extend({
            'book': self.market_id(symbol),
        }, params))
        ticker = response['payload']
        timestamp = self.parse8601(ticker['created_at'])
        vwap = float(ticker['vwap'])
        baseVolume = float(ticker['volume'])
        quoteVolume = baseVolume * vwap
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'bid': float(ticker['bid']),
            'ask': float(ticker['ask']),
            'vwap': vwap,
            'open': None,
            'close': None,
            'first': None,
            'last': float(ticker['last']),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': baseVolume,
            'quoteVolume': quoteVolume,
            'info': ticker,
        }

    def parse_trade(self, trade, market=None):
        timestamp = self.parse8601(trade['created_at'])
        symbol = None
        if market is None:
            marketId = self.safe_string(trade, 'book')
            if marketId in self.markets_by_id:
                market = self.markets_by_id[marketId]
        if market is not None:
            symbol = market['symbol']
        side = self.safe_string(trade, 'side')
        if side is None:
            side = self.safe_string(trade, 'maker_side')
        amount = self.safe_float(trade, 'amount')
        if amount is None:
            amount = self.safe_float(trade, 'major')
        if amount is not None:
            amount = abs(amount)
        fee = None
        feeCost = self.safe_float(trade, 'fees_amount')
        if feeCost is not None:
            feeCurrency = self.safe_string(trade, 'fees_currency')
            if feeCurrency is not None:
                if feeCurrency in self.currencies_by_id:
                    feeCurrency = self.currencies_by_id[feeCurrency]['code']
            fee = {
                'cost': feeCost,
                'currency': feeCurrency,
            }
        cost = self.safe_float(trade, 'minor')
        if cost is not None:
            cost = abs(cost)
        price = self.safe_float(trade, 'price')
        orderId = self.safe_string(trade, 'oid')
        return {
            'id': str(trade['tid']),
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'order': orderId,
            'type': None,
            'side': side,
            'price': price,
            'amount': amount,
            'cost': cost,
            'fee': fee,
        }

    def fetch_trades(self, symbol, since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetTrades(self.extend({
            'book': market['id'],
        }, params))
        return self.parse_trades(response['payload'], market, since, limit)

    def fetch_my_trades(self, symbol=None, since=None, limit=25, params={}):
        self.load_markets()
        market = self.market(symbol)
        # the don't support fetching trades starting from a date yet
        # use the `marker` extra param for that
        # self is not a typo, the variable name is 'marker'(don't confuse with 'market')
        markerInParams = ('marker' in list(params.keys()))
        # warn the user with an exception if the user wants to filter
        # starting from since timestamp, but does not set the trade id with an extra 'marker' param
        if (since is not None) and not markerInParams:
            raise ExchangeError(self.id + ' fetchMyTrades does not support fetching trades starting from a timestamp with the `since` argument, use the `marker` extra param to filter starting from an integer trade id')
        # convert it to an integer unconditionally
        if markerInParams:
            params = self.extend(params, {
                'marker': int(params['marker']),
            })
        request = {
            'book': market['id'],
            'limit': limit,  # default = 25, max = 100
            # 'sort': 'desc',  # default = desc
            # 'marker': id,  # integer id to start from
        }
        response = self.privateGetUserTrades(self.extend(request, params))
        return self.parse_trades(response['payload'], market, since, limit)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        order = {
            'book': self.market_id(symbol),
            'side': side,
            'type': type,
            'major': self.amount_to_precision(symbol, amount),
        }
        if type == 'limit':
            order['price'] = price

        response = self.privatePostOrders(self.extend(order, params))
        return {
            'info': response,
            'id': response['payload']['oid'],
        }

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        return self.privateDeleteOrdersOid({'oid': id})

    def parse_order_status(self, status):
        statuses = {
            'partial-fill': 'open',  # self is a common substitution in ccxt
        }
        if status in statuses:
            return statuses['status']
        return status

    def parse_order(self, order, market=None):
        side = order['side']
        status = self.parse_order_status(order['status'])
        symbol = None
        if market is None:
            marketId = order['book']
            if marketId in self.markets_by_id:
                market = self.markets_by_id[marketId]
        if market:
            symbol = market['symbol']
        orderType = order['type']
        timestamp = self.parse8601(order['created_at'])
        amount = float(order['original_amount'])
        remaining = float(order['unfilled_amount'])
        filled = amount - remaining
        result = {
            'info': order,
            'id': order['oid'],
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'type': orderType,
            'side': side,
            'price': self.safe_float(order, 'price'),
            'amount': amount,
            'cost': None,
            'remaining': remaining,
            'filled': filled,
            'status': status,
            'fee': None,
        }
        return result

    def fetch_open_orders(self, symbol=None, since=None, limit=25, params={}):
        self.load_markets()
        market = self.market(symbol)
        # the don't support fetching trades starting from a date yet
        # use the `marker` extra param for that
        # self is not a typo, the variable name is 'marker'(don't confuse with 'market')
        markerInParams = ('marker' in list(params.keys()))
        # warn the user with an exception if the user wants to filter
        # starting from since timestamp, but does not set the trade id with an extra 'marker' param
        if (since is not None) and not markerInParams:
            raise ExchangeError(self.id + ' fetchOpenOrders does not support fetching orders starting from a timestamp with the `since` argument, use the `marker` extra param to filter starting from an integer trade id')
        # convert it to an integer unconditionally
        if markerInParams:
            params = self.extend(params, {
                'marker': int(params['marker']),
            })
        request = {
            'book': market['id'],
            'limit': limit,  # default = 25, max = 100
            # 'sort': 'desc',  # default = desc
            # 'marker': id,  # integer id to start from
        }
        response = self.privateGetOpenOrders(self.extend(request, params))
        orders = self.parse_orders(response['payload'], market, since, limit)
        return orders

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        endpoint = '/' + self.version + '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if method == 'GET':
            if query:
                endpoint += '?' + self.urlencode(query)
        url = self.urls['api'] + endpoint
        if api == 'private':
            self.check_required_credentials()
            nonce = str(self.nonce())
            request = ''.join([nonce, method, endpoint])
            if method != 'GET':
                if query:
                    body = self.json(query)
                    request += body
            signature = self.hmac(self.encode(request), self.encode(self.secret))
            auth = self.apiKey + ':' + nonce + ':' + signature
            headers = {
                'Authorization': 'Bitso ' + auth,
                'Content-Type': 'application/json',
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'success' in response:
            if response['success']:
                return response
        raise ExchangeError(self.id + ' ' + self.json(response))
